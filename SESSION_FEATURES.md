# Session-Based Image Generator - Updated Features

## Overview
The application has been updated according to the requirements in `context.txt` to implement a comprehensive session-based image generation system.

## Key Features Implemented

### 🔄 Session Management
- **Automatic Session Creation**: Each user gets a unique session ID when they start the website
- **Session Isolation**: All uploaded files and generated content are isolated per session
- **Session Cleanup**: Automatic cleanup of old sessions (1 hour timeout)
- **Manual Session Reset**: Users can create a new session at any time

### 📤 Image Upload & Tagging
- **Session-Based Upload**: Images are uploaded to session-specific directories
- **Individual Image Tagging**: Each uploaded image can be assigned a unique tag
- **Batch Tag Assignment**: Support for assigning multiple tags at once
- **Tag Management**: Visual interface to manage and assign tags to images
- **Image Preview**: Thumbnail previews of uploaded images with tag status

### 🏷️ Tag-Based Prompting
- **@Tag Syntax**: Use `@tagName` in prompts to reference specific images
- **Tag Validation**: System validates that referenced tags exist
- **Smart Tag Suggestions**: Available tags are displayed and can be clicked to insert
- **Example Prompts**: Dynamic example prompts based on available tags

### 🎨 Image Generation
- **Static Image Composition**: Generate composite images with tagged elements
- **Position-Based Layout**: Support for background, foreground, center, left, right, top, bottom positioning
- **Smart Image Resizing**: Automatic resizing based on intended position
- **Canvas Management**: 1080x1080 canvas with proper image placement

### 🎬 Animation System
- **Movement Descriptions**: Parse natural language movement instructions
- **Supported Animations**:
  - Left to right movement
  - Right to left movement
  - Top to bottom movement
  - Bottom to top movement
  - Rotation effects
  - Bouncing effects
  - Fade effects
- **Frame Generation**: Create smooth animations with configurable frame counts
- **Stable Elements**: Support for static background elements

### 👀 Preview & Refinement
- **Real-time Preview**: Immediate preview of generated content
- **Error Handling**: Graceful error handling with user-friendly messages
- **Content Validation**: Validate prompts and tag references before generation
- **Loading States**: Clear loading indicators during generation

### 📥 Export Functionality
- **Download Images**: Export generated static images as PNG
- **Download GIFs**: Export generated animations as GIF files
- **Automatic Naming**: Timestamped filenames for downloads
- **Multiple Formats**: Support for various image formats

### 🧹 Session Lifecycle
- **Automatic Cleanup**: Sessions are automatically cleaned up after 1 hour of inactivity
- **Manual Reset**: Users can manually reset their session
- **File Isolation**: Each session maintains its own file storage
- **Memory Management**: Efficient session storage with automatic cleanup

## API Endpoints

### Session Management
- `POST /session/create/` - Create a new session
- `GET /session/{session_id}/` - Get session information
- `DELETE /session/{session_id}/` - Clean up a session

### Image Upload & Tagging
- `POST /upload/{session_id}/` - Upload images to session
- `POST /session/{session_id}/tag/` - Assign tag to specific image
- `POST /session/{session_id}/tags/batch/` - Batch assign tags

### Image Generation
- `POST /session/{session_id}/generate/` - Generate image/GIF from prompt

### File Access
- `GET /session/{session_id}/uploads/{filename}` - Get uploaded image
- `GET /session/{session_id}/output/{filename}` - Download generated content

## Usage Examples

### Basic Workflow
1. **Start Session**: Application automatically creates a session
2. **Upload Images**: Upload multiple images to the session
3. **Assign Tags**: Tag each image (e.g., "BG", "logo", "product")
4. **Create Prompt**: Use @tag syntax in prompts
5. **Generate**: Create static images or animated GIFs
6. **Preview & Export**: Download the generated content

### Example Prompts
- Static: `"Set @BG as background and @logo as front image"`
- Animation: `"@BG is stable background and @logo is moving from left to right"`
- Complex: `"Place @product in center, @logo on top right, and @BG as background"`

## Technical Implementation

### Backend (FastAPI)
- Session management with UUID-based session IDs
- File system organization by session
- Tag parsing with regex pattern matching
- Image composition with PIL (Pillow)
- Animation generation with frame-based approach

### Frontend (React)
- Session state management
- Real-time tag management interface
- Dynamic prompt suggestions
- File upload with progress indication
- Export functionality with download handling

### File Structure
```
backend/static/
├── uploads/
│   └── {session_id}/
│       └── {unique_filename}
└── output/
    └── {session_id}/
        └── {generated_filename}
```

## Benefits
- **Isolation**: Each user session is completely isolated
- **Scalability**: Automatic cleanup prevents storage bloat
- **User Experience**: Intuitive tag-based interface
- **Flexibility**: Support for both static and animated content
- **Reliability**: Comprehensive error handling and validation
