# Ollama Setup Guide for AI Image Generation

## Overview
This application now integrates with Llama3 via Ollama for AI-powered image generation. The system uses Llama3 to process user prompts and generate detailed image descriptions, then creates images using AI generation models.

## Prerequisites

### 1. Install Ollama
Download and install Ollama from: https://ollama.ai/

### 2. Install Required Models

#### Llama3 (for prompt processing)
```bash
ollama pull llama3
```

#### Image Generation Model (choose one)

**Option A: Stable Diffusion (Recommended)**
```bash
# If you have access to Stable Diffusion via Ollama
ollama pull stable-diffusion
```

**Option B: Alternative Image Generation Models**
```bash
# Other options (if available in your Ollama setup)
ollama pull flux
ollama pull sdxl
```

### 3. Verify Installation
```bash
# Check if models are installed
ollama list

# Test Llama3
ollama run llama3 "Hello, how are you?"

# Test image generation model (if available)
ollama run stable-diffusion "a beautiful landscape"
```

## Configuration

### Backend Configuration
The application is configured to use:
- **Ollama URL**: `http://localhost:11434` (default)
- **Llama3 Model**: `llama3` (for prompt processing)
- **Image Model**: `stable-diffusion` (for image generation)

### Custom Configuration
You can modify the Ollama configuration in `backend/ollama_handler.py`:

```python
class OllamaImageGenerator:
    def __init__(self, ollama_url: str = "http://localhost:11434"):
        self.ollama_url = ollama_url
        self.model = "llama3"  # Change this if using different model
```

## How It Works

### 1. Prompt Processing
1. User enters a prompt with @tags (e.g., "Set @BG as background and @logo as front")
2. Llama3 processes the prompt and generates a detailed image generation description
3. The AI prompt is optimized for image generation models

### 2. Image Generation
1. The processed prompt is sent to the image generation model
2. AI generates a new image based on the prompt
3. Generated image is saved to the session output directory

### 3. Refinement
1. User can provide feedback on generated images
2. Llama3 processes the feedback and refines the original prompt
3. A new image is generated with the refined prompt

## API Endpoints

### New AI Generation Endpoints
- `POST /session/{session_id}/generate/` - Generate AI image from prompt
- `POST /session/{session_id}/refine/` - Refine image with AI feedback

### Request Format
```json
{
  "prompt": "Set @BG as background and @logo as front image",
  "generate_gif": false
}
```

### Refinement Request Format
```json
{
  "original_prompt": "Set @BG as background and @logo as front image",
  "feedback": "Make the logo bigger and add a shadow effect",
  "generate_gif": false
}
```

## Fallback System

The application includes a robust fallback system:

1. **Primary**: AI generation via Ollama
2. **Fallback**: Composite image generation (original system)
3. **External API**: Placeholder for external image generation services

If Ollama is not available or fails, the system automatically falls back to the original composite image generation.

## Troubleshooting

### Common Issues

#### 1. Ollama Not Running
```bash
# Start Ollama service
ollama serve
```

#### 2. Model Not Found
```bash
# Check available models
ollama list

# Pull required models
ollama pull llama3
ollama pull stable-diffusion
```

#### 3. Permission Issues
```bash
# Make sure Ollama has proper permissions
sudo chmod +x /usr/local/bin/ollama
```

#### 4. Port Conflicts
If port 11434 is in use, you can change the Ollama URL in the configuration.

### Debug Mode
Enable debug logging by checking the console output for error messages. The system will log:
- Ollama command execution
- Prompt processing results
- Image generation status
- Fallback activations

## Performance Optimization

### 1. Model Selection
- Use smaller models for faster processing
- Consider using quantized versions for better performance

### 2. Caching
- Generated prompts are cached in session memory
- Consider implementing persistent caching for better performance

### 3. Resource Management
- Monitor system resources during generation
- Adjust timeout values based on your hardware

## Security Considerations

### 1. Local Processing
- All AI processing happens locally via Ollama
- No external API calls for sensitive data

### 2. Session Isolation
- Each session maintains its own generated content
- Automatic cleanup prevents data accumulation

### 3. Input Validation
- All prompts are validated before processing
- Tag references are verified against session images

## Future Enhancements

### 1. External API Integration
The system includes placeholders for external image generation APIs:
- Replicate API
- Hugging Face Inference API
- Stability AI API
- Custom image generation services

### 2. Advanced Prompt Engineering
- Template-based prompt generation
- Style transfer capabilities
- Multi-modal input support

### 3. Batch Processing
- Multiple image generation
- Batch refinement capabilities
- Queue-based processing

## Support

For issues related to:
- **Ollama**: Check Ollama documentation and community
- **Model Installation**: Refer to Ollama model repository
- **Application Integration**: Check application logs and error messages

The system is designed to be robust and will gracefully handle failures by falling back to the original composite image generation system.
