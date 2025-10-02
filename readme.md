# 🤖 [AI Vision Text API](https://github.com/mhabil-i/visiontextapi)

A Flask-based API that combines **local vision models** with **local or cloud text models** for multimodal AI conversations. Perfect for processing images while keeping your data private!

## ✨ Features

- 🖼️ **Vision Processing**: Always runs locally to keep your images private
- 💬 **Text Generation**: Choose between local models (private) or cloud APIs (more powerful)
- 🔄 **Streaming Support**: Real-time responses for chat applications
- 🔌 **OpenAI Compatible**: Works with existing OpenAI API clients
- 🛡️ **Privacy First**: Images never leave your machine

## 🎯 Perfect For

- ChatGPT-style image analysis with local privacy
- Building multimodal chatbots
- Image captioning and description
- Visual Q&A systems
- Integration with existing OpenAI-compatible apps

## 🎭 The Problem We Solve

Most AI setups force you to choose:
- **Roleplay models** → Great personality, but blind to images
- **Vision models** → Can see images, but boring and robotic

This API bridges that gap by:
- 🖼️ Processing images with **local vision models** (private, fast)
- 🎭 Sending descriptions to **smart roleplay models** (personality, creativity)
- 🔒 Keeping your images **on your machine** (no cloud uploads)

Perfect for **[Open-LLM-VTuber](https://github.com/Open-LLM-VTuber/Open-LLM-VTuber)** and other applications where you want:
- Your AI character to react to screenshots, photos, memes
- Personality-rich responses to visual content
- Privacy (images never leave your computer)

## 🎮 Perfect For Open-LLM-VTuber Users

**Scenario 1: Gaming Stream**
- You: *shows game screenshot*
- Vision model: "A player character in a medieval fantasy game"
- Your AI VTuber: "Ooh~ That armor looks so cool! Are you going on an adventure? I wish I could join you and cast some magic spells! ✨"

**Scenario 2: Meme Sharing**
- You: *shows funny meme*
- Vision model: "A cat sitting in a box with text"
- Your AI VTuber: "Hehe, that cat looks just like me when I'm being lazy! 😸 Cats really do love their boxes, don't they?"

**Scenario 3: Real Life Photos**
- You: *shows your dinner*
- Vision model: "A plate of pasta with tomato sauce"
- Your AI VTuber: "That pasta looks delicious! 🍝 You're making me hungry... I wish I could taste food like humans do!"

## 📋 Requirements

### Essential Software
- **Python 3.8+** - [Download from python.org](https://python.org/downloads/)
- **[LM Studio](https://lmstudio.ai/)** - For running local vision models

### Recommended Models

**🎭 Text Model (Roleplay):**
- **[Venice AI (Dolphin Mistral 24B)](https://openrouter.ai/cognitivecomputations/dolphin-mistral-24b-venice-edition:free)** via OpenRouter ⭐ **FREE & UNCENSORED**
- Requires: **[OpenRouter API Key](https://openrouter.ai/settings/keys)** (free signup)
- Perfect for: Roleplay, creative responses, personality-rich conversations

**👁️ Vision Model (Local):**
- **[Gemma 3 (4B Vision)](https://lmstudio.ai/models/google/gemma-3-4b)** ⭐ **RECOMMENDED**
- Download through LM Studio's model browser
- Perfect for: Fast, accurate image understanding while keeping images private

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/mhabil-i/visiontextapi.git
cd visiontextapi
```

### 2. Install Dependencies
**Windows:**
```bash
scripts/install.bat
```

**Manual:**
```bash
pip install -r requirements.txt
cp config/config_example.py config/config.py
```

### 3. Setup LM Studio
1. Download and install [LM Studio](https://lmstudio.ai/)
2. Download a vision model (recommended: `google/gemma-3-4b`)
3. Start the model on port 1234

### 4. Configure Settings
Edit `config/config.py`:
```python
CONFIG = {
    "text": {
        "provider": "openai",  # or "local"
        "model": "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
        "url": "https://openrouter.ai/api/v1/chat/completions",
        "api_key": "YOUR_OPENROUTER_API_KEY_HERE"  # Get from openrouter.ai
    },
    "vision": {
        "model": "google/gemma-3-4b",
        "url": "http://localhost:1234/v1/chat/completions"
    }
}
```

### 5. Run the Server
**Windows:**
```bash
run.bat
```

**Manual:**
```bash
python src/app.py
```

### 6. Test It!
```powershell
# Run the test script
./tests/test_api.ps1
```

## 📝 Usage Examples

### Python Client
```python
import requests

response = requests.post("http://localhost:5000/v1/chat/completions", json={
    "model": "any-model-name",
    "messages": [
        {
            "role": "user", 
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {"type": "image_url", "image_url": {"url": 
                "https://httpbin.org/image/jpeg"}}
            ]
        }
    ]
})

print(response.json()["choices"][0]["message"]["content"])
```

### cURL
```bash
(Invoke-RestMethod -Method POST `
    -Uri "http://localhost:5000/v1/chat/completions" `
    -Headers @{"Content-Type" = "application/json"} `
    -Body '{
        "model": "test",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Describe this image"},
                    {"type": "image_url", "image_url": {
                      "url": "https://httpbin.org/image/jpeg"}
                    }
                ]
            }
        ]
    }' `
    -ContentType "application/json").choices[0].message.content
```

## 🔧 Configuration Options

### Text Model Providers

**Local (Private):**
```python
"text": {
    "provider": "local",
    "model": "deepseek-r1-distill-qwen-7b",
    "url": "http://localhost:1234/v1/chat/completions"
}
```

**Cloud (Powerful):**
```python
"text": {
    "provider": "openai", 
    "model": "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
    "url": "https://openrouter.ai/api/v1/chat/completions",
    "api_key": "your-key-here"
}
```

### Supported Image Formats
- Local file paths: `C:/images/photo.jpg`
- URLs: `https://example.com/image.png`
- Base64: `data:image/jpeg;base64,/9j/4AAQ...` (from apps like Open-LLM-VTuber)

## 🗂️ Recommended Models

See `config/models.txt` for a full list of tested models.

**Vision Models (Local):**
- `google/gemma-3-4b` (4B Vision, recommended)
- `llava-1.5-7b-hf`
- `moondream2`

**Text Models:**
- **Free Cloud**: `cognitivecomputations/dolphin-mistral-24b-venice-edition:free`
- **Paid Cloud**: `anthropic/claude-3.5-sonnet`
- **Local**: `deepseek-r1-distill-qwen-7b`

## 🆘 Troubleshooting

### Common Issues

**"500 Internal Server Error"**
- ✅ Check if LM Studio is running on port 1234
- ✅ Verify your vision model is loaded in LM Studio
- ✅ Check Flask console for detailed error messages

**"400 Bad Request"**
- ✅ Make sure your vision model supports the image format
- ✅ Check if the image URL is accessible
- ✅ Verify your message format matches OpenAI spec

**"API Key Issues"**
- ✅ Get a free API key from [OpenRouter](https://openrouter.ai/)
- ✅ Set environment variable: `set OPENROUTER_API_KEY=your-key`
- ✅ Or edit `config/config.py` directly

## 📡 Open-LLM-VTuber Configuration

For Open-LLM-VTuber users, you can configure the API settings in the `conf.yaml` file. Below is an example configuration snippet:

```yaml
openai_compatible_llm:
  base_url: 'http://localhost:5000/v1'
  llm_api_key: 'somethingelse'
  organization_id: null
  project_id: null
  model: 'deepseek-r1-distill-qwen-7b' # model name does not matter
  temperature: 1.0 # value between 0 to 2
  interrupt_method: 'user'
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

MIT License - see `LICENSE` file for details.

## 🙏 Acknowledgments

- [LM Studio](https://lmstudio.ai/) for local model hosting
- [OpenRouter](https://openrouter.ai/) for cloud model access
- [Hugging Face](https://huggingface.co/) for model distribution

## ⭐ Star This Project

If this helped you, please give it a star! It helps others discover the project.