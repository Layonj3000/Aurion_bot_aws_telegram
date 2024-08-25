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
        
        
def audio_user(chat_id, file_id, bucket_name):

    s3_key = handle_audio_message(chat_id, file_id, bucket_name)
    job_name = start_transcription(chat_id, s3_key, bucket_name)
    status_transcribe = check_transcription_status(job_name)
    user_transcription = transcription_to_user(chat_id, status_transcribe)
    
    return user_transcription

def handle_audio_message(chat_id, file_id, bucket_name):
    print("handle_audio_message(chat_id, file_id)")
    file_path = get_telegram_file_path(file_id)
    print("file path audio: ", file_path)
    file_url = f"https://api.telegram.org/file/bot{os.getenv('tokenTelegram')}/{file_path}"
    audio_data = download_audio(file_url)
    s3_key = f'{chat_id}/audio.ogg'
    s3.put_object(Bucket= bucket_name, Key=s3_key, Body=audio_data)

    return s3_key