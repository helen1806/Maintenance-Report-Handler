"use client";

import { Send } from "lucide-react";
import { useState } from "react";

interface InputTextProps {
  onSend: (text: string) => void;
  disabled?: boolean;
}

export default function InputText({ onSend, disabled = false }: InputTextProps) {
  const [text, setText] = useState("");

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (text.trim() && !disabled) {
      onSend(text.trim());
      setText("");
    }
  };

  return (
    <form className="w-full" onSubmit={handleSubmit}>
      <div className="flex items-center gap-3 rounded-full border border-gray-300 bg-white px-5 py-3 shadow-sm">
        <input
          type="text"
          value={text}
          onChange={(e) => setText(e.target.value)}
          disabled={disabled}
          placeholder="Ask about your maintenance reports..."
          className="flex-1 bg-transparent placeholder:italic placeholder:text-gray-500 focus:outline-none disabled:opacity-50"
        />

        <button
          type="submit"
          disabled={!text.trim() || disabled}
          className="flex h-10 w-10 items-center justify-center rounded-full bg-gray-100 hover:bg-gray-200 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          <Send size={18} className="text-gray-700" />
        </button>
      </div>
    </form>
  );
}