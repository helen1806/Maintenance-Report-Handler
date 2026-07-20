"use client";

import { useState } from "react";
import { Message } from "@/types/chat";
import InputText from "./Input";
import MessageList from "./MessageList";
import SuggestionGrid from "../frontcard/SuggestionGrid";

export default function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async (text: string) => {
    // 1. Add the user's message to the chat
    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: text,
      createdAt: new Date(),
    };
    
    setMessages((prev) => [...prev, userMessage]);
    setIsLoading(true);

    try {
      // 2. Extract recent history (last 6 messages max)
      const history = messages.slice(-6).map((msg) => ({
        role: msg.role,
        content: msg.content,
      }));

      // 3. Send the question and history to the backend
      const response = await fetch("http://localhost:8000/ask", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ question: text, history }),
      });

      const data = await response.json();

      let assistantContent = "";

      // 3. Handle success and our custom structured error responses
      if (response.ok && data.answer) {
        assistantContent = data.answer;
      } else {
        assistantContent = `Error: ${data.message || "Failed to get an answer."}\n${
          data.details ? `Details: ${data.details}` : ""
        }`;
      }

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: assistantContent.trim(),
        createdAt: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      // Handle network crashes or CORS issues
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: "Network error: Unable to reach the backend server. Please ensure the FastAPI server is running.",
        createdAt: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="flex h-full flex-col">
      {messages.length === 0 ? (
        // Empty state: show suggestions in the middle of the screen
        <div className="flex-1 flex flex-col justify-center max-w-4xl mx-auto w-full px-4">
          <SuggestionGrid onSuggestionClick={handleSend} />
        </div>
      ) : (
        // Active chat state
        <MessageList messages={messages} isLoading={isLoading} />
      )}

      {/* Fixed input bar at the bottom */}
      <div className="w-full max-w-4xl mx-auto p-4 mt-auto">
        <InputText onSend={handleSend} disabled={isLoading} />
      </div>
    </div>
  );
}
