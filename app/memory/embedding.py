# app/memory/embedding.py

import boto3
import os
import json
from dotenv import load_dotenv
load_dotenv()

BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")
EMBEDDING_MODEL_ID = os.getenv("EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v1")

bedrock = boto3.client("bedrock-runtime", region_name=BEDROCK_REGION)

def get_embedding(text: str):
    body = {
        "inputText": text
    }

    response = bedrock.invoke_model(
        modelId=EMBEDDING_MODEL_ID,
        body=json.dumps(body),
        accept="application/json",
        contentType="application/json"
    )

    result = json.loads(response["body"].read())
    return result["embedding"]
