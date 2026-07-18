import { Upload } from "lucide-react";

export default function UploadFile() {
  return (
    <button
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
      "
    >
      <Upload size={20} />
      Upload files to get started
    </button>
  );
}