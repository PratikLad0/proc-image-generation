import React, { useState, useEffect, useCallback } from "react";
import TagManager from "./TagManager";

export default function UploadSection({ sessionId, onUpload, onSessionUpdate }) {
  const [files, setFiles] = useState([]);
  const [uploadedFiles, setUploadedFiles] = useState([]);
  const [imageTags, setImageTags] = useState({});
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");

  const fetchSessionImages = useCallback(async () => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/session/${sessionId}/`);
      if (response.ok) {
        const data = await response.json();
        setUploadedFiles(Object.keys(data.images));
        setImageTags(data.images);
        onSessionUpdate(data.images);
      }
    } catch (error) {
      console.error("Error fetching session images:", error);
    }
  }, [sessionId, onSessionUpdate]);

  // Fetch session images when sessionId changes
  useEffect(() => {
    if (sessionId) {
      fetchSessionImages();
    }
  }, [sessionId, fetchSessionImages]);

  const handleFileChange = (e) => {
    setFiles(Array.from(e.target.files));
  };

  const handleUpload = async () => {
    if (files.length === 0) {
      setMessage("Please select at least one image.");
      return;
    }

    setLoading(true);
    setMessage("");

    const formData = new FormData();
    files.forEach((file) => formData.append("files", file));

    try {
      const response = await fetch(`http://127.0.0.1:5000/upload/${sessionId}/`, {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error("Upload failed");
      const result = await response.json();
      
      // Auto-assign tags based on upload order
      await autoAssignTags(result.files);
      
      setMessage(`Uploaded ${result.count || files.length} image(s) successfully with auto-tags.`);
      
      // Refresh session images
      await fetchSessionImages();
      onUpload(files);
      
      // Clear file input
      setFiles([]);
    } catch (err) {
      setMessage("Error uploading files: " + err.message);
    } finally {
      setLoading(false);
    }
  };

  const autoAssignTags = async (newFiles) => {
    try {
      // Get current image count from state to continue numbering from where we left off
      const existingImageCount = uploadedFiles.length;
      const assignments = newFiles.map((filename, index) => ({
        filename: filename,
        tag: `Image${existingImageCount + index + 1}`
      }));

      const response = await fetch(`http://127.0.0.1:5000/session/${sessionId}/tags/batch/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ assignments }),
      });

      if (!response.ok) throw new Error("Failed to assign auto-tags");
      
    } catch (err) {
      console.error("Error assigning auto-tags:", err);
    }
  };

  const handleTagAssign = async (filename, tag) => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/session/${sessionId}/tag/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ filename, tag }),
      });

      if (!response.ok) throw new Error("Failed to assign tag");
      
      // Update local state
      setImageTags(prev => ({ ...prev, [filename]: tag }));
      onSessionUpdate({ ...imageTags, [filename]: tag });
      setMessage(`Tag '${tag}' assigned to ${filename}`);
    } catch (err) {
      setMessage("Error assigning tag: " + err.message);
    }
  };

  const handleBatchTagAssign = async (assignments) => {
    try {
      const response = await fetch(`http://127.0.0.1:5000/session/${sessionId}/tags/batch/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ assignments }),
      });

      if (!response.ok) throw new Error("Failed to assign tags");
      
      // Update local state
      const newTags = { ...imageTags };
      assignments.forEach(({ filename, tag }) => {
        if (filename && tag) {
          newTags[filename] = tag;
        }
      });
      setImageTags(newTags);
      onSessionUpdate(newTags);
      setMessage(`Assigned ${assignments.length} tags successfully`);
    } catch (err) {
      setMessage("Error assigning tags: " + err.message);
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6 bg-gray-900 text-white rounded-2xl shadow-lg">
      <h2 className="text-2xl font-bold mb-4">📤 Upload & Tag Images</h2>

      {/* File Upload Section */}
      <div className="mb-6">
        <input
          type="file"
          multiple
          accept="image/*"
          onChange={handleFileChange}
          className="block w-full mb-4 text-gray-300"
        />

        <div className="flex items-center gap-4">
          <button
            onClick={handleUpload}
            disabled={loading || files.length === 0}
            className="bg-blue-600 hover:bg-blue-700 px-4 py-2 rounded-md disabled:bg-gray-600"
          >
            {loading ? "Uploading..." : `Upload ${files.length} Image(s)`}
          </button>
          
          {files.length > 0 && (
            <div className="text-sm text-gray-300">
              📋 Will auto-tag as: {files.map((_, index) => `Image${uploadedFiles.length + index + 1}`).join(", ")}
            </div>
          )}
        </div>
        
        <div className="mt-2 text-xs text-gray-400">
          💡 Images will be automatically tagged as Image1, Image2, Image3, etc. based on upload order
        </div>
      </div>

      {/* Uploaded Images and Tag Management */}
      {uploadedFiles.length > 0 && (
        <div className="mt-6">
          <h3 className="text-lg font-semibold mb-4">
            📋 Manage Uploaded Images ({uploadedFiles.length})
          </h3>
          <TagManager
            files={uploadedFiles}
            tags={imageTags}
            onTagAssign={handleTagAssign}
            onBatchTagAssign={handleBatchTagAssign}
            sessionId={sessionId}
          />
        </div>
      )}

      {message && (
        <div className="mt-4 p-3 bg-blue-800 rounded-md text-sm">
          {message}
        </div>
      )}
    </div>
  );
}
