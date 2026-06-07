import { useState } from "react";
import { Hash, Sparkles, Activity } from "lucide-react";
import { PageHeader } from "../shared/PageHeader";
import { CryptoCard } from "../shared/CryptoCard";
import { TextArea, PrimaryButton, Tag } from "../shared/Field";
import { CopyButton } from "../shared/CopyButton";
import { ROUTE_TITLES } from "../nav";

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

const MOCK: Record<string, string> = {
  sha1: "aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d",
  sha224: "ea09ae9cc6768c50fcee903ed054556e5bfc8347907f12598aa24193",
  sha256: "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
  sha384:
    "59e1748777448c69de6b800d7a33bbfb9ff1b463e44354c3553bcdb9c666fa90125a3c79f90397bdf5f6a13de828684f",
  sha512:
    "9b71d224bd62f3785d96d46ad3ea3d73319bfbc2890caadae2dff72519673ca72323c3d99ba5c11d7c7acc6e14b8c5da0c4663475c2e5c3adef46f73bcdec043",
  sha3_256: "3338be694f50c5f338814986cdf0686453a888b84f424d792af4b9202398f392",
  sha3_512:
    "75d527c368f2efe848ecf6b073a36767800805e9eef2b1857d5f984f036eb6df891d75f72d9b154518c1cd58835286d1da9a38deba3de98b5a53e5ed78a84976",
  ripemd160: "108f07b8382412612c048d07d13f814118445acd",
};

export function HashView() {
  const meta = ROUTE_TITLES.hash;
  const [text, setText] = useState("hello");
  const [selected, setSelected] = useState<string[]>(["sha1", "sha256", "sha3_256", "ripemd160"]);
  const [results, setResults] = useState<Record<string, string>>({});
  const [loading, setLoading] = useState(false);

  const toggle = (k: string) =>
    setSelected((s) => (s.includes(k) ? s.filter((x) => x !== k) : [...s, k]));

  const run = () => {
    setLoading(true);
    setResults({});
    setTimeout(() => {
      const r: Record<string, string> = {};
      selected.forEach((k) => (r[k] = MOCK[k] || "0".repeat(64)));
      setResults(r);
      setLoading(false);
    }, 500);
  };

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
      </CryptoCard>

      {/* Results */}
      <div className="space-y-3">
        {selected.map((k, i) => {
          const algo = ALGORITHMS.find((a) => a.key === k)!;
          const v = results[k];
          return (
            <div
              key={k}
              className="bg-white rounded-lg border border-[var(--cl-border-light)] p-4 cl-fade-up"
              style={{ animationDelay: `${i * 50}ms` }}
            >
              <div className="flex items-center justify-between mb-2">
                <div className="flex items-center gap-2">
                  <span className="text-sm">{algo.label}</span>
                  <Tag tone="neutral">{algo.bits} 位</Tag>
                </div>
                {v && <CopyButton text={v} />}
              </div>
              {loading || !v ? (
                <div className="h-5 rounded bg-[var(--cl-bg-page)] animate-pulse" />
              ) : (
                <div className="font-mono text-[12.5px] text-[var(--cl-text-primary)] break-all leading-relaxed bg-[var(--cl-bg-code)] rounded p-2.5">
                  {v}
                </div>
              )}
            </div>
          );
        })}

        {Object.keys(results).length >= 2 && (
          <div className="mt-2 px-4 py-3 rounded-md bg-[var(--cl-primary-light)] border border-[#BFDFFF] text-xs text-[var(--cl-primary-dark)] inline-flex items-center gap-2">
            <Activity size={14} />
            <span>
              SHA-256 与 SHA3-256 字节匹配 0 / 64 (0%) —— 不同算法的输出完全独立,体现密码学摘要的随机性。
            </span>
          </div>
        )}
      </div>
    </>
  );
}
