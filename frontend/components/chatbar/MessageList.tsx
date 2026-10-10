"use client";

import { useEffect, useRef, useState } from "react";
import { Message as MessageType } from "@/types/chat";
import Message from "./Message";
import { Loader2 } from "lucide-react";

interface MessageListProps {
  messages: MessageType[];
  isLoading: boolean;
}

export default function MessageList({ messages, isLoading }: MessageListProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const [loadingText, setLoadingText] = useState("Thinking...");

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, isLoading, loadingText]);

  useEffect(() => {
    let timeout: NodeJS.Timeout;
    if (isLoading) {
      setLoadingText("Thinking...");
      timeout = setTimeout(() => {
        setLoadingText("Waking up the server... (This first request can take up to 3 minutes, please hold on!)");
      }, 5000);
    }
    return () => clearTimeout(timeout);
  }, [isLoading]);

  return (
    <div className="flex-1 overflow-y-auto px-4 py-6 scroll-smooth">
      <div className="mx-auto max-w-4xl">
        {messages.map((msg) => (
          <Message key={msg.id} message={msg} />
        ))}
        
        {isLoading && (
          <div className="flex w-full justify-start mb-6">
            <div className="flex max-w-[80%] gap-4 flex-row">
              <div className="flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full bg-emerald-500 text-white">
                <Loader2 size={20} className="animate-spin" />
              </div>
              <div className="flex flex-col items-start justify-center">
                <div className="rounded-2xl px-5 py-3 shadow-sm bg-white border border-gray-200 text-gray-500 italic rounded-tl-none">
                  {loadingText}
                </div>
              </div>
            </div>
          </div>
        )}
        
        <div ref={bottomRef} />
      </div>
    </div>
  );
}
