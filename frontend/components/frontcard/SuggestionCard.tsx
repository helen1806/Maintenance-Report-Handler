import { SendHorizontal } from "lucide-react";

interface SuggestionCardProps {
  text: string;
  onClick: () => void;
}

export default function SuggestionCard({
  text,
  onClick,
}: SuggestionCardProps) {
  return (
    <button 
      onClick={onClick}
      className="flex w-full items-center justify-between rounded-2xl border border-gray-200 bg-white px-6 py-5 text-left shadow-sm transition hover:bg-gray-50"
    >
      <span className="text-lg text-gray-900">
        {text}
      </span>

      <SendHorizontal
        size={22}
        className="text-gray-500"
      />
    </button>
  );
}