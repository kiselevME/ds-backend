import requests


class ImageProviderClient:
    def __init__(self, host: str):
        self.host = host

    def get_image(self, image_id: int, timeout: int = 1) -> str:
        res = requests.get(url=f'{self.host}/images/{image_id}',
                           timeout=timeout)

        return res.content
