import { useState } from "react";
import { ScrollText, Filter, RotateCcw, X } from "lucide-react";
import { PageHeader } from "../shared/PageHeader";
import { CryptoCard } from "../shared/CryptoCard";
import { TextInput, GhostButton, Select, Tag, PrimaryButton } from "../shared/Field";
import { ROUTE_TITLES } from "../nav";

interface LogItem {
  trace: string;
  op: string;
  algo: string;
  key: string;
  status: number;
  dur: number;
  time: string;
}

const LOGS: LogItem[] = [
  { trace: "a1b2c3d4", op: "aes_encrypt", algo: "AES-GCM", key: "b7e15163-…", status: 1000, dur: 0.42, time: "14:32:15" },
  { trace: "d4e5f6g7", op: "rsa_keygen", algo: "RSA-1024", key: "c8f26274-…", status: 1000, dur: 234.5, time: "14:31:48" },
  { trace: "g7h8i9j0", op: "sha256", algo: "SHA-256", key: "—", status: 1000, dur: 0.08, time: "14:28:02" },
  { trace: "j0k1l2m3", op: "aes_decrypt", algo: "AES-GCM", key: "b7e15163-…", status: 3002, dur: 0.31, time: "14:21:09" },
  { trace: "n4o5p6q7", op: "ecdsa_sign", algo: "secp160r1", key: "fb1595a7-…", status: 1000, dur: 3.5, time: "14:18:32" },
  { trace: "r8s9t0u1", op: "pbkdf2", algo: "HMAC-SHA256", key: "—", status: 1000, dur: 45.2, time: "14:15:21" },
  { trace: "v2w3x4y5", op: "rsa_verify", algo: "RSA-1024", key: "c8f26274-…", status: 1000, dur: 4.1, time: "14:12:08" },
  { trace: "z6a7b8c9", op: "hmac", algo: "HMAC-SHA256", key: "0c26a6b8-…", status: 1000, dur: 0.05, time: "14:10:55" },
  { trace: "d0e1f2g3", op: "sha3_256", algo: "SHA3-256", key: "—", status: 1000, dur: 0.12, time: "14:08:14" },
  { trace: "h4i5j6k7", op: "base64_decode", algo: "Base64", key: "—", status: 2003, dur: 0.02, time: "14:05:32" },
];

function statusInfo(code: number) {
  if (code === 1000) return { tone: "success", label: "1000 成功" } as const;
  if (code < 3000) return { tone: "warn", label: `${code} 参数错误` } as const;
  if (code < 4000) return { tone: "warn", label: `${code} 业务错误` } as const;
  if (code < 5000) return { tone: "danger", label: `${code} 鉴权错误` } as const;
  return { tone: "danger", label: `${code} 服务异常` } as const;
}

export function AuditView() {
  const meta = ROUTE_TITLES.audit;
  const [selected, setSelected] = useState<LogItem | null>(null);

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
            const v = Math.max(0, Math.sin(i / 3) * 0.6 + 0.4 + Math.random() * 0.2);
            return (
              <div key={i} className="flex flex-col items-center gap-1">
                <div
                  className="w-full h-7 rounded-sm transition-transform hover:scale-110 cursor-pointer"
                  style={{ backgroundColor: `rgba(64, 158, 255, ${v.toFixed(2)})` }}
                  title={`${i}:00 · ${Math.round(v * 30)} 次`}
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
            value="all"
            onChange={() => {}}
            options={[
              { value: "all", label: "全部算法" },
              { value: "aes", label: "AES" },
              { value: "rsa", label: "RSA" },
              { value: "sha", label: "SHA 系列" },
            ]}
          />
          <Select
            value="all"
            onChange={() => {}}
            options={[
              { value: "all", label: "全部状态" },
              { value: "1000", label: "1000 成功" },
              { value: "4xxx", label: "4xxx 错误" },
            ]}
          />
          <TextInput placeholder="起始日期" className="w-36" type="date" defaultValue="2026-06-07" />
          <TextInput placeholder="终止日期" className="w-36" type="date" defaultValue="2026-06-07" />
          <PrimaryButton>查询</PrimaryButton>
          <GhostButton>
            <RotateCcw size={14} /> 重置
          </GhostButton>
        </div>
      </CryptoCard>

      <CryptoCard bodyClassName="p-0">
        <table className="w-full text-sm">
          <thead className="bg-[var(--cl-bg-page)]/60 text-[var(--cl-text-secondary)] text-xs">
            <tr>
              <th className="text-left font-normal px-4 py-2.5">Trace ID</th>
              <th className="text-left font-normal px-4 py-2.5">操作</th>
              <th className="text-left font-normal px-4 py-2.5">算法</th>
              <th className="text-left font-normal px-4 py-2.5">Key ID</th>
              <th className="text-right font-normal px-4 py-2.5">耗时</th>
              <th className="text-right font-normal px-4 py-2.5">状态</th>
              <th className="text-right font-normal px-4 py-2.5">时间</th>
            </tr>
          </thead>
          <tbody>
            {LOGS.map((l) => {
              const s = statusInfo(l.status);
              return (
                <tr
                  key={l.trace}
                  onClick={() => setSelected(l)}
                  className="border-t border-[var(--cl-border-light)] hover:bg-[var(--cl-bg-page)]/60 cursor-pointer transition-colors"
                >
                  <td className="px-4 py-2.5 font-mono text-[11.5px]">{l.trace}-…</td>
                  <td className="px-4 py-2.5 font-mono text-xs">{l.op}</td>
                  <td className="px-4 py-2.5 text-[var(--cl-text-regular)]">{l.algo}</td>
                  <td className="px-4 py-2.5 font-mono text-xs text-[var(--cl-text-secondary)]">{l.key}</td>
                  <td className="px-4 py-2.5 text-right font-mono text-xs tabular-nums">{l.dur.toFixed(2)} ms</td>
                  <td className="px-4 py-2.5 text-right">
                    <Tag tone={s.tone}>{s.label}</Tag>
                  </td>
                  <td className="px-4 py-2.5 text-right text-xs text-[var(--cl-text-secondary)] font-mono">{l.time}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
        <div className="px-4 py-3 flex items-center justify-between text-xs text-[var(--cl-text-secondary)] border-t border-[var(--cl-border-light)]">
          <span>显示 1 - 20 条 / 共 156 条</span>
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
                  trace_id · {selected.trace}-e5f6-7890-abcd
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
                ["用户 ID", "1"],
                ["操作", selected.op],
                ["算法", selected.algo],
                ["Key ID", selected.key],
                ["状态码", statusInfo(selected.status).label],
                ["耗时", `${selected.dur} ms`],
                ["客户端 IP", "127.0.0.1"],
                ["发生时间", `2026-06-07 ${selected.time}.123Z`],
              ].map(([k, v]) => (
                <div key={k} className="flex justify-between gap-4">
                  <span className="text-xs text-[var(--cl-text-secondary)]">{k}</span>
                  <span className="font-mono text-xs text-right max-w-[260px] break-all">{v}</span>
                </div>
              ))}
              <div className="pt-3 border-t border-[var(--cl-border-light)]">
                <div className="text-xs text-[var(--cl-text-secondary)] mb-1.5">输入哈希 (SHA-256)</div>
                <div className="font-mono text-[11px] p-2.5 rounded bg-[var(--cl-bg-code)] break-all leading-relaxed">
                  2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
                </div>
                <div className="text-xs text-[var(--cl-text-secondary)] mb-1.5 mt-3">输出哈希 (SHA-256)</div>
                <div className="font-mono text-[11px] p-2.5 rounded bg-[var(--cl-bg-code)] break-all leading-relaxed">
                  9b74c9897bac770ffc029ffd720d2b6b0a5f5e15e21ad45fde6a78ac7e51e2f3
                </div>
              </div>
            </div>
          </div>
        </>
      )}
    </>
  );
}
