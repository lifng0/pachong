import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import time
import random

headers = {
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36 Edg/135.0.0.0',
    'Cookie': '6333762c95037d16=qgPGaLGHOLWfL8LGlgoWE4w01W735UF1mwpdzcCC8IaDOBJr4wLzigg7V5zvKKbnZaDf17Z78Jpu%2Bu5qqK%2BaUOrwEV1V2G0p56SNH5c00oqs760bPa7K1jXkxn5tLDo06RHwG0RY03qgKCNEvgIywHyGHNjxgEEcvjodQZA46TSDfJfvHaLquMICVecGgdkTmmqmTVs0vBRPS2rr15h8m2As5Jukdf84QVe%2F4PyknHZF8rawlQILgi4CDyf7xRRWgQ8j6K1EpuV%2FmeydmrgSFEPsyak2suWJXFdQdUIpa7f8X%2FEdQBskpA%3D%3D; _TDID_CK=1747666848062; ll="118318"; bid=A40cF04mKZI; __utmz=30149280.1743322459.1.1.utmcsr=cn.bing.com|utmccn=(referral)|utmcmd=referral|utmcct=/; __utmv=30149280.28806; __utmz=81379588.1743322679.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); _pk_id.100001.3ac3=18167503bf9c78de.1743322679.; _vwo_uuid_v2=D9CE31149EEEBB508B6664973BB93BD36|6f451e8f163754af08f47967c0ae259c; __yadk_uid=GYViX8c1hexRaf0DG90SknHVVlcxhiQy; ap_v=0,6.0; __utma=30149280.88765349.1743322459.1743322459.1747664769.2; __utmc=30149280; dbcl2="288063378:e2GYp5tqhKw"; ck=fR32; push_noty_num=0; push_doumail_num=0; frodotk_db="4fcc8b933e5de83cef65a2b9bb19b8b4"; __utma=81379588.2074737077.1743322679.1743322679.1747666125.2; __utmc=81379588; _pk_ses.100001.3ac3=1; _gid=GA1.2.1921254748.1747666277; __utmt=1; __utmt=1; _ga=GA1.2.1124582434.1743322691; _ga_Y4GN1R87RG=GS2.1.s1747666276$o2$g1$t1747666801$j0$l0$h0; __utmt_douban=1; __utmb=30149280.13.10.1747664769; __utmb=81379588.7.10.1747666125'
}


def book_crawler(book_id):
    base_url = f'https://book.douban.com/subject/{book_id}/reviews?start='
    pages = 1
    comment_lib = []
    for page in range(pages):
        url = base_url + str(page * 20)
        resp = requests.get(url, headers=headers)
        time.sleep(random.uniform(1, 2))
        bs = BeautifulSoup(resp.text, 'html.parser')
        book_name = bs.h1.text.strip()
        for comment_item in bs.find_all('div', class_='main review-item'):
            comment_id = comment_item.get('data-cid', '')
            time_span = comment_item.find('span', class_='main-meta')
            time_string = time_span.text.strip()
            timestamp = int(datetime.strptime(time_string, '%Y-%m-%d %H:%M:%S').timestamp())
            user_name = comment_item.find('a', class_='name').text.strip()
            rating_span = comment_item.find('span', class_='main-title-rating')
            rating_map = {'力荐': 5, '推荐': 4, '还行': 3, '较差': 2, '很差': 1}
            comment_rating = rating_map.get(rating_span['title'].strip(), "") if rating_span and rating_span.has_attr(
                'title') else ""
            comment_content = comment_item.find('div', class_='short-content').text.strip()
            comment_popular = comment_item.find('span', class_='count').text.strip()

            comment = {
                'book_name': book_name,
                'comment_id': comment_id,
                'comment_username': user_name,
                'comment_timestamp': timestamp,
                'comment_rating': comment_rating,
                'comment_content': comment_content,
                'comment_popular': comment_popular
            }
            comment_lib.append(comment)

    print(f"成功爬取id为{book_id}的书评")
    return comment_lib

if __name__ == "__main__":
    data = book_crawler('1007305')
    with open("douban_book_comments.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(1)