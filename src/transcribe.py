import datetime
import json
import os
import time
import urllib.request

import boto3

transcribe = boto3.client('transcribe')
s3 = boto3.client('s3')

def get_telegram_file_path(file_id):
    print("def get_telegram_file_path(file_id):")
    # Obter o caminho do arquivo no Telegram
    tokenTelegram = os.getenv('tokenTelegram')
    url = f"https://api.telegram.org/bot{tokenTelegram}/getFile?file_id={file_id}"
    with urllib.request.urlopen(url) as response:
        data = json.load(response)
        return data['result']['file_path']


def download_audio(file_url):
    with urllib.request.urlopen(file_url) as response:
        if response.status == 200:
            return response.read()
        else:
            raise Exception(f"Failed to download audio file: {response.status}")
        
        

