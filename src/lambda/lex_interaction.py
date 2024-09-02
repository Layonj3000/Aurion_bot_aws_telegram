import json
import logging
import os

import boto3

from dynamo import delete_user, get_user_state, update_user_state
from telegram_interaction import send_message

logger = logging.getLogger()
lex_client = boto3.client('lexv2-runtime')

def call_lex(chat_id, message):
    try:
        botId = os.getenv('botId')
        botAliasId = os.getenv('botAliasId')

        response = lex_client.recognize_text(
            botId=botId,
            botAliasId=botAliasId,
            localeId='pt_BR',
            sessionId=str(chat_id),
            text=str(message)
        )
        logger.info(f"Lex response: {response}")
        return response

    except Exception as e:
        logger.error(f"Error in call_lex: {str(e)}")
        return {'statusCode': 400, 'body': json.dumps('error')}

def process_lex_response(chat_id, response):
    intent_name = response['sessionState']['intent']['name']
    logger.info(f"Processing Lex response, intent name: {intent_name}")

    reply = response.get('messages', [{}])[0].get('content', 'Desculpe, não entendi isso.')
    send_message(chat_id, reply)

    if intent_name == 'Saudacoes':
        logger.info("Intent Saudacoes recognized.")
        buttons = [
            [{'text': 'Como Funciona?', 'callback_data': 'Funcionalidades'}],
            [{'text': 'Analisar Imagem', 'callback_data': 'Analisar Imagem Menu'}],
            [{'text': 'Procurar Rótulo', 'callback_data': 'Rotulo Menu'}]
        ]
        send_message(chat_id, "Escolha uma opção:", buttons)

    if intent_name == 'AnalisarTexto':
        update_user_state(chat_id, 'ROTULO')
    if intent_name == 'AnalisarImagem':
        update_user_state(chat_id, 'ANALISAR')
    return intent_name
