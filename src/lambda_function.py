import json
import logging
import os
import urllib.request 

import boto3
from bedrock import generate_image_description
from rekognition import detect_labels
from transcribe import audio_user

logger = logging.getLogger() 
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    try:
        # Verifique se o evento vem do Telegram (presença de 'body')
        if 'body' in event:
            body = json.loads(event['body'])

            # Verifique se o evento é um callback_query
            if 'callback_query' in body:
                callback_data = body['callback_query']['data']
                chat_id = body['callback_query']['message']['chat']['id']
                message = callback_data  # Use o callback_data como a mensagem a ser enviada para o Lex
                
                send_message(chat_id,message) 
                
                response_lex = call_lex(chat_id, message)
                process_lex_response(chat_id, response_lex)
                
                                
            elif 'photo' in body['message']:
                print("elif 'photo' in body['message']:")
                chat_id = body['message']['chat']['id'] 
                handle_non_text_message(chat_id, body)

            elif 'text' in body['message']:
                print("elif 'text' in body['message']:")
                chat_id = body['message']['chat']['id'] 
                message = body['message']['text']
                # update_user_state(chat_id,'AWAITING_TEXT')
                response_lex = call_lex(chat_id, message)
                process_lex_response(chat_id, response_lex)
                #adicionar a intent que retorna
            
            elif 'voice' in body['message']:
                print("elif 'voice' in body['message']:")
                
                chat_id = body['message']['chat']['id'] 
                print(chat_id)

                file_id = body['message']['voice']['file_id']
                
                audio_text = audio_user(chat_id, file_id, s3_bucket_name)
                print("audio_Text ", audio_text)
                print(type(audio_text))
                send_message(chat_id, audio_text)

                


            else:
                logger.error("Unrecognized message format!")
                return {
                    'statusCode': 400,
                    'body': json.dumps('Bad Request: Unrecognized message format.')
                }

    except Exception as e:
        logger.error(f"Error processing message: in lambda_handler {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps('error')
            }
        
    
    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }
    
def call_lex(chat_id, message):
    try:
        botId = os.getenv('botId')
        botAliasId = os.getenv('botAliasId')
        
        # Solicitação ao Lex V2
        response = lex_client.recognize_text(
            botId= botId,  # Substitua pelo ID do seu bot
            botAliasId= botAliasId,  # Substitua pelo ID do alias do seu bot
            localeId= 'pt_BR',  # Substitua pela localidade apropriada
            sessionId= str(chat_id),
            text= str(message)
        )
        logger.info(f"Lex response: {response}")
        
        # reply = response.get('messages', [{}])[0].get('content', 'Desculpe, não entendi isso.')
        
        return response

    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return {
            'statusCode': 400,
            'body': json.dumps('error')
            }

def process_lex_response(chat_id, response):
    intent_name = response['sessionState']['intent']['name']

    logger.info("procces_lex_response, intent name {intent_name}")

    reply = response.get('messages', [{}])[0].get('content', 'Desculpe, não entendi isso.')
            
    send_message(chat_id, reply)
    
    if intent_name == 'Saudacoes':
        logger.info("Intent Saudacoes reconhecida.")
        
        # Crie um menu com botões
        buttons = [
            [{'text': 'Analisar Imagem🔎', 'callback_data': 'analisar_imagem'}],
            [{'text': 'Opção 2', 'callback_data': 'opcao_2'}],
            [{'text': 'Opção 3', 'callback_data': 'opcao_3'}]
        ]
        
        send_message(chat_id, "Escolha uma opção:", buttons)

    return intent_name

def handle_non_text_message(chat_id, body):
    print(" handle_non_text_message(chat_id, body):")

    photo = body['message']['photo'][-1]  # Pega a imagem de maior resolução
    file_id = photo['file_id']
    tokenTelegram = os.getenv('tokenTelegram')
    # Pegar o arquivo do Telegram
    file_path = get_telegram_file_path(file_id)
    file_url = f"https://api.telegram.org/file/bot{tokenTelegram}/{file_path}"
        
    # Baixar a imagem
    image_data = download_image(file_url)
    
    # Armazenar no S3
    store_image_in_s3(chat_id, image_data)
    response_rekognition = detect_labels(s3_bucket_name,chat_id)
        
    bedrock = generate_image_description(response_rekognition)
    print("lambda bedrock ", bedrock)
    send_message(chat_id,response_rekognition )
    send_message(chat_id, bedrock)
    return send_message(chat_id, "Imagem armazenada com sucesso!")


def send_message(chat_id, text, buttons=None):
    print("def send_message(chat_id, text, buttons=None)")
    url = f"https://api.telegram.org/bot{os.environ['tokenTelegram']}/sendMessage"
    
    payload = {
        'chat_id': chat_id,
        'text': text,
        'parse_mode': 'HTML' 
    }
    
    if buttons:
        payload['reply_markup'] = json.dumps({
            'inline_keyboard': buttons
        })
    
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
    return {
        'statusCode': 200,
        'body': json.dumps('Success')
    }

