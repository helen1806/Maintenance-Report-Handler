import SuggestionCard from "./SuggestionCard";

const suggestions = [
  "What caused the pump failure?",
  "Summarize this report.",
  "Which asset has recurring issues?",
  "Draft a work order for the highest-priority item.",
];

interface SuggestionGridProps {
  onSuggestionClick: (text: string) => void;
}

export default function SuggestionGrid({ onSuggestionClick }: SuggestionGridProps) {
  return (
    <div className="grid grid-cols-2 gap-4">
      {suggestions.map((item) => (
        <SuggestionCard
          key={item}
          text={item}
          onClick={() => onSuggestionClick(item)}
        />
      ))}
    </div>
  );
}