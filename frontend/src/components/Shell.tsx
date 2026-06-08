import { useState, type ReactNode } from "react";
import { useNavigate, useLocation } from "react-router-dom";
import {
  ShieldCheck,
  Search,
  LogOut,
  ChevronDown,
  Command,
  Sparkles,
  User as UserIcon,
  PanelLeftClose,
  PanelLeft,
} from "lucide-react";
import { NAV_GROUPS, type RouteKey } from "./nav";
import { useAuth } from "@/stores/auth";

interface ShellProps {
  children: ReactNode;
}

export function Shell({ children }: ShellProps) {
  const [collapsed, setCollapsed] = useState(false);
  const [userOpen, setUserOpen] = useState(false);
  const navigate = useNavigate();
  const location = useLocation();
  const { username, logout } = useAuth();

  const route = (location.pathname.slice(1) || "dashboard") as RouteKey;

  const handleLogout = async () => {
    await logout();
    navigate("/login");
  };

  const handleNavigate = (key: RouteKey) => {
    navigate("/" + key);
  };

  return (
    <div className="h-screen w-full flex flex-col bg-[var(--cl-bg-page)] text-[var(--cl-text-primary)]">
      {/* Header */}
      <header className="h-16 shrink-0 bg-white border-b border-[var(--cl-border-light)] flex items-center px-5 gap-4 z-20">
        <div className="flex items-center gap-2.5">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--cl-primary)] to-[#1D6FE0] flex items-center justify-center shadow-[0_2px_8px_rgba(64,158,255,0.35)]">
            <ShieldCheck size={18} className="text-white" />
          </div>
          <div className="leading-tight">
            <div className="text-[15px] tracking-tight">CryptoLab</div>
            <div className="text-[10px] text-[var(--cl-text-secondary)]">密码算法实验平台</div>
          </div>
        </div>

        <button
          onClick={() => setCollapsed((c) => !c)}
          className="ml-2 w-9 h-9 rounded-md hover:bg-[var(--cl-bg-page)] text-[var(--cl-text-secondary)] inline-flex items-center justify-center transition-colors"
          title={collapsed ? "展开侧栏" : "收起侧栏"}
        >
          {collapsed ? <PanelLeft size={16} /> : <PanelLeftClose size={16} />}
        </button>

        {/* Command Search */}
        <div className="flex-1 max-w-md mx-auto">
          <button className="w-full h-9 px-3 rounded-md bg-[var(--cl-bg-page)] border border-transparent hover:border-[var(--cl-border)] inline-flex items-center gap-2 text-sm text-[var(--cl-text-secondary)] transition-colors">
            <Search size={14} />
            <span>搜索算法、密钥或日志…</span>
            <span className="ml-auto inline-flex items-center gap-0.5 text-[10px] font-mono px-1.5 py-0.5 rounded bg-white border border-[var(--cl-border-light)]">
              <Command size={10} /> K
            </span>
          </button>
        </div>

        {/* User menu */}
        <div className="relative">
          <button
            onClick={() => setUserOpen((o) => !o)}
            className="h-9 pl-1 pr-2.5 rounded-md hover:bg-[var(--cl-bg-page)] inline-flex items-center gap-2 transition-colors"
          >
            <div className="w-7 h-7 rounded-full bg-gradient-to-br from-[#9B59B6] to-[#5B3A8F] text-white text-xs inline-flex items-center justify-center uppercase">
              {(username || "U").slice(0, 1)}
            </div>
            <div className="text-left leading-tight">
              <div className="text-[13px]">{username || "用户"}</div>
              <div className="text-[10px] text-[var(--cl-text-secondary)]">普通用户</div>
            </div>
            <ChevronDown size={14} className={`text-[var(--cl-text-secondary)] transition-transform ${userOpen ? "rotate-180" : ""}`} />
          </button>
          {userOpen && (
            <>
              <div className="fixed inset-0 z-30" onClick={() => setUserOpen(false)} />
              <div
                className="absolute right-0 top-11 w-56 bg-white rounded-md shadow-[0_8px_24px_rgba(0,0,0,0.12)] border border-[var(--cl-border-light)] py-1 z-40 cl-scale-pop"
                style={{ transformOrigin: "top right" }}
              >
                <div className="px-3 py-2 border-b border-[var(--cl-border-light)]">
                  <div className="text-xs text-[var(--cl-text-secondary)]">已登录为</div>
                  <div className="text-sm">{username}</div>
                </div>
                <button className="w-full px-3 py-2 text-sm text-left hover:bg-[var(--cl-bg-page)] inline-flex items-center gap-2">
                  <UserIcon size={14} /> 个人资料
                </button>
                <button className="w-full px-3 py-2 text-sm text-left hover:bg-[var(--cl-bg-page)] inline-flex items-center gap-2">
                  <Sparkles size={14} /> 偏好设置
                </button>
                <div className="border-t border-[var(--cl-border-light)] my-1" />
                <button
                  onClick={handleLogout}
                  className="w-full px-3 py-2 text-sm text-left hover:bg-[#FEF0F0] text-[var(--cl-danger)] inline-flex items-center gap-2"
                >
                  <LogOut size={14} /> 退出登录
                </button>
              </div>
            </>
          )}
        </div>
      </header>

      <div className="flex-1 flex min-h-0">
        {/* Sidebar */}
        <aside
          className="bg-white border-r border-[var(--cl-border-light)] shrink-0 transition-[width] duration-300 ease-[var(--cl-ease-out)] overflow-hidden"
          style={{ width: collapsed ? 64 : 240 }}
        >
          <nav className="h-full overflow-y-auto py-3">
            {NAV_GROUPS.map((group) => (
              <div key={group.label} className="mb-3">
                {!collapsed && (
                  <div className="px-4 py-1.5 text-[10px] uppercase tracking-wider text-[var(--cl-text-placeholder)]">
                    {group.label}
                  </div>
                )}
                <div className="px-2 space-y-0.5">
                  {group.items.map((item) => {
                    const Icon = item.icon;
                    const active = route === item.key;
                    return (
                      <button
                        key={item.key}
                        onClick={() => handleNavigate(item.key)}
                        title={collapsed ? item.label : undefined}
                        className={`group relative w-full flex items-center gap-2.5 px-2.5 py-2 rounded-md text-sm transition-colors ${
                          active
                            ? "bg-[var(--cl-primary-light)] text-[var(--cl-primary-dark)]"
                            : "text-[var(--cl-text-regular)] hover:bg-[var(--cl-bg-page)]"
                        }`}
                      >
                        {active && (
                          <span className="absolute left-0 top-1.5 bottom-1.5 w-[3px] rounded-r bg-[var(--cl-primary)]" />
                        )}
                        <Icon
                          size={16}
                          className={active ? "text-[var(--cl-primary)]" : "text-[var(--cl-text-secondary)] group-hover:text-[var(--cl-text-regular)]"}
                        />
                        {!collapsed && (
                          <span className="truncate flex-1 text-left">{item.label}</span>
                        )}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </nav>
        </aside>

        {/* Main */}
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-[1280px] mx-auto px-8 py-7">
            <div key={route} className="cl-fade-up">
              {children}
            </div>
          </div>
          <footer className="px-8 pb-6 text-xs text-[var(--cl-text-placeholder)] max-w-[1280px] mx-auto">
            Built with Rust + Python · 15 hand-written cryptographic algorithms · BUPT 安全编程课程作品
          </footer>
        </main>
      </div>
    </div>
  );
}
