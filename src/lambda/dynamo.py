import os

import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.client('dynamodb')
table_name = os.getenv('tableName')

def update_user_state(user_id, state):
    dynamodb.put_item(
        TableName=table_name,
        Item={
            'user_id': {'S': str(user_id)},
            'state': {'S': state}
        }
    )

def get_user_state(user_id):
    response = dynamodb.get_item(
        TableName=table_name,
        Key={'user_id': {'S': str(user_id)}}
    )
    if 'Item' in response:
        return response['Item']['state']['S']
    return None
    
    