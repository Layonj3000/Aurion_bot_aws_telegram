import datetime
import json
import os
import time
import urllib.request

import boto3

transcribe = boto3.client('transcribe')
s3 = boto3.client('s3')
bucket_name = os.getenv("bucketName")


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
        
        
def audio_user(chat_id, file_id):

    s3_key = handle_audio_message(chat_id, file_id)
    job_name = start_transcription(chat_id, s3_key)
    status_transcribe = check_transcription_status(job_name)
    user_transcription = transcription_to_user(chat_id, status_transcribe)
    
    return user_transcription

def handle_audio_message(chat_id, file_id):
    print("handle_audio_message(chat_id, file_id)")
    file_path = get_telegram_file_path(file_id)
    print("file path audio: ", file_path)
    file_url = f"https://api.telegram.org/file/bot{os.getenv('tokenTelegram')}/{file_path}"
    audio_data = download_audio(file_url)
    s3_key = f'{chat_id}/audio.ogg'
    s3.put_object(Bucket= bucket_name, Key=s3_key, Body=audio_data)

    return s3_key

def generate_unique_job_name(chat_id, base_name="transcription-job"):
    return f"{base_name}-{chat_id}-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

def start_transcription(chat_id, s3_key):
    job_name = generate_unique_job_name(chat_id)
    transcribe.start_transcription_job(
        TranscriptionJobName=job_name,
        Media={'MediaFileUri': f's3://{bucket_name}/{s3_key}'},
        MediaFormat='ogg',
        LanguageCode='pt-BR',
        OutputBucketName= bucket_name
    )

    return job_name

def check_transcription_status(job_name):
    print("def check_transcription_status(job_name):")
    while True:
        result = transcribe.get_transcription_job(TranscriptionJobName=job_name)
        status = result['TranscriptionJob']['TranscriptionJobStatus']
        if status == 'COMPLETED':
            return result['TranscriptionJob']['Transcript']['TranscriptFileUri']
        elif status == 'FAILED':
            print("failed")
            raise Exception("Transcription failed")
        time.sleep(5)
        
def transcription_to_user(chat_id, transcript_url):
    print("def send_transcription_to_user(chat_id, transcript_url):")
    try:
        # Fazendo a requisição para obter os dados de transcrição
        with urllib.request.urlopen(transcript_url) as response:
            transcript_data = json.load(response)
            transcript_text = transcript_data['results']['transcripts'][0]['transcript']
            print("transcript_text:", transcript_text)
            return transcript_text
    except Exception as e:
        print(f"Error retrieving transcription: {str(e)}")
        return None