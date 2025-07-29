# app/embedding.py

import os
import boto3
from dotenv import load_dotenv
import json
load_dotenv()

BEDROCK_REGION = os.getenv("BEDROCK_REGION", "us-east-1")
EMBEDDING_MODEL_ID = os.getenv("EMBEDDING_MODEL_ID", "amazon.titan-embed-text-v1")

# 🧠 AWS Bedrock Boto3 Client
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

    output = json.loads(response["body"].read())
    return output["embedding"]
