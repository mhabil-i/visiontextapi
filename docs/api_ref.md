# 📚 API Reference

This API follows the OpenAI Chat Completions format, making it compatible with existing OpenAI clients.

## Base URL
```
http://localhost:5000
```

## Endpoints

### POST /v1/chat/completions

Main endpoint for text and vision processing.

#### Request Format

```json
{
  "model": "any-model-name",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": "What do you see in this image?"
        },
        {
          "type": "image_url",
          "image_url": {
            "url": "path/to/image.jpg"
          }
        }
      ]
    }
  ],
  "stream": false,
  "temperature": 0.7,
  "max_tokens": 1000
}
```

#### Supported Image Formats

**Local Files:**
```json
{
  "type": "image_url",
  "image_url": {
    "url": "C:/Users/username/Pictures/photo.jpg"
  }
}
```

**URLs:**
```json
{
  "type": "image_url", 
  "image_url": {
    "url": "https://example.com/image.png"
  }
}
```

**Base64 (from OpenLLMVtuber):**
```json
{
  "type": "image_url",
  "image_url": {
    "url": "data:image/jpeg;base64,/9j/4AAQSkZJRg..."
  }
}
```

#### Text-Only Request

```json
{
  "model": "test",
  "messages": [
    {
      "role": "user",
      "content": "Hello, how are you?"
    }
  ]
}
```

#### Parameters

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `model` | string | From config | Model name (can be any string) |
| `messages` | array | Required | Array of message objects |
| `stream` | boolean | false | Enable streaming responses |
| `temperature` | float | 0.7 | Randomness (0.0-2.0) |
| `max_tokens` | integer | - | Maximum tokens to generate |
| `top_p` | float | 1.0 | Nucleus sampling |
| `frequency_penalty` | float | 0.0 | Frequency penalty (-2.0 to 2.0) |
| `presence_penalty` | float | 0.0 | Presence penalty (-2.0 to 2.0) |

#### Response Format

**Non-streaming:**
```json
{
  "id": "chatcmpl-123456",
  "object": "chat.completion",
  "created": 1677652288,
  "model": "test-model",
  "choices": [
    {
      "index": 0,
      "message": {
        "role": "assistant",
        "content": "I can see a coyote walking on a dirt path..."
      },
      "finish_reason": "stop"
    }
  ],
  "usage": {
    "prompt_tokens": 25,
    "completion_tokens": 50,
    "total_tokens": 75
  }
}
```

**Streaming:**
```
data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"test","choices":[{"index":0,"delta":{"content":"I"},"finish_reason":null}]}

data: {"id":"chatcmpl-123","object":"chat.completion.chunk","created":1677652288,"model":"test","choices":[{"index":0,"delta":{"content":" can"},"finish_reason":null}]}

data: [DONE]
```

### GET /health

Health check endpoint.

#### Response
```json
{
  "status": "healthy",
  "timestamp": 1677652288,
  "version": "1.0.0",
  "text_provider": "openai",
  "vision_model": "huihui-internvl3-2b-abliterated"
}
```

### GET /config

Get current configuration (API keys hidden).

#### Response
```json
{
  "text": {
    "provider": "openai",
    "model": "cognitivecomputations/dolphin-mistral-24b-venice-edition:free",
    "url": "https://openrouter.ai/api/v1/chat/completions",
    "api_key": "***hidden***"
  },
  "vision": {
    "model": "huihui-internvl3-2b-abliterated",
    "url": "http://localhost:1234/v1/chat/completions"
  }
}
```

## Processing Flow

1. **Request received** → Parse messages and detect images
2. **If images found:**
   - Convert images to base64 (download URLs, encode local files)
   - Send to **local vision model**
   - Get image description
   - Combine with user text
3. **Text processing:**
   - Send combined prompt to configured text model (local or cloud)
   - Return response

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid request format"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error: Model connection failed"
}
```

## Client Examples

### Python with requests
```python
import requests

response = requests.post("http://localhost:5000/v1/chat/completions", json={
    "model": "test",
    "messages": [
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {"type": "image_url", "image_url": {"url": "image.jpg"}}
            ]
        }
    ]
})

print(response.json()["choices"][0]["message"]["content"])
```

### JavaScript/Node.js
```javascript
const response = await fetch('http://localhost:5000/v1/chat/completions', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    model: 'test',
    messages: [
      {
        role: 'user',
        content: [
          { type: 'text', text: 'Describe this image' },
          { type: 'image_url', image_url: { url: 'https://example.com/image.jpg' } }
        ]
      }
    ]
  })
});

const data = await response.json();
console.log(data.choices[0].message.content);
```

### cURL
```bash
curl -X POST http://localhost:5000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "test",
    "messages": [
      {
        "role": "user",
        "content": [
          {"type": "text", "text": "What do you see?"},
          {"type": "image_url", "image_url": {"url": "image.jpg"}}
        ]
      }
    ],
    "temperature": 0.7,
    "max_tokens": 500
  }'
```

## OpenAI Client Compatibility

This API is compatible with OpenAI Python client:

```python
from openai import OpenAI

client = OpenAI(
    base_url="http://localhost:5000/v1",
    api_key="dummy-key"  # Not used, but required by client
)

response = client.chat.completions.create(
    model="test",
    messages=[
        {
            "role": "user",
            "content": [
                {"type": "text", "text": "What's in this image?"},
                {"type": "image_url", "image_url": {"url": "path/to/image.jpg"}}
            ]
        }
    ]
)

print(response.choices[0].message.content)
```

## Rate Limits

No rate limits are implemented. However, be mindful of:
- Vision model processing time (2-5 seconds per image)
- Cloud API rate limits (if using OpenRouter/OpenAI)
- Local hardware limitations

## Best Practices

1. **Optimize image size** - Smaller images process faster
2. **Use appropriate formats** - JPEG for photos, PNG for screenshots
3. **Handle errors gracefully** - Network issues can cause timeouts
4. **Cache results** - Vision processing is expensive
5. **Monitor local resources** - Vision models use significant VRAM