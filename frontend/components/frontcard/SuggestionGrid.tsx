import SuggestionCard from "./SuggestionCard";

const suggestions = [
  "What caused the pump failure?",
  "Summarize the maintenance cases.",
  "Which asset has recurring issues?",
  "How can the bearing wear be resolved",
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