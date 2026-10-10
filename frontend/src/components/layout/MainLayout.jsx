import { Suspense } from "react";
import { Outlet } from "react-router-dom";
import Navbar from "./Navbar";
import Footer from "./Footer";
import Loading from "../common/Loading";

export default function MainLayout() {
  return (
    <div className="flex min-h-screen flex-col bg-[#090a0f] text-neutral-100">
      <Navbar />
      <main className="flex-1">
        <Suspense fallback={<Loading message="Loading view..." />}>
          <Outlet />
        </Suspense>
      </main>
      <Footer />
    </div>
  );
}
