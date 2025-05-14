import matplotlib.pyplot as plt
from wordcloud import WordCloud
import json
import jieba
import os
from datetime import datetime
from collections import Counter
from pylab import mpl



def generate_visuals(mode,item_id):
    mpl.rcParams["font.sans-serif"] = ["SimHei"]
    mpl.rcParams["axes.unicode_minus"] = False  

    assert mode in ['movie', 'book'], 'mode must be movie or book'

    comment_path = f'data/{mode}/comment/{item_id}.json'
    emotion_path = f'data/{mode}/emotion/{item_id}.json'
    output_dir = f'static/visuals/{mode}/{item_id}'
    os.makedirs(output_dir, exist_ok=True)

    with open(comment_path, 'r', encoding='utf-8') as f:
        comments = json.load(f)
    with open(emotion_path, 'r', encoding='utf-8') as f:
        emotions = json.load(f)

    # 1. 饼图
    if os.path.exists(f"{output_dir}/pie.png") != 1:
        pos_count = sum(1 for e in emotions if e['is_positive'] == 1)
        neg_count = len(emotions) - pos_count
        labels = ['正面', '负面']
        sizes = [pos_count, neg_count]
        plt.figure()
        plt.pie(sizes, labels=labels, autopct='%1.1f%%', colors=['green', 'red'])
        plt.title('好评率饼图')
        plt.savefig(f'{output_dir}/pie.png')
        plt.close()

    # 2. 词云图
    if os.path.exists(f"{output_dir}/wordcloud.png") != 1:
        all_text = ''.join(comment['comment_content'] for comment in comments)
        cut_text = ' '.join(jieba.lcut(all_text))
        with open("useless.txt","r",encoding="utf-8") as f:
            stopwords = f.read()
        stopwords = ['\n',' ',''] + stopwords.split()
        wordcloud = WordCloud(font_path='simhei.ttf', background_color='white', width=800, height=400,stopwords = stopwords).generate(cut_text)
        plt.figure(figsize=(10, 5))
        plt.imshow(wordcloud, interpolation='bilinear')
        plt.axis('off')
        plt.title('热词云图')
        plt.savefig(f'{output_dir}/wordcloud.png')
        plt.close()

    # 3. 柱状图
    if os.path.exists(f"{output_dir}/bar.png") != 1:
        total = len(emotions)
        plt.bar(['正面', '负面', '总计'], [pos_count, neg_count, total], color=['green', 'red', 'gray'])
        plt.title('评论数量柱状图')
        plt.savefig(f'{output_dir}/bar.png')
        plt.close()

    # 4.分数图
    if os.path.exists(f"{output_dir}/star.png") != 1:
        rating_list = [0,0,0,0,0]
        for comment in comments:
            rating_list[comment["comment_rating"]-1] += 1
        plt.bar(['一星', '二星', '三星','四星','五星'], rating_list, color=['red','brown','gray','yellow','green'])
        plt.title('评价星级图')
        plt.savefig(f'{output_dir}/star.png')
        plt.close()
