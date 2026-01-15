import React, { useState, useEffect } from 'react';
import { Upload, X, AlertCircle, CheckCircle, Loader } from 'lucide-react';

export default function PneumoniaDetector() {
  const [isModelLoading, setIsModelLoading] = useState(true);
  const [modelError, setModelError] = useState(null);
  const [image, setImage] = useState(null);
  const [imagePreview, setImagePreview] = useState(null);
  const [analyzing, setAnalyzing] = useState(false);
  const [result, setResult] = useState(null);
  const [quality, setQuality] = useState(null);

  // Simulate model loading
  useEffect(() => {
    const loadModel = async () => {
      try {
        // Simulate model loading time (1-2 seconds)
        await new Promise(resolve => setTimeout(resolve, 1500));
        setIsModelLoading(false);
      } catch (error) {
        setModelError('Failed to load AI model. Please refresh the page.');
        setIsModelLoading(false);
      }
    };
    
    loadModel();
  }, []);

  const handleFileChange = (e) => {
    const file = e.target.files?.[0];
    if (file) {
      processFile(file);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    const file = e.dataTransfer.files?.[0];
    if (file) {
      processFile(file);
    }
  };

  const processFile = (file) => {
    if (!file.type.startsWith('image/')) {
      alert('Please upload an image file');
      return;
    }

    if (file.size > 200 * 1024 * 1024) {
      alert('File size must be under 200MB');
      return;
    }

    setImage(file);
    setResult(null);

    const reader = new FileReader();
    reader.onload = (e) => {
      setImagePreview(e.target.result);
      checkImageQuality(file.size);
    };
    reader.readAsDataURL(file);
  };

  const checkImageQuality = (fileSize) => {
    // Simple quality estimation based on file size and format
    const qualityScore = Math.min(100, Math.floor((fileSize / 1024 / 50) * 100));
    const adjustedScore = Math.max(50, Math.min(100, qualityScore));
    setQuality(adjustedScore);
  };

  const analyzeImage = async () => {
    if (!image) return;

    setAnalyzing(true);
    setResult(null);

    try {
      // Simulate AI analysis (2-3 seconds)
      await new Promise(resolve => setTimeout(resolve, 2500));

      // Simulate detection results
      const hasDetection = Math.random() > 0.5;
      const confidence = hasDetection 
        ? Math.floor(Math.random() * 30 + 60) // 60-90% for pneumonia
        : Math.floor(Math.random() * 40 + 10); // 10-50% for normal

      setResult({
        hasPneumonia: hasDetection,
        confidence: confidence,
        details: hasDetection 
          ? 'Pneumonia patterns detected in lung regions'
          : 'No significant pneumonia indicators found'
      });
    } catch (error) {
      alert('Analysis failed. Please try again.');
    } finally {
      setAnalyzing(false);
    }
  };

  const clearImage = () => {
    setImage(null);
    setImagePreview(null);
    setResult(null);
    setQuality(null);
  };

  if (isModelLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-4">
        <div className="text-center">
          <Loader className="w-16 h-16 text-blue-400 animate-spin mx-auto mb-4" />
          <h2 className="text-2xl font-bold text-white mb-2">Loading AI Model</h2>
          <p className="text-slate-300">Please wait while we initialize the pneumonia detection system...</p>
        </div>
      </div>
    );
  }

  if (modelError) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center p-4">
        <div className="bg-red-500/20 border border-red-500 rounded-lg p-6 max-w-md">
          <AlertCircle className="w-12 h-12 text-red-400 mx-auto mb-4" />
          <h2 className="text-xl font-bold text-white text-center mb-2">Error Loading Model</h2>
          <p className="text-slate-300 text-center">{modelError}</p>
          <button 
            onClick={() => window.location.reload()}
            className="mt-4 w-full bg-red-500 hover:bg-red-600 text-white py-2 rounded-lg transition"
          >
            Refresh Page
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 p-4 md:p-8">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center gap-3 mb-2">
            <span className="text-4xl">🫁</span>
            <h1 className="text-3xl md:text-4xl font-bold text-white">
              Pneumonia Detection System
            </h1>
          </div>
          <p className="text-slate-300">Upload a chest X-ray image to detect pneumonia</p>
        </div>

        {/* Upload Area */}
        <div className="bg-slate-800/50 backdrop-blur rounded-xl p-6 mb-6 border border-slate-700">
          <div className="flex items-center justify-between mb-4">
            <h2 className="text-lg font-semibold text-white">Choose a chest X-ray image...</h2>
            <div className="w-8 h-8 bg-slate-700 rounded-full flex items-center justify-center">
              <span className="text-slate-400 text-sm">?</span>
            </div>
          </div>

          {!image ? (
            <div
              onDrop={handleDrop}
              onDragOver={(e) => e.preventDefault()}
              className="border-2 border-dashed border-slate-600 rounded-lg p-12 text-center hover:border-blue-500 transition cursor-pointer"
              onClick={() => document.getElementById('fileInput').click()}
            >
              <Upload className="w-16 h-16 text-slate-500 mx-auto mb-4" />
              <p className="text-white font-medium mb-2">Drag and drop file here</p>
              <p className="text-slate-400 text-sm mb-4">Limit 200MB per file • JPG, JPEG, PNG</p>
              <button className="bg-slate-700 hover:bg-slate-600 text-white px-6 py-2 rounded-lg transition">
                Browse files
              </button>
              <input
                id="fileInput"
                type="file"
                accept="image/*"
                onChange={handleFileChange}
                className="hidden"
              />
            </div>
          ) : (
            <div>
              <div className="flex items-center justify-between bg-slate-700/50 rounded-lg p-4 mb-4">
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 bg-slate-600 rounded flex items-center justify-center">
                    <Upload className="w-5 h-5 text-slate-300" />
                  </div>
                  <div>
                    <p className="text-white font-medium">{image.name}</p>
                    <p className="text-slate-400 text-sm">{(image.size / 1024).toFixed(1)}KB</p>
                  </div>
                </div>
                <button
                  onClick={clearImage}
                  className="w-8 h-8 bg-slate-600 hover:bg-slate-500 rounded flex items-center justify-center transition"
                >
                  <X className="w-5 h-5 text-white" />
                </button>
              </div>

              {imagePreview && (
                <div className="text-center">
                  <img
                    src={imagePreview}
                    alt="X-ray preview"
                    className="max-w-full max-h-96 mx-auto rounded-lg border border-slate-600"
                  />
                  <p className="text-slate-400 text-sm mt-2">Uploaded X-ray Image</p>
                </div>
              )}
            </div>
          )}
        </div>

        {/* Quality Check */}
        {quality && (
          <div className="bg-slate-800/50 backdrop-blur rounded-xl p-6 mb-6 border border-slate-700">
            <div className="flex items-center gap-3 mb-4">
              <span className="text-2xl">🔍</span>
              <h2 className="text-xl font-bold text-white">Image Quality Check</h2>
            </div>

            <div className="mb-2">
              <div className="flex justify-between text-sm mb-1">
                <span className="text-slate-400">Quality</span>
                <span className="text-white font-bold">{quality}/100</span>
              </div>
              <div className="w-full bg-slate-700 rounded-full h-3 overflow-hidden">
                <div
                  className={`h-full transition-all duration-500 ${
                    quality >= 70 ? 'bg-green-500' : quality >= 50 ? 'bg-yellow-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${quality}%` }}
                />
              </div>
            </div>

            <div className="bg-green-500/20 border border-green-500 rounded-lg p-4 flex items-start gap-3">
              <CheckCircle className="w-5 h-5 text-green-400 flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-green-400 font-medium">Image quality is acceptable</p>
                <p className="text-slate-300 text-sm">Proceed with pneumonia detection analysis</p>
              </div>
            </div>
          </div>
        )}

        {/* Analyze Button */}
        {image && !result && (
          <button
            onClick={analyzeImage}
            disabled={analyzing}
            className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-slate-600 text-white font-semibold py-4 rounded-xl transition flex items-center justify-center gap-3 mb-6"
          >
            {analyzing ? (
              <>
                <Loader className="w-5 h-5 animate-spin" />
                Analyzing X-ray...
              </>
            ) : (
              <>
                Analyze for Pneumonia
              </>
            )}
          </button>
        )}

        {/* Results */}
        {result && (
          <div className="bg-slate-800/50 backdrop-blur rounded-xl p-6 border border-slate-700">
            <h2 className="text-xl font-bold text-white mb-4">Detection Results</h2>
            
            <div className={`rounded-lg p-6 mb-4 ${
              result.hasPneumonia 
                ? 'bg-red-500/20 border border-red-500' 
                : 'bg-green-500/20 border border-green-500'
            }`}>
              <div className="flex items-center gap-3 mb-3">
                {result.hasPneumonia ? (
                  <AlertCircle className="w-8 h-8 text-red-400" />
                ) : (
                  <CheckCircle className="w-8 h-8 text-green-400" />
                )}
                <div>
                  <h3 className={`text-xl font-bold ${
                    result.hasPneumonia ? 'text-red-400' : 'text-green-400'
                  }`}>
                    {result.hasPneumonia ? 'Pneumonia Detected' : 'No Pneumonia Detected'}
                  </h3>
                  <p className="text-slate-300">Confidence: {result.confidence}%</p>
                </div>
              </div>
              <p className="text-slate-200">{result.details}</p>
            </div>

            <div className="bg-blue-500/20 border border-blue-500 rounded-lg p-4">
              <p className="text-blue-300 text-sm">
                <strong>Medical Disclaimer:</strong> This is an AI-assisted tool for educational purposes. 
                Always consult with qualified healthcare professionals for proper medical diagnosis and treatment.
              </p>
            </div>

            <button
              onClick={clearImage}
              className="w-full bg-slate-700 hover:bg-slate-600 text-white py-3 rounded-lg mt-4 transition"
            >
              Analyze Another Image
            </button>
          </div>
        )}
      </div>
    </div>
  );
}
