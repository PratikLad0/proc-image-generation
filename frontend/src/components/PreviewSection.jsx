import React, { useState } from "react";

function PreviewSection({ image, gif }) {
  const [downloading, setDownloading] = useState(false);

  const handleDownload = async (filePath, filename) => {
    setDownloading(true);
    try {
      const response = await fetch(`http://127.0.0.1:5000${filePath}`);
      if (response.ok) {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        console.error('Download failed');
      }
    } catch (error) {
      console.error('Download error:', error);
    } finally {
      setDownloading(false);
    }
  };

  const getImageUrl = (filePath) => {
    return `http://127.0.0.1:5000${filePath}`;
  };

  if (!image && !gif) {
    return (
      <div className="p-6 bg-white shadow rounded-xl text-center">
        <h2 className="font-semibold text-lg mb-4">🎨 Preview</h2>
        <div className="text-gray-500 py-8">
          <p>No generated content yet.</p>
          <p className="text-sm mt-2">Upload images, assign tags, and generate content to see preview here.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="p-6 bg-white shadow rounded-xl">
      <h2 className="font-semibold text-lg mb-4">🎨 Preview & Export</h2>
      
      <div className="space-y-6">
        {/* Static Image Preview */}
        {image && (
          <div className="text-center">
            <h3 className="text-md font-medium mb-3">Generated Image</h3>
            <div className="relative inline-block">
              <img
                src={getImageUrl(image)}
                alt="Generated"
                className="rounded-lg max-h-[400px] border shadow-lg"
                onError={(e) => {
                  e.target.src = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNDAwIiBoZWlnaHQ9IjQwMCIgdmlld0JveD0iMCAwIDQwMCA0MDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSI0MDAiIGhlaWdodD0iNDAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxwYXRoIGQ9Ik0xNzUgMTUwSDIyNVYyNTBIMTc1VjE1MFoiIHN0cm9rZT0iIzlDQTNBRiIgc3Ryb2tlLXdpZHRoPSIyIi8+CjxwYXRoIGQ9Ik0xNzUgMTUwTDIyNSAyMDBMMTc1IDI1MEwyMjUgMjAwTDE3NSAxNTAiIHN0cm9rZT0iIzlDQTNBRiIgc3Ryb2tlLXdpZHRoPSIyIi8+Cjx0ZXh0IHg9IjIwMCIgeT0iMzAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjOUNBM0FGIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTQiPkltYWdlIG5vdCBmb3VuZDwvdGV4dD4KPC9zdmc+Cg==";
                }}
              />
              <button
                onClick={() => handleDownload(image, `generated_image_${Date.now()}.png`)}
                disabled={downloading}
                className="absolute top-2 right-2 bg-blue-600 hover:bg-blue-700 text-white px-3 py-1 rounded text-sm disabled:bg-gray-400"
              >
                {downloading ? "..." : "📥"}
              </button>
            </div>
          </div>
        )}

        {/* Animated GIF Preview */}
        {gif && (
          <div className="text-center">
            <h3 className="text-md font-medium mb-3">Generated Animation</h3>
            <div className="relative inline-block">
              <img
                src={getImageUrl(gif)}
                alt="Generated GIF"
                className="rounded-lg max-h-[300px] border shadow-lg"
                onError={(e) => {
                  e.target.src = "data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzAwIiBoZWlnaHQ9IjMwMCIgdmlld0JveD0iMCAwIDMwMCAzMDAiIGZpbGw9Im5vbmUiIHhtbG5zPSJodHRwOi8vd3d3LnczLm9yZy8yMDAwL3N2ZyI+CjxyZWN0IHdpZHRoPSIzMDAiIGhlaWdodD0iMzAwIiBmaWxsPSIjRjNGNEY2Ii8+CjxjaXJjbGUgY3g9IjE1MCIgY3k9IjE1MCIgcj0iNTAiIHN0cm9rZT0iIzlDQTNBRiIgc3Ryb2tlLXdpZHRoPSIyIiBmaWxsPSJub25lIi8+Cjx0ZXh0IHg9IjE1MCIgeT0iMjAwIiB0ZXh0LWFuY2hvcj0ibWlkZGxlIiBmaWxsPSIjOUNBM0FGIiBmb250LWZhbWlseT0iQXJpYWwiIGZvbnQtc2l6ZT0iMTIiPkFuaW1hdGlvbiBub3QgZm91bmQ8L3RleHQ+Cjwvc3ZnPgo=";
                }}
              />
              <button
                onClick={() => handleDownload(gif, `generated_animation_${Date.now()}.gif`)}
                disabled={downloading}
                className="absolute top-2 right-2 bg-green-600 hover:bg-green-700 text-white px-3 py-1 rounded text-sm disabled:bg-gray-400"
              >
                {downloading ? "..." : "📥"}
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Export Options */}
      {(image || gif) && (
        <div className="mt-6 p-4 bg-gray-50 rounded-lg">
          <h3 className="text-sm font-medium mb-3">Export Options</h3>
          <div className="flex flex-wrap gap-2">
            {image && (
              <button
                onClick={() => handleDownload(image, `generated_image_${Date.now()}.png`)}
                disabled={downloading}
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded text-sm disabled:bg-gray-400"
              >
                📥 Download Image
              </button>
            )}
            {gif && (
              <button
                onClick={() => handleDownload(gif, `generated_animation_${Date.now()}.gif`)}
                disabled={downloading}
                className="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded text-sm disabled:bg-gray-400"
              >
                📥 Download GIF
              </button>
            )}
          </div>
        </div>
      )}
    </div>
  );
}

export default PreviewSection;
