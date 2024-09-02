import json
import logging

from dynamo import delete_user, get_user_state, update_user_state
from textract import extract_text_from_image

from lex_interaction import call_lex, process_lex_response
from telegram_interaction import handle_non_text_message, send_message
from transcribe import audio_user

logger = logging.getLogger()
logger.setLevel(logging.INFO)

def lambda_handler(event, context):
    logger.info(f"Received event: {json.dumps(event)}")
    try:
        if 'body' in event:
            body = json.loads(event['body'])

            if 'callback_query' in body:
                print("if 'callback_query' in body:")
                callback_data = body['callback_query']['data']
                print("callback_data",callback_data)
                chat_id = body['callback_query']['message']['chat']['id']
                message = callback_data
                print("message = ", message)
                
                if message == 'Analisar Imagem':
                    print("if message is 'Analisar Imagem':")
                    # update_user_state(chat_id, 'ANALISAR')
                    handle_non_text_message(chat_id)
                    # delete_user(chat_id)
                elif message == 'Rotulo':
                    print("if message is 'rotulo':")
                    # update_user_state(chat_id, 'ROTULO')
                    send_message(chat_id, "É pra já! aqui está os rótulos:")
                    rotulo = extract_text_from_image(chat_id)
                    logger.info(f"Rotulo:  {rotulo}")
                    # delete_user(chat_id)
                    send_message(chat_id, rotulo)
                    
                elif message == 'Rotulo Menu':
                    update_user_state(chat_id, 'ROTULO')
                    send_message(chat_id, message)
                    send_message(chat_id, "Desculpa, ainda nao tenho essa intent")
                    send_message(chat_id, "mas nao tem problema️")
                    send_message(chat_id,"Manda a foto")
                    
                elif message == 'Analisar Imagem Menu':
                    update_user_state(chat_id, 'ANALISAR')
                    send_message(chat_id, message)
                    response_lex = call_lex(chat_id, message)
                    process_lex_response(chat_id, response_lex)
                elif message == 'Funcionalidades':
                    send_message(chat_id, message)
                    response_lex = call_lex(chat_id, message)
                    process_lex_response(chat_id, response_lex)

            elif 'photo' in body['message']:
                chat_id = body['message']['chat']['id']
                handle_non_text_message(chat_id, body)

            elif 'text' in body['message']:
                chat_id = body['message']['chat']['id']
                message = body['message']['text']
                response_lex = call_lex(chat_id, message)
                process_lex_response(chat_id, response_lex)

            elif 'voice' in body['message']:
                chat_id = body['message']['chat']['id']
                file_id = body['message']['voice']['file_id']
                audio_text = audio_user(chat_id, file_id)
                send_message(chat_id, audio_text)
            else:
                logger.error("Unrecognized message format!")
                return {'statusCode': 400, 'body': json.dumps('Bad Request: Unrecognized message format.')}

    except Exception as e:
        logger.error(f"Error processing message in lambda_handler: {str(e)}")
        return {'statusCode': 400, 'body': json.dumps('error')}

    return {'statusCode': 200, 'body': json.dumps('Success')}
