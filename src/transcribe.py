import datetime
import json
import os
import time
import urllib.request

import boto3

transcribe = boto3.client('transcribe')
s3 = boto3.client('s3')