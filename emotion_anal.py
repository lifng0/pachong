from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import json
import os


def emotion(film_data):
    emotion_lib = []
    c_json = film_data
    for row in c_json:
        comment_content = row.get('comment_content')
        semantic_cls = pipeline(Tasks.text_classification,'iic/nlp_structbert_sentiment-classification_chinese-base',device="cuda")
        result = semantic_cls(input=comment_content)
        sorted_lables_scores = sorted(zip(result['labels'], result['scores']),key=lambda x:x[0] == '正面', reverse=True)
        positive_lable,positive_probs = sorted_lables_scores[0]
        negative_lable,negative_probs = sorted_lables_scores[1]
        is_positive = 1 if positive_probs >= negative_probs else 0
        key_list = ['is_positive','positive_probs','negative_probs']
        value = {'is_positive':is_positive,'positive_probs':format(positive_probs,'.4f'),'negative_probs':format(negative_probs,'.4f')}
        emotion_lib.append(value)
    return json.dumps(emotion_lib,  ensure_ascii=False, indent=4)
if __name__ == "__main__":
    with open("test_comment.json","r",encoding="utf-8") as f:
        data = json.loads(f.read())
    output = emotion(data)
    with open("output.txt","w") as f:
        f.write(output)
    print(1)