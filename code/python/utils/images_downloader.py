import requests
import os


class ImageRenderDownloader():
    def __init__(self,anime_id,image_url_path):
        self.image_directory_path = 'images/covers/'
        self.anime_id = anime_id
        self.image_url_path = image_url_path
        

    def download(self):
        target_url = self.image_url_path
        target_directory = f'{self.image_directory_path}{self.anime_id}.jpg'

        if os.path.isfile(target_directory):
            return target_directory
        else:
            r = requests.get(target_url, allow_redirects=True)
            if r.status_code == 200:
                open(target_directory, 'wb').write(r.content)
                return target_directory
            else:
                return None