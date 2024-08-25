import os

import boto3

# Configurações
s3_bucket_name = os.getenv('bucketName')
rekognition = boto3.client('rekognition')
s3_client = boto3.client('s3')

def detect_labels(bucket, chat_id):
    try:
        image_path = f'{chat_id}/image.jpg'
        response = rekognition.detect_labels(
            Image={'S3Object': {'Bucket': bucket, 'Name': image_path}},
            MaxLabels=10,
            MinConfidence=80
        )
        labels = [label['Name'] for label in response['Labels']]
        print(labels)
        return labels

    except Exception as e:
        print(e)