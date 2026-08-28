import { NavLink, Outlet, useNavigate } from "react-router-dom";
import { useAuth } from "../auth/AuthContext";

const links = [["/", "Dashboard"], ["/products", "Products"], ["/suppliers", "Suppliers"], ["/quotes", "Quotes"], ["/intelligence", "Procurement Intelligence"]];
export function AppShell() {
  const { logout } = useAuth(); const navigate = useNavigate();
  const signOut = () => { logout(); navigate("/login"); };
  return <div className="shell"><aside><div className="brand">SPI <span>Procurement</span></div><nav>{links.map(([to, label]) => <NavLink key={to} to={to} end={to === "/"}>{label}</NavLink>)}</nav><button className="logout" onClick={signOut}>Logout</button></aside><main><header><div><p className="eyebrow">INTERNAL PROCUREMENT PLATFORM</p><h1>Supplier Price Intelligence</h1></div><div className="user-indicator">Authenticated session</div></header><Outlet /></main></div>;
}
