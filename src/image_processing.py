import os
import urllib.request
import json
import boto3

def get_telegram_file_path(file_id):
    tokenTelegram = os.getenv('tokenTelegram')
    url = f"https://api.telegram.org/bot{tokenTelegram}/getFile?file_id={file_id}"
    with urllib.request.urlopen(url) as response:
        data = json.load(response)
        return data['result']['file_path']

def download_image(url):
    with urllib.request.urlopen(url) as response:
        return response.read()

def store_image_in_s3(chat_id, image_data):
    s3 = boto3.client('s3')
    s3_bucket_name = os.getenv('bucketName')
    s3.put_object(Bucket=s3_bucket_name, Key=f'{chat_id}/image.jpg', Body=image_data)
