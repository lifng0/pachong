import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json

from crawler_film import film_name

headers = {
    'user-agent':
'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
    'Cookie':'6333762c95037d16=Ld09bfpg8mds4jw8i04xop5uzvV0AEw60ECm9ru3yWew0Yss8Bwj0vsKZr%2FYJdrlB%2BFX%2FXme7kk8LXHHhzOnz7UQE3JY%2B8ccm6lAOHCURqa8E2E1%2Fx0H5ON0%2BRVaXU3v5fzaBvWs6ChA5GKMZpBc3%2FcY5RulUDrHnHck4nqWDncxaGhOiDObCCmwNZ%2BbmfONNAGazkRhnt3o8zoq79gsxZSCV57qPZi4bb1kX4njFARATV5iLc03hVP0VB0La6V%2BWE6AqUu9Ai1cyK0Wg2jxgZtJ%2FICZDoStcufnXc1CvIoE13EuOp3c4w%3D%3D; _TDID_CK=1746112423612; bid=5duzgNo--48; _pk_id.100001.4cf6=15207e036b2a31d8.1743593729.; __yadk_uid=bic1cyUzaJteTdgLNflCDjTLC9uUi2Dt; ll="118318"; _vwo_uuid_v2=D15111954AAD860312E19CFB3C10FF757|dcd77b28f269eda7a6e5e5a3d522d697; dbcl2="288466461:zGBUqCsMhpE"; push_noty_num=0; push_doumail_num=0; __utmv=30149280.28846; ck=KgOD; __utmc=30149280; __utmc=223695111; __utmz=223695111.1746111521.3.2.utmcsr=ntp.msn.cn|utmccn=(referral)|utmcmd=referral|utmcct=/; frodotk_db="84571b718d4143d28d055254a7c3cb76"; __utma=223695111.1332976608.1743593730.1746153123.1746155438.5; _pk_ref.100001.4cf6=%5B%22%22%2C%22%22%2C1746161564%2C%22https%3A%2F%2Fntp.msn.cn%2F%22%5D; _pk_ses.100001.4cf6=1; ap_v=0,6.0; __utma=30149280.2043400998.1743593730.1746155438.1746161636.6; __utmz=30149280.1746161636.6.3.utmcsr=movie.douban.com|utmccn=(referral)|utmcmd=referral|utmcct=/subject/1292052/comments; __utmt=1; __utmb=30149280.2.10.1746161636',
}
def crawler(film_id):
    base_url = f'https://movie.douban.com/subject/{film_id}/comments?&limit=20&status=P&sort=new_score&start='
    pages = 1
    comment_lib = []
    for page in range(pages):
        url = base_url + str(page * 20)
        resp = requests.get(url, headers=headers)
        print(resp.status_code)
        bs = BeautifulSoup(resp.text, 'html.parser')
        film_name = bs.h1.get_text()
        # time.sleep(random.uniform(1,2))
        for comment_item in bs.find_all('div', {'class': 'comment-item'}):
            id = comment_item['data-cid']
            time_span = comment_item.find('span', class_='comment-time')
            time_string = time_span.get('title')
            time_format = '%Y-%m-%d %H:%M:%S'
            timestamp = int(datetime.strptime(time_string, time_format).timestamp())
            comment_content = comment_item.find('span', {'class': 'short'}).get_text()
            user_name = comment_item.find('a').get('title')
            comment_popular = comment_item.find('span', {'class': 'votes vote-count'}).get_text()
            star_span = comment_item.find('span', {'class': lambda x: x and x.startswith('allstar')})
            comment_rating = []
            if star_span and star_span.has_attr('class'):
                star_class = star_span['class'][0]
                comment_rating = star_class[-2]
            else:
                continue

            comment = {
                'film_name': film_name,
                'comment_id': id,
                'comment_username': user_name,
                'comment_timestamp': timestamp,
                'comment_rating': comment_rating,
                'comment_content': comment_content,
                'comment_popular': comment_popular
            }
            comment_lib.append(comment)

    with open(f'{film_id}.json', 'w', encoding='utf-8') as f:
        json.dump(comment_lib, f, ensure_ascii=False, indent=4)
