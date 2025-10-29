# Quick Usage Guide - Enhanced Image Generator

## 🚀 Quick Start

### 1. Upload Images
- Click "Choose Files" and select multiple images
- Images are automatically tagged as **Image1**, **Image2**, **Image3**, etc.
- Upload more images later - numbering continues (Image4, Image5...)
- Manually rename tags if needed

### 2. Create Images with Prompts

#### Basic Image Generation
```
@Image1 as background, @Image2 in center
```

#### Custom Size
```
1024x1920 with @Image1 background and @Image2 center
```

#### Custom Background Color
```
Portrait with blue background, @Image1 center, @Image2 right
```

#### With Text
```
@Image1 background with text "Hello World"
```

#### With Hindi Text
```
@Image1 center, add text "नमस्ते" in hindi
```

#### Promotional Layout (with AI guidance)
```
Create promotional Instagram image with @Image1 and @Image2
```

### 3. Generate GIFs

#### Animated GIF
```
Check "Generate Animated GIF" box
@Image1 is moving from left to right, @Image2 is stable
```

#### Presentation/Slideshow (with text)
```
Check "Generate Animated GIF" box
Create presentation with @Image1, @Image2, @Image3, add text
```

#### Presentation without text
```
Check "Generate Animated GIF" box
Show images @Image1, @Image2, @Image3 as slideshow
```

### 4. Download Results
- **Download Image** - Single PNG file
- **Download GIF** - Single animated GIF
- **📦 Download All as ZIP** - All outputs in one file

---

## 📋 Supported Features

### Image Sizes
- **Exact dimensions**: `1024x1920`, `1920x1080`, `800 by 600`
- **Common formats**: `square`, `portrait`, `landscape`, `instagram`, `youtube`, `facebook`, `twitter`

### Background Colors
**Color names**: white, black, red, green, blue, yellow, cyan, magenta, gray, orange, purple, pink, brown, lightblue, darkblue, lightgreen, darkgreen

**RGB format**: `rgb(255, 0, 0)` for custom colors

**Hex format**: `#FF0000` for custom colors

### Image Positioning
- `center` - Center of canvas
- `left` - Left side
- `right` - Right side  
- `top` - Top position
- `bottom` - Bottom position
- `background` - Full canvas background
- `front`/`foreground` - Main focus

### Text Features
- **Only added when requested** (keywords: "add text", "with text", "text:")
- **Languages**: English, Hindi (हिंदी), Spanish, French
- **Position**: top, center, bottom
- **Color**: white, black, red, blue
- **Format**: Quoted text `"Hello World"` or pattern `text: Hello World`

### Animation Types (for GIFs)
- `moving left to right`
- `moving right to left`
- `moving top to bottom`
- `moving bottom to top`
- `rotating`
- `bouncing`
- `stable` - No movement
- `presentation`/`slideshow` - Show images in sequence

---

## 💡 Example Prompts

### Static Images

#### Simple Composition
```
@logo center, @background as background
```

#### With Custom Size and Color
```
1920x1080 with red background, @product center, @logo top right
```

#### With Text
```
@bg background, @logo center, add text "Welcome" at bottom
```

#### With Hindi Text
```
1024x1920 portrait with blue background, @product center, text "स्वागत है" in hindi
```

#### Promotional
```
Create promotional Facebook post with @product and @logo for marketing campaign
```

### Animated GIFs

#### Moving Elements
```
@background is stable, @logo is moving from left to right
```

#### Presentation/Slideshow without text
```
Create slideshow with @Image1, @Image2, @Image3
```

#### Presentation with text
```
Show presentation with @Image1, @Image2, @Image3, add text for each slide
```

#### With Custom Text
```
Create presentation with @Image1, @Image2, @Image3, add text "विशेष ऑफर" in hindi
```

---

## 🎯 Pro Tips

### 1. Auto-Tagging
- First upload: Image1, Image2, Image3
- Second upload: Image4, Image5 (continues from where it left off)
- Check the preview before uploading to see what tags will be assigned

### 2. Text Handling
- ✅ **Adds text**: `@bg with text "Hello"`, `add text "World"`, `text: Sample`
- ❌ **No text**: `@bg background`, `@logo center` (no text keywords)

### 3. Color Specification
- Quick: Use color names (`red background`, `blue color`)
- Precise: Use RGB (`rgb(255, 165, 0)`) or hex (`#FFA500`)

### 4. Size Specification
- Quick: Use presets (`portrait`, `landscape`, `instagram`, `youtube`)
- Custom: Use dimensions (`1024x1920`, `1920 by 1080`)

### 5. Promotional Images
- Include keywords like "promotional", "marketing", "advertisement"
- LLM will provide specialized layout guidance
- Specify target platform (Instagram, Facebook, etc.)

### 6. Multiple Downloads
- Generate multiple images/GIFs in one session
- Use **📦 Download All as ZIP** to get everything at once
- Organized with outputs in separate folders

---

## 🔧 Troubleshooting

### Text Not Showing
- ✅ Use keywords: "add text", "with text", "text:"
- ✅ Put text in quotes: "Hello World"
- ❌ Don't just describe text without keywords

### Wrong Tag Numbering
- Check existing images count before uploading
- Preview shows what tags will be assigned
- Manually rename tags if needed

### Image Not Positioned Correctly
- Be specific: "center", "top", "bottom left"
- Use "background" for full-canvas images
- Use "front" or "foreground" for main focus

### GIF Not Animating
- Check "Generate Animated GIF" checkbox
- Use movement keywords: "moving", "rotating", "sliding"
- For slideshows, use "presentation" or "slideshow"

### Hindi/Other Language Text Not Rendering
- Ensure proper font is installed on server
- System falls back to default font if specific font unavailable
- Text will still be rendered, just may not look perfect

---

## 📞 Common Use Cases

### E-commerce Product Image
```
1080x1080 with white background, @product center, @logo top right, add text "50% Off"
```

### Social Media Post
```
Create promotional Instagram image with @product and @brand_logo, text "New Arrival"
```

### Presentation Slides
```
Create presentation with @slide1, @slide2, @slide3, @slide4, add text for each
```

### Animated Banner
```
1920x400 banner with @background stable, @logo moving left to right, @product bouncing
```

### Multilingual Content
```
@bg background, @product center, text "विशेष ऑफर" in hindi, white text
```

---

## 🎨 Best Practices

1. **Upload all images first** before generating
2. **Use descriptive tags** instead of default Image1, Image2
3. **Be specific** with positioning and colors
4. **Test simple prompts first** before complex ones
5. **Use ZIP download** for multiple outputs
6. **Quote text content** for clarity: "Hello World"
7. **Specify language** when using non-English text
8. **Use promotional keywords** for marketing materials

---

## 🆘 Need Help?

Check `UPDATES_SUMMARY.md` for detailed technical documentation and all features.

Remember: The system is smart! It understands natural language, so be descriptive and specific with your requirements.

