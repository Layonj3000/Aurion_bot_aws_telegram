import boto3
import json

bedrock = boto3.client('bedrock-runtime')

def invoke_bedrock_model(model_id, request_text):
    body = json.dumps({"inputText": request_text})
    
    try:
        response = bedrock.invoke_model(
            modelId=model_id,
            contentType='application/json',
            body=body
        )
        response_body = response['body'].read().decode('utf-8')
        result = json.loads(response_body)
        
        return result['results'][0]['outputText']
    
    except Exception as e:
        print(f"Erro ao invocar o modelo Bedrock: {str(e)}")
        return None

def generate_image_description(image_labels):
    image_labels_text = ', '.join(image_labels)

    prompt_1 = (
        f"Gere uma descrição detalhada e clara, em texto corrido de uma imagem que contém "
        f"os seguintes elementos: {image_labels_text}. A descrição deve ser objetiva e precisa, evitando qualquer "
        f"tipo de opinião, julgamento de valor, ou interpretação emocional. Limite-se a descrever apenas os "
        f"elementos visíveis mencionados nos labels, sem adicionar informações ou suposições sobre elementos. Em português."
    )
    
    response_1 = invoke_bedrock_model('amazon.titan-text-premier-v1:0', prompt_1)
    
    if not response_1:
        return "Ocorreu um erro ao gerar a descrição da imagem."

    prompt_2 = (
        f"Analise esse texto que representa a descrição de uma imagem: {response_1}. "
        f"Se a descrição fizer sentido, for coerente, de fácil entendimento e possuir elementos que geralmente "
        f"se correlacionam como {image_labels_text}, responda apenas com 'Sim'. Se houver elementos que normalmente "
        f"não se associam entre si, ou a combinação parecer incoerente, responda apenas com 'Não'."
    )

    response_2 = invoke_bedrock_model('amazon.titan-text-premier-v1:0', prompt_2)
    
    if response_2 and response_2.strip().lower() == 'sim':
        return response_1
    else:
        return "Desculpe, não consegui analisar essa imagem. Poderia enviar outra, por favor?"