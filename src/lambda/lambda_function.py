
import json
import logging

from dynamo import delete_user, get_user_state, update_user_state
from lex_interaction import call_lex, process_lex_response
from telegram_interaction import (handle_non_text_message, save_image,
                                  send_message)
from textract import extract_text_from_image
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
                    send_message(chat_id, "Isso pode demorar alguns intantes...")
                    send_message(chat_id, "🔎")
                    rotulo = extract_text_from_image(chat_id)
                    
                    if not rotulo.strip():
                        send_message(chat_id, "Nenhum texto foi encontrado na imagem.")
                        delete_user(chat_id)
                    else:
                        logger.info(f"Rotulo:  {rotulo}")
                        send_message(chat_id, rotulo)
                        # delete_user(chat_id)
                        # send_message(chat_id, rotulo)
                    
                elif message == 'Rotulo Menu':
                    update_user_state(chat_id, 'ROTULO')
                    #send_message(chat_id, message)
                    response_lex = call_lex(chat_id, message)
                    process_lex_response(chat_id, response_lex)
                    
                elif message == 'Analisar Imagem Menu':
                    update_user_state(chat_id, 'ANALISAR')
                    #send_message(chat_id, message)
                    response_lex = call_lex(chat_id, message)
                    process_lex_response(chat_id, response_lex)
                elif message == 'Funcionalidades':
                    #send_message(chat_id, message)
                    response_lex = call_lex(chat_id, message)
                    process_lex_response(chat_id, response_lex)
                elif message == 'Como Usar':
                    #send_message(chat_id, message)
                    response_lex = call_lex(chat_id, message)
                    process_lex_response(chat_id, response_lex)

            elif 'photo' in body['message']:
                chat_id = body['message']['chat']['id']

                # Verificar se o usuário existe no banco de dados
                user_state = get_user_state(chat_id)
                save_image(chat_id, body)
                
                if user_state is None:
                    # Se o usuário não existir, perguntar o que ele deseja fazer
                    logger.info(f"Usuário {chat_id} não encontrado no banco de dados.")
                   
                    buttons = [
                        [{'text': 'Gerar Descrição da Imagem', 'callback_data': 'Analisar Imagem'}],
                        [{'text': 'Extrair Texto da Imagem', 'callback_data': 'Rotulo'}]
                    ]
                    send_message(chat_id, "O que você deseja fazer com a imagem enviada?", buttons)
                    
                else:
                    # Se o usuário existir, continue com o fluxo normal
                    logger.info(f"Usuário {chat_id} encontrado no banco de dados com estado: {user_state}")
                    
                    if user_state == 'ROTULO':
                        send_message(chat_id, "Isso pode demorar alguns intantes...")
                        send_message(chat_id, "🔎")
                        rotulo = extract_text_from_image(chat_id)
                        if not rotulo.strip():
                            send_message(chat_id, "Nenhum texto foi encontrado na imagem.")
                            delete_user(chat_id)
                        else:
                            logger.info(f"Rotulo:  {rotulo}")
                            # delete_user(chat_id)
                            
                            send_message(chat_id, rotulo)
                            delete_user(chat_id)
                       
                    
                    elif user_state == 'ANALISAR':
                        
                        handle_non_text_message(chat_id)
                        delete_user(chat_id)
                        
            elif 'text' in body['message']:
                chat_id = body['message']['chat']['id']
                message = body['message']['text']
                response_lex = call_lex(chat_id, message)
                process_lex_response(chat_id, response_lex)

            elif 'voice' in body['message']:
                
                chat_id = body['message']['chat']['id']
                file_id = body['message']['voice']['file_id']
                send_message(chat_id, "Analisando áudio...")
                audio_text = audio_user(chat_id, file_id)
               
                if not audio_text.strip():
                    send_message(chat_id, "O áudio enviado está vazio ou não pôde ser entendido. Por favor, envie um áudio claro.")
                else:
                    # Caso o áudio tenha conteúdo, continue com a chamada ao Lex
                    send_message(chat_id, audio_text)
                    response = call_lex(chat_id,audio_text)
                    process_lex_response(chat_id,response)
                
            else:
                logger.error("Unrecognized message format!")
                chat_id = body['message']['chat']['id']
                send_message(chat_id,"Desculpe, mas não suporto esse tipo de entrada")
                return {'statusCode': 200, 'body': json.dumps('Bad Request: Unrecognized message format.')}

    except Exception as e:
        logger.error(f"Error processing message in lambda_handler: {str(e)}")
        return {'statusCode': 400, 'body': json.dumps('error')}

    return {'statusCode': 200, 'body': json.dumps('Success')}
