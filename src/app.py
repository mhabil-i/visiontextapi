import os
import sys

# Add config directory to Python path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'config'))

try:
    from config import CONFIG
except ImportError:
    print("❌ ERROR: config.py not found!")
    print("Please copy config_example.py to config.py and configure it.")
    print("See docs/SETUP.md for detailed instructions.")
    sys.exit(1)

from flask import Flask, request, jsonify, Response
import requests, time, uuid, base64, json

app = Flask(__name__)

def call_local_stream(model, url, messages, **kwargs):
    """Call local LMStudio API for streaming responses"""
    payload = {"model": model, "messages": messages, **kwargs}
    headers = {"Content-Type": "application/json"}
    return requests.post(url, headers=headers, json=payload, timeout=60, stream=True)

def call_local_sync(model, url, messages, **kwargs):
    """Call local LMStudio API for non-streaming responses"""
    payload = {"model": model, "messages": messages, **kwargs}
    headers = {"Content-Type": "application/json"}
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def call_openai_stream(model, url, messages, api_key, **kwargs):
    """Call OpenAI-compatible API for streaming responses"""
    payload = {"model": model, "messages": messages, "stream": True, **kwargs}
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    return requests.post(url, headers=headers, json=payload, timeout=60, stream=True)

def call_openai_sync(model, url, messages, api_key, **kwargs):
    """Call OpenAI-compatible API for non-streaming responses"""
    payload = {"model": model, "messages": messages, **kwargs}
    headers = {"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"}
    r = requests.post(url, headers=headers, json=payload, timeout=60)
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"]

def encode_image_to_base64(filepath):
    """Encode image file to base64"""
    with open(filepath, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")

def download_and_encode_image(url):
    """Download image from URL and convert to base64"""
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")
    except Exception as e:
        print(f"❌ Error downloading image from {url}: {e}")
        return None

def has_image_content(messages):
    """Check if any message contains image content"""
    for m in messages:
        content = m.get("content", [])
        if isinstance(content, list):
            for item in content:
                if item.get("type") in ["image", "image_url"]:
                    return True
    return False

def extract_text_from_messages(messages):
    """Extract all text content from messages"""
    chat_messages = []
    for m in messages:
        content = m.get("content", [])
        
        if isinstance(content, str):
            chat_messages.append({"role": m["role"], "content": content})
            continue
            
        if isinstance(content, list):
            texts = [c.get("text", "") for c in content if c.get("type") == "text"]
            if texts:
                chat_messages.append({"role": m["role"], "content": " ".join(texts)})
    
    return chat_messages

def prepare_vision_messages(messages):
    """Prepare messages for vision model by converting image paths/URLs to base64"""
    vision_messages = []
    
    for m in messages:
        content = m.get("content", [])
        if not isinstance(content, list):
            continue
            
        new_content = []
        for c in content:
            if c.get("type") in ["image", "image_url"]:
                image_url = c.get("url", c.get("image_url", {}).get("url", ""))
                
                # Skip if already base64 encoded (from OpenLLMVtuber)
                if image_url.startswith("data:image/"):
                    new_content.append({
                        "type": "image_url",
                        "image_url": {"url": image_url}
                    })
                # Handle local file paths
                elif os.path.exists(image_url):
                    try:
                        b64_data = encode_image_to_base64(image_url)
                        new_content.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/png;base64,{b64_data}"}
                        })
                    except Exception as e:
                        print(f"❌ Error encoding local image: {e}")
                        continue
                # Handle URLs - download and convert to base64
                elif image_url.startswith("http"):
                    print(f"🔍 Downloading image from URL: {image_url}")
                    b64_data = download_and_encode_image(image_url)
                    if b64_data:
                        new_content.append({
                            "type": "image_url",
                            "image_url": {"url": f"data:image/jpeg;base64,{b64_data}"}
                        })
                    else:
                        print(f"❌ Failed to download image from {image_url}")
                        continue
                else:
                    new_content.append(c)
            elif c.get("type") == "text":
                new_content.append({"type": "text", "text": c.get("text", "")})
        
        if new_content:
            vision_messages.append({"role": m["role"], "content": new_content})
    
    return vision_messages

@app.route("/v1/chat/completions", methods=["POST"])
def chat_completions():
    try:
        data = request.json
        user_messages = data.get("messages", [])
        model = data.get("model", CONFIG["text"]["model"])
        is_streaming = data.get("stream", False)
        
        # Extract OpenAI parameters
        openai_params = {k: v for k, v in data.items() if k not in ["messages", "model"]}
        
        print(f"📥 Processing request: streaming={is_streaming}, messages={len(user_messages)}")
        
        # Check for images
        has_image = has_image_content(user_messages)
        
        if has_image:
            print("🖼️  Image detected - processing with LOCAL vision model first")
            
            # Process with LOCAL vision model (always non-streaming)
            vision_messages = prepare_vision_messages(user_messages)
            
            # --- INSERT SYSTEM PROMPT AND CLEANING HERE (CRITICAL BLOCK) ---
            # 1. Inject the strict system prompt to control the Vision Model
            strict_system_prompt = {
                "role": "system",
                "content": (
                    "You are a purely factual, non-conversational, and concise image analysis engine. "
                    "Your sole function is to generate an objective description of the image. "
                    "DO NOT use first-person pronouns (I, my). DO NOT respond to conversational messages. "
                    "DO NOT use emojis. Respond ONLY with the generated description text."
                )
            }
            
            # Prepend the strict prompt to the messages array sent to the Vision Model
            vision_messages = [strict_system_prompt] + vision_messages
            
            # 2. Call the Vision Model
            vision_params = {k: v for k, v in openai_params.items() if k != "stream"}
            
            # The vision_messages now include the strict system prompt!
            vision_output = call_local_sync(
                CONFIG["vision"]["model"], 
                CONFIG["vision"]["url"], 
                vision_messages, 
                **vision_params
            )
            
            # 3. Clean the output (Safety net against any missed yapping)
            offending_phrases = [
                "You're right to notice that!", 
                "I am Gemma,", 
                "it's interesting to see your workspace", 
                "😊", 
                "I am a large language model"
            ]
            for phrase in offending_phrases:
                vision_output = vision_output.replace(phrase, "")
            vision_output = vision_output.strip()
            # --- END CRITICAL BLOCK ---
            
            # Extract text and combine with vision output
            chat_messages = extract_text_from_messages(user_messages)
            user_text = " ".join([msg["content"] for msg in chat_messages if msg["role"] == "user"])

            if user_text.strip():
                system_prompt = f"""Image: {vision_output}
User: {user_text}
Answer concisely based on the image.
"""
            else:
                system_prompt = f"""Describe this image concisely: {vision_output}"""
            
            final_messages = chat_messages + [{"role": "system", "content": system_prompt}]
            
        else:
            print("💬 Text-only request")
            # Check if already has vision system message
            has_vision_msg = any(
                msg.get("role") == "system" and "image with this description" in msg.get("content", "")
                for msg in user_messages
            )
            
            final_messages = user_messages if has_vision_msg else extract_text_from_messages(user_messages)
        
        # Generate response - THIS IS WHERE WE SWITCH BETWEEN LOCAL/OPENAI
        text_config = CONFIG["text"]
        
        if is_streaming:
            print(f"⚡ Streaming response using {text_config['provider']} provider")
            
            def generate():
                try:
                    if text_config["provider"] == "openai":
                        response = call_openai_stream(
                            text_config["model"], 
                            text_config["url"], 
                            final_messages, 
                            text_config["api_key"], 
                            **openai_params
                        )
                    else:
                        response = call_local_stream(
                            text_config["model"], 
                            text_config["url"], 
                            final_messages, 
                            **openai_params
                        )
                    
                    for line in response.iter_lines():
                        if line:
                            decoded_line = line.decode('utf-8')
                            if decoded_line.startswith('data: '):
                                yield decoded_line + '\n\n'
                                
                except Exception as e:
                    print(f"❌ Streaming error: {e}")
                    error_data = {
                        "id": f"chatcmpl-{uuid.uuid4()}",
                        "object": "chat.completion.chunk",
                        "created": int(time.time()),
                        "model": model,
                        "choices": [{"index": 0, "delta": {"content": f"Error: {str(e)}"}, "finish_reason": "stop"}]
                    }
                    yield f"data: {json.dumps(error_data)}\n\n"
                    yield "data: [DONE]\n\n"
            
            return Response(generate(), mimetype='text/event-stream', headers={
                'Cache-Control': 'no-cache',
                'Connection': 'keep-alive',
                'Access-Control-Allow-Origin': '*'
            })
        
        else:
            print(f"🔄 Non-streaming response using {text_config['provider']} provider")
            
            if text_config["provider"] == "openai":
                content = call_openai_sync(
                    text_config["model"], 
                    text_config["url"], 
                    final_messages, 
                    text_config["api_key"], 
                    **openai_params
                )
            else:
                content = call_local_sync(
                    text_config["model"], 
                    text_config["url"], 
                    final_messages, 
                    **openai_params
                )
            
            response = {
                "id": f"chatcmpl-{uuid.uuid4()}",
                "object": "chat.completion",
                "created": int(time.time()),
                "model": model,
                "choices": [{"index": 0, "message": {"role": "assistant", "content": content}, "finish_reason": "stop"}],
                "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
            }
            return jsonify(response)
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return jsonify({"error": f"Internal server error: {str(e)}"}), 500

@app.route("/health", methods=["GET"])
def health_check():
    """Health check endpoint"""
    return jsonify({
        "status": "healthy", 
        "timestamp": int(time.time()),
        "version": "1.0.0",
        "text_provider": CONFIG["text"]["provider"],
        "vision_model": CONFIG["vision"]["model"]
    })

@app.route("/config", methods=["GET"])
def get_config():
    """Get current configuration (without API keys)"""
    safe_config = {
        "text": {
            "provider": CONFIG["text"]["provider"],
            "model": CONFIG["text"]["model"],
            "url": CONFIG["text"]["url"],
            "api_key": "***hidden***" if CONFIG["text"].get("api_key") else None
        },
        "vision": {
            "model": CONFIG["vision"]["model"],
            "url": CONFIG["vision"]["url"]
        }
    }
    return jsonify(safe_config)

if __name__ == "__main__":
    print("🚀 Starting AI Vision Text API...")
    print(f"📊 Text Provider: {CONFIG['text']['provider']}")
    print(f"🤖 Text Model: {CONFIG['text']['model']}")
    print(f"👁️  Vision Model: {CONFIG['vision']['model']}")
    print(f"🌐 Server: http://{CONFIG['server']['host']}:{CONFIG['server']['port']}")
    print("📖 API Docs: http://localhost:5000/health")
    print("\n✨ Ready to process images and text!")
    
    app.run(
        host=CONFIG["server"]["host"], 
        port=CONFIG["server"]["port"], 
        debug=CONFIG["server"]["debug"]
    )