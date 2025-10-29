# LM Studio Setup Guide

## Overview
The image generation project has been updated to use LM Studio instead of Ollama. LM Studio provides a local AI server that can run various language models.

## Installation

### 1. Download LM Studio
1. Go to [https://lmstudio.ai/](https://lmstudio.ai/)
2. Download LM Studio for your operating system
3. Install and launch LM Studio

### 2. Load a Model
1. Open LM Studio
2. Go to the "Models" tab
3. Search for and download a suitable model (recommended: Llama 3, Mistral, or similar)
4. Load the model in LM Studio

### 3. Start Local Server
1. In LM Studio, go to the "Local Server" tab
2. Click "Start Server"
3. Note the server URL (default: `http://localhost:1234`)
4. Keep LM Studio running while using the image generator

## Configuration

### Default Settings
- **Server URL**: `http://localhost:1234`
- **Model**: `local-model` (LM Studio automatically uses the loaded model)
- **API Endpoint**: `/v1/chat/completions`

### Custom Configuration
If you need to change the server URL or port, update the `LMStudioImageGenerator` class in `backend/ollama_handler.py`:

```python
class LMStudioImageGenerator:
    def __init__(self, lm_studio_url: str = "http://localhost:1234"):
        self.lm_studio_url = lm_studio_url
        self.model = "local-model"
```

## API Endpoints Used

### Chat Completions
- **Endpoint**: `POST /v1/chat/completions`
- **Purpose**: Generate and refine image prompts
- **Payload**:
```json
{
    "model": "local-model",
    "messages": [
        {
            "role": "user",
            "content": "Your prompt here"
        }
    ],
    "temperature": 0.7,
    "max_tokens": 500,
    "stream": false
}
```

### Image Generation (Optional)
- **Endpoint**: `POST /v1/images/generations`
- **Purpose**: Generate images directly (if supported by your model)
- **Payload**:
```json
{
    "model": "local-model",
    "prompt": "Image generation prompt",
    "width": 1024,
    "height": 1024,
    "format": "png"
}
```

## Troubleshooting

### Connection Issues
1. **Check if LM Studio is running**: Make sure the local server is started
2. **Verify URL**: Default is `http://localhost:1234`
3. **Check port**: Ensure no other service is using port 1234
4. **Firewall**: Make sure firewall allows connections to localhost:1234

### Model Issues
1. **No model loaded**: Load a model in LM Studio before starting the server
2. **Model compatibility**: Some models may not support image generation
3. **Memory requirements**: Ensure sufficient RAM for the loaded model

### API Errors
1. **404 Not Found**: Check if the server is running and the URL is correct
2. **500 Internal Error**: Check LM Studio logs for model errors
3. **Timeout**: Increase timeout values in the code if needed

## Fallback Behavior

If LM Studio is not available or fails:
1. The system falls back to composite image generation using PIL
2. Uses the original prompt for basic image composition
3. Still supports all features (custom sizes, colors, text, positioning)

## Performance Tips

1. **Model Selection**: Choose a model that balances quality and speed
2. **Memory Management**: Close other applications to free up RAM
3. **Batch Processing**: Process multiple requests in sequence rather than parallel
4. **Caching**: LM Studio may cache responses for similar prompts

## Supported Models

LM Studio supports various models including:
- Llama 3 (recommended)
- Mistral
- CodeLlama
- Phi-3
- And many others from Hugging Face

Choose a model based on:
- **Quality**: Larger models generally provide better results
- **Speed**: Smaller models are faster
- **Memory**: Ensure your system can handle the model size

## Example Usage

Once LM Studio is running:

1. **Start the image generator backend**:
   ```bash
   cd backend
   python main.py
   ```

2. **Start the frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

3. **Use the application**:
   - Upload images
   - Create prompts with @tags
   - LM Studio will enhance your prompts for better results
   - Generate images with AI-powered layout suggestions

## Migration from Ollama

The migration from Ollama to LM Studio is seamless:
- Same functionality
- Same API interface
- Same prompt processing
- Better model management through LM Studio UI
- More stable local server

## Additional Features

LM Studio provides additional benefits:
- **Model Management**: Easy switching between models
- **Performance Monitoring**: Track usage and performance
- **Custom Models**: Load your own fine-tuned models
- **API Documentation**: Built-in API documentation
- **Web Interface**: User-friendly interface for testing

---

## Quick Start Checklist

- [ ] Download and install LM Studio
- [ ] Download a suitable model (Llama 3 recommended)
- [ ] Load the model in LM Studio
- [ ] Start the local server (port 1234)
- [ ] Verify server is running at `http://localhost:1234`
- [ ] Start the image generator backend
- [ ] Test with a simple prompt

Your image generator is now powered by LM Studio! 🚀
