import { useState } from "react";
import { ShieldCheck, Sparkles, CheckCircle2, XCircle, FileSignature } from "lucide-react";
import { PageHeader } from "../shared/PageHeader";
import { CryptoCard } from "../shared/CryptoCard";
import { Field, TextInput, TextArea, PrimaryButton, Tag } from "../shared/Field";
import { HexViewer } from "../shared/HexViewer";
import { OperationTimer } from "../shared/OperationTimer";
import { ROUTE_TITLES } from "../nav";

const QX = "0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b";
const QY = "9f8e7d6c5b4a39281706f5e4d3c2b1a09f8e7d6c";

export function EccView() {
  const meta = ROUTE_TITLES.ecc;
  const [dir, setDir] = useState<"sign" | "verify">("sign");
  const [msg, setMsg] = useState("Hello, ECDSA!");
  const [loading, setLoading] = useState(false);
  const [signResult, setSignResult] = useState<{ r: string; s: string; ms: number } | null>(null);
  const [verifyResult, setVerifyResult] = useState<{ valid: boolean; ms: number } | null>(null);

  const run = () => {
    setLoading(true);
    setSignResult(null);
    setVerifyResult(null);
    setTimeout(() => {
      if (dir === "sign")
        setSignResult({
          r: "0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b",
          s: "5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f",
          ms: 3.5,
        });
      else setVerifyResult({ valid: true, ms: 4.2 });
      setLoading(false);
    }, 450);
  };

  return (
    <>
      <PageHeader title={meta.title} subtitle={meta.subtitle} breadcrumb={meta.breadcrumb} />

      <CryptoCard className="mb-5" bodyClassName="py-3">
        <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm">
          <span className="text-[var(--cl-text-secondary)] text-xs">曲线参数</span>
          <span className="font-mono text-xs">
            <span className="text-[var(--cl-text-secondary)]">curve</span>{" "}
            <span className="text-[var(--cl-text-primary)]">secp160r1</span>
          </span>
          <span className="font-mono text-xs">
            <span className="text-[var(--cl-text-secondary)]">field</span>{" "}
            <span className="text-[var(--cl-text-primary)]">160-bit</span>
          </span>
          <span className="font-mono text-xs">
            <span className="text-[var(--cl-text-secondary)]">group order</span>{" "}
            <span className="text-[var(--cl-text-primary)]">~2^160</span>
          </span>
          <Tag tone="info">RFC 6979 确定性 k</Tag>
        </div>
      </CryptoCard>

      <CryptoCard
        title="椭圆曲线密钥对"
        subtitle="基于 secp160r1 生成"
        icon={<ShieldCheck size={14} />}
        extra={<Tag tone="success">就绪</Tag>}
        className="mb-5"
      >
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_auto] gap-5 items-center">
          <div>
            <HexViewer value={QX} label="公钥 Qx (40 hex)" maxLines={1} />
            <div className="mt-3">
              <HexViewer value={QY} label="公钥 Qy (40 hex)" maxLines={1} />
            </div>
          </div>
          <CurveDiagram />
        </div>
      </CryptoCard>

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
                {d === "sign" ? "签名" : "验签"}
              </button>
            ))}
          </div>
          <Field label="消息">
            <TextArea value={msg} onChange={(e) => setMsg(e.target.value)} rows={3} className="!font-sans" />
          </Field>
          {dir === "verify" && (
            <>
              <Field label="r (hex)">
                <TextInput defaultValue={QX} className="font-mono" />
              </Field>
              <Field label="s (hex)">
                <TextInput defaultValue="5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f" className="font-mono" />
              </Field>
            </>
          )}
          <PrimaryButton onClick={run} loading={loading}>
            <Sparkles size={14} />
            {dir === "sign" ? "执行 ECDSA 签名" : "执行 ECDSA 验签"}
          </PrimaryButton>
        </CryptoCard>

        <CryptoCard
          title="运算结果"
          icon={<ShieldCheck size={14} />}
          extra={
            (signResult || verifyResult) && (
              <OperationTimer durationMs={(signResult?.ms || verifyResult?.ms)!} operation="ECDSA" />
            )
          }
        >
          {signResult && (
            <div className="space-y-3">
              <HexViewer value={signResult.r} label="r (40 hex)" maxLines={1} />
              <HexViewer value={signResult.s} label="s (40 hex)" maxLines={1} />
              <div className="flex items-center gap-2 pt-1">
                <Tag tone="success">签名成功</Tag>
                <Tag tone="neutral">curve secp160r1</Tag>
              </div>
            </div>
          )}
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
                </>
              ) : (
                <>
                  <XCircle size={48} className="text-[var(--cl-danger)] mb-3" />
                  <div className="text-[var(--cl-danger)]">签名无效</div>
                </>
              )}
            </div>
          )}
          {!signResult && !verifyResult && (
            <div className="text-sm text-[var(--cl-text-placeholder)] py-8 text-center">
              填写消息后执行 ECDSA 运算
            </div>
          )}
        </CryptoCard>
      </div>
    </>
  );
}

function CurveDiagram() {
  // Simple elliptic-curve scatter visualization
  const points = Array.from({ length: 38 }, (_, i) => {
    const t = (i / 38) * Math.PI * 2;
    const x = 60 + Math.cos(t) * 38;
    const y = 60 + Math.sin(t * 2) * 24;
    return { x, y };
  });
  return (
    <div className="w-32 h-32 relative">
      <svg viewBox="0 0 120 120" className="w-full h-full">
        <defs>
          <radialGradient id="cg" cx="50%" cy="50%" r="50%">
            <stop offset="0%" stopColor="rgba(64,158,255,0.18)" />
            <stop offset="100%" stopColor="rgba(64,158,255,0)" />
          </radialGradient>
        </defs>
        <circle cx="60" cy="60" r="55" fill="url(#cg)" />
        <path
          d="M 5 90 Q 60 -10 115 90"
          fill="none"
          stroke="var(--cl-primary)"
          strokeWidth="1.2"
          opacity="0.45"
        />
        <path
          d="M 5 30 Q 60 130 115 30"
          fill="none"
          stroke="var(--cl-primary)"
          strokeWidth="1.2"
          opacity="0.45"
        />
        {points.map((p, i) => (
          <circle key={i} cx={p.x} cy={p.y} r="1.2" fill="var(--cl-primary)" opacity="0.6" />
        ))}
        <circle cx="98" cy="48" r="4" fill="var(--cl-primary)" className="cl-pulse" />
      </svg>
      <div className="absolute -bottom-1 right-0 text-[10px] text-[var(--cl-text-placeholder)] font-mono">
        点 Q
      </div>
    </div>
  );
}
