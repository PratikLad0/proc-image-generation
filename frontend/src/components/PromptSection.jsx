import React, { useState, useEffect, useRef } from "react";

function PromptSection({ sessionId, sessionImages, onResult }) {
  const [prompt, setPrompt] = useState("");
  const [generateGif, setGenerateGif] = useState(false);
  const [loading, setLoading] = useState(false);
  const [message, setMessage] = useState("");
  const [availableTags, setAvailableTags] = useState([]);
  const [lastPrompt, setLastPrompt] = useState("");
  const [refinementMode, setRefinementMode] = useState(false);
  const [feedback, setFeedback] = useState("");
  
  // Voice-to-text states
  const [isRecording, setIsRecording] = useState(false);
  const [isSupported, setIsSupported] = useState(false);
  const [voiceMessage, setVoiceMessage] = useState("");
  const recognitionRef = useRef(null);

  // Update available tags when session images change
  useEffect(() => {
    const tags = Object.values(sessionImages).filter(tag => tag && tag.trim());
    setAvailableTags(tags);
  }, [sessionImages]);

  // Initialize voice recognition
  useEffect(() => {
    if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
      const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
      recognitionRef.current = new SpeechRecognition();
      
      recognitionRef.current.continuous = false;
      recognitionRef.current.interimResults = false;
      recognitionRef.current.lang = 'en-US';
      
      recognitionRef.current.onresult = (event) => {
        const transcript = event.results[0][0].transcript;
        setVoiceMessage(transcript);
        setPrompt(prev => prev + (prev ? ' ' : '') + transcript);
      };
      
      recognitionRef.current.onerror = (event) => {
        setVoiceMessage(`Voice recognition error: ${event.error}`);
        setIsRecording(false);
      };
      
      recognitionRef.current.onend = () => {
        setIsRecording(false);
      };
      
      setIsSupported(true);
    }
    
    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.stop();
      }
    };
  }, []);

  const handleGenerate = async () => {
    if (!prompt.trim()) {
      setMessage("Please enter a prompt");
      return;
    }

    // Check if prompt contains @tags
    const tagMatches = prompt.match(/@(\w+)/g);
    if (!tagMatches) {
      setMessage("Please use @tag syntax to reference your images (e.g., @BG, @logo)");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(`http://127.0.0.1:5000/session/${sessionId}/generate/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          prompt: prompt.trim(),
          generate_gif: generateGif,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Generation failed");
      }

      const result = await response.json();
      setMessage(result.message);
      setLastPrompt(prompt.trim());
      
      // Pass the result to parent component
      onResult(result.image_path, result.gif_path);
    } catch (error) {
      setMessage("Error: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const handleRefine = async () => {
    if (!feedback.trim()) {
      setMessage("Please enter feedback for refinement");
      return;
    }

    if (!lastPrompt) {
      setMessage("No previous prompt to refine. Generate an image first.");
      return;
    }

    setLoading(true);
    setMessage("");

    try {
      const response = await fetch(`http://127.0.0.1:5000/session/${sessionId}/refine/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          original_prompt: lastPrompt,
          feedback: feedback.trim(),
          generate_gif: generateGif,
        }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || "Refinement failed");
      }

      const result = await response.json();
      setMessage(result.message);
      setLastPrompt(result.refined_prompt);
      setFeedback("");
      setRefinementMode(false);
      
      // Pass the result to parent component
      onResult(result.image_path, result.gif_path);
    } catch (error) {
      setMessage("Error: " + error.message);
    } finally {
      setLoading(false);
    }
  };

  const startVoiceRecording = () => {
    if (recognitionRef.current && !isRecording) {
      setVoiceMessage("Listening...");
      setIsRecording(true);
      recognitionRef.current.start();
    }
  };

  const stopVoiceRecording = () => {
    if (recognitionRef.current && isRecording) {
      recognitionRef.current.stop();
      setIsRecording(false);
    }
  };

  const insertTag = (tag) => {
    const cursorPos = document.getElementById("prompt-textarea").selectionStart;
    const textBefore = prompt.substring(0, cursorPos);
    const textAfter = prompt.substring(cursorPos);
    const newPrompt = textBefore + `@${tag} ` + textAfter;
    setPrompt(newPrompt);
  };

  const getPromptExamples = () => {
    if (availableTags.length === 0) return [];
    
    const examples = [
      `Set @${availableTags[0]} as background and @${availableTags[1] || availableTags[0]} as front image`,
      `@${availableTags[0]} is stable background and @${availableTags[1] || availableTags[0]} is moving from left to right`,
      `Place @${availableTags[0]} in center and @${availableTags[1] || availableTags[0]} on the right`,
    ];
    
    return examples.filter(example => {
      const tagsInExample = example.match(/@(\w+)/g);
      return tagsInExample && tagsInExample.every(tag => availableTags.includes(tag.replace('@', '')));
    });
  };

  return (
    <div className="p-6 bg-white shadow rounded-xl">
      <h2 className="font-semibold text-lg mb-4">🧠 Generate with Tags</h2>
      
      {/* Available Tags */}
      {availableTags.length > 0 && (
        <div className="mb-4">
          <h3 className="text-sm font-medium mb-2">Available Tags:</h3>
          <div className="flex flex-wrap gap-2">
            {availableTags.map((tag) => (
              <button
                key={tag}
                onClick={() => insertTag(tag)}
                className="bg-blue-100 hover:bg-blue-200 text-blue-800 px-2 py-1 rounded text-sm"
              >
                @{tag}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Prompt Input */}
      <div className="mb-4">
        <label className="block text-sm font-medium mb-2">
          Prompt (use @tag syntax to reference images):
        </label>
        <div className="relative">
          <textarea
            id="prompt-textarea"
            placeholder="Example: Set @BG as background and @logo as front image"
            className="w-full border rounded p-3 h-24 resize-none pr-12"
            value={prompt}
            onChange={(e) => setPrompt(e.target.value)}
          />
          {isSupported && (
            <div className="absolute right-2 top-2 flex flex-col gap-1">
              {!isRecording ? (
                <button
                  onClick={startVoiceRecording}
                  className="bg-blue-500 hover:bg-blue-600 text-white p-2 rounded-full text-sm"
                  title="Start voice recording"
                >
                  🎤
                </button>
              ) : (
                <button
                  onClick={stopVoiceRecording}
                  className="bg-red-500 hover:bg-red-600 text-white p-2 rounded-full text-sm animate-pulse"
                  title="Stop voice recording"
                >
                  ⏹️
                </button>
              )}
            </div>
          )}
        </div>
        {voiceMessage && (
          <div className="mt-2 text-xs text-blue-600">
            Voice: {voiceMessage}
          </div>
        )}
        {!isSupported && (
          <div className="mt-2 text-xs text-gray-500">
            Voice recognition not supported in this browser
          </div>
        )}
      </div>

      {/* Example Prompts */}
      {availableTags.length > 0 && (
        <div className="mb-4">
          <h3 className="text-sm font-medium mb-2">Example Prompts:</h3>
          <div className="space-y-1">
            {getPromptExamples().slice(0, 2).map((example, index) => (
              <button
                key={index}
                onClick={() => setPrompt(example)}
                className="block w-full text-left text-xs text-gray-600 hover:text-gray-800 p-2 bg-gray-50 rounded"
              >
                {example}
              </button>
            ))}
          </div>
        </div>
      )}

      {/* Controls */}
      <div className="flex items-center gap-4 mb-4">
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={generateGif}
            onChange={(e) => setGenerateGif(e.target.checked)}
          />
          Generate Animated GIF
        </label>
        <button
          className="bg-green-600 hover:bg-green-700 text-white px-6 py-2 rounded disabled:bg-gray-400"
          onClick={handleGenerate}
          disabled={loading || !prompt.trim()}
        >
          {loading ? "Generating..." : generateGif ? "Generate GIF" : "Generate Image"}
        </button>
        {lastPrompt && (
          <button
            onClick={() => setRefinementMode(!refinementMode)}
            className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded text-sm"
          >
            {refinementMode ? "Cancel Refine" : "Refine Image"}
          </button>
        )}
      </div>

      {/* Refinement Section */}
      {refinementMode && (
        <div className="mb-4 p-4 bg-purple-50 rounded-lg border border-purple-200">
          <h3 className="text-sm font-medium mb-2">🔄 Refine with AI Feedback</h3>
          <p className="text-xs text-gray-600 mb-2">
            Last prompt: <span className="font-mono bg-gray-100 px-1 rounded">{lastPrompt}</span>
          </p>
          <textarea
            placeholder="Describe what you'd like to change or improve..."
            className="w-full border rounded p-2 h-16 resize-none text-sm"
            value={feedback}
            onChange={(e) => setFeedback(e.target.value)}
          />
          <div className="flex gap-2 mt-2">
            <button
              onClick={handleRefine}
              disabled={loading || !feedback.trim()}
              className="bg-purple-600 hover:bg-purple-700 text-white px-4 py-2 rounded text-sm disabled:bg-gray-400"
            >
              {loading ? "Refining..." : "Refine with AI"}
            </button>
            <button
              onClick={() => {
                setRefinementMode(false);
                setFeedback("");
              }}
              className="bg-gray-500 hover:bg-gray-600 text-white px-4 py-2 rounded text-sm"
            >
              Cancel
            </button>
          </div>
        </div>
      )}

      {/* Message Display */}
      {message && (
        <div className={`p-3 rounded text-sm ${
          message.includes("Error") || message.includes("failed") 
            ? "bg-red-100 text-red-800" 
            : "bg-green-100 text-green-800"
        }`}>
          {message}
        </div>
      )}

      {/* Help Text */}
      <div className="mt-4 text-xs text-gray-500">
        <p><strong>AI-Powered Generation Tips:</strong></p>
        <ul className="list-disc list-inside space-y-1">
          <li>Use @tag syntax to reference your uploaded images</li>
          <li>Click 🎤 to record voice prompts (browser must support speech recognition)</li>
          <li>AI will understand your intent and generate detailed prompts</li>
          <li>For static images: "Set @BG as background and @logo as front"</li>
          <li>For animations: "@BG is stable and @logo is moving from left to right"</li>
          <li>Custom dimensions: "1920x1080", "landscape", "instagram", "youtube"</li>
          <li>After generation, use "Refine Image" to improve with AI feedback</li>
          <li>Supported movements: left to right, right to left, top to bottom, bottom to top, rotate, bounce</li>
        </ul>
      </div>
    </div>
  );
}

export default PromptSection;
