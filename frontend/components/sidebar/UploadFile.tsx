"use client";

import { Upload, Loader2, CheckCircle2, XCircle } from "lucide-react";
import { useRef, useState } from "react";

export default function UploadFile() {
  const fileInputRef = useRef<HTMLInputElement>(null);
  
  const [isUploading, setIsUploading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [status, setStatus] = useState<"idle" | "success" | "error">("idle");
  const [message, setMessage] = useState("");

  const handleUploadClick = () => {
    if (fileInputRef.current) {
      fileInputRef.current.click();
    }
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files && e.target.files.length > 0) {
      uploadFiles(e.target.files);
    }
  };

  const uploadFiles = (files: FileList) => {
    setIsUploading(true);
    setStatus("idle");
    setMessage("");
    setProgress(0);

    const formData = new FormData();
    for (let i = 0; i < files.length; i++) {
      formData.append("files", files[i]);
    }

    const xhr = new XMLHttpRequest();
    const apiUrl = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
    xhr.open("POST", `${apiUrl}/upload`, true);

    xhr.upload.onprogress = (event) => {
      if (event.lengthComputable) {
        const percentComplete = Math.round((event.loaded / event.total) * 100);
        setProgress(percentComplete);
      }
    };

    xhr.onload = () => {
      setIsUploading(false);
      if (xhr.status >= 200 && xhr.status < 300) {
        setStatus("success");
        try {
          const response = JSON.parse(xhr.responseText);
          const { summary } = response;
          setMessage(`Success: ${summary.successful} | Failed: ${summary.failed} | Skipped: ${summary.skipped}`);
        } catch (e) {
          setMessage("Upload completed successfully!");
        }
      } else {
        setStatus("error");
        setMessage("Upload failed. Please try again.");
      }
      
      // Clear the file input so the same files can be selected again if needed
      if (fileInputRef.current) {
        fileInputRef.current.value = "";
      }
    };

    xhr.onerror = () => {
      setIsUploading(false);
      setStatus("error");
      setMessage("Network error occurred. Ensure backend is running.");
    };

    xhr.send(formData);
  };

  return (
    <div className="w-full flex flex-col gap-2">
      <input 
        type="file" 
        multiple 
        accept=".pdf" 
        ref={fileInputRef} 
        onChange={handleFileChange} 
        className="hidden" 
      />
      
      <button
        onClick={handleUploadClick}
        disabled={isUploading}
        className="
          flex
          w-full
          items-center
          justify-center
          gap-2
          rounded-xl
          bg-indigo-600
          px-4
          py-3
          font-medium
          text-white
          transition-colors
          hover:bg-indigo-700
          disabled:bg-indigo-400
          disabled:cursor-not-allowed
        "
      >
        {isUploading ? (
          <>
            <Loader2 size={20} className="animate-spin" />
            {progress < 100 ? `Uploading ${progress}%` : "Processing..."}
          </>
        ) : (
          <>
            <Upload size={20} />
            Upload files to get started
          </>
        )}
      </button>

      {status === "success" && (
        <div className="flex items-center gap-2 text-sm text-green-600 mt-1 px-2 font-medium">
          <CheckCircle2 size={16} />
          <span>{message}</span>
        </div>
      )}
      
      {status === "error" && (
        <div className="flex items-center gap-2 text-sm text-red-600 mt-1 px-2 font-medium">
          <XCircle size={16} />
          <span>{message}</span>
        </div>
      )}
    </div>
  );
}