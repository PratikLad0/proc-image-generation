from PIL import Image, ImageDraw
import os
import re
import math

def create_animated_gif(image_paths: dict, prompt: str, output_path: str, duration=500, frame_count=10):
    """
    Create an animated GIF based on prompt with movement descriptions or presentation slideshow.
    
    Args:
        image_paths: Dict mapping tags to image file paths
        prompt: Text prompt describing the animation
        output_path: Output file path
        duration: Duration per frame in milliseconds
        frame_count: Number of frames to generate
    """
    # Check if this is a presentation-style prompt
    if is_presentation_prompt(prompt):
        return create_presentation_gif(image_paths, prompt, output_path, duration)
    
    # Parse animation instructions from prompt
    animation_instructions = parse_animation_instructions(prompt)
    
    # Extract custom dimensions from prompt
    canvas_size = extract_canvas_size_from_prompt(prompt)
    
    # Create frames
    frames = []
    
    for frame_idx in range(frame_count):
        # Create base canvas
        canvas = Image.new("RGB", canvas_size, color=(255, 255, 255))
        
        # Process each tagged image
        for tag, image_path in image_paths.items():
            if os.path.exists(image_path):
                try:
                    img = Image.open(image_path).convert("RGBA")
                    
                    # Get animation instruction for this tag
                    instruction = animation_instructions.get(tag, {"type": "static"})
                    
                    # Calculate position for this frame
                    x, y = calculate_animated_position(
                        img.size, instruction, canvas_size, frame_idx, frame_count
                    )
                    
                    # Resize image if needed
                    img = resize_for_animation(img, instruction, canvas_size)
                    
                    # Paste image onto canvas
                    if img.mode == "RGBA":
                        canvas.paste(img, (int(x), int(y)), img)
                    else:
                        canvas.paste(img, (int(x), int(y)))
                        
                except Exception as e:
                    # Skip problematic images
                    continue
        
        frames.append(canvas)
    
    # Save as animated GIF
    if frames:
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            optimize=False,
            duration=duration,
            loop=0,
        )
    
    return output_path


def is_presentation_prompt(prompt: str) -> bool:
    """Check if the prompt is asking for a presentation-style slideshow"""
    prompt_lower = prompt.lower()
    presentation_keywords = [
        "presentation", "slideshow", "shift images", "slide", "show images",
        "display images", "sequence", "order", "one by one", "turn by turn"
    ]
    return any(keyword in prompt_lower for keyword in presentation_keywords)


def should_add_text_overlay(prompt: str) -> bool:
    """Check if the prompt specifically requests text overlays"""
    prompt_lower = prompt.lower()
    text_keywords = [
        "add text", "with text", "text overlay", "show text", "display text",
        "tag name", "label", "caption", "title", "white text", "text color"
    ]
    return any(keyword in prompt_lower for keyword in text_keywords)


def extract_canvas_size_from_prompt(prompt: str) -> tuple:
    """Extract custom width and height from prompt"""
    import re
    
    # Look for various dimension patterns
    patterns = [
        r'(\d+)\s*x\s*(\d+)',  # 1920x1080, 1920 x 1080
        r'(\d+)\s*by\s*(\d+)',  # 1920 by 1080
        r'(\d+)\s*width\s*(\d+)\s*height',  # 1920 width 1080 height
        r'width\s*(\d+)\s*height\s*(\d+)',  # width 1920 height 1080
        r'(\d+)\s*wide\s*(\d+)\s*tall',  # 1920 wide 1080 tall
        r'(\d+)\s*pixels?\s*wide\s*(\d+)\s*pixels?\s*tall',  # 1920 pixels wide 1080 pixels tall
        r'size\s*(\d+)\s*x\s*(\d+)',  # size 1920x1080
        r'dimensions?\s*(\d+)\s*x\s*(\d+)',  # dimensions 1920x1080
    ]
    
    for pattern in patterns:
        match = re.search(pattern, prompt.lower())
        if match:
            width = int(match.group(1))
            height = int(match.group(2))
            
            # Validate reasonable dimensions
            if 100 <= width <= 4000 and 100 <= height <= 4000:
                return (width, height)
    
    # Look for common aspect ratios
    aspect_ratios = {
        'square': (1080, 1080),
        'landscape': (1920, 1080),
        'portrait': (1080, 1920),
        'widescreen': (1920, 1080),
        'instagram': (1080, 1080),
        'youtube': (1920, 1080),
        'facebook': (1200, 630),
        'twitter': (1200, 675),
    }
    
    prompt_lower = prompt.lower()
    for ratio_name, dimensions in aspect_ratios.items():
        if ratio_name in prompt_lower:
            return dimensions
    
    # Default size
    return (1080, 1080)


def create_presentation_gif(image_paths: dict, prompt: str, output_path: str, duration=2000):
    """
    Create a presentation-style GIF that shows images in sequence with text overlays.
    """
    import re
    from PIL import ImageDraw, ImageFont
    
    # Extract timing information from prompt
    timing_match = re.search(r'(\d+)\s*seconds?', prompt.lower())
    if timing_match:
        duration = int(timing_match.group(1)) * 1000  # Convert to milliseconds
    
    # Extract custom dimensions from prompt
    canvas_size = extract_canvas_size_from_prompt(prompt)
    
    # Extract image order from prompt
    tag_order = extract_image_order_from_prompt(prompt, list(image_paths.keys()))
    
    # Create frames for each image
    frames = []
    
    for tag in tag_order:
        if tag in image_paths and os.path.exists(image_paths[tag]):
            try:
                # Create base canvas
                canvas = Image.new("RGB", canvas_size, color=(0, 0, 0))  # Black background
                
                # Load and resize image
                img = Image.open(image_paths[tag]).convert("RGBA")
                img = resize_for_presentation(img, canvas_size)
                
                # Center the image
                x = (canvas_size[0] - img.size[0]) // 2
                y = (canvas_size[1] - img.size[1]) // 2
                
                # Paste image onto canvas
                if img.mode == "RGBA":
                    canvas.paste(img, (x, y), img)
                else:
                    canvas.paste(img, (x, y))
                
                # Add text overlay only if requested in prompt
                if should_add_text_overlay(prompt):
                    add_text_overlay_to_frame(canvas, tag, canvas_size, prompt)
                
                frames.append(canvas)
                
            except Exception as e:
                # Skip problematic images
                continue
    
    # Add a blank frame at the end for better presentation
    if frames:
        blank_frame = Image.new("RGB", canvas_size, color=(0, 0, 0))
        if should_add_text_overlay(prompt):
            add_text_overlay_to_frame(blank_frame, "End", canvas_size, prompt)
        frames.append(blank_frame)
    
    # Save as animated GIF
    if frames:
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            optimize=False,
            duration=duration,
            loop=0,
        )
        # Presentation GIF created successfully
    
    return output_path


def extract_image_order_from_prompt(prompt: str, available_tags: list) -> list:
    """Extract the order of images from the prompt"""
    import re
    
    # Look for explicit order in prompt
    order_match = re.search(r'order\s+@(\w+)(?:\s*,\s*@(\w+))*(?:\s*and\s*@(\w+))?', prompt.lower())
    if order_match:
        order = [order_match.group(1)]
        if order_match.group(2):
            order.append(order_match.group(2))
        if order_match.group(3):
            order.append(order_match.group(3))
        return [tag for tag in order if tag in available_tags]
    
    # Look for @tag references in sequence
    tag_sequence = re.findall(r'@(\w+)', prompt)
    ordered_tags = []
    for tag in tag_sequence:
        if tag in available_tags and tag not in ordered_tags:
            ordered_tags.append(tag)
    
    # If no specific order found, use available tags in original order
    if not ordered_tags:
        ordered_tags = available_tags
    
    return ordered_tags


def resize_for_presentation(img: Image.Image, canvas_size: tuple) -> Image.Image:
    """Resize image for presentation while maintaining aspect ratio"""
    canvas_width, canvas_height = canvas_size
    img_width, img_height = img.size
    
    # Calculate scaling to fit within canvas with some padding
    max_width = canvas_width - 100  # 50px padding on each side
    max_height = canvas_height - 150  # 75px padding top/bottom for text
    
    # Calculate scale factor
    scale_w = max_width / img_width
    scale_h = max_height / img_height
    scale = min(scale_w, scale_h, 1.0)  # Don't upscale
    
    new_width = int(img_width * scale)
    new_height = int(img_height * scale)
    
    return img.resize((new_width, new_height), Image.Resampling.LANCZOS)


def extract_text_content_from_prompt(prompt: str) -> str:
    """Extract custom text content from prompt"""
    import re
    
    # Look for quoted text
    quoted_pattern = r'["\']([^"\']+)["\']'
    match = re.search(quoted_pattern, prompt)
    if match:
        return match.group(1)
    
    # Look for "text: <content>" pattern
    text_pattern = r'text[:\s]+([^,\.]+)'
    match = re.search(text_pattern, prompt.lower())
    if match:
        # Get the original case text
        start_pos = match.start(1)
        text_content = prompt[start_pos:match.end(1)].strip()
        return text_content
    
    # Return None if no specific text found
    return None


def add_text_overlay_to_frame(canvas: Image.Image, text: str, canvas_size: tuple, prompt: str = ""):
    """Add text overlay to a frame"""
    from PIL import ImageDraw, ImageFont
    
    # Check if we should use custom text from prompt
    custom_text = extract_text_content_from_prompt(prompt) if prompt else None
    if custom_text:
        text = custom_text
    
    # Detect language
    language = "english"
    if prompt:
        prompt_lower = prompt.lower()
        if "hindi" in prompt_lower or "हिंदी" in prompt:
            language = "hindi"
    
    draw = ImageDraw.Draw(canvas)
    
    # Try to use a larger font based on language
    try:
        if language == "hindi":
            # Try to load a font that supports Devanagari script
            try:
                font = ImageFont.truetype("NotoSansDevanagari-Regular.ttf", 48)
            except:
                try:
                    font = ImageFont.truetype("/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf", 48)
                except:
                    font = ImageFont.load_default()
        else:
            # Try to load a system font
            try:
                font = ImageFont.truetype("arial.ttf", 48)
            except:
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
                except:
                    try:
                        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
                    except:
                        font = ImageFont.load_default()
    except:
        font = ImageFont.load_default()
    
    # Calculate text position (bottom center)
    text_bbox = draw.textbbox((0, 0), text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    x = (canvas_size[0] - text_width) // 2
    y = canvas_size[1] - text_height - 30  # 30px from bottom
    
    # Extract text color from prompt
    text_color = (255, 255, 255)  # Default white for GIFs
    if prompt:
        prompt_lower = prompt.lower()
        if "black text" in prompt_lower:
            text_color = (0, 0, 0)
        elif "red text" in prompt_lower:
            text_color = (255, 0, 0)
        elif "blue text" in prompt_lower:
            text_color = (0, 0, 255)
    
    # Add text with outline for better visibility
    # Draw outline
    outline_color = (0, 0, 0) if text_color == (255, 255, 255) else (255, 255, 255)
    for adj_x in [-2, -1, 0, 1, 2]:
        for adj_y in [-2, -1, 0, 1, 2]:
            if adj_x != 0 or adj_y != 0:
                draw.text((x + adj_x, y + adj_y), text, fill=outline_color, font=font)
    
    # Draw main text
    draw.text((x, y), text, fill=text_color, font=font)


def parse_animation_instructions(prompt: str) -> dict:
    """Parse animation instructions from prompt"""
    instructions = {}
    prompt_lower = prompt.lower()
    
    # Look for movement keywords
    for tag in re.findall(r'@(\w+)', prompt):
        instructions[tag] = {"type": "static"}  # Default
        
        if "moving" in prompt_lower or "move" in prompt_lower:
            if "left to right" in prompt_lower:
                instructions[tag] = {"type": "slide_horizontal", "direction": "left_to_right"}
            elif "right to left" in prompt_lower:
                instructions[tag] = {"type": "slide_horizontal", "direction": "right_to_left"}
            elif "up to down" in prompt_lower or "top to bottom" in prompt_lower:
                instructions[tag] = {"type": "slide_vertical", "direction": "top_to_bottom"}
            elif "down to up" in prompt_lower or "bottom to top" in prompt_lower:
                instructions[tag] = {"type": "slide_vertical", "direction": "bottom_to_top"}
            elif "rotate" in prompt_lower or "spinning" in prompt_lower:
                instructions[tag] = {"type": "rotate"}
            elif "bounce" in prompt_lower:
                instructions[tag] = {"type": "bounce"}
            elif "fade" in prompt_lower:
                instructions[tag] = {"type": "fade"}
        
        if "stable" in prompt_lower or "static" in prompt_lower:
            instructions[tag] = {"type": "static"}
    
    return instructions


def calculate_animated_position(img_size: tuple, instruction: dict, canvas_size: tuple, 
                              frame_idx: int, total_frames: int) -> tuple:
    """Calculate position for a specific frame based on animation type"""
    img_width, img_height = img_size
    canvas_width, canvas_height = canvas_size
    
    # Progress from 0 to 1
    progress = frame_idx / (total_frames - 1) if total_frames > 1 else 0
    
    if instruction["type"] == "static":
        # Center the image
        x = (canvas_width - img_width) // 2
        y = (canvas_height - img_height) // 2
        return (x, y)
    
    elif instruction["type"] == "slide_horizontal":
        direction = instruction.get("direction", "left_to_right")
        if direction == "left_to_right":
            x = int(progress * (canvas_width - img_width))
            y = (canvas_height - img_height) // 2
        else:  # right_to_left
            x = int((1 - progress) * (canvas_width - img_width))
            y = (canvas_height - img_height) // 2
        return (x, y)
    
    elif instruction["type"] == "slide_vertical":
        direction = instruction.get("direction", "top_to_bottom")
        if direction == "top_to_bottom":
            x = (canvas_width - img_width) // 2
            y = int(progress * (canvas_height - img_height))
        else:  # bottom_to_top
            x = (canvas_width - img_width) // 2
            y = int((1 - progress) * (canvas_height - img_height))
        return (x, y)
    
    elif instruction["type"] == "rotate":
        # Center position with rotation effect (simplified as position change)
        center_x = canvas_width // 2
        center_y = canvas_height // 2
        radius = min(canvas_width, canvas_height) // 4
        
        angle = progress * 2 * math.pi
        x = center_x + radius * math.cos(angle) - img_width // 2
        y = center_y + radius * math.sin(angle) - img_height // 2
        return (x, y)
    
    elif instruction["type"] == "bounce":
        # Bouncing effect
        bounce_height = canvas_height // 4
        bounce_progress = abs(math.sin(progress * math.pi * 2))
        
        x = (canvas_width - img_width) // 2
        y = canvas_height - img_height - int(bounce_height * bounce_progress)
        return (x, y)
    
    elif instruction["type"] == "fade":
        # Position stays same, but we could modify alpha (handled elsewhere)
        x = (canvas_width - img_width) // 2
        y = (canvas_height - img_height) // 2
        return (x, y)
    
    else:
        # Default to center
        x = (canvas_width - img_width) // 2
        y = (canvas_height - img_height) // 2
        return (x, y)


def resize_for_animation(img: Image.Image, instruction: dict, canvas_size: tuple) -> Image.Image:
    """Resize image for animation"""
    canvas_width, canvas_height = canvas_size
    img_width, img_height = img.size
    
    # For most animations, keep image at reasonable size
    max_size = min(canvas_width, canvas_height) // 3
    
    if max(img_width, img_height) > max_size:
        ratio = max_size / max(img_width, img_height)
        new_width = int(img_width * ratio)
        new_height = int(img_height * ratio)
        return img.resize((new_width, new_height), Image.Resampling.LANCZOS)
    
    return img
