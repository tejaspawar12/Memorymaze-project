import gradio as gr
import requests

BASE_URL = "http://127.0.0.1:8000"
token = None  # Global variable to hold token after login

def login(username, password):
    global token
    response = requests.post(f"{BASE_URL}/login", data={"username": username, "password": password})

    try:
        data = response.json()
    except Exception:
        return f"❌ Login failed. Server response: {response.text}"

    if "access_token" in data:
        token = data["access_token"]
        return f"✅ Login successful! Token: {token[:15]}..."
    else:
        return f"❌ Login failed: {data.get('detail', 'Unknown error')}"

def chat_with_mmaze(message):
    global token
    if not token:
        return "⚠️ Please login first to get access token."

    headers = {"Authorization": f"Bearer {token}"}
    payload = {"message": message}

    try:
        response = requests.post(f"{BASE_URL}/chat", json=payload, headers=headers)

        print("▶️ Sending to /chat:", payload)
        print("▶️ Headers:", headers)
        print("▶️ Status Code:", response.status_code)
        print("▶️ Response Text:", response.text)

        if response.status_code == 200:
            return response.json().get("response", "✅ Success, but no content returned.")
        else:
            try:
                return f"❌ Error: {response.json().get('detail', 'Unknown error')}"
            except Exception:
                return f"❌ Error: Could not decode JSON. Raw response: {response.text}"

    except Exception as e:
        return f"❌ Exception occurred: {str(e)}"

with gr.Blocks() as demo:
    gr.Markdown("## 🔐 M-Maze Login + Chat Interface")

    with gr.Row():
        username_input = gr.Textbox(label="Username")
        password_input = gr.Textbox(label="Password", type="password")
        login_button = gr.Button("Login")
        login_output = gr.Textbox(label="Login Response")

    login_button.click(fn=login, inputs=[username_input, password_input], outputs=login_output)

    with gr.Row():
        chat_input = gr.Textbox(label="Your Message to M-Maze")
        chat_button = gr.Button("Send")
        chat_output = gr.Textbox(label="M-Maze Reply")

    chat_button.click(fn=chat_with_mmaze, inputs=[chat_input], outputs=chat_output)

demo.launch(server_port=7861)
