import { useEffect, useMemo, useState } from "react";
import { ScrollText, Filter, RotateCcw, X } from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { CryptoCard } from "@/components/shared/CryptoCard";
import { TextInput, GhostButton, Select, Tag, PrimaryButton } from "@/components/shared/Field";
import { ROUTE_TITLES } from "@/components/nav";
import { getAuditLogs } from "@/api/audit";

interface LogItem {
  log_id?: number | string;
  user_id?: number | string;
  username?: string;
  algorithm?: string;
  operation_type?: string;
  status?: number;
  input_hash?: string;
  output_hash?: string;
  duration_ms?: number;
  ip_address?: string;
  trace_id?: string;
  created_at?: string;
}

function statusInfo(code: number) {
  if (code === 1000) return { tone: "success" as const, label: "1000 成功" };
  if (code < 3000) return { tone: "warn" as const, label: `${code} 参数错误` };
  if (code < 4000) return { tone: "warn" as const, label: `${code} 业务错误` };
  if (code < 5000) return { tone: "danger" as const, label: `${code} 鉴权错误` };
  return { tone: "danger" as const, label: `${code} 服务异常` };
}

function shortTrace(trace?: string): string {
  if (!trace) return "—";
  return trace.length > 8 ? `${trace.slice(0, 8)}-…` : trace;
}

function formatTime(iso?: string): string {
  if (!iso) return "—";
  try {
    const d = new Date(iso);
    return d.toLocaleTimeString("zh-CN", { hour12: false });
  } catch {
    return iso;
  }
}

function formatDateTime(iso?: string): string {
  if (!iso) return "—";
  try {
    const d = new Date(iso);
    return d.toISOString().replace("T", " ").replace("Z", "Z");
  } catch {
    return iso;
  }
}

export function AuditView() {
  const meta = ROUTE_TITLES.audit;
  const today = new Date().toISOString().slice(0, 10);

  const [selected, setSelected] = useState<LogItem | null>(null);
  const [logs, setLogs] = useState<LogItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [algorithmFilter, setAlgorithmFilter] = useState("all");
  const [statusFilter, setStatusFilter] = useState("all");
  const [startDate, setStartDate] = useState(today);
  const [endDate, setEndDate] = useState(today);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      setError(null);
      const filters: Record<string, any> = { limit: 50, offset: 0 };
      if (algorithmFilter !== "all") filters.algorithm = algorithmFilter;
      if (startDate) filters.since = `${startDate}T00:00:00`;
      if (endDate) filters.until = `${endDate}T23:59:59`;

      const resp = await getAuditLogs(filters);
      if (resp.code === 1000) {
        let data = Array.isArray(resp.data) ? resp.data : [];
        if (statusFilter === "1000") {
          data = data.filter((l: any) => l.status === 1000);
        }
        if (statusFilter === "4xxx") {
          data = data.filter((l: any) => typeof l.status === "number" && l.status >= 4000 && l.status < 5000);
        }
        setLogs(data);
      } else {
        setError(resp.message || "查询失败");
      }
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || "网络错误");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  const resetFilters = () => {
    setAlgorithmFilter("all");
    setStatusFilter("all");
    setStartDate(today);
    setEndDate(today);
  };

  // Compute hourly heatmap from current logs
  const hourlyCounts = useMemo(() => {
    const counts = Array.from({ length: 24 }, () => 0);
    for (const l of logs) {
      if (!l.created_at) continue;
      try {
        const h = new Date(l.created_at).getHours();
        if (h >= 0 && h < 24) counts[h] += 1;
      } catch {
        /* ignore */
      }
    }
    return counts;
  }, [logs]);

  const maxHourly = useMemo(() => Math.max(1, ...hourlyCounts), [hourlyCounts]);

  return (
    <>
      <PageHeader title={meta.title} subtitle={meta.subtitle} breadcrumb={meta.breadcrumb} />

      {/* Heatmap */}
      <CryptoCard
        className="mb-5"
        title="今日操作热力分布"
        subtitle="按小时统计 · 颜色越深表示操作越频繁"
        icon={<ScrollText size={14} />}
      >
        <div className="grid grid-cols-24 gap-1" style={{ gridTemplateColumns: "repeat(24, minmax(0, 1fr))" }}>
          {Array.from({ length: 24 }).map((_, i) => {
            const count = hourlyCounts[i];
            const v = count > 0 ? Math.max(0.15, count / maxHourly) : 0.05;
            return (
              <div key={i} className="flex flex-col items-center gap-1">
                <div
                  className="w-full h-7 rounded-sm transition-transform hover:scale-110 cursor-pointer"
                  style={{ backgroundColor: `rgba(64, 158, 255, ${v.toFixed(2)})` }}
                  title={`${i}:00 · ${count} 次`}
                />
                <span className="text-[9px] text-[var(--cl-text-placeholder)] font-mono">
                  {i % 4 === 0 ? `${i}:00` : ""}
                </span>
              </div>
            );
          })}
        </div>
      </CryptoCard>

      {/* Filters */}
      <CryptoCard className="mb-5" bodyClassName="py-3">
        <div className="flex items-center gap-3 flex-wrap">
          <Filter size={14} className="text-[var(--cl-text-secondary)]" />
          <Select
            value={algorithmFilter}
            onChange={setAlgorithmFilter}
            options={[
              { value: "all", label: "全部算法" },
              { value: "AES", label: "AES" },
              { value: "RSA", label: "RSA" },
              { value: "SHA-256", label: "SHA 系列" },
              { value: "ECDSA", label: "ECDSA" },
              { value: "HMAC", label: "HMAC" },
            ]}
          />
          <Select
            value={statusFilter}
            onChange={setStatusFilter}
            options={[
              { value: "all", label: "全部状态" },
              { value: "1000", label: "1000 成功" },
              { value: "4xxx", label: "4xxx 错误" },
            ]}
          />
          <TextInput
            placeholder="起始日期"
            className="w-36"
            type="date"
            value={startDate}
            onChange={(e) => setStartDate(e.target.value)}
          />
          <TextInput
            placeholder="终止日期"
            className="w-36"
            type="date"
            value={endDate}
            onChange={(e) => setEndDate(e.target.value)}
          />
          <PrimaryButton onClick={fetchLogs} loading={loading}>
            查询
          </PrimaryButton>
          <GhostButton
            onClick={() => {
              resetFilters();
              // refresh after reset on next tick so state has updated
              setTimeout(fetchLogs, 0);
            }}
          >
            <RotateCcw size={14} /> 重置
          </GhostButton>
        </div>
        {error && (
          <div className="mt-3 px-3 py-2 rounded-md bg-[#FEF0F0] border border-[#FBC4C4] text-xs text-[#C45656] cl-shake">
            {error}
          </div>
        )}
      </CryptoCard>

      <CryptoCard bodyClassName="p-0">
        <table className="w-full text-sm">
          <thead className="bg-[var(--cl-bg-page)]/60 text-[var(--cl-text-secondary)] text-xs">
            <tr>
              <th className="text-left font-normal px-4 py-2.5">Trace ID</th>
              <th className="text-left font-normal px-4 py-2.5">操作</th>
              <th className="text-left font-normal px-4 py-2.5">算法</th>
              <th className="text-left font-normal px-4 py-2.5">用户</th>
              <th className="text-right font-normal px-4 py-2.5">耗时</th>
              <th className="text-right font-normal px-4 py-2.5">状态</th>
              <th className="text-right font-normal px-4 py-2.5">时间</th>
            </tr>
          </thead>
          <tbody>
            {logs.length === 0 && !loading ? (
              <tr>
                <td colSpan={7} className="px-4 py-8 text-center text-sm text-[var(--cl-text-placeholder)]">
                  暂无审计记录
                </td>
              </tr>
            ) : (
              logs.map((l) => {
                const s = statusInfo(typeof l.status === "number" ? l.status : 1000);
                return (
                  <tr
                    key={l.log_id ?? l.trace_id ?? Math.random()}
                    onClick={() => setSelected(l)}
                    className="border-t border-[var(--cl-border-light)] hover:bg-[var(--cl-bg-page)]/60 cursor-pointer transition-colors"
                  >
                    <td className="px-4 py-2.5 font-mono text-[11.5px]">{shortTrace(l.trace_id)}</td>
                    <td className="px-4 py-2.5 font-mono text-xs">{l.operation_type || "—"}</td>
                    <td className="px-4 py-2.5 text-[var(--cl-text-regular)]">{l.algorithm || "—"}</td>
                    <td className="px-4 py-2.5 font-mono text-xs text-[var(--cl-text-secondary)]">
                      {l.username || (l.user_id != null ? String(l.user_id) : "—")}
                    </td>
                    <td className="px-4 py-2.5 text-right font-mono text-xs tabular-nums">
                      {typeof l.duration_ms === "number" ? l.duration_ms.toFixed(2) : "—"} ms
                    </td>
                    <td className="px-4 py-2.5 text-right">
                      <Tag tone={s.tone}>{s.label}</Tag>
                    </td>
                    <td className="px-4 py-2.5 text-right text-xs text-[var(--cl-text-secondary)] font-mono">
                      {formatTime(l.created_at)}
                    </td>
                  </tr>
                );
              })
            )}
          </tbody>
        </table>
        <div className="px-4 py-3 flex items-center justify-between text-xs text-[var(--cl-text-secondary)] border-t border-[var(--cl-border-light)]">
          <span>
            显示 {logs.length === 0 ? 0 : 1} - {logs.length} 条
          </span>
          <div className="inline-flex gap-1">
            {["‹", 1, 2, 3, "…", 8, "›"].map((n, i) => (
              <button
                key={i}
                className={`min-w-7 h-7 px-1.5 rounded ${n === 1 ? "bg-[var(--cl-primary)] text-white" : "hover:bg-[var(--cl-bg-page)]"}`}
              >
                {n}
              </button>
            ))}
          </div>
        </div>
      </CryptoCard>

      {/* Drawer */}
      {selected && (
        <>
          <div className="fixed inset-0 bg-black/30 z-30 cl-fade-up" onClick={() => setSelected(null)} />
          <div
            className="fixed top-0 right-0 bottom-0 w-[440px] bg-white border-l border-[var(--cl-border)] z-40 overflow-y-auto"
            style={{ animation: "cl-fade-up 300ms var(--cl-ease-out)" }}
          >
            <div className="px-5 py-4 border-b border-[var(--cl-border-light)] flex items-center justify-between">
              <div>
                <div className="text-sm">操作详情</div>
                <div className="text-xs text-[var(--cl-text-secondary)] font-mono mt-0.5">
                  trace_id · {selected.trace_id || "—"}
                </div>
              </div>
              <button
                onClick={() => setSelected(null)}
                className="w-8 h-8 rounded hover:bg-[var(--cl-bg-page)] inline-flex items-center justify-center text-[var(--cl-text-secondary)]"
              >
                <X size={16} />
              </button>
            </div>
            <div className="p-5 space-y-3 text-sm">
              {[
                ["用户 ID", selected.user_id != null ? String(selected.user_id) : "—"],
                ["用户名", selected.username || "—"],
                ["操作", selected.operation_type || "—"],
                ["算法", selected.algorithm || "—"],
                [
                  "状态码",
                  statusInfo(typeof selected.status === "number" ? selected.status : 1000).label,
                ],
                [
                  "耗时",
                  typeof selected.duration_ms === "number" ? `${selected.duration_ms} ms` : "—",
                ],
                ["客户端 IP", selected.ip_address || "—"],
                ["发生时间", formatDateTime(selected.created_at)],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between gap-4">
                  <span className="text-xs text-[var(--cl-text-secondary)]">{k}</span>
                  <span className="font-mono text-xs text-right max-w-[260px] break-all">{v}</span>
                </div>
              ))}
              <div className="pt-3 border-t border-[var(--cl-border-light)]">
                <div className="text-xs text-[var(--cl-text-secondary)] mb-1.5">输入哈希 (SHA-256)</div>
                <div className="font-mono text-[11px] p-2.5 rounded bg-[var(--cl-bg-code)] break-all leading-relaxed">
                  {selected.input_hash || "—"}
                </div>
                <div className="text-xs text-[var(--cl-text-secondary)] mb-1.5 mt-3">输出哈希 (SHA-256)</div>
                <div className="font-mono text-[11px] p-2.5 rounded bg-[var(--cl-bg-code)] break-all leading-relaxed">
                  {selected.output_hash || "—"}
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
}
