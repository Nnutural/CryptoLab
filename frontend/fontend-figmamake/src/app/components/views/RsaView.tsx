import { useState } from "react";
import { KeyRound, Lock, FileSignature, CheckCircle2, XCircle, Sparkles, ShieldCheck } from "lucide-react";
import { PageHeader } from "../shared/PageHeader";
import { CryptoCard } from "../shared/CryptoCard";
import { Field, TextInput, TextArea, PrimaryButton, GhostButton, Tag } from "../shared/Field";
import { HexViewer } from "../shared/HexViewer";
import { OperationTimer } from "../shared/OperationTimer";
import { ROUTE_TITLES } from "../nav";

const N_HEX =
  "00b3a7c9e1f5d2a8b6c4e3f7d1a9b5c8e2f6d4a0b7c3e9f5d1a8b4c6e0f2d7a9b5c8e2f6d4a0b7c3e9f5d1a8b4c6e0f2d7a9b5c8e2f6d4a0b7c3e9f5d1a8b4c6e0f2d7a9b5c8e2f6d4a0b7c3e9f5d1a8b4c6e0f2d7a9b5c8e2f6d4a0b7c3e9f5d1a8b4c6e0f2d7a9b5c8e2f6d4a0b7c3e9";
const CIPHER_HEX =
  "4a3f8b2c1d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8b9c0d1e2f3a4b5c6d";
const SIG_HEX =
  "7d2f3a8c9b1e4d5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0a1b2";

export function RsaView() {
  const meta = ROUTE_TITLES.rsa;
  const [hasKey, setHasKey] = useState(true);
  const [generating, setGenerating] = useState(false);
  const [tab, setTab] = useState<"enc" | "sign">("enc");

  const generate = () => {
    setGenerating(true);
    setTimeout(() => {
      setGenerating(false);
      setHasKey(true);
    }, 1200);
  };

  return (
    <>
      <PageHeader title={meta.title} subtitle={meta.subtitle} breadcrumb={meta.breadcrumb} />

      {/* Keygen panel */}
      <CryptoCard
        title="RSA-1024 密钥对"
        subtitle={hasKey ? "已生成密钥对,可直接执行后续运算" : "尚未生成任何 RSA 密钥"}
        icon={<KeyRound size={14} />}
        extra={
          hasKey ? (
            <Tag tone="success">就绪</Tag>
          ) : (
            <PrimaryButton onClick={generate} loading={generating}>
              <Sparkles size={14} /> 生成密钥对
            </PrimaryButton>
          )
        }
        className="mb-5"
      >
        {generating ? (
          <div>
            <div className="text-xs text-[var(--cl-text-regular)] mb-2">
              正在生成 1024 位素数(Miller-Rabin 素性检测)…
            </div>
            <div className="h-2 rounded bg-[var(--cl-bg-page)] overflow-hidden relative">
              <div className="cl-marquee-bar absolute inset-y-0 w-1/3 bg-[var(--cl-primary)]" />
            </div>
            <div className="mt-3 font-mono text-[11px] text-[var(--cl-text-placeholder)] grid grid-cols-2 gap-x-4">
              <span>候选 p: 0xb3a7… ✓</span>
              <span>候选 q: 0x9f1e… 测试中</span>
              <span>n = p · q (1024 bit)</span>
              <span>e = 65537 (0x010001)</span>
            </div>
          </div>
        ) : hasKey ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="text-xs text-[var(--cl-text-secondary)] mb-1.5">公钥 Key ID</div>
              <div className="font-mono text-xs px-3 py-2 rounded bg-[var(--cl-bg-code)] border border-[var(--cl-border-light)]">
                c8f26274-5bfe-3caf-ad98-64e9b3087f2b
              </div>
              <div className="text-xs text-[var(--cl-text-secondary)] mt-3 mb-1.5">私钥 Key ID</div>
              <div className="font-mono text-xs px-3 py-2 rounded bg-[var(--cl-bg-code)] border border-[var(--cl-border-light)]">
                b7e15163-4aed-2b9e-9c87-53d8a2f77e1a
              </div>
            </div>
            <div>
              <HexViewer value={N_HEX} label="模数 n_hex (1024 bit)" maxLines={2} />
              <div className="mt-3 inline-flex items-center gap-2 text-xs text-[var(--cl-text-regular)]">
                <span className="text-[var(--cl-text-secondary)]">公钥指数 e</span>
                <span className="font-mono px-2 py-0.5 rounded bg-[var(--cl-bg-code)] border border-[var(--cl-border-light)]">
                  0x010001 (65537)
                </span>
              </div>
            </div>
          </div>
        ) : null}
      </CryptoCard>

      {/* Tabs */}
      <div className="inline-flex bg-white rounded-md border border-[var(--cl-border-light)] p-0.5 mb-5">
        {[
          { k: "enc", label: "加密 / 解密", icon: Lock },
          { k: "sign", label: "签名 / 验签", icon: FileSignature },
        ].map((t) => (
          <button
            key={t.k}
            onClick={() => setTab(t.k as any)}
            className={`px-4 py-1.5 rounded text-sm transition-all inline-flex items-center gap-1.5 ${
              tab === t.k
                ? "bg-[var(--cl-primary-light)] text-[var(--cl-primary-dark)]"
                : "text-[var(--cl-text-secondary)] hover:text-[var(--cl-text-regular)]"
            }`}
          >
            <t.icon size={13} />
            {t.label}
          </button>
        ))}
      </div>

      {tab === "enc" ? <EncPanel /> : <SignPanel />}
    </>
  );
}

function EncPanel() {
  const [dir, setDir] = useState<"enc" | "dec">("enc");
  const [text, setText] = useState("Secret message");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ hex: string; ms: number } | null>(null);

  const run = () => {
    setLoading(true);
    setResult(null);
    setTimeout(() => {
      setResult({ hex: CIPHER_HEX, ms: 8 + Math.random() * 8 });
      setLoading(false);
    }, 500);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <CryptoCard title="参数" icon={<Lock size={14} />}>
        <div className="flex gap-2 mb-4">
          {(["enc", "dec"] as const).map((d) => (
            <button
              key={d}
              onClick={() => setDir(d)}
              className={`flex-1 h-9 rounded-md text-sm border transition-all ${
                dir === d
                  ? "border-[var(--cl-primary)] bg-[var(--cl-primary-light)] text-[var(--cl-primary-dark)]"
                  : "border-[var(--cl-border)] text-[var(--cl-text-regular)]"
              }`}
            >
              {d === "enc" ? "加密(使用公钥)" : "解密(使用私钥)"}
            </button>
          ))}
        </div>
        <Field label="密钥 ID">
          <TextInput
            value={dir === "enc" ? "c8f26274-…087f2b (公钥)" : "b7e15163-…77e1a (私钥)"}
            readOnly
            className="font-mono"
          />
        </Field>
        <Field label={dir === "enc" ? "明文" : "密文 (hex)"}>
          <TextArea value={text} onChange={(e) => setText(e.target.value)} rows={3} className={dir === "enc" ? "!font-sans" : ""} />
        </Field>
        <PrimaryButton onClick={run} loading={loading}>
          <Lock size={14} /> 执行 RSA {dir === "enc" ? "加密" : "解密"}
        </PrimaryButton>
      </CryptoCard>

      <CryptoCard
        title="运算结果"
        icon={<Sparkles size={14} />}
        extra={result && <OperationTimer durationMs={result.ms} operation="RSA" />}
      >
        {result ? (
          <HexViewer value={result.hex} label="密文 (hex · 256 chars)" maxLines={4} />
        ) : (
          <div className="text-sm text-[var(--cl-text-placeholder)] py-8 text-center">
            选择方向并执行运算
          </div>
        )}
      </CryptoCard>
    </div>
  );
}

function SignPanel() {
  const [dir, setDir] = useState<"sign" | "verify">("sign");
  const [msg, setMsg] = useState("Important document content");
  const [sig, setSig] = useState(SIG_HEX);
  const [tamper, setTamper] = useState(false);
  const [loading, setLoading] = useState(false);
  const [signResult, setSignResult] = useState<{ hex: string; ms: number } | null>(null);
  const [verifyResult, setVerifyResult] = useState<{ valid: boolean; ms: number } | null>(null);

  const run = () => {
    setLoading(true);
    setSignResult(null);
    setVerifyResult(null);
    setTimeout(() => {
      if (dir === "sign") setSignResult({ hex: SIG_HEX, ms: 12 + Math.random() * 4 });
      else setVerifyResult({ valid: !tamper, ms: 3 + Math.random() * 2 });
      setLoading(false);
    }, 500);
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <CryptoCard title="参数" icon={<FileSignature size={14} />}>
        <div className="flex gap-2 mb-4">
          {(["sign", "verify"] as const).map((d) => (
            <button
              key={d}
              onClick={() => setDir(d)}
              className={`flex-1 h-9 rounded-md text-sm border transition-all ${
                dir === d
                  ? "border-[var(--cl-primary)] bg-[var(--cl-primary-light)] text-[var(--cl-primary-dark)]"
                  : "border-[var(--cl-border)] text-[var(--cl-text-regular)]"
              }`}
            >
              {d === "sign" ? "签名(私钥)" : "验签(公钥)"}
            </button>
          ))}
        </div>
        <Field label="消息">
          <TextArea value={msg} onChange={(e) => setMsg(e.target.value)} rows={3} className="!font-sans" />
        </Field>
        {dir === "verify" && (
          <>
            <Field label="签名 signature (hex)">
              <TextArea value={sig} onChange={(e) => setSig(e.target.value)} rows={3} />
            </Field>
            <label className="inline-flex items-center gap-2 text-xs text-[var(--cl-text-regular)] mb-3">
              <input
                type="checkbox"
                checked={tamper}
                onChange={(e) => setTamper(e.target.checked)}
                className="accent-[var(--cl-danger)]"
              />
              模拟篡改:验签将失败
            </label>
          </>
        )}
        <PrimaryButton onClick={run} loading={loading}>
          {dir === "sign" ? "生成签名" : "验证签名"}
        </PrimaryButton>
      </CryptoCard>

      <CryptoCard title="运算结果" icon={<ShieldCheck size={14} />}>
        {signResult && <HexViewer value={signResult.hex} label="signature_hex" maxLines={4} />}
        {verifyResult && (
          <div
            className={`flex flex-col items-center justify-center py-8 ${
              verifyResult.valid ? "cl-scale-pop" : "cl-shake"
            }`}
          >
            {verifyResult.valid ? (
              <>
                <CheckCircle2 size={48} className="text-[var(--cl-success)] mb-3" />
                <div className="text-[var(--cl-success)]">签名有效</div>
                <div className="text-xs text-[var(--cl-text-secondary)] mt-1">消息与签名匹配</div>
              </>
            ) : (
              <>
                <XCircle size={48} className="text-[var(--cl-danger)] mb-3" />
                <div className="text-[var(--cl-danger)]">签名无效</div>
                <div className="text-xs text-[var(--cl-text-secondary)] mt-1">消息可能已被篡改</div>
              </>
            )}
          </div>
        )}
        {!signResult && !verifyResult && (
          <div className="text-sm text-[var(--cl-text-placeholder)] py-8 text-center">
            填写消息后执行 {dir === "sign" ? "签名" : "验签"}
          </div>
        )}
      </CryptoCard>
    </div>
  );
}
