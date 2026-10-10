import { lazy } from "react";
import { BrowserRouter, Routes, Route } from "react-router-dom";
import MainLayout from "./components/layout/MainLayout";

// Route-level lazy loading
const HomePage = lazy(() => import("./pages/HomePage"));
const CreatorDirectoryPage = lazy(() => import("./pages/CreatorDirectoryPage"));
const GangDirectoryPage = lazy(() => import("./pages/GangDirectoryPage"));
const PersonProfilePage = lazy(() => import("./pages/PersonProfilePage"));
const NotFoundPage = lazy(() => import("./pages/NotFoundPage"));

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<MainLayout />}>
          <Route index element={<HomePage />} />
          <Route path="creators" element={<CreatorDirectoryPage />} />
          <Route path="gangs" element={<GangDirectoryPage />} />
          <Route path="person/:slug" element={<PersonProfilePage />} />
          <Route path="*" element={<NotFoundPage />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
