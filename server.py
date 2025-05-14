from sanic import Sanic, response
from sanic.response import html, json as sanic_json
from package import package_results
from draw_picture import generate_visuals
import os
import json
import time
import glob

app = Sanic("MovieAnalysis")
app.static("/static", "./static")

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
            movie_data = [
        {   
            "film_name" : "三体",
            "book_id": "6518605",
            "comment_id": "3678666406",
            "comment_username": "世明",
            "comment_timestamp": 1675433363,
            "comment_location": "天津",
            "comment_rating": 5,
            "comment_content": "我感觉读完三体我不是我了",
            "comment_isuseful": 0
        },
        {
            "book_id": "6518605",
            "comment_id": "3678524581",
            "comment_username": "上善若水",
            "comment_timestamp": 1675427550,
            "comment_location": "湖北",
            "comment_rating": 5,
            "comment_content": "不谈宇宙的宏观与生命体的微小，光是人性的善与恶就足够深刻的体会。",
            "comment_isuseful": 0
        },
        {
            "book_id": "6518605",
            "comment_id": "3678485751",
            "comment_username": "有序度在降低",
            "comment_timestamp": 1675425657,
            "comment_location": "山东",
            "comment_rating": 5,
            "comment_content": "只能满分了",
            "comment_isuseful": 0
        },
        {
            "book_id": "6518605",
            "comment_id": "3678389545",
            "comment_username": "笑脸",
            "comment_timestamp": 1675420298,
            "comment_location": "北京",
            "comment_rating": 5,
            "comment_content": "脑洞很大，力荐。\n人多渺小，作者带你贯穿宇宙纪元。\n提升宇宙观的佳作。",
            "comment_isuseful": 0
        },
        {
            "book_id": "6518605",
            "comment_id": "3678221270",
            "comment_username": "罗伯斯庇尔",
            "comment_timestamp": 1675410677,
            "comment_location": "天津",
            "comment_rating": 1,
            "comment_content": "随着年龄的增长，我越来越厌恶这本书",
            "comment_isuseful": 0
        },
        {
            "book_id": "6518605",
            "comment_id": "3678104235",
            "comment_username": "喏，次饼干",
            "comment_timestamp": 1675403789,
            "comment_location": "江苏",
            "comment_rating": 5,
            "comment_content": "不管在哪，人性都不会让人失望\n宇宙如此宏大，我有个猜想，我们所说的神仙不就是高维度群体，因为高维度意味着拥有更多选择和干预事物的能力",
            "comment_isuseful": 0
        },
        {
            "book_id": "6518605",
            "comment_id": "3678027580",
            "comment_username": "小D发呆是常态",
            "comment_timestamp": 1675399236,
            "comment_location": "山东",
            "comment_rating": 5,
            "comment_content": "2022年底，三体电视剧开播之前看完了全三部，感觉今后每一次抬头看星空都仿佛看见命运的齿轮在暗夜里一直缓缓转动，从古到今从未停止过。",
            "comment_isuseful": 0
        }]
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
            positive = sum(1 for r in comment["reviews"] if r["rating"] >=4 )
            total = len(comment["reviews"])
            analysis = {
                "id": movie_id,
                "positive_rate": f"{(positive/total)*100:.1f}%",
                "avg_rating": sum(r["rating"] for r in comment["reviews"]) / total,
                "hot_score": total * 2.5  # 模拟热度计算
            }
            with open(f'{DATA_DIR}/movie/emotion/{movie_id}.json',"w"):
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
    generate_visuals(mode, item_id)
    package_results(mode, item_id)
    clean_old_files(mode = mode)
    return await response.file(
        os.path.join(CURRENT_DIR, "templates", "show.html")
    )


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