import requests

class FBBService:
    def __init__(self, access_token: str, insta_account: str):
        self.access_token = access_token
        self.insta_acc_id = insta_account
        self.base_url = 'https://graph.facebook.com/v22.0'

    def _create_media(self, caption: str, image_url: str):
        url = f"https://graph.facebook.com/v22.0/{self.insta_acc_id}/media?access_token={self.access_token}"
        payload = {
            "caption": caption,
            "image_url": image_url
        }
        response = requests.post(url, data=payload)
        
        print(f"Media creation res: {response.text}")
        
        if response.status_code == 200:
            return response.json()["id"]
        else:
            return None

    def _publish_media(self, media_id: str):
        url = f"https://graph.facebook.com/v22.0/{self.insta_acc_id}/media_publish?access_token={self.access_token}"
        payload = {
            "creation_id": media_id
        }
        response = requests.post(url, data=payload)
        
        print(f"Media publication res: {response.text}")

        if response.status_code == 200:
            return response.json()["id"]
        else:
            return None

    def send_post(self, caption: str, image_url: str) -> str:
        media_id = self._create_media(caption, image_url)
        if media_id:
            return self._publish_media(media_id)
        else:
            return None
