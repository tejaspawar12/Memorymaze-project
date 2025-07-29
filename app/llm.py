# app/llm.py

import boto3
import os
import json
from dotenv import load_dotenv

load_dotenv()

BEDROCK_CLIENT = boto3.client(
    service_name="bedrock-runtime",
    region_name=os.getenv("AWS_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY"),
)

MODEL_ID = os.getenv("LLM_MODEL_ID", "meta.llama3-1-8b-instruct-v1:0")

def build_prompt(user_input: str, memory_chunks: list) -> str:
    memory_text = "\n".join([f"- {item.payload['text']}" for item in memory_chunks])
    prompt = f"""You are M-Maze, a personal AI memory assistant.

User's past memories:
{memory_text}

Now the user says: "{user_input}"

Respond helpfully, referencing relevant past memories if needed."""
    return prompt

def generate_response(user_input: str, memory_chunks: list) -> str:
    prompt = build_prompt(user_input, memory_chunks)
    
    response = BEDROCK_CLIENT.invoke_model(
        modelId=MODEL_ID,
        contentType="application/json",
        accept="application/json",
        body=json.dumps({
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "max_tokens": 500,
            "temperature": 0.7,
        })
    )

    output = response["body"].read().decode("utf-8")
    return json.loads(output)["content"][0]["text"]
