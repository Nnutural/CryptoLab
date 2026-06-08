import { useEffect, useState } from "react";
import { ShieldCheck, Sparkles, CheckCircle2, XCircle, FileSignature } from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { CryptoCard } from "@/components/shared/CryptoCard";
import { Field, TextInput, TextArea, PrimaryButton, Tag } from "@/components/shared/Field";
import { HexViewer } from "@/components/shared/HexViewer";
import { OperationTimer } from "@/components/shared/OperationTimer";
import { ROUTE_TITLES } from "@/components/nav";
import { eccKeygen, ecdsaSign, ecdsaVerify } from "@/api/pubkey";
import { listKeys } from "@/api/keys";

interface EccKey {
  key_id: string;
  label?: string;
  algorithm?: string;
  curve?: string;
  x_hex?: string;
  y_hex?: string;
  public_key_hex?: string;
}

export function EccView() {
  const meta = ROUTE_TITLES.ecc;
  const [dir, setDir] = useState<"sign" | "verify">("sign");
  const [msg, setMsg] = useState("Hello, ECDSA!");
  const [rHex, setRHex] = useState("");
  const [sHex, setSHex] = useState("");
  const [loading, setLoading] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [signResult, setSignResult] = useState<{ r: string; s: string; ms: number } | null>(null);
  const [verifyResult, setVerifyResult] = useState<{ valid: boolean; ms: number } | null>(null);
  const [keyInfo, setKeyInfo] = useState<EccKey | null>(null);
  const [keyError, setKeyError] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  const loadKeys = async () => {
    try {
      const resp = await listKeys();
      if (resp.code === 1000 && Array.isArray(resp.data)) {
        const eccKeys = resp.data.filter(
          (k: any) => k.algorithm === "ECC" || k.algorithm === "ECDSA" || (k.curve && typeof k.curve === "string")
        );
        if (eccKeys.length > 0) {
          const first = eccKeys[0];
          setKeyInfo({
            key_id: first.key_id,
            label: first.label,
            algorithm: first.algorithm,
            curve: first.curve || "secp160r1",
            x_hex: first.x_hex,
            y_hex: first.y_hex,
            public_key_hex: first.public_key_hex,
          });
        } else {
          setKeyInfo(null);
        }
      }
    } catch (err: any) {
      setKeyError(err?.response?.data?.message || err?.message || "加载密钥失败");
    }
  };

  useEffect(() => {
    loadKeys();
  }, []);

  const generate = async () => {
    try {
      setGenerating(true);
      setKeyError(null);
      const resp = await eccKeygen({ curve: "secp160r1", label: `ecc-${Date.now()}` });
      if (resp.code === 1000) {
        const data = resp.data;
        setKeyInfo({
          key_id: data.key_id,
          curve: data.curve,
          x_hex: data.x_hex,
          y_hex: data.y_hex,
          public_key_hex: data.public_key_hex,
          algorithm: "ECC",
        });
      } else {
        setKeyError(resp.message || "生成密钥失败");
      }
    } catch (err: any) {
      setKeyError(err?.response?.data?.message || err?.message || "网络错误");
    } finally {
      setGenerating(false);
    }
  };

  const run = async () => {
    if (!keyInfo?.key_id) {
      setError("请先生成 ECC 密钥对");
      return;
    }
    try {
      setLoading(true);
      setError(null);
      setSignResult(null);
      setVerifyResult(null);
      const curve = keyInfo.curve || "secp160r1";
      if (dir === "sign") {
        const resp = await ecdsaSign({ message: msg, key_id: keyInfo.key_id, curve });
        if (resp.code === 1000) {
          setSignResult({ r: resp.data.r_hex, s: resp.data.s_hex, ms: resp.data.duration_ms });
          setRHex(resp.data.r_hex);
          setSHex(resp.data.s_hex);
        } else {
          setError(resp.message || "签名失败");
        }
      } else {
        const resp = await ecdsaVerify({
          message: msg,
          r_hex: rHex,
          s_hex: sHex,
          key_id: keyInfo.key_id,
          curve,
        });
        if (resp.code === 1000) {
          setVerifyResult({ valid: !!resp.data.valid, ms: resp.data.duration_ms });
        } else {
          setError(resp.message || "验签失败");
        }
      }
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || "网络错误");
    } finally {
      setLoading(false);
    }
  };

  const QX = keyInfo?.x_hex || "—";
  const QY = keyInfo?.y_hex || "—";

  return (
    <>
      <PageHeader title={meta.title} subtitle={meta.subtitle} breadcrumb={meta.breadcrumb} />

      <CryptoCard className="mb-5" bodyClassName="py-3">
        <div className="flex flex-wrap items-center gap-x-6 gap-y-2 text-sm">
          <span className="text-[var(--cl-text-secondary)] text-xs">曲线参数</span>
          <span className="font-mono text-xs">
            <span className="text-[var(--cl-text-secondary)]">curve</span>{" "}
            <span className="text-[var(--cl-text-primary)]">{keyInfo?.curve || "secp160r1"}</span>
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
        extra={
          keyInfo ? (
            <Tag tone="success">就绪</Tag>
          ) : (
            <PrimaryButton onClick={generate} loading={generating}>
              <Sparkles size={14} /> 生成密钥对
            </PrimaryButton>
          )
        }
        className="mb-5"
      >
        {keyError && (
          <div className="mb-3 px-3 py-2 rounded-md bg-[#FEF0F0] border border-[#FBC4C4] text-xs text-[#C45656] cl-shake">
            {keyError}
          </div>
        )}
        <div className="grid grid-cols-1 lg:grid-cols-[1fr_auto] gap-5 items-center">
          <div>
            <HexViewer value={QX} label="公钥 Qx (40 hex)" maxLines={1} />
            <div className="mt-3">
              <HexViewer value={QY} label="公钥 Qy (40 hex)" maxLines={1} />
            </div>
            {keyInfo?.key_id && (
              <div className="mt-3 text-xs text-[var(--cl-text-secondary)] font-mono break-all">
                key_id · {keyInfo.key_id}
              </div>
            )}
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
                <TextInput value={rHex} onChange={(e) => setRHex(e.target.value)} className="font-mono" />
              </Field>
              <Field label="s (hex)">
                <TextInput value={sHex} onChange={(e) => setSHex(e.target.value)} className="font-mono" />
              </Field>
            </>
          )}
          {error && (
            <div className="mb-3 px-3 py-2 rounded-md bg-[#FEF0F0] border border-[#FBC4C4] text-xs text-[#C45656] cl-shake">
              {error}
            </div>
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
                <Tag tone="neutral">curve {keyInfo?.curve || "secp160r1"}</Tag>
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
