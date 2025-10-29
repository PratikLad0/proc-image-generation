import React, { useState, useEffect } from "react";
import UploadSection from "./components/UploadSections";
import PromptSection from "./components/PromptSection";
import PreviewSection from "./components/PreviewSection";

function App() {
  const [sessionId, setSessionId] = useState(null);
  const [, setUploadedFiles] = useState([]);
  const [sessionImages, setSessionImages] = useState({});
  const [outputImage, setOutputImage] = useState(null);
  const [outputGif, setOutputGif] = useState(null);
  const [loading, setLoading] = useState(false);

  // Create session on component mount
  useEffect(() => {
    createSession();
  }, []);

  const createSession = async () => {
    try {
      setLoading(true);
      const response = await fetch("http://127.0.0.1:5000/session/create/", {
        method: "POST",
      });
      
      if (response.ok) {
        const data = await response.json();
        setSessionId(data.session_id);
        console.log("Session created:", data.session_id);
      } else {
        console.error("Failed to create session");
      }
    } catch (error) {
      console.error("Error creating session:", error);
    } finally {
      setLoading(false);
    }
  };

  const handleUpload = (files) => {
    setUploadedFiles(files);
  };

  const handleSessionUpdate = (images) => {
    setSessionImages(images);
  };

  const handleResult = (img, gif) => {
    setOutputImage(img);
    setOutputGif(gif);
  };

  const handleRefresh = () => {
    // Clean up current session and create new one
    if (sessionId) {
      fetch(`http://127.0.0.1:5000/session/${sessionId}/`, {
        method: "DELETE",
      }).then(() => {
        setSessionId(null);
        setUploadedFiles([]);
        setSessionImages({});
        setOutputImage(null);
        setOutputGif(null);
        createSession();
      });
    }
  };

  if (loading && !sessionId) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl">Creating session...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen flex flex-col items-center p-6 space-y-8">
      <div className="flex items-center justify-between w-full max-w-3xl">
        <h1 className="text-3xl font-bold text-blue-700">🧠 Session-Based Image Generator</h1>
        <div className="flex items-center space-x-4">
          <span className="text-sm text-gray-600">
            Session: {sessionId ? sessionId.substring(0, 8) + "..." : "None"}
          </span>
          <button
            onClick={handleRefresh}
            className="bg-red-500 hover:bg-red-600 text-white px-3 py-1 rounded text-sm"
          >
            New Session
          </button>
        </div>
      </div>
      
      <div className="w-full max-w-3xl space-y-6">
        {sessionId && (
          <>
            <UploadSection 
              sessionId={sessionId}
              onUpload={handleUpload} 
              onSessionUpdate={handleSessionUpdate}
            />
            <PromptSection 
              sessionId={sessionId}
              sessionImages={sessionImages} 
              onResult={handleResult} 
            />
            <PreviewSection 
              image={outputImage} 
              gif={outputGif}
              sessionId={sessionId}
            />
          </>
        )}
      </div>
    </div>
  );
}

export default App;
