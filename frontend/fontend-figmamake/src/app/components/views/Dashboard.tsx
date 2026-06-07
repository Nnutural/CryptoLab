import { useEffect, useState } from "react";
import {
  Lock,
  Hash,
  Code2,
  KeyRound,
  ShieldCheck,
  Database,
  AlertTriangle,
  Send,
  Gauge,
  Sigma,
  ArrowRight,
  TrendingUp,
  Activity,
  Cpu,
  Clock3,
} from "lucide-react";
import { PageHeader } from "../shared/PageHeader";
import { CryptoCard } from "../shared/CryptoCard";
import type { RouteKey } from "../nav";

function useCountUp(target: number, duration = 900) {
  const [value, setValue] = useState(0);
  useEffect(() => {
    let raf: number;
    const start = performance.now();
    const tick = (now: number) => {
      const t = Math.min(1, (now - start) / duration);
      const eased = 1 - Math.pow(1 - t, 3);
      setValue(target * eased);
      if (t < 1) raf = requestAnimationFrame(tick);
    };
    raf = requestAnimationFrame(tick);
    return () => cancelAnimationFrame(raf);
  }, [target, duration]);
  return value;
}

function StatCard({
  label,
  value,
  unit,
  icon,
  trend,
  decimals = 0,
}: {
  label: string;
  value: number;
  unit?: string;
  icon: React.ReactNode;
  trend?: string;
  decimals?: number;
}) {
  const v = useCountUp(value);
  return (
    <div className="bg-white rounded-lg border border-[var(--cl-border-light)] p-5 hover:shadow-[0_4px_16px_rgba(0,0,0,0.06)] hover:-translate-y-0.5 transition-all duration-200">
      <div className="flex items-start justify-between">
        <span className="inline-flex items-center justify-center w-9 h-9 rounded-md bg-[var(--cl-primary-light)] text-[var(--cl-primary)]">
          {icon}
        </span>
        {trend && (
          <span className="text-[11px] text-[var(--cl-success)] inline-flex items-center gap-0.5">
            <TrendingUp size={12} /> {trend}
          </span>
        )}
      </div>
      <div className="mt-4">
        <div className="text-[28px] tracking-tight tabular-nums leading-none">
          {v.toFixed(decimals)}
          {unit && <span className="text-sm text-[var(--cl-text-secondary)] ml-1">{unit}</span>}
        </div>
        <div className="text-xs text-[var(--cl-text-secondary)] mt-1.5">{label}</div>
      </div>
    </div>
  );
}

interface DashboardProps {
  username: string;
  onNavigate: (r: RouteKey) => void;
}

const CATALOG: { route: RouteKey; title: string; sub: string; meta: string; icon: any; color: string }[] = [
  { route: "symmetric", title: "对称加密", sub: "AES · SM4 · RC6", meta: "ECB / CBC / CTR / GCM", icon: Lock, color: "from-[#409EFF] to-[#1D6FE0]" },
  { route: "hash", title: "哈希函数", sub: "SHA · RIPEMD", meta: "8 种算法", icon: Hash, color: "from-[#9B59B6] to-[#5B3A8F]" },
  { route: "hmac-pbkdf2", title: "消息认证 / 派生", sub: "HMAC · PBKDF2", meta: "SHA-1 / SHA-256", icon: Sigma, color: "from-[#67C23A] to-[#3F9114]" },
  { route: "encoding", title: "编码转换", sub: "Base64 · UTF-8", meta: "编码 / 解码", icon: Code2, color: "from-[#E6A23C] to-[#B88230]" },
  { route: "rsa", title: "RSA 密码算法", sub: "RSA-1024", meta: "加密 / 签名 / 验签", icon: KeyRound, color: "from-[#F56C6C] to-[#C45656]" },
  { route: "ecc", title: "ECC 椭圆曲线", sub: "secp160r1", meta: "ECDSA 签名 / 验签", icon: ShieldCheck, color: "from-[#13C2C2] to-[#08807F]" },
  { route: "keys", title: "密钥管理", sub: "KEK 包装存储", meta: "导出 / 撤销", icon: Database, color: "from-[#536DFE] to-[#3D5AFE]" },
  { route: "demos", title: "安全演示", sub: "4 个攻击复现", meta: "ECB / k 复用 / e=3", icon: AlertTriangle, color: "from-[#FA541C] to-[#D43A0F]" },
  { route: "scenarios", title: "安全文件传输", sub: "综合协议实验", meta: "RSA + AES + ECDSA", icon: Send, color: "from-[#722ED1] to-[#4F1D9C]" },
];

const RECENT = [
  { time: "14:32:15", op: "aes_encrypt", algo: "AES-GCM", dur: 0.42, code: 1000 },
  { time: "14:31:48", op: "rsa_keygen", algo: "RSA-1024", dur: 234.5, code: 1000 },
  { time: "14:28:02", op: "sha256", algo: "SHA-256", dur: 0.08, code: 1000 },
  { time: "14:25:31", op: "ecdsa_sign", algo: "secp160r1", dur: 3.5, code: 1000 },
  { time: "14:21:09", op: "aes_decrypt", algo: "AES-GCM", dur: 0.31, code: 3002 },
];

export function Dashboard({ username, onNavigate }: DashboardProps) {
  return (
    <>
      <PageHeader
        title={`欢迎回来,${username}`}
        subtitle="这里是 CryptoLab 平台的总览面板,展示你最近的实验与所有可用算法。"
        breadcrumb={["控制台"]}
        badge={
          <span className="px-2 py-0.5 rounded-full text-[10px] bg-[var(--cl-primary-light)] text-[var(--cl-primary-dark)] uppercase tracking-wider">
            用户角色 · user
          </span>
        }
      />

      {/* Stats */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-7">
        <StatCard label="可用算法总数" value={15} icon={<Cpu size={18} />} trend="完整覆盖" />
        <StatCard label="已存储密钥" value={24} icon={<KeyRound size={18} />} trend="+3 本周" />
        <StatCard label="今日操作次数" value={156} icon={<Activity size={18} />} trend="+18%" />
        <StatCard label="平均响应延迟" value={0.83} decimals={2} unit="ms" icon={<Clock3 size={18} />} />
      </div>

      {/* Catalog */}
      <div className="mb-7">
        <div className="flex items-end justify-between mb-3">
          <h2 className="text-[16px]">算法目录</h2>
          <span className="text-xs text-[var(--cl-text-secondary)]">点击卡片进入实验</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {CATALOG.map((c, i) => {
            const Icon = c.icon;
            return (
              <button
                key={c.route}
                onClick={() => onNavigate(c.route)}
                className="group text-left bg-white rounded-lg border border-[var(--cl-border-light)] p-5 hover:shadow-[0_8px_28px_rgba(0,0,0,0.08)] hover:-translate-y-0.5 hover:border-[var(--cl-primary)]/40 transition-all duration-200 cl-fade-up relative overflow-hidden"
                style={{ animationDelay: `${i * 40}ms` }}
              >
                <div className={`absolute -top-10 -right-10 w-32 h-32 rounded-full bg-gradient-to-br ${c.color} opacity-[0.06] group-hover:opacity-[0.12] transition-opacity`} />
                <div className={`relative inline-flex items-center justify-center w-11 h-11 rounded-lg bg-gradient-to-br ${c.color} text-white shadow-[0_4px_12px_rgba(0,0,0,0.12)]`}>
                  <Icon size={20} />
                </div>
                <div className="mt-3.5">
                  <div className="text-[15px]">{c.title}</div>
                  <div className="text-xs text-[var(--cl-text-secondary)] mt-0.5">{c.sub}</div>
                </div>
                <div className="mt-4 flex items-center justify-between">
                  <span className="text-[11px] text-[var(--cl-text-placeholder)] font-mono">{c.meta}</span>
                  <span className="inline-flex items-center gap-1 text-xs text-[var(--cl-primary)] opacity-0 group-hover:opacity-100 -translate-x-1 group-hover:translate-x-0 transition-all">
                    打开 <ArrowRight size={12} />
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Recent activity */}
      <CryptoCard
        title="最近操作"
        subtitle="过去 24 小时的密码运算记录"
        icon={<Gauge size={14} />}
        extra={
          <button
            onClick={() => onNavigate("audit")}
            className="text-xs text-[var(--cl-primary)] hover:underline inline-flex items-center gap-1"
          >
            查看全部审计日志 <ArrowRight size={12} />
          </button>
        }
        bodyClassName="p-0"
      >
        <table className="w-full text-sm">
          <thead className="bg-[var(--cl-bg-page)]/60 text-[var(--cl-text-secondary)] text-xs">
            <tr>
              <th className="text-left font-normal px-5 py-2.5">时间</th>
              <th className="text-left font-normal px-5 py-2.5">操作</th>
              <th className="text-left font-normal px-5 py-2.5">算法</th>
              <th className="text-right font-normal px-5 py-2.5">耗时</th>
              <th className="text-right font-normal px-5 py-2.5">状态</th>
            </tr>
          </thead>
          <tbody>
            {RECENT.map((r, i) => (
              <tr key={i} className="border-t border-[var(--cl-border-light)] hover:bg-[var(--cl-bg-page)]/50 transition-colors">
                <td className="px-5 py-2.5 text-[var(--cl-text-secondary)] font-mono text-xs">{r.time}</td>
                <td className="px-5 py-2.5 font-mono text-xs">{r.op}</td>
                <td className="px-5 py-2.5 text-[var(--cl-text-regular)]">{r.algo}</td>
                <td className="px-5 py-2.5 text-right font-mono text-xs tabular-nums">{r.dur.toFixed(2)} ms</td>
                <td className="px-5 py-2.5 text-right">
                  {r.code === 1000 ? (
                    <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] bg-[#E8F8E1] text-[#3F9114]">
                      1000 成功
                    </span>
                  ) : (
                    <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] bg-[#FEF0F0] text-[#C45656]">
                      {r.code} 失败
                    </span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </CryptoCard>
    </>
  );
}
