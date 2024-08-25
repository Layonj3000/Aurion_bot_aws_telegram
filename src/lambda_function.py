import json
import logging
import os
import urllib.request 

import boto3
from bedrock import generate_image_description
from rekognition import detect_labels
from transcribe import audio_user

logger = logging.getLogger() 
logger.setLevel(logging.INFO)
