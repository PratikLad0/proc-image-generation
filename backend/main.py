from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, JSONResponse
from typing import List, Dict, Optional
import os
import uuid
import shutil
from PIL import Image
import re
from datetime import datetime
import zipfile

# Initialize app
app = FastAPI(title="Proc Image Generator API")

# Enable CORS for frontend (Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to ["http://localhost:5173"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Folders
BASE_DIR = "backend/static"
UPLOAD_DIR = f"{BASE_DIR}/uploads"
OUTPUT_DIR = f"{BASE_DIR}/output"
TEMP_DIR = f"{BASE_DIR}/temp"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(TEMP_DIR, exist_ok=True)

# Session storage
sessions: Dict[str, Dict] = {}

class SessionManager:
    @staticmethod
    def create_session() -> str:
        session_id = str(uuid.uuid4())
        session_dir = os.path.join(UPLOAD_DIR, session_id)
        output_dir = os.path.join(OUTPUT_DIR, session_id)
        os.makedirs(session_dir, exist_ok=True)
        os.makedirs(output_dir, exist_ok=True)
        
        sessions[session_id] = {
            "created_at": datetime.now(),
            "upload_dir": session_dir,
            "output_dir": output_dir,
            "images": {},  # filename -> tag mapping
            "last_activity": datetime.now()
        }
        return session_id
    
    @staticmethod
    def get_session(session_id: str) -> Optional[Dict]:
        if session_id in sessions:
            sessions[session_id]["last_activity"] = datetime.now()
            return sessions[session_id]
        return None
    
    @staticmethod
    def cleanup_session(session_id: str):
        if session_id in sessions:
            session = sessions[session_id]
            # Remove directories
            if os.path.exists(session["upload_dir"]):
                shutil.rmtree(session["upload_dir"])
            if os.path.exists(session["output_dir"]):
                shutil.rmtree(session["output_dir"])
            # Remove from memory
            del sessions[session_id]
    
    @staticmethod
    def cleanup_old_sessions():
        """Clean up sessions older than 1 hour"""
        current_time = datetime.now()
        to_remove = []
        for session_id, session_data in sessions.items():
            if (current_time - session_data["last_activity"]).seconds > 3600:
                to_remove.append(session_id)
        
        for session_id in to_remove:
            SessionManager.cleanup_session(session_id)


@app.get("/")
def root():
    return {"message": "Backend running successfully on port 5000"}


# ==========================================
# 🔄 Session Management
# ==========================================
@app.post("/session/create/")
async def create_session():
    """Create a new session"""
    session_id = SessionManager.create_session()
    return {"session_id": session_id, "message": "Session created successfully"}


@app.get("/session/{session_id}/")
async def get_session_info(session_id: str):
    """Get session information"""
    session = SessionManager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session_id,
        "created_at": session["created_at"],
        "images": session["images"],
        "image_count": len(session["images"])
    }


@app.delete("/session/{session_id}/")
async def cleanup_session(session_id: str):
    """Clean up a session and all its files"""
    SessionManager.cleanup_session(session_id)
    return {"message": "Session cleaned up successfully"}


# ==========================================
# 📤 Upload Images with Tags
# ==========================================
@app.post("/upload/{session_id}/")
async def upload_images(session_id: str, files: List[UploadFile] = File(...)):
    """Upload images to a specific session"""
    session = SessionManager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    saved_files = []
    for file in files:
        # Generate unique filename to avoid conflicts
        file_extension = os.path.splitext(file.filename)[1]
        unique_filename = f"{uuid.uuid4()}{file_extension}"
        file_path = os.path.join(session["upload_dir"], unique_filename)
        
        with open(file_path, "wb") as f:
            f.write(await file.read())
        
        # Add to session images without tag initially
        session["images"][unique_filename] = None
        saved_files.append(unique_filename)

    return {"count": len(saved_files), "files": saved_files, "session_id": session_id}


# ==========================================
# 🏷️ Assign Tags to Images
# ==========================================
@app.post("/session/{session_id}/tag/")
async def assign_tag(session_id: str, payload: dict):
    """Assign a tag to a specific image in the session"""
    session = SessionManager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    filename = payload.get("filename")
    tag = payload.get("tag")
    
    if not filename or not tag:
        raise HTTPException(status_code=400, detail="Both filename and tag are required")
    
    if filename not in session["images"]:
        raise HTTPException(status_code=404, detail="Image not found in session")
    
    session["images"][filename] = tag
    return {"message": f"Tag '{tag}' assigned to {filename}"}


@app.post("/session/{session_id}/tags/batch/")
async def assign_tags_batch(session_id: str, payload: dict):
    """Assign multiple tags to images in batch"""
    session = SessionManager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    tag_assignments = payload.get("assignments", [])
    
    for assignment in tag_assignments:
        filename = assignment.get("filename")
        tag = assignment.get("tag")
        
        if filename and tag and filename in session["images"]:
            session["images"][filename] = tag
    
    return {"message": f"Assigned {len(tag_assignments)} tags", "session_id": session_id}


# ==========================================
# 🧠 Tag Parsing and Image Generation
# ==========================================
def parse_prompt_tags(prompt: str) -> List[str]:
    """Extract @tag references from prompt"""
    tag_pattern = r'@(\w+)'
    return re.findall(tag_pattern, prompt)

def get_tagged_images(session: Dict, tags: List[str]) -> Dict[str, str]:
    """Get image filenames for given tags"""
    tagged_images = {}
    for tag in tags:
        for filename, assigned_tag in session["images"].items():
            if assigned_tag == tag:
                tagged_images[tag] = filename
                break
    return tagged_images

@app.post("/session/{session_id}/generate/")
async def generate_image(session_id: str, payload: dict):
    """Generate image based on prompt with tagged images"""
    session = SessionManager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    prompt = payload.get("prompt", "")
    generate_gif = payload.get("generate_gif", False)
    
    if not prompt:
        raise HTTPException(status_code=400, detail="Prompt is required")
    
    # Parse tags from prompt
    tags = parse_prompt_tags(prompt)
    if not tags:
        raise HTTPException(status_code=400, detail="No @tags found in prompt")
    
    # Get tagged images
    tagged_images = get_tagged_images(session, tags)
    if not tagged_images:
        raise HTTPException(status_code=400, detail="No images found for the specified tags")
    
    # Check if all tags have corresponding images
    missing_tags = [tag for tag in tags if tag not in tagged_images]
    if missing_tags:
        raise HTTPException(status_code=400, detail=f"Images not found for tags: {missing_tags}")
    
    try:
        if generate_gif:
            # Generate animated GIF
            output_path = await generate_animated_gif(session, tagged_images, prompt)
            
            # Check if file was actually created
            if not os.path.exists(output_path):
                raise Exception("GIF file was not created")
            
            return {
                "message": "Animated GIF generated successfully",
                "gif_path": f"/session/{session_id}/output/{os.path.basename(output_path)}",
                "session_id": session_id
            }
        else:
            # Generate static image
            output_path = await generate_static_image(session, tagged_images, prompt)
            return {
                "message": "Image generated successfully",
                "image_path": f"/session/{session_id}/output/{os.path.basename(output_path)}",
                "session_id": session_id
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")


async def generate_static_image(session: Dict, tagged_images: Dict[str, str], prompt: str) -> str:
    """Generate a static image using AI (Llama3 + Ollama)"""
    from .ollama_handler import generate_ai_image
    
    output_filename = f"generated_{uuid.uuid4()}.png"
    output_path = os.path.join(session["output_dir"], output_filename)
    
    try:
        # Generate AI image using Llama3 + Ollama (dimensions will be extracted from prompt)
        ai_image_path = generate_ai_image(prompt, tagged_images)
        
        if ai_image_path and os.path.exists(ai_image_path):
            # Move the generated image to session output directory
            import shutil
            shutil.move(ai_image_path, output_path)
            return output_path
        else:
            # Fallback to composite image generation
            from .image_composer import compose_image_with_tags
            image_paths = {}
            for tag, filename in tagged_images.items():
                image_paths[tag] = os.path.join(session["upload_dir"], filename)
            compose_image_with_tags(image_paths, prompt, output_path)
            return output_path
            
    except Exception as e:
        # Fallback to composite image generation
        from .image_composer import compose_image_with_tags
        image_paths = {}
        for tag, filename in tagged_images.items():
            image_paths[tag] = os.path.join(session["upload_dir"], filename)
        compose_image_with_tags(image_paths, prompt, output_path)
        return output_path


async def generate_animated_gif(session: Dict, tagged_images: Dict[str, str], prompt: str) -> str:
    """Generate an animated GIF based on prompt"""
    from .gif_generator import create_animated_gif
    
    output_filename = f"animated_{uuid.uuid4()}.gif"
    output_path = os.path.join(session["output_dir"], output_filename)
    
    # Prepare image paths
    image_paths = {}
    for tag, filename in tagged_images.items():
        image_paths[tag] = os.path.join(session["upload_dir"], filename)
    
    # Check if we have images to work with
    if not image_paths:
        raise Exception("No tagged images found for GIF generation")
    
    # Check if images exist
    missing_images = []
    for tag, path in image_paths.items():
        if not os.path.exists(path):
            missing_images.append(f"{tag}: {path}")
    
    if missing_images:
        # Remove missing images from the list
        image_paths = {tag: path for tag, path in image_paths.items() if os.path.exists(path)}
    
    if not image_paths:
        raise Exception("No valid images found for GIF generation")
    
    # Generate animated GIF
    create_animated_gif(image_paths, prompt, output_path)
    return output_path


# ==========================================
# 📥 Download Generated Files
# ==========================================
@app.get("/session/{session_id}/output/{filename}")
async def download_output(session_id: str, filename: str):
    """Download generated image or GIF"""
    session = SessionManager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    file_path = os.path.join(session["output_dir"], filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found")
    
    # Determine media type
    if filename.lower().endswith('.gif'):
        media_type = "image/gif"
    else:
        media_type = "image/png"
    
    return FileResponse(file_path, media_type=media_type, filename=filename)


@app.get("/session/{session_id}/uploads/{filename}")
async def get_uploaded_image(session_id: str, filename: str):
    """Get uploaded image from session"""
    session = SessionManager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    file_path = os.path.join(session["upload_dir"], filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Image not found")
    
    # Determine media type based on file extension
    if filename.lower().endswith('.gif'):
        media_type = "image/gif"
    elif filename.lower().endswith(('.jpg', '.jpeg')):
        media_type = "image/jpeg"
    elif filename.lower().endswith('.png'):
        media_type = "image/png"
    else:
        media_type = "image/jpeg"  # Default
    
    return FileResponse(file_path, media_type=media_type)


# ==========================================
# 🔄 Image Refinement with AI
# ==========================================
@app.post("/session/{session_id}/refine/")
async def refine_image(session_id: str, payload: dict):
    """Refine an image based on user feedback using AI"""
    session = SessionManager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    original_prompt = payload.get("original_prompt", "")
    user_feedback = payload.get("feedback", "")
    generate_gif = payload.get("generate_gif", False)
    
    if not original_prompt or not user_feedback:
        raise HTTPException(status_code=400, detail="Both original prompt and feedback are required")
    
    try:
        from .ollama_handler import refine_ai_image
        
        # Refine the prompt using AI
        refined_prompt = refine_ai_image(original_prompt, user_feedback)
        
        # Get tagged images for the session
        tagged_images = {}
        for filename, tag in session["images"].items():
            if tag:
                tagged_images[tag] = filename
        
        if generate_gif:
            # Generate refined animated GIF
            output_path = await generate_animated_gif(session, tagged_images, refined_prompt)
            return {
                "message": "Refined animated GIF generated successfully",
                "gif_path": f"/session/{session_id}/output/{os.path.basename(output_path)}",
                "refined_prompt": refined_prompt,
                "session_id": session_id
            }
        else:
            # Generate refined static image
            output_path = await generate_static_image(session, tagged_images, refined_prompt)
            return {
                "message": "Refined image generated successfully",
                "image_path": f"/session/{session_id}/output/{os.path.basename(output_path)}",
                "refined_prompt": refined_prompt,
                "session_id": session_id
            }
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refinement failed: {str(e)}")


# ==========================================
# 🧹 Cleanup Old Sessions (Background Task)
# ==========================================
@app.post("/test/gif/")
async def test_gif_generation(payload: dict):
    """Test endpoint for debugging GIF generation"""
    try:
        from .gif_generator import create_presentation_gif, is_presentation_prompt
        
        prompt = payload.get("prompt", "")
        image_paths = payload.get("image_paths", {})
        
        # Test GIF generation
        
        # Create test output path
        test_output = "backend/static/temp/test_debug.gif"
        os.makedirs(os.path.dirname(test_output), exist_ok=True)
        
        # Test the generation
        result = create_presentation_gif(image_paths, prompt, test_output)
        
        if os.path.exists(result):
            file_size = os.path.getsize(result)
            return {
                "success": True,
                "message": f"Test GIF created successfully",
                "file_path": result,
                "file_size": file_size,
                "is_presentation": is_presentation_prompt(prompt)
            }
        else:
            return {
                "success": False,
                "message": "Test GIF was not created",
                "file_path": result
            }
            
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        return {
            "success": False,
            "message": f"Test failed: {str(e)}",
            "error_details": error_details
        }


# ==========================================
# 🎤 Voice-to-Text Processing
# ==========================================
@app.post("/voice/transcribe/")
async def transcribe_voice(audio_file: UploadFile = File(...)):
    """Transcribe audio file to text (fallback for browsers without speech recognition)"""
    try:
        # This is a placeholder for voice transcription
        # You would integrate with services like:
        # - Google Speech-to-Text API
        # - Azure Speech Services
        # - AWS Transcribe
        # - OpenAI Whisper API
        
        # For now, return a placeholder response
        return {
            "success": False,
            "message": "Voice transcription not implemented. Please use browser speech recognition.",
            "transcript": ""
        }
        
    except Exception as e:
        return {
            "success": False,
            "message": f"Voice transcription failed: {str(e)}",
            "transcript": ""
        }


@app.post("/session/{session_id}/zip/")
async def create_zip_archive(session_id: str, payload: dict):
    """Create a ZIP archive of generated images or all session files"""
    session = SessionManager.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    include_outputs = payload.get("include_outputs", True)
    include_uploads = payload.get("include_uploads", False)
    
    try:
        # Create ZIP file
        zip_filename = f"session_{session_id}_{uuid.uuid4()}.zip"
        zip_path = os.path.join(TEMP_DIR, zip_filename)
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add output files
            if include_outputs and os.path.exists(session["output_dir"]):
                for filename in os.listdir(session["output_dir"]):
                    file_path = os.path.join(session["output_dir"], filename)
                    if os.path.isfile(file_path):
                        zipf.write(file_path, f"outputs/{filename}")
            
            # Add upload files
            if include_uploads and os.path.exists(session["upload_dir"]):
                for filename in os.listdir(session["upload_dir"]):
                    file_path = os.path.join(session["upload_dir"], filename)
                    if os.path.isfile(file_path):
                        zipf.write(file_path, f"uploads/{filename}")
        
        # Return the ZIP file
        return FileResponse(
            zip_path,
            media_type="application/zip",
            filename=f"session_{session_id}.zip",
            headers={"Content-Disposition": f"attachment; filename=session_{session_id}.zip"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create ZIP: {str(e)}")


@app.on_event("startup")
async def startup_event():
    """Clean up old sessions on startup"""
    SessionManager.cleanup_old_sessions()
