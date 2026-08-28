import { Navigate, Route, Routes } from "react-router-dom";
import { useAuth } from "./auth/AuthContext";
import { AppShell } from "./components/AppShell";
import { DashboardPage, ProductsPage, QuotesPage, SuppliersPage } from "./pages/DataPages";
import { IntelligencePage } from "./pages/IntelligencePage";
import { LoginPage } from "./pages/LoginPage";
function Protected() { return useAuth().authenticated ? <AppShell /> : <Navigate to="/login" replace />; }
export default function App() { return <Routes><Route path="/login" element={<LoginPage />} /><Route element={<Protected />}><Route path="/" element={<DashboardPage />} /><Route path="/products" element={<ProductsPage />} /><Route path="/suppliers" element={<SuppliersPage />} /><Route path="/quotes" element={<QuotesPage />} /><Route path="/intelligence" element={<IntelligencePage />} /></Route><Route path="*" element={<Navigate to="/" replace />} /></Routes>; }
