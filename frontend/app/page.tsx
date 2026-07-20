import SideBar from "@/components/sidebar/SideBar";
import ChatInterface from "@/components/chatbar/ChatInterface";

export default function Home() {
  return (
    <main className="flex h-screen">
      <SideBar />

      <div className="flex flex-1 flex-col bg-gray-50 overflow-hidden">
        <ChatInterface />
      </div>
    </main>
  );
}