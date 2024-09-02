import os

import boto3
from botocore.exceptions import ClientError

dynamodb = boto3.client('dynamodb')
table_name = os.getenv('tableName')