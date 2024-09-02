import os

import boto3

textract = boto3.client('textract')

def extract_text_from_image(chat_id):
    try:
        bucket = os.getenv('bucketName')
        image_path = f'{chat_id}/image.jpg'
        response = textract.detect_document_text(
            Document={'S3Object': {'Bucket': bucket, 'Name': image_path}}
        )

        lines = []

        for item in response["Blocks"]:
            if item["BlockType"] == "LINE":
                lines.append(item["Text"])

        extracted_text = "\n".join(lines)
        print(extracted_text)

        return extracted_text

    except Exception as e:
        return str(e)