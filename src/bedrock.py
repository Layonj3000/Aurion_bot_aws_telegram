import boto3
import json

bedrock = boto3.client('bedrock-runtime')

def generate_image_description(image_labels):
    image_labels_text = ','.join(image_labels)

    prompt = f"Descreva uma imagem que contém os seguintes elementos (labels) retirados do AWS Rekognition: {image_labels_text}."
    request_text = f"Faça em português, de forma resumida: {prompt}"
    

    body = json.dumps({"inputText": request_text})

    try:
        # Invoca o modelo para gerar a resposta
        response = bedrock.invoke_model(
            modelId='amazon.titan-text-premier-v1:0',
            contentType='application/json',
            body=body
        )

        response_body = response['body'].read().decode('utf-8')
        result = json.loads(response_body)

        response_text = result['results'][0]['outputText']
        return response_text

    except Exception as e:
        return str(e)