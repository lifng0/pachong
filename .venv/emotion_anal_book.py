from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
import json

def emotion(book_data):
    semantic_cls = pipeline(Tasks.text_classification,
                            'iic/nlp_structbert_sentiment-classification_chinese-base',
                            device="cuda")
    emotion_lib = []
    c_json = book_data  
    for row in c_json:
        output_row = {
            'book_name': row.get('book_name'),
            'comment_id': row.get('comment_id'),
            'comment_username': row.get('comment_username'),
            'comment_timestamp': row.get('comment_timestamp'),
            'comment_rating': row.get('comment_rating'),
            'comment_content': row.get('comment_content'),
            'comment_popular': row.get('comment_popular')
        }
        comment_content = row.get('comment_content')
        result = semantic_cls(input=comment_content)
        sorted_lables_scores = sorted(zip(result['labels'], result['scores']),
                                      key=lambda x: x[0] == '正面', reverse=True)
        positive_lable, positive_probs = sorted_lables_scores[0]
        negative_lable, negative_probs = sorted_lables_scores[1]
        is_positive = 1 if positive_probs >= negative_probs else 0
        output_row.update({
            'sentiment_analysis': {
                'is_positive': is_positive,
                'positive_probs': format(positive_probs, '.4f'),
                'negative_probs': format(negative_probs, '.4f')
            }
        })
        emotion_lib.append(output_row)
    return json.dumps(emotion_lib, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    with open("douban_book_comments.json", "r", encoding="utf-8") as f:
        data = json.loads(f.read())
    output = emotion(data)
    with open("book_sentiment_output.json", "w", encoding="utf-8") as f:
        f.write(output)

    print(1)