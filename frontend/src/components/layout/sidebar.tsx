import { LayoutDashboard, ShieldAlert, ShieldCheck, FolderKanban } from "lucide-react";
import { NavLink } from "react-router-dom";

import { cn } from "@/lib/utils";

const NAV_ITEMS = [
  { to: "/", label: "Dashboard", icon: LayoutDashboard, end: true },
  { to: "/projects", label: "Projetos", icon: FolderKanban, end: false },
  { to: "/findings", label: "Vulnerabilidades", icon: ShieldAlert, end: false },
];

export function Sidebar() {
  return (
    <aside className="hidden w-56 shrink-0 flex-col border-r border-border bg-card/40 md:flex">
      <div className="flex h-14 items-center gap-2 border-b border-border px-4">
        <ShieldCheck className="size-5 text-primary" />
        <span className="text-sm font-semibold tracking-tight">SAST Platform</span>
      </div>
      <nav className="flex flex-1 flex-col gap-1 p-3">
        {NAV_ITEMS.map(({ to, label, icon: Icon, end }) => (
          <NavLink
            key={to}
            to={to}
            end={end}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-2.5 rounded-md px-3 py-2 text-sm font-medium transition-colors",
                isActive
                  ? "bg-primary/10 text-primary"
                  : "text-muted-foreground hover:bg-accent hover:text-accent-foreground",
              )
            }
          >
            <Icon className="size-4" />
            {label}
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
