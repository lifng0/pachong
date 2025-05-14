import zipfile
import os

def package_results(mode, item_id):
    assert mode in ['movie', 'book']
    output_dir = f'static/visuals/{mode}/{item_id}'
    zip_path = f'static/visuals/{mode}/{item_id}/{item_id}.zip'
    if os.path.exists(f'static/visuals/{mode}/{item_id}/{item_id}.zip') != 1:
        with zipfile.ZipFile(zip_path, 'w') as z:
            for file in os.listdir(output_dir):
                if file != f"{item_id}.zip":
                    z.write(os.path.join(output_dir, file), arcname=file)
            z.write(f'data/{mode}/comment/{item_id}.json', arcname='comment.json')
            z.write(f'data/{mode}/emotion/{item_id}.json', arcname='emotion.json')
    return zip_path