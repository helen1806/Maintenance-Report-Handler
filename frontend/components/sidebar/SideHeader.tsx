import { Wrench } from "lucide-react";

export default function SidebarHeader() {
  return (
    <div className="flex items-center gap-4">
      {/* Logo */}
      <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-indigo-100">
        <Wrench className="h-7 w-7 text-indigo-900" />
      </div>

      {/* Title */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900">
          GraphFix AI
        </h1>

        <p className="text-xl text-gray-500">
          Report Assistant for Complaints
        </p>
      </div>
    </div>
  );
}