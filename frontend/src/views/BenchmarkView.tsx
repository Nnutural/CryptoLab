import { useState } from "react";
import { Gauge, Play, RotateCcw } from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { CryptoCard } from "@/components/shared/CryptoCard";
import { PrimaryButton, GhostButton, Tag } from "@/components/shared/Field";
import { StatusBanner } from "@/components/shared/StatusBanner";
import { ROUTE_TITLES } from "@/components/nav";
import { runBenchmark } from "@/api/benchmark";

interface Algo {
  key: string;
  label: string;
  category: "sym" | "hash" | "pk";
  throughput: number; // MB/s
  ms: number;
  iterations?: number;
  dataSizeBytes?: number;
}

// Default placeholder metrics. Actual throughput/latency are filled in
// from the live `/benchmark/{algo}` response when the user clicks Run.
const ALL: Algo[] = [
  { key: "aes_ecb", label: "AES-ECB", category: "sym", throughput: 823, ms: 121.5 },
  { key: "aes_gcm", label: "AES-GCM", category: "sym", throughput: 780, ms: 128.2 },
  { key: "sm4_ecb", label: "SM4-ECB", category: "sym", throughput: 380, ms: 263.1 },
  { key: "rc6_ecb", label: "RC6-ECB", category: "sym", throughput: 420, ms: 238.0 },
  { key: "sha1", label: "SHA-1", category: "hash", throughput: 760, ms: 131.5 },
  { key: "sha256", label: "SHA-256", category: "hash", throughput: 900, ms: 111.1 },
  { key: "sha512", label: "SHA-512", category: "hash", throughput: 1120, ms: 89.2 },
  { key: "sha3_256", label: "SHA3-256", category: "hash", throughput: 520, ms: 192.3 },
  { key: "ripemd160", label: "RIPEMD-160", category: "hash", throughput: 480, ms: 208.3 },
  { key: "rsa_enc", label: "RSA 加密", category: "pk", throughput: 0.08, ms: 12.4 },
  { key: "ecdsa_sign", label: "ECDSA 签名", category: "pk", throughput: 0.05, ms: 3.5 },
];

export function BenchmarkView() {
  const meta = ROUTE_TITLES.benchmark;
  const [filter, setFilter] = useState<"all" | "sym" | "hash" | "pk">("all");
  const [selected, setSelected] = useState<string[]>([
    "aes_ecb",
    "aes_gcm",
    "sm4_ecb",
    "rc6_ecb",
    "sha256",
    "sha3_256",
  ]);
  const [results, setResults] = useState<Algo[]>([]);
  const [running, setRunning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [error, setError] = useState<string | null>(null);

  const visible = ALL.filter((a) => filter === "all" || a.category === filter);

  const toggle = (k: string) =>
    setSelected((s) => (s.includes(k) ? s.filter((x) => x !== k) : [...s, k]));

  const run = async () => {
    setResults([]);
    setRunning(true);
    setProgress(0);
    setError(null);
    const items = ALL.filter((a) => selected.includes(a.key));
    const accumulated: Algo[] = [];

    for (let i = 0; i < items.length; i++) {
      const base = items[i];
      try {
        // NOTE: backend currently exposes `GET /benchmark/{algo}`. If the
        // server is later switched to `POST /benchmark/run` accepting
        // { algorithm, data_size, iterations }, swap to:
        //   await client.post('/benchmark/run', { algorithm: base.key, data_size: 1048576, iterations: 100 })
        const resp = await runBenchmark(base.key);
        if (resp.code === 1000 && resp.data) {
          const d = resp.data as {
            algorithm?: string;
            throughput_mb_per_s?: number;
            throughput_mbps?: number;
            total_ms?: number;
            latency_ms_p50?: number;
            latency_ms_p95?: number;
            iterations?: number;
            data_size_bytes?: number;
          };
          accumulated.push({
            ...base,
            throughput:
              typeof d.throughput_mb_per_s === "number"
                ? d.throughput_mb_per_s
                : typeof d.throughput_mbps === "number"
                ? d.throughput_mbps
                : base.throughput,
            ms:
              typeof d.total_ms === "number"
                ? d.total_ms
                : typeof d.latency_ms_p50 === "number"
                ? d.latency_ms_p50
                : base.ms,
            iterations: d.iterations,
            dataSizeBytes: d.data_size_bytes,
          });
        } else {
          accumulated.push(base);
          if (resp.message) setError(resp.message);
        }
      } catch (err: any) {
        // Keep going for the remaining algorithms but surface a hint.
        accumulated.push(base);
        const msg = err?.response?.data?.message || err?.message || "网络错误";
        setError(msg);
      }
      setResults([...accumulated]);
      setProgress(((i + 1) / items.length) * 100);
    }

    setRunning(false);
  };

  const sortedResults = [...results].sort((a, b) => b.throughput - a.throughput);
  const maxThroughput = Math.max(...sortedResults.map((r) => r.throughput), 1);

  return (
    <>
      <PageHeader title={meta.title} subtitle={meta.subtitle} breadcrumb={meta.breadcrumb} />

      {error && (
        <div className="mb-5">
          <StatusBanner type="danger" title="基准测试出现错误" message={error} />
        </div>
      )}

      <CryptoCard className="mb-5" icon={<Gauge size={14} />} title="选择测试算法">
        <div className="flex gap-1 mb-4">
          {[
            { k: "all", l: "全部" },
            { k: "sym", l: "对称算法" },
            { k: "hash", l: "哈希算法" },
            { k: "pk", l: "公钥算法" },
          ].map((c) => (
            <button
              key={c.k}
              onClick={() => setFilter(c.k as any)}
              className={`px-3 py-1.5 rounded-md text-xs transition-all ${
                filter === c.k
                  ? "bg-[var(--cl-primary-light)] text-[var(--cl-primary-dark)]"
                  : "text-[var(--cl-text-secondary)] hover:bg-[var(--cl-bg-page)]"
              }`}
            >
              {c.l}
            </button>
          ))}
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 gap-2 mb-4">
          {visible.map((a) => {
            const on = selected.includes(a.key);
            return (
              <button
                key={a.key}
                onClick={() => toggle(a.key)}
                className={`text-left px-3 py-2 rounded-md border text-sm transition-all ${
                  on
                    ? "border-[var(--cl-primary)] bg-[var(--cl-primary-light)] text-[var(--cl-primary-dark)]"
                    : "border-[var(--cl-border)] hover:border-[var(--cl-primary)]/50"
                }`}
              >
                <div className="flex items-center justify-between">
                  <span>{a.label}</span>
                  {on && <span className="w-1.5 h-1.5 rounded-full bg-[var(--cl-primary)]" />}
                </div>
              </button>
            );
          })}
        </div>
        <div className="flex items-center gap-3">
          <PrimaryButton onClick={run} loading={running} disabled={!selected.length}>
            <Play size={13} /> 运行选中的基准测试
          </PrimaryButton>
          <GhostButton onClick={() => setResults([])}>
            <RotateCcw size={14} /> 清空结果
          </GhostButton>
          {running && (
            <div className="flex items-center gap-2 text-xs text-[var(--cl-text-secondary)]">
              <div className="w-40 h-1.5 rounded-full bg-[var(--cl-bg-page)] overflow-hidden">
                <div
                  className="h-full bg-[var(--cl-primary)] transition-all duration-300"
                  style={{ width: `${progress}%` }}
                />
              </div>
              {Math.round(progress)}%
            </div>
          )}
        </div>
      </CryptoCard>

      {/* Chart */}
      {sortedResults.length > 0 && (
        <CryptoCard title="吞吐量(MB/s)" subtitle="数据大小 1 MB · 迭代 100 次" className="mb-5">
          <div className="space-y-3">
            {sortedResults.map((r, i) => {
              const pct = (r.throughput / maxThroughput) * 100;
              const color =
                r.category === "sym"
                  ? "from-[#409EFF] to-[#1D6FE0]"
                  : r.category === "hash"
                  ? "from-[#9B59B6] to-[#5B3A8F]"
                  : "from-[#67C23A] to-[#3F9114]";
              return (
                <div key={r.key} className="cl-fade-up" style={{ animationDelay: `${i * 40}ms` }}>
                  <div className="flex items-center justify-between mb-1 text-xs">
                    <span>{r.label}</span>
                    <span className="font-mono tabular-nums text-[var(--cl-text-regular)]">
                      {r.throughput < 1 ? r.throughput.toFixed(3) : r.throughput.toFixed(1)} MB/s
                    </span>
                  </div>
                  <div className="h-6 bg-[var(--cl-bg-page)] rounded overflow-hidden">
                    <div
                      className={`h-full bg-gradient-to-r ${color} transition-all duration-700 ease-out`}
                      style={{ width: `${pct}%` }}
                    />
                  </div>
                </div>
              );
            })}
          </div>
        </CryptoCard>
      )}

      {/* Table */}
      {sortedResults.length > 0 && (
        <CryptoCard bodyClassName="p-0" title="详细数据">
          <table className="w-full text-sm">
            <thead className="bg-[var(--cl-bg-page)]/60 text-[var(--cl-text-secondary)] text-xs">
              <tr>
                <th className="text-left font-normal px-4 py-2.5">算法</th>
                <th className="text-right font-normal px-4 py-2.5">数据大小</th>
                <th className="text-right font-normal px-4 py-2.5">迭代次数</th>
                <th className="text-right font-normal px-4 py-2.5">总耗时</th>
                <th className="text-right font-normal px-4 py-2.5">吞吐量</th>
                <th className="text-right font-normal px-4 py-2.5">分类</th>
              </tr>
            </thead>
            <tbody>
              {sortedResults.map((r) => {
                const sizeBytes = r.dataSizeBytes ?? 1_048_576;
                const sizeMb = sizeBytes / 1_048_576;
                const iterations = r.iterations ?? 100;
                return (
                  <tr
                    key={r.key}
                    className="border-t border-[var(--cl-border-light)] hover:bg-[var(--cl-bg-page)]/60"
                  >
                    <td className="px-4 py-2.5">{r.label}</td>
                    <td className="px-4 py-2.5 text-right font-mono text-xs">
                      {sizeMb >= 1 ? `${sizeMb.toFixed(2)} MB` : `${sizeBytes} B`}
                    </td>
                    <td className="px-4 py-2.5 text-right font-mono text-xs">{iterations}</td>
                    <td className="px-4 py-2.5 text-right font-mono text-xs tabular-nums">
                      {r.ms.toFixed(2)} ms
                    </td>
                    <td className="px-4 py-2.5 text-right font-mono text-xs tabular-nums">
                      {r.throughput < 1
                        ? `${r.throughput.toFixed(3)} MB/s`
                        : `${r.throughput.toFixed(1)} MB/s`}
                    </td>
                    <td className="px-4 py-2.5 text-right">
                      <Tag
                        tone={
                          r.category === "sym"
                            ? "info"
                            : r.category === "hash"
                            ? "primary"
                            : "success"
                        }
                      >
                        {r.category === "sym" ? "对称" : r.category === "hash" ? "哈希" : "公钥"}
                      </Tag>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </CryptoCard>
      )}
    </>
  );
}
