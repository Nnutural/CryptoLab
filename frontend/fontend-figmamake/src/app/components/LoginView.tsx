import { useState, useMemo, useEffect } from "react";
import { ShieldCheck, User, Lock, Loader2, KeyRound, Hash, Hexagon } from "lucide-react";

interface LoginViewProps {
  onLogin: (username: string) => void;
}

const HEX = "0123456789abcdef";

export function LoginView({ onLogin }: LoginViewProps) {
  const [tab, setTab] = useState<"login" | "register">("login");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [lastChar, setLastChar] = useState<string | null>(null);

  useEffect(() => {
    if (!lastChar) return;
    const t = setTimeout(() => setLastChar(null), 220);
    return () => clearTimeout(t);
  }, [lastChar]);

  const particles = useMemo(
    () =>
      Array.from({ length: 14 }).map((_, i) => ({
        id: i,
        left: Math.random() * 100,
        top: Math.random() * 100,
        dx: (Math.random() - 0.5) * 200,
        dy: (Math.random() - 0.5) * 200,
        dr: (Math.random() - 0.5) * 360,
        dur: 10 + Math.random() * 12,
        delay: Math.random() * -14,
        icon: i % 3,
        size: 14 + Math.random() * 14,
      })),
    []
  );

  const submit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (username.length < 3) {
      setError("用户名至少需要 3 个字符");
      return;
    }
    if (password.length < 8 && tab === "register") {
      setError("注册密码至少需要 8 个字符");
      return;
    }
    setLoading(true);
    setTimeout(() => {
      setLoading(false);
      onLogin(username || "alice");
    }, 700);
  };

  return (
    <div className="min-h-screen w-full relative overflow-hidden bg-gradient-to-br from-[#0F1729] via-[#1A2342] to-[#16213e]">
      {/* particle background */}
      <div className="absolute inset-0 pointer-events-none">
        {particles.map((p) => {
          const Icon = [KeyRound, ShieldCheck, Hexagon][p.icon];
          return (
            <span
              key={p.id}
              className="absolute cl-particle text-white/30"
              style={
                {
                  left: `${p.left}%`,
                  top: `${p.top}%`,
                  ["--dx" as any]: `${p.dx}px`,
                  ["--dy" as any]: `${p.dy}px`,
                  ["--dr" as any]: `${p.dr}deg`,
                  ["--dur" as any]: `${p.dur}s`,
                  animationDelay: `${p.delay}s`,
                } as React.CSSProperties
              }
            >
              <Icon size={p.size} />
            </span>
          );
        })}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,transparent_30%,rgba(15,23,41,0.6)_100%)]" />
      </div>

      <div className="relative min-h-screen flex flex-col items-center justify-center px-6 py-12">
        {/* Brand */}
        <div className="text-center mb-8 cl-fade-up">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-gradient-to-br from-[var(--cl-primary)] to-[#1D6FE0] shadow-[0_8px_30px_rgba(64,158,255,0.45)] mb-4">
            <ShieldCheck size={28} className="text-white" />
          </div>
          <h1 className="text-white text-[28px] tracking-tight">CryptoLab</h1>
          <p className="text-white/55 text-sm mt-1.5">密码算法实验平台</p>
        </div>

        {/* Card */}
        <div
          className="w-full max-w-[420px] bg-white rounded-xl shadow-[0_20px_60px_rgba(0,0,0,0.35)] cl-scale-pop overflow-hidden"
        >
          {/* Tabs */}
          <div className="relative flex border-b border-[var(--cl-border-light)]">
            {(["login", "register"] as const).map((t) => (
              <button
                key={t}
                onClick={() => {
                  setTab(t);
                  setError(null);
                }}
                className={`flex-1 py-3.5 text-sm transition-colors ${
                  tab === t
                    ? "text-[var(--cl-primary)]"
                    : "text-[var(--cl-text-secondary)] hover:text-[var(--cl-text-regular)]"
                }`}
              >
                {t === "login" ? "登录" : "注册"}
              </button>
            ))}
            <div
              className="absolute bottom-0 h-[2px] bg-[var(--cl-primary)] transition-all duration-300"
              style={{
                width: "50%",
                left: tab === "login" ? "0%" : "50%",
              }}
            />
          </div>

          <form onSubmit={submit} className="p-7">
            <label className="block text-xs text-[var(--cl-text-regular)] mb-1.5">用户名</label>
            <div className="relative mb-4">
              <User
                size={16}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--cl-text-placeholder)]"
              />
              <input
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="输入用户名"
                className="w-full h-10 pl-9 pr-3 rounded-md border border-[var(--cl-border)] bg-white text-sm focus:border-[var(--cl-primary)] focus:ring-2 focus:ring-[var(--cl-primary)]/15 outline-none transition-all"
              />
            </div>

            <label className="block text-xs text-[var(--cl-text-regular)] mb-1.5">密码</label>
            <div className="relative mb-1">
              <Lock
                size={16}
                className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--cl-text-placeholder)]"
              />
              <input
                type="password"
                value={password}
                onChange={(e) => {
                  setPassword(e.target.value);
                  if (e.target.value.length > password.length) {
                    const r = HEX[Math.floor(Math.random() * 16)] + HEX[Math.floor(Math.random() * 16)];
                    setLastChar(`0x${r}`);
                  }
                }}
                placeholder={tab === "register" ? "至少 8 个字符" : "输入密码"}
                className="w-full h-10 pl-9 pr-20 rounded-md border border-[var(--cl-border)] bg-white text-sm focus:border-[var(--cl-primary)] focus:ring-2 focus:ring-[var(--cl-primary)]/15 outline-none transition-all"
              />
              <span
                className={`absolute right-3 top-1/2 -translate-y-1/2 font-mono text-[11px] tracking-wider text-[var(--cl-primary)] transition-all duration-200 ${
                  lastChar ? "opacity-100 scale-100" : "opacity-0 scale-90"
                }`}
              >
                {lastChar}
              </span>
            </div>
            <div className="text-[11px] text-[var(--cl-text-placeholder)] mb-5 h-4">
              {tab === "register" ? "密码至少 8 位,建议包含大小写字母与数字" : " "}
            </div>

            {error && (
              <div className="mb-3 px-3 py-2 rounded-md bg-[#FEF0F0] border border-[#FBC4C4] text-xs text-[#C45656] cl-shake">
                {error}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full h-11 rounded-md bg-gradient-to-r from-[var(--cl-primary)] to-[#1D6FE0] text-white text-sm shadow-[0_4px_14px_rgba(64,158,255,0.35)] hover:shadow-[0_6px_20px_rgba(64,158,255,0.5)] disabled:opacity-70 transition-all inline-flex items-center justify-center gap-2"
            >
              {loading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  请稍候
                </>
              ) : tab === "login" ? (
                "登 录"
              ) : (
                "注 册"
              )}
            </button>

            <div className="mt-5 flex items-center justify-center gap-1.5 text-[11px] text-[var(--cl-text-secondary)]">
              <Hash size={12} />
              <span className="font-mono">JWT · Bearer Token · 1h 有效期</span>
            </div>
          </form>
        </div>

        <div className="mt-8 text-white/40 text-xs">
          Powered by Rust + Python · BUPT 2026
        </div>
      </div>
    </div>
  );
}
