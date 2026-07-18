import SidebarHeader from "./SideHeader";
import UploadFile from "./UploadFile";
import EmptyStateCard from "./EmptyState";

export default function SideBar(){
  return (
    <aside className="w-80 border-r bg-white p-6">
      <SidebarHeader />
       

      <div className="mt-4">
        <UploadFile />
      </div>

      <div className="mt-6">
        <EmptyStateCard />
      </div>
    </aside>
  );
}
