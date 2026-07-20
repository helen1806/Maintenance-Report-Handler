import { Message as MessageType } from "@/types/chat";
import { User, Bot } from "lucide-react";

interface MessageProps {
  message: MessageType;
}

export default function Message({ message }: MessageProps) {
  const isUser = message.role === "user";

  return (
    <div className={`flex w-full ${isUser ? "justify-end" : "justify-start"} mb-6`}>
      <div className={`flex max-w-[80%] gap-4 ${isUser ? "flex-row-reverse" : "flex-row"}`}>
        {/* Avatar */}
        <div
          className={`flex h-10 w-10 flex-shrink-0 items-center justify-center rounded-full ${
            isUser ? "bg-indigo-600 text-white" : "bg-emerald-500 text-white"
          }`}
        >
          {isUser ? <User size={20} /> : <Bot size={20} />}
        </div>

        {/* Message Bubble */}
        <div
          className={`flex flex-col ${isUser ? "items-end" : "items-start"}`}
        >
          <div
            className={`rounded-2xl px-5 py-3 shadow-sm ${
              isUser
                ? "bg-indigo-600 text-white rounded-tr-none"
                : "bg-white border border-gray-200 text-gray-800 rounded-tl-none"
            }`}
          >
            <p className="whitespace-pre-wrap leading-relaxed">{message.content}</p>
          </div>
          <span className="text-xs text-gray-400 mt-1 px-1">
            {message.createdAt.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
          </span>
        </div>
      </div>
    </div>
  );
}
