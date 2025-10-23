#!/usr/bin/env python3
"""
Test script for GIF generation to debug the blank GIF issue.
"""

import os
import sys
from gif_generator import create_presentation_gif, is_presentation_prompt

def test_presentation_detection():
    """Test if presentation prompts are detected correctly"""
    test_prompts = [
        "I want to create gif in which genrates a presentation shift images in 2 seconds also add Text with White color on the bottom of tag name create in order @Sunny, @Vally and @Alien",
        "Create a slideshow with @Sunny, @Vally, @Alien",
        "Show images one by one",
        "Display images in sequence",
        "Make @Sunny move from left to right"
    ]
    
    print("Testing presentation prompt detection:")
    for prompt in test_prompts:
        is_presentation = is_presentation_prompt(prompt)
        print(f"  '{prompt[:50]}...' -> {is_presentation}")
    print()

def test_gif_generation():
    """Test GIF generation with sample data"""
    # Sample image paths (you'll need to replace these with actual paths)
    image_paths = {
        "Sunny": "backend/uploads/test_sunny.jpg",
        "Vally": "backend/uploads/test_vally.jpg", 
        "Alien": "backend/uploads/test_alien.jpg"
    }
    
    prompt = "I want to create gif in which genrates a presentation shift images in 2 seconds also add Text with White color on the bottom of tag name create in order @Sunny, @Vally and @Alien"
    output_path = "backend/static/temp/test_presentation.gif"
    
    print("Testing GIF generation:")
    print(f"  Prompt: {prompt}")
    print(f"  Images: {image_paths}")
    print(f"  Output: {output_path}")
    
    # Check if images exist
    missing_images = []
    for tag, path in image_paths.items():
        if not os.path.exists(path):
            missing_images.append(f"{tag}: {path}")
    
    if missing_images:
        print(f"  Missing images: {missing_images}")
        print("  Creating dummy images for testing...")
        
        # Create dummy images for testing
        from PIL import Image, ImageDraw
        os.makedirs("backend/uploads", exist_ok=True)
        
        for tag, path in image_paths.items():
            if not os.path.exists(path):
                # Create a simple colored image
                img = Image.new("RGB", (400, 300), color=(100, 150, 200))
                draw = ImageDraw.Draw(img)
                draw.text((50, 50), f"Test {tag}", fill=(255, 255, 255))
                img.save(path)
                print(f"    Created dummy image: {path}")
    
    try:
        # Test the presentation GIF generation
        result = create_presentation_gif(image_paths, prompt, output_path)
        print(f"  Result: {result}")
        
        if os.path.exists(output_path):
            file_size = os.path.getsize(output_path)
            print(f"  GIF created successfully! Size: {file_size} bytes")
        else:
            print("  ERROR: GIF file was not created!")
            
    except Exception as e:
        print(f"  ERROR: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main test function"""
    print("=== GIF Generation Test ===")
    print()
    
    test_presentation_detection()
    test_gif_generation()
    
    print("=== Test Complete ===")

if __name__ == "__main__":
    main()
