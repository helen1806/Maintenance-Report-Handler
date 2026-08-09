import SidebarHeader from "./SideHeader";
import UploadFile from "./UploadFile";
import EmptyStateCard from "./EmptyState";
import Link from "next/link"; // We need Next.js Link for fast routing!

export default function SideBar() {
  return (
    // We added `flex flex-col h-full` so we can push the button to the bottom
    <aside className="w-80 border-r bg-white p-6 flex flex-col h-full">
      <SidebarHeader />

      <div className="mt-4">
        <UploadFile />
      </div>

      <div className="mt-6">
        <EmptyStateCard />
      </div>

      {/* Added Dashboard Button pushed to the bottom */}
      <div className="mt-auto pt-6 border-t border-gray-100">
        <Link
          href="/dashboard"
          className="flex items-center justify-center gap-2 w-full py-3 px-4 rounded-lg bg-indigo-600 text-white hover:bg-indigo-700 font-semibold transition-colors shadow-sm"
        >
          📊 View Analytics Dashboard
        </Link>
      </div>
    </aside>
  );
}
