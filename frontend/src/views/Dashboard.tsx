import { useEffect, useMemo, useState, type ReactNode } from "react";
import { useNavigate } from "react-router-dom";
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  Clock3,
  Code2,
  Cpu,
  Database,
  Gauge,
  Hash,
  KeyRound,
  Lock,
  Send,
  ShieldCheck,
  Sigma,
  TrendingUp,
} from "lucide-react";
import {
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { PageHeader } from "@/components/shared/PageHeader";
import { CryptoCard } from "@/components/shared/CryptoCard";
import type { RouteKey } from "@/components/nav";
import { useAuth } from "@/stores/auth";
import { getAuditLogs } from "@/api/audit";
import { listKeys } from "@/api/keys";
import { getMetrics, type MetricPoint } from "@/api/metrics";

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
  hint,
  decimals = 0,
}: {
  label: string;
  value: number;
  unit?: string;
  icon: ReactNode;
  trend?: string;
  hint?: ReactNode;
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
        {hint && <div className="mt-2 text-[11px] leading-relaxed text-[var(--cl-text-secondary)]">{hint}</div>}
      </div>
    </div>
  );
}

const CATALOG: {
  route: RouteKey;
  title: string;
  sub: string;
  meta: string;
  icon: any;
  accent: string;
}[] = [
  { route: "symmetric", title: "Symmetric ciphers", sub: "AES / SM4 / RC6", meta: "ECB / CBC / CTR / GCM", icon: Lock, accent: "#409EFF" },
  { route: "hash", title: "Hash functions", sub: "SHA / RIPEMD", meta: "Digest algorithms", icon: Hash, accent: "#9B59B6" },
  { route: "hmac-pbkdf2", title: "HMAC / PBKDF2", sub: "Authentication / KDF", meta: "SHA-1 / SHA-256", icon: Sigma, accent: "#67C23A" },
  { route: "encoding", title: "Encoding", sub: "Base64 / UTF-8", meta: "Encode / decode", icon: Code2, accent: "#E6A23C" },
  { route: "rsa", title: "RSA", sub: "RSA-1024", meta: "OAEP / PSS", icon: KeyRound, accent: "#F56C6C" },
  { route: "ecc", title: "ECC / ECDSA", sub: "secp160r1", meta: "Sign / verify", icon: ShieldCheck, accent: "#13C2C2" },
  { route: "keys", title: "Key store", sub: "KEK wrapped keys", meta: "Export / revoke", icon: Database, accent: "#536DFE" },
  { route: "demos", title: "Security demos", sub: "Attack cases", meta: "ECB / k reuse / e=3", icon: AlertTriangle, accent: "#FA541C" },
  { route: "scenarios", title: "Secure transfer", sub: "Integrated workflow", meta: "RSA + AES + ECDSA", icon: Send, accent: "#722ED1" },
];

interface RecentRow {
  time: string;
  op: string;
  algo: string;
  dur: number;
  code: number;
}

function formatTime(iso: string): string {
  const d = new Date(iso);
  if (Number.isNaN(d.getTime())) return "--:--:--";
  const hh = String(d.getHours()).padStart(2, "0");
  const mm = String(d.getMinutes()).padStart(2, "0");
  const ss = String(d.getSeconds()).padStart(2, "0");
  return `${hh}:${mm}:${ss}`;
}

function seriesKey(row: MetricPoint): string {
  return `${row.algorithm}:${row.operation}`;
}

const CHART_COLORS = [
  "var(--cl-primary)",
  "var(--cl-success)",
  "var(--cl-warning)",
  "var(--cl-danger)",
  "#13C2C2",
  "#722ED1",
];

export function Dashboard() {
  const navigate = useNavigate();
  const { username } = useAuth();
  const displayName = username || "user";

  const [keyCount, setKeyCount] = useState(0);
  const [opCount, setOpCount] = useState(0);
  const [avgLatency, setAvgLatency] = useState(0);
  const [recent, setRecent] = useState<RecentRow[]>([]);
  const [metrics, setMetrics] = useState<MetricPoint[]>([]);

  useEffect(() => {
    let cancelled = false;

    (async () => {
      try {
        const resp = await listKeys();
        if (!cancelled && resp.code === 1000 && Array.isArray(resp.data)) {
          setKeyCount(resp.data.length);
        }
      } catch {
        if (!cancelled) setKeyCount(0);
      }
    })();

    (async () => {
      try {
        const resp = await getAuditLogs({ limit: 100 });
        if (!cancelled && resp.code === 1000 && Array.isArray(resp.data)) {
          const rows = resp.data;
          setOpCount(rows.length);
          const total = rows.reduce(
            (acc: number, r: any) => acc + (typeof r.duration_ms === "number" ? r.duration_ms : 0),
            0,
          );
          setAvgLatency(rows.length ? total / rows.length : 0);
          setRecent(
            rows.slice(0, 5).map((r: any) => ({
              time: formatTime(r.created_at),
              op: r.operation ?? "-",
              algo: r.algorithm ?? "-",
              dur: typeof r.duration_ms === "number" ? r.duration_ms : 0,
              code: typeof r.status_code === "number" ? r.status_code : 0,
            })),
          );
        }
      } catch {
        if (!cancelled) {
          setOpCount(0);
          setAvgLatency(0);
          setRecent([]);
        }
      }
    })();

    (async () => {
      try {
        const since = new Date(Date.now() - 7 * 24 * 60 * 60 * 1000).toISOString();
        const resp = await getMetrics({ since, limit: 200 });
        if (!cancelled && resp.code === 1000 && Array.isArray(resp.data)) {
          setMetrics(resp.data);
        }
      } catch {
        if (!cancelled) setMetrics([]);
      }
    })();

    return () => {
      cancelled = true;
    };
  }, []);

  const metricSeries = useMemo(
    () => Array.from(new Set(metrics.map(seriesKey))).slice(0, 6),
    [metrics],
  );

  const chartData = useMemo(
    () =>
      metrics.slice(-120).map((row) => ({
        time: formatTime(row.recorded_at),
        [seriesKey(row)]: row.duration_ns / 1_000_000,
      })),
    [metrics],
  );

  const handleNavigate = (key: RouteKey) => navigate("/" + key);

  return (
    <>
      <PageHeader
        title={`Welcome back, ${displayName}`}
        subtitle="CryptoLab operational dashboard for algorithms, keys, audits, and runtime metrics."
        breadcrumb={["Overview", "Dashboard"]}
        badge={
          <span className="px-2 py-0.5 rounded-full text-[10px] bg-[var(--cl-primary-light)] text-[var(--cl-primary-dark)] uppercase tracking-wider">
            role / user
          </span>
        }
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-7">
        <StatCard label="Algorithms" value={15} icon={<Cpu size={18} />} trend="covered" />
        <StatCard
          label="Stored keys"
          value={keyCount}
          icon={<KeyRound size={18} />}
          hint={
            keyCount === 0 ? (
              <>
                还没有密钥，去{" "}
                <button
                  type="button"
                  onClick={() => handleNavigate("keys")}
                  className="text-[var(--cl-primary)] hover:underline"
                >
                  密钥管理
                </button>{" "}
                生成第一个。
              </>
            ) : undefined
          }
        />
        <StatCard label="Recent operations" value={opCount} icon={<Activity size={18} />} />
        <StatCard label="Average latency" value={avgLatency} decimals={2} unit="ms" icon={<Clock3 size={18} />} />
      </div>

      <CryptoCard
        className="mb-7"
        title="Algorithm performance trend"
        subtitle="Last 7 days, sampled API calls and benchmark runs"
        icon={<TrendingUp size={14} />}
        extra={
          <button
            onClick={() => handleNavigate("benchmark")}
            className="text-xs text-[var(--cl-primary)] hover:underline inline-flex items-center gap-1"
          >
            Benchmark <ArrowRight size={12} />
          </button>
        }
      >
        {chartData.length === 0 ? (
          <div className="h-56 flex items-center justify-center text-xs text-[var(--cl-text-placeholder)]">
            No metrics recorded yet.
          </div>
        ) : (
          <div className="h-64">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={chartData} margin={{ top: 8, right: 16, left: 0, bottom: 0 }}>
                <CartesianGrid stroke="var(--cl-border-light)" strokeDasharray="4 4" />
                <XAxis
                  dataKey="time"
                  tick={{ fontSize: 11, fill: "var(--cl-text-secondary)" }}
                  tickLine={false}
                  axisLine={{ stroke: "var(--cl-border)" }}
                  minTickGap={24}
                />
                <YAxis
                  width={48}
                  tick={{ fontSize: 11, fill: "var(--cl-text-secondary)" }}
                  tickLine={false}
                  axisLine={{ stroke: "var(--cl-border)" }}
                  tickFormatter={(value) => `${Number(value).toFixed(1)}`}
                />
                <Tooltip
                  formatter={(value: any, name: any) => [
                    `${Number(value).toFixed(3)} ms`,
                    String(name),
                  ]}
                  labelFormatter={(label) => `Time ${label}`}
                />
                <Legend wrapperStyle={{ fontSize: 12 }} />
                {metricSeries.map((key, index) => (
                  <Line
                    key={key}
                    type="monotone"
                    dataKey={key}
                    stroke={CHART_COLORS[index % CHART_COLORS.length]}
                    strokeWidth={2}
                    dot={false}
                    connectNulls
                    isAnimationActive={false}
                  />
                ))}
              </LineChart>
            </ResponsiveContainer>
          </div>
        )}
      </CryptoCard>

      <div className="mb-7">
        <div className="flex items-end justify-between mb-3">
          <h2 className="text-[16px]">Algorithm catalog</h2>
          <span className="text-xs text-[var(--cl-text-secondary)]">15 implemented primitives</span>
        </div>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4">
          {CATALOG.map((c, i) => {
            const Icon = c.icon;
            return (
              <button
                key={c.route}
                onClick={() => handleNavigate(c.route)}
                className="group text-left bg-white rounded-lg border border-[var(--cl-border-light)] p-5 hover:shadow-[0_8px_28px_rgba(0,0,0,0.08)] hover:-translate-y-0.5 hover:border-[var(--cl-primary)]/40 transition-all duration-200 cl-fade-up"
                style={{ animationDelay: `${i * 40}ms` }}
              >
                <div
                  className="inline-flex items-center justify-center w-11 h-11 rounded-lg text-white shadow-[0_4px_12px_rgba(0,0,0,0.12)]"
                  style={{ backgroundColor: c.accent }}
                >
                  <Icon size={20} />
                </div>
                <div className="mt-3.5">
                  <div className="text-[15px]">{c.title}</div>
                  <div className="text-xs text-[var(--cl-text-secondary)] mt-0.5">{c.sub}</div>
                </div>
                <div className="mt-4 flex items-center justify-between">
                  <span className="text-[11px] text-[var(--cl-text-placeholder)] font-mono">{c.meta}</span>
                  <span className="inline-flex items-center gap-1 text-xs text-[var(--cl-primary)] opacity-0 group-hover:opacity-100 -translate-x-1 group-hover:translate-x-0 transition-all">
                    Open <ArrowRight size={12} />
                  </span>
                </div>
              </button>
            );
          })}
        </div>
      </div>

      <CryptoCard
        title="Recent activity"
        subtitle="Latest audited cryptographic operations"
        icon={<Gauge size={14} />}
        extra={
          <button
            onClick={() => handleNavigate("audit")}
            className="text-xs text-[var(--cl-primary)] hover:underline inline-flex items-center gap-1"
          >
            Audit logs <ArrowRight size={12} />
          </button>
        }
        bodyClassName="p-0"
      >
        <table className="w-full text-sm">
          <thead className="bg-[var(--cl-bg-page)]/60 text-[var(--cl-text-secondary)] text-xs">
            <tr>
              <th className="text-left font-normal px-5 py-2.5">Time</th>
              <th className="text-left font-normal px-5 py-2.5">Operation</th>
              <th className="text-left font-normal px-5 py-2.5">Algorithm</th>
              <th className="text-right font-normal px-5 py-2.5">Duration</th>
              <th className="text-right font-normal px-5 py-2.5">Status</th>
            </tr>
          </thead>
          <tbody>
            {recent.length === 0 ? (
              <tr>
                <td
                  colSpan={5}
                  className="px-5 py-8 text-center text-xs text-[var(--cl-text-placeholder)]"
                >
                  No audit records.
                </td>
              </tr>
            ) : (
              recent.map((r, i) => (
                <tr
                  key={`${r.time}-${i}`}
                  className="border-t border-[var(--cl-border-light)] hover:bg-[var(--cl-bg-page)]/50 transition-colors"
                >
                  <td className="px-5 py-2.5 text-[var(--cl-text-secondary)] font-mono text-xs">{r.time}</td>
                  <td className="px-5 py-2.5 font-mono text-xs">{r.op}</td>
                  <td className="px-5 py-2.5 text-[var(--cl-text-regular)]">{r.algo}</td>
                  <td className="px-5 py-2.5 text-right font-mono text-xs tabular-nums">{r.dur.toFixed(2)} ms</td>
                  <td className="px-5 py-2.5 text-right">
                    {r.code === 1000 ? (
                      <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] bg-[#E8F8E1] text-[#3F9114]">
                        1000 OK
                      </span>
                    ) : (
                      <span className="inline-flex items-center px-1.5 py-0.5 rounded text-[10px] bg-[#FEF0F0] text-[#C45656]">
                        {r.code} failed
                      </span>
                    )}
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </CryptoCard>
    </>
  );
}
