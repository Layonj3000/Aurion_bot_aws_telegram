import json
import logging
import os
import urllib.request

from bedrock import generate_image_description
from image_processing import (download_image, get_telegram_file_path,
                              store_image_in_s3)
from rekognition import detect_labels

logger = logging.getLogger()
s3_bucket_name = os.getenv('bucketName')


def save_image(chat_id, body):
    photo = body['message']['photo'][-1]
    file_id = photo['file_id']
    tokenTelegram = os.getenv('tokenTelegram')

    file_path = get_telegram_file_path(file_id)
    file_url = f"https://api.telegram.org/file/bot{tokenTelegram}/{file_path}"
    image_data = download_image(file_url)

    store_image_in_s3(chat_id, image_data)

def handle_non_text_message(chat_id):
    
    send_message(chat_id, "Isso pode demorar alguns intantes...")
    send_message(chat_id, "🔎")
    response_rekognition = detect_labels(s3_bucket_name, chat_id)
    bedrock = generate_image_description(response_rekognition)
    # send_message(chat_id, response_rekognition)
    send_message(chat_id, bedrock)

def send_message(chat_id, text, buttons=None):
    url = f"https://api.telegram.org/bot{os.getenv('tokenTelegram')}/sendMessage"

    payload = {'chat_id': chat_id, 'text': text, 'parse_mode': 'HTML'}
    if buttons:
        payload['reply_markup'] = json.dumps({'inline_keyboard': buttons})

    headers = {'Content-Type': 'application/json'}

    try:
        req = urllib.request.Request(url, data=json.dumps(payload).encode('utf-8'), headers=headers, method='POST')
        with urllib.request.urlopen(req) as response:
            response_data = response.read().decode('utf-8')
            logger.info(f"Telegram API response: {response_data}")
            return json.loads(response_data)

    except urllib.error.HTTPError as e:
        logger.error(f"HTTPError: {e.code} {e.reason}")
        return {'error': f'HTTPError: {e.code} {e.reason}'}

    except urllib.error.URLError as e:
        logger.error(f"URLError: {e.reason}")
        return {'error': f'URLError: {e.reason}'}

    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}")
        return {'error': f'Unexpected error: {str(e)}'}