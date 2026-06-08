import { useState } from "react";
import { Hash, Sparkles, Activity } from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { CryptoCard } from "@/components/shared/CryptoCard";
import { TextArea, PrimaryButton, Tag } from "@/components/shared/Field";
import { CopyButton } from "@/components/shared/CopyButton";
import { OperationTimer } from "@/components/shared/OperationTimer";
import { ROUTE_TITLES } from "@/components/nav";
import { computeHash } from "@/api/hash";

const ALGORITHMS = [
  { key: "sha1", label: "SHA-1", bits: 160 },
  { key: "sha224", label: "SHA-224", bits: 224 },
  { key: "sha256", label: "SHA-256", bits: 256 },
  { key: "sha384", label: "SHA-384", bits: 384 },
  { key: "sha512", label: "SHA-512", bits: 512 },
  { key: "sha3_256", label: "SHA3-256", bits: 256 },
  { key: "sha3_512", label: "SHA3-512", bits: 512 },
  { key: "ripemd160", label: "RIPEMD-160", bits: 160 },
];

interface HashResult {
  digest: string;
  durationMs: number;
}

export function HashView() {
  const meta = ROUTE_TITLES.hash;
  const [text, setText] = useState("hello");
  const [selected, setSelected] = useState<string[]>(["sha1", "sha256", "sha3_256", "ripemd160"]);
  const [results, setResults] = useState<Record<string, HashResult>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const toggle = (k: string) =>
    setSelected((s) => (s.includes(k) ? s.filter((x) => x !== k) : [...s, k]));

  const run = async () => {
    try {
      setLoading(true);
      setError(null);
      setResults({});

      const entries = await Promise.all(
        selected.map(async (algo) => {
          try {
            const resp = await computeHash(algo, text);
            if (resp.code === 1000 && resp.data) {
              return [
                algo,
                {
                  digest: resp.data.digest_hex ?? "",
                  durationMs:
                    typeof resp.data.duration_ms === "number" ? resp.data.duration_ms : 0,
                } as HashResult,
              ] as const;
            }
            return [algo, null] as const;
          } catch {
            return [algo, null] as const;
          }
        }),
      );

      const next: Record<string, HashResult> = {};
      entries.forEach(([algo, result]) => {
        if (result) next[algo] = result;
      });

      if (Object.keys(next).length === 0) {
        setError("所有算法计算均失败,请检查网络或重试");
      }

      setResults(next);
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || "网络错误");
    } finally {
      setLoading(false);
    }
  };

  // Compare SHA-256 vs SHA3-256 byte agreement if both computed
  const sha256 = results["sha256"]?.digest;
  const sha3 = results["sha3_256"]?.digest;
  let comparison: { matches: number; total: number; pct: number } | null = null;
  if (sha256 && sha3 && sha256.length === sha3.length) {
    let matches = 0;
    const total = sha256.length / 2;
    for (let i = 0; i < sha256.length; i += 2) {
      if (sha256[i] === sha3[i] && sha256[i + 1] === sha3[i + 1]) matches++;
    }
    comparison = { matches, total, pct: total ? Math.round((matches / total) * 100) : 0 };
  }

  return (
    <>
      <PageHeader title={meta.title} subtitle={meta.subtitle} breadcrumb={meta.breadcrumb} />

      <CryptoCard
        title="输入文本"
        subtitle="实时计算多种哈希算法,体验雪崩效应"
        icon={<Hash size={14} />}
        className="mb-5"
      >
        <TextArea
          rows={4}
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="输入需要计算哈希的文本…"
          className="!font-sans"
        />
        <div className="flex items-center justify-between mt-1.5">
          <span className="text-[11px] text-[var(--cl-text-placeholder)] font-mono">
            字符数 {text.length} · 字节 {new Blob([text]).size}
          </span>
        </div>

        <div className="mt-4">
          <div className="text-xs text-[var(--cl-text-secondary)] mb-2">选择算法(可多选)</div>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {ALGORITHMS.map((a) => {
              const on = selected.includes(a.key);
              return (
                <button
                  key={a.key}
                  onClick={() => toggle(a.key)}
                  className={`text-left px-3 py-2 rounded-md border transition-all text-sm ${
                    on
                      ? "border-[var(--cl-primary)] bg-[var(--cl-primary-light)] text-[var(--cl-primary-dark)]"
                      : "border-[var(--cl-border)] bg-white text-[var(--cl-text-regular)] hover:border-[var(--cl-primary)]/50"
                  }`}
                >
                  <div className="flex items-center justify-between">
                    <span>{a.label}</span>
                    {on && <span className="w-2 h-2 rounded-full bg-[var(--cl-primary)]" />}
                  </div>
                  <div className="text-[10px] text-[var(--cl-text-placeholder)] mt-0.5 font-mono">
                    {a.bits} 位
                  </div>
                </button>
              );
            })}
          </div>
        </div>

        <div className="mt-4 flex items-center gap-2">
          <PrimaryButton onClick={run} loading={loading} disabled={!selected.length || !text}>
            <Sparkles size={14} /> 计算哈希
          </PrimaryButton>
          <span className="text-xs text-[var(--cl-text-placeholder)]">
            已选 {selected.length} 个算法
          </span>
        </div>

        {error && (
          <div className="mt-3 px-3 py-2 rounded-md bg-[#FEF0F0] border border-[#FBC4C4] text-xs text-[#C45656]">
            {error}
          </div>
        )}
      </CryptoCard>

      {/* Results */}
      <div className="space-y-3">
        {selected.map((k, i) => {
          const algo = ALGORITHMS.find((a) => a.key === k)!;
          const r = results[k];
          return (
            <div
              key={k}
              className="bg-white rounded-lg border border-[var(--cl-border-light)] p-4 cl-fade-up"
              style={{ animationDelay: `${i * 50}ms` }}
            >
              <div className="flex items-center justify-between mb-2 gap-2 flex-wrap">
                <div className="flex items-center gap-2">
                  <span className="text-sm">{algo.label}</span>
                  <Tag tone="neutral">{algo.bits} 位</Tag>
                  {r && <OperationTimer durationMs={r.durationMs} operation={algo.label} />}
                </div>
                {r?.digest && <CopyButton text={r.digest} />}
              </div>
              {loading || !r ? (
                <div className="h-5 rounded bg-[var(--cl-bg-page)] animate-pulse" />
              ) : (
                <div className="font-mono text-[12.5px] text-[var(--cl-text-primary)] break-all leading-relaxed bg-[var(--cl-bg-code)] rounded p-2.5">
                  {r.digest}
                </div>
              )}
            </div>
          );
        })}

        {comparison && (
          <div className="mt-2 px-4 py-3 rounded-md bg-[var(--cl-primary-light)] border border-[#BFDFFF] text-xs text-[var(--cl-primary-dark)] inline-flex items-center gap-2">
            <Activity size={14} />
            <span>
              SHA-256 与 SHA3-256 字节匹配 {comparison.matches} / {comparison.total} ({comparison.pct}
              %) —— 不同算法的输出完全独立,体现密码学摘要的随机性。
            </span>
          </div>
        )}
      </div>
    </>
  );
}
