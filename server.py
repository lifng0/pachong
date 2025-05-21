from sanic import Sanic, response
from sanic.response import html, json as sanic_json
from sanic.exceptions import SanicException
from package import package_results
from draw_picture import generate_visuals
from emotion_anal import emotion
from crawler_film1 import crawler
import os
import json
import time
import glob

app = Sanic("MovieAnalysis")
app.static("/static", "./static")

MAX_FILE_SIZE = 10 * 1024 * 1024
MAX_FILES = 50
DATA_DIR = "./data"
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(f"{DATA_DIR}/movie/comment",exist_ok=True)
os.makedirs(f"{DATA_DIR}/movie/emotion",exist_ok=True)
os.makedirs(f"{DATA_DIR}/book/comment",exist_ok=True)
os.makedirs(f"{DATA_DIR}/book/emotion",exist_ok=True)

def clean_old_files(base_path='static/visuals',mode = "movie", expire_seconds=86400):  # 24h
    now = time.time()
    base_path += f"/{mode}"
    for folder in os.listdir(base_path):
        full_path = os.path.join(base_path, folder)
        if os.path.isdir(full_path):
            last_modified = os.path.getmtime(full_path)
            if now - last_modified > expire_seconds:
                import shutil
                shutil.rmtree(full_path)
                print(f"[清理] 删除了过期文件夹: {full_path}")

    # 清理 ZIP 文件
    for file in os.listdir(base_path):
        if file.endswith('.zip'):
            full_path = os.path.join(base_path, file)
            last_modified = os.path.getmtime(full_path)
            if now - last_modified > expire_seconds:
                os.remove(full_path)
                print(f"[清理] 删除了过期压缩包: {full_path}")


def cleanup_old_files(location:str):
    files = glob.glob(os.path.join(location,"*.json"))
    files.sort(key=lambda x: os.path.getmtime(x))
    num_to_delete = len(files) - MAX_FILES
    if num_to_delete > 0:
        for old_file in files[:num_to_delete]:  
            os.remove(old_file)
            print(f"已清理文件{old_file}")

@app.get("/welcome")
async def welcome(request):
    file_path = os.path.join(CURRENT_DIR, "templates")
    file_path = os.path.join(file_path,"welcome.html")
    return await response.file(file_path,headers={"Content-Type": "text/html; charset=utf-8"})

@app.post("/movie/process/<movie_id:int>")
async def process_movie(request,movie_id):
    if os.path.exists(f"{DATA_DIR}/movie/comment/{movie_id}.json"):
        with open(f"{DATA_DIR}/movie/comment/{movie_id}.json","r") as f:
            movie_data = json.load(f)
        return sanic_json({"status":"success","massage":"数据已经存在，跳过爬取过程","name":movie_data[0]["film_name"]})
    else:
        try:
            movie_data = crawler(movie_id)
            name = movie_data[0]["film_name"]
            with open(f"{DATA_DIR}/movie/comment/{movie_id}.json","w") as f:
                json.dump(movie_data,f)
            cleanup_old_files(f"{DATA_DIR}/movie/comment/")
            return sanic_json({"status":"success","massage":"成功爬取数据","name":name})
        except Exception as e:
            return sanic_json({"error":f"爬虫失败:{str(e)}"})
    
@app.post("/movie/emotion/<movie_id:int>")
async def movie_emotion(request,movie_id):
    if os.path.exists(f"{DATA_DIR}/movie/emotion/{movie_id}.json"):
        return sanic_json({"status":"success","massage":"目标已经存在"})
    else:
        if os.path.exists(f"{DATA_DIR}/movie/comment/{movie_id}.json"):
            with open(f"{DATA_DIR}/movie/comment/{movie_id}.json") as f:
                comment = json.load(f)
                analysis = emotion(comment)
            with open(f'{DATA_DIR}/movie/emotion/{movie_id}.json',"w") as f:
                json.dump(analysis, f)
            cleanup_old_files(f"{DATA_DIR}/movie/emotion/")
            return sanic_json({"status":"success","massage":"分析已经完成"})
        else:
            return sanic_json({"error":f"未找到comment {movie_id}"})
    
@app.get("/show")
async def show_analysis(request):
    item_id = request.args.get('id')
    mode = request.args.get('mode')  
    name = request.args.get("name")
    if not item_id or mode not in ['movie', 'book']:
        return "参数错误", 400
    clean_old_files(mode = mode)
    generate_visuals(mode, item_id)
    package_results(mode, item_id)
    return await response.file(

        os.path.join(CURRENT_DIR, "templates", "show.html")
    )

@app.post("/update/<mode>/<the_type>")
async def update_files(request,mode,the_type):
    if mode not in ['movie', 'book']:
        raise SanicException("无效的模式", status_code=400)
    
    if 'file' not in request.files:
        raise SanicException("未收到文件", status_code=400)
    
    uploaded_files = request.files.get('file')

    the_file = uploaded_files
    
    # 检查文件大小
    if len(the_file.name) > MAX_FILE_SIZE:
        raise SanicException("文件过大，最大限制10MB", status_code=400)
    
    # 检查文件扩展名
    if not the_file.name.endswith(".json"):
        raise SanicException("不支持的文件类型", status_code=400)
    
    
    with open(f"{DATA_DIR}/{mode}/{the_type}/{the_file.name}","wb") as f:
        f.write(the_file.body)
    
    return response.json({
        "success": True,
        "message": f"文件 {the_file.name} 上传成功至 {mode}/{the_type}"
    })

@app.route('/download/<mode>/<item_id>/<name>')
async def download(request, mode, item_id,name):
    zip_path = f'static/visuals/{mode}/{item_id}/{item_id}.zip'
    if not os.path.exists(zip_path):
        return "文件不存在", 404
    return await response.file(
        zip_path,
        filename=f"{name}.zip", 
        mime_type="application/zip"
    )
if __name__ == "__main__":
    app.run()