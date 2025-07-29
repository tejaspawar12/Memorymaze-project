# app/llm/client.py
import os
import boto3
import json
from dotenv import load_dotenv
import re
load_dotenv()

REGION = os.getenv("AWS_REGION", "us-east-1")
LLM_MODEL_ID = os.getenv("LLM_MODEL_ARN", "arn:aws:bedrock:us-east-1:290516076537:inference-profile/us.meta.llama3-1-8b-instruct-v1:0")

bedrock = boto3.client("bedrock-runtime", region_name=REGION)

def remove_repetitions(text: str) -> str:
    """
    Remove repeated sentences or phrases that appear too frequently in the LLM output.
    """
    sentences = re.split(r'(?<=[.!?]) +', text)
    seen = set()
    cleaned = []
    for sentence in sentences:
        if sentence not in seen:
            seen.add(sentence)
            cleaned.append(sentence)
    return ' '.join(cleaned)


def query_llm(prompt: str, context: str = "", max_tokens: int = 512) -> str:
    """
    Query LLaMA 3 model from Amazon Bedrock with memory/context.
    """
    # Final prompt structure
    full_prompt = f"{context}\n\nUser: {prompt}\nAssistant:"

    body = {
        "prompt": full_prompt,
        "max_gen_len": max_tokens,
        "temperature": 0.5,
        "top_p": 0.9,
    }

    try:
        response = bedrock.invoke_model(
            modelId=LLM_MODEL_ID,
            body=json.dumps(body),
            accept="application/json",
            contentType="application/json"
        )
        result = json.loads(response['body'].read())

        # Extract raw response
        text = result['generation']
        return remove_repetitions(text.strip())

    except Exception as e:
        return f"❌ Error querying LLM: {str(e)}"
