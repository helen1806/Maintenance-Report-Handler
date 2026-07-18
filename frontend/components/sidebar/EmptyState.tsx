import { FileText } from "lucide-react";

export default function EmptyStateCard() {
  return (
    <div className="flex flex-col items-center justify-center rounded-xl border border-dashed border-gray-300 bg-white p-8 text-center">
      <FileText className="mb-4 h-10 w-10 text-gray-500" />

      <p className="text-lg text-gray-600"> 
        No reports yet. Upload PDFs to start asking questions.
      </p>
    </div>
  );
}