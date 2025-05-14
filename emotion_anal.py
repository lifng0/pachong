from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import json
import os


def emotion(filmname):
    emotion_lib = []
    file_name = f'C:/Users/22762/PycharmProjects/crawler_doubanfilm/{filmname}.json'
    with open(file_name,encoding='utf-8') as f:
        c_json = json.load(f)
    for row in c_json:
        comment_content = row.get('comment_content')
        print(comment_content)
        semantic_cls = pipeline(Tasks.text_classification,'iic/nlp_structbert_sentiment-classification_chinese-base')
        result = semantic_cls(input=comment_content)
        print(result)
        sorted_lables_scores = sorted(zip(result['labels'], result['scores']),key=lambda x:x[0] == '正面', reverse=True)
        positive_lable,positive_probs = sorted_lables_scores[0]
        negative_lable,negative_probs = sorted_lables_scores[1]
        is_positive = 1 if positive_probs >= negative_probs else 0
        print(is_positive,positive_probs,negative_probs)
        key_list = ['is_positive','positive_probs','negative_probs']
        value = {'is_positive':is_positive,'positive_probs':format(positive_probs,'.4f'),'negative_probs':format(negative_probs,'.4f')}
        emotion_lib.append(value)
    with open(f'{filmname}_emotion.json', 'w', encoding='utf-8') as f:
        json.dump(emotion_lib, f, ensure_ascii=False, indent=4)
emotion('肖申克的救赎')
print(1)