import React, { useState } from "react";

export default function TagManager({ files, tags, onTagAssign, onBatchTagAssign, sessionId }) {
  const [editingTags, setEditingTags] = useState({});
  const [batchMode, setBatchMode] = useState(false);
  const [batchTags, setBatchTags] = useState({});

  const handleTagChange = (filename, value) => {
    setEditingTags(prev => ({ ...prev, [filename]: value }));
  };

  const handleTagSubmit = (filename) => {
    const tag = editingTags[filename];
    if (tag && tag.trim()) {
      onTagAssign(filename, tag.trim());
      setEditingTags(prev => {
        const newTags = { ...prev };
        delete newTags[filename];
        return newTags;
      });
    }
  };

  const handleBatchTagChange = (filename, value) => {
    setBatchTags(prev => ({ ...prev, [filename]: value }));
  };

  const handleBatchSubmit = () => {
    const assignments = Object.entries(batchTags)
      .filter(([, tag]) => tag && tag.trim())
      .map(([filename, tag]) => ({ filename, tag: tag.trim() }));
    
    if (assignments.length > 0) {
      onBatchTagAssign(assignments);
      setBatchTags({});
      setBatchMode(false);
    }
  };

  const getImageUrl = (filename) => {
    return `http://127.0.0.1:5000/session/${sessionId}/uploads/${filename}`;
  };

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h3 className="font-semibold text-lg">🏷️ Assign Tags to Images</h3>
        <button
          onClick={() => setBatchMode(!batchMode)}
          className="bg-purple-600 hover:bg-purple-700 px-3 py-1 rounded text-sm"
        >
          {batchMode ? "Exit Batch Mode" : "Batch Mode"}
        </button>
      </div>

      {batchMode && (
        <div className="bg-purple-900 p-3 rounded-md mb-4">
          <p className="text-sm mb-2">Batch Mode: Assign tags to multiple images at once</p>
          <button
            onClick={handleBatchSubmit}
            disabled={Object.keys(batchTags).length === 0}
            className="bg-purple-600 hover:bg-purple-700 px-3 py-1 rounded text-sm disabled:bg-gray-600"
          >
            Apply Batch Tags
          </button>
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {files.map((filename) => (
          <div key={filename} className="flex items-center gap-3 p-3 bg-gray-800 rounded-lg">
            <img
              src={getImageUrl(filename)}
              alt={filename}
              className="w-20 h-20 object-cover rounded border"
              onError={(e) => {
                e.target.src = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iODAiIGhlaWdodD0iODAiIHZpZXdCb3g9IjAgMCA4MCA4MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHJlY3Qgd2lkdGg9IjgwIiBoZWlnaHQ9IjgwIiBmaWxsPSIjMzc0MTUxIi8+CjxwYXRoIGQ9Ik0yMCAyMEg2MFY2MEgyMFYyMFoiIHN0cm9rZT0iIzlDQTNBRiIgc3Ryb2tlLXdpZHRoPSIyIi8+CjxwYXRoIGQ9Ik0zMCAzMEw1MCA1MEw0MCA0MEwzMCAzMFoiIHN0cm9rZT0iIzlDQTNBRiIgc3Ryb2tlLXdpZHRoPSIyIi8+Cjwvc3ZnPgo=";
              }}
            />
            <div className="flex-1">
              <p className="text-xs text-gray-400 mb-1 truncate">{filename}</p>
              {tags[filename] && (
                <div className="mb-2">
                  <span className="bg-green-600 text-xs px-2 py-1 rounded">
                    Tagged: {tags[filename]}
                  </span>
                </div>
              )}
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="Enter tag (e.g., BG, logo)"
                  value={batchMode ? (batchTags[filename] || "") : (editingTags[filename] || "")}
                  onChange={(e) => 
                    batchMode 
                      ? handleBatchTagChange(filename, e.target.value)
                      : handleTagChange(filename, e.target.value)
                  }
                  className="border border-gray-600 bg-gray-700 text-white p-1 rounded text-sm flex-1"
                />
                {!batchMode && (
                  <button
                    onClick={() => handleTagSubmit(filename)}
                    disabled={!editingTags[filename]?.trim()}
                    className="bg-green-600 hover:bg-green-700 px-2 py-1 rounded text-xs disabled:bg-gray-600"
                  >
                    Set
                  </button>
                )}
              </div>
            </div>
          </div>
        ))}
      </div>

      {files.length === 0 && (
        <p className="text-gray-400 text-center py-4">No images uploaded yet</p>
      )}
    </div>
  );
}
