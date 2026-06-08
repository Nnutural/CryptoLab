import { useState, useMemo } from "react";
import { Sigma, Sparkles, Key, AlertTriangle } from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { CryptoCard } from "@/components/shared/CryptoCard";
import { Field, TextInput, PrimaryButton, Tag } from "@/components/shared/Field";
import { HexViewer } from "@/components/shared/HexViewer";
import { OperationTimer } from "@/components/shared/OperationTimer";
import { StatusBanner } from "@/components/shared/StatusBanner";
import { ROUTE_TITLES } from "@/components/nav";
import { computeHmac, computePbkdf2 } from "@/api/hash";

export function HmacPbkdf2View() {
  const meta = ROUTE_TITLES["hmac-pbkdf2"];
  const [tab, setTab] = useState<"hmac" | "pbkdf2">("hmac");

  return (
    <>
      <PageHeader title={meta.title} subtitle={meta.subtitle} breadcrumb={meta.breadcrumb} />

      <div className="inline-flex bg-white rounded-md border border-[var(--cl-border-light)] p-0.5 mb-5">
        {(["hmac", "pbkdf2"] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={`px-4 py-1.5 rounded text-sm transition-all ${
              tab === t
                ? "bg-[var(--cl-primary-light)] text-[var(--cl-primary-dark)]"
                : "text-[var(--cl-text-secondary)] hover:text-[var(--cl-text-regular)]"
            }`}
          >
            {t === "hmac" ? "HMAC 消息认证" : "PBKDF2 密钥派生"}
          </button>
        ))}
      </div>

      {tab === "hmac" ? <HmacPanel /> : <Pbkdf2Panel />}
    </>
  );
}

function HmacPanel() {
  const [key, setKey] = useState("secret-key");
  const [msg, setMsg] = useState("Hello, HMAC!");
  const [algo, setAlgo] = useState<"sha1" | "sha256">("sha256");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ hex: string; ms: number } | null>(null);

  const run = async () => {
    try {
      setLoading(true);
      setError(null);
      setResult(null);
      const resp = await computeHmac(algo, {
        key,
        message: msg,
        algorithm: algo,
      });
      if (resp.code === 1000) {
        const data = resp.data || {};
        setResult({
          hex: data.mac_hex || "",
          ms: data.duration_ms ?? 0,
        });
      } else {
        setError(resp.message || "HMAC 计算失败");
      }
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || "网络错误");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <CryptoCard title="HMAC 输入" icon={<Sigma size={14} />}>
        <Field label="密钥 Key">
          <TextInput value={key} onChange={(e) => setKey(e.target.value)} className="font-mono" />
        </Field>
        <Field label="消息 Message">
          <TextInput value={msg} onChange={(e) => setMsg(e.target.value)} />
        </Field>
        <Field label="底层哈希算法">
          <div className="flex gap-2">
            {(["sha1", "sha256"] as const).map((a) => (
              <button
                key={a}
                onClick={() => setAlgo(a)}
                className={`flex-1 h-9 rounded-md text-sm border transition-all ${
                  algo === a
                    ? "border-[var(--cl-primary)] bg-[var(--cl-primary-light)] text-[var(--cl-primary-dark)]"
                    : "border-[var(--cl-border)] text-[var(--cl-text-regular)] hover:border-[var(--cl-primary)]/50"
                }`}
              >
                {a === "sha1" ? "SHA-1" : "SHA-256"}
              </button>
            ))}
          </div>
        </Field>
        {error && (
          <div className="mb-3 px-3 py-2 rounded-md bg-[#FEF0F0] border border-[#FBC4C4] text-xs text-[#C45656] cl-shake">
            {error}
          </div>
        )}
        <PrimaryButton onClick={run} loading={loading}>
          <Sparkles size={14} /> 计算 HMAC
        </PrimaryButton>
      </CryptoCard>

      <CryptoCard
        title="MAC 值"
        subtitle={`HMAC-${algo.toUpperCase()}`}
        icon={<Key size={14} />}
        extra={result && <OperationTimer durationMs={result.ms} operation="HMAC" />}
      >
        {result ? (
          <HexViewer value={result.hex} label="MAC (hex)" maxLines={3} />
        ) : (
          <div className="text-sm text-[var(--cl-text-placeholder)] py-8 text-center">
            填写密钥与消息后执行计算
          </div>
        )}
      </CryptoCard>
    </div>
  );
}

function Pbkdf2Panel() {
  const [password, setPassword] = useState("my-password");
  const [salt, setSalt] = useState("random-salt-value");
  const [iterations, setIterations] = useState(100000);
  const [keyLen, setKeyLen] = useState(32);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<{ hex: string; ms: number; warn: boolean } | null>(null);

  const estimate = useMemo(() => {
    return (iterations / 100000) * 45;
  }, [iterations]);

  const run = async () => {
    try {
      setLoading(true);
      setError(null);
      setResult(null);
      const resp = await computePbkdf2({
        password,
        salt,
        iterations,
        key_len: keyLen,
      });
      if (resp.code === 1000) {
        const data = resp.data || {};
        setResult({
          hex: data.derived_key_hex || "",
          ms: data.duration_ms ?? 0,
          warn: iterations < 100000,
        });
      } else {
        setError(resp.message || "PBKDF2 派生失败");
      }
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || "网络错误");
    } finally {
      setLoading(false);
    }
  };

  const setLog = (e: React.ChangeEvent<HTMLInputElement>) => {
    const v = Number(e.target.value);
    setIterations(Math.round(Math.pow(10, 3 + v * 3)));
  };

  const logVal = Math.log10(iterations / 1000) / 3;

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <CryptoCard title="PBKDF2 参数" icon={<Sigma size={14} />}>
        <Field label="密码 Password">
          <TextInput value={password} onChange={(e) => setPassword(e.target.value)} />
        </Field>
        <Field label="盐值 Salt">
          <TextInput value={salt} onChange={(e) => setSalt(e.target.value)} className="font-mono" />
        </Field>
        <Field
          label={`迭代次数 Iterations: ${iterations.toLocaleString()}`}
          hint={`预计耗时 ≈ ${estimate.toFixed(1)} ms`}
        >
          <input
            type="range"
            min={0}
            max={1}
            step={0.01}
            value={logVal}
            onChange={setLog}
            className="w-full accent-[var(--cl-primary)]"
          />
          <div className="flex justify-between text-[10px] text-[var(--cl-text-placeholder)] mt-1 font-mono">
            <span>1K</span>
            <span>10K</span>
            <span>100K</span>
            <span>1M</span>
          </div>
        </Field>
        <Field label="派生密钥长度(字节)">
          <TextInput
            type="number"
            value={keyLen}
            onChange={(e) => setKeyLen(Number(e.target.value) || 32)}
            className="font-mono"
          />
        </Field>
        {error && (
          <div className="mb-3 px-3 py-2 rounded-md bg-[#FEF0F0] border border-[#FBC4C4] text-xs text-[#C45656] cl-shake">
            {error}
          </div>
        )}
        <PrimaryButton onClick={run} loading={loading}>
          <Sparkles size={14} /> 派生密钥
        </PrimaryButton>
      </CryptoCard>

      <CryptoCard
        title="派生密钥"
        subtitle="PBKDF2-HMAC-SHA256"
        icon={<Key size={14} />}
        extra={result && <OperationTimer durationMs={result.ms} operation="PBKDF2" />}
      >
        {result ? (
          <>
            <HexViewer value={result.hex} label="derived_key (hex)" maxLines={3} />
            <div className="mt-3 flex items-center gap-2">
              <Tag tone="neutral">迭代 {iterations.toLocaleString()}</Tag>
              <Tag tone="neutral">长度 {keyLen} 字节</Tag>
            </div>
            {result.warn && (
              <div className="mt-3">
                <StatusBanner
                  type="warning"
                  title="安全性告警"
                  message="迭代次数低于 100,000 次,密码哈希强度不足,易受暴力破解。"
                />
              </div>
            )}
          </>
        ) : (
          <div className="text-sm text-[var(--cl-text-placeholder)] py-8 text-center">
            <AlertTriangle size={20} className="mx-auto mb-2 text-[var(--cl-warning)]" />
            高迭代数会显著增加耗时,请耐心等待
          </div>
        )}
      </CryptoCard>
    </div>
  );
}
