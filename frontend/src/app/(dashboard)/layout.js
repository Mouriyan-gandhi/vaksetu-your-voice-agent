import Navbar from "@/components/Navbar";

export default function DashboardLayout({ children }) {
  return (
    <>
      <Navbar />
      <div className="pt-16 noise-bg min-h-screen">
        {children}
      </div>
    </>
  );
}
