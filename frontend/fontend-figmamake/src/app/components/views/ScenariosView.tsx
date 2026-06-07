import { useState } from "react";
import {
  Send,
  Upload,
  Download,
  KeyRound,
  Lock,
  Hash,
  FileSignature,
  CheckCircle2,
  Package,
  ShieldCheck,
  ArrowRight,
} from "lucide-react";
import { PageHeader } from "../shared/PageHeader";
import { CryptoCard } from "../shared/CryptoCard";
import { Field, TextArea, PrimaryButton, GhostButton, Tag } from "../shared/Field";
import { HexViewer } from "../shared/HexViewer";
import { CopyButton } from "../shared/CopyButton";
import { ROUTE_TITLES } from "../nav";

const STEPS = [
  { key: "pub", icon: KeyRound, label: "获取接收方 RSA 公钥", detail: "RSA-1024" },
  { key: "gen", icon: Lock, label: "生成随机 AES-256 会话密钥", detail: "256-bit" },
  { key: "wrap", icon: KeyRound, label: "RSA 加密会话密钥", detail: "RSA-OAEP" },
  { key: "enc", icon: Lock, label: "AES-GCM 加密文件", detail: "AEAD" },
  { key: "hash", icon: Hash, label: "计算文件 SHA-256 摘要", detail: "256-bit" },
  { key: "sign", icon: FileSignature, label: "ECDSA 对摘要签名", detail: "secp160r1" },
  { key: "pack", icon: Package, label: "打包安全信封", detail: "JSON" },
];

const ENVELOPE = `{
  "version": 1,
  "alg": {
    "kem": "RSA-OAEP-SHA256",
    "dem": "AES-256-GCM",
    "sig": "ECDSA-secp160r1-SHA256"
  },
  "recipient_kid": "c8f26274-5bfe-3caf-ad98-64e9b3087f2b",
  "sender_kid":    "ea048496-7d0f-5ec0-cf1a-86fbc52a9f4d",
  "wrapped_key":   "9f3a...c41e",
  "iv":            "5b8c2e1a7f3d9b4c6e0a1d8f",
  "ciphertext":    "a1b2c3d4e5f6...8f9a0b1c2d3e",
  "tag":           "4f7a9c2e1b8d5a3f6c0e9d2b",
  "digest":        "9b74c9897bac770ffc029ffd720d2b6b0a5f5e15e21ad45fde6a78ac7e51e2f3",
  "signature":     { "r": "0a1b2c3d...8a9b", "s": "5e6f7a8b...3e4f" },
  "issued_at":     "2026-06-07T14:30:00Z"
}`;

export function ScenariosView() {
  const meta = ROUTE_TITLES.scenarios;
  const [mode, setMode] = useState<"send" | "receive">("send");
  const [plaintext, setPlaintext] = useState("机密文件内容 — 仅授权接收方可读。");
  const [running, setRunning] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [done, setDone] = useState(false);

  const run = () => {
    setRunning(true);
    setDone(false);
    setCurrentStep(-1);
    STEPS.forEach((_, i) => {
      setTimeout(() => {
        setCurrentStep(i);
        if (i === STEPS.length - 1) {
          setTimeout(() => {
            setRunning(false);
            setDone(true);
          }, 400);
        }
      }, 400 + i * 350);
    });
  };

  return (
    <>
      <PageHeader title={meta.title} subtitle={meta.subtitle} breadcrumb={meta.breadcrumb} />

      <CryptoCard className="mb-5" bodyClassName="py-3">
        <div className="flex items-center gap-2">
          {(["send", "receive"] as const).map((m) => (
            <button
              key={m}
              onClick={() => {
                setMode(m);
                setDone(false);
                setCurrentStep(-1);
              }}
              className={`px-4 h-9 rounded-md text-sm border transition-all inline-flex items-center gap-2 ${
                mode === m
                  ? "border-[var(--cl-primary)] bg-[var(--cl-primary-light)] text-[var(--cl-primary-dark)]"
                  : "border-[var(--cl-border)] text-[var(--cl-text-regular)] hover:border-[var(--cl-primary)]/50"
              }`}
            >
              {m === "send" ? <Upload size={14} /> : <Download size={14} />}
              {m === "send" ? "发送方" : "接收方"}
            </button>
          ))}
          <span className="ml-auto text-xs text-[var(--cl-text-secondary)]">
            混合密码学 · 端到端机密性 · 完整性 · 不可否认性
          </span>
        </div>
      </CryptoCard>

      <div className="grid grid-cols-1 xl:grid-cols-[1fr_460px] gap-5">
        <div className="space-y-5">
          <CryptoCard
            title={mode === "send" ? "1. 选择文件 / 输入内容" : "1. 粘贴安全信封"}
            icon={mode === "send" ? <Upload size={14} /> : <Download size={14} />}
          >
            {mode === "send" ? (
              <>
                <Field label="待加密内容" hint="生产环境下将是文件二进制流。这里以文本演示。">
                  <TextArea
                    value={plaintext}
                    onChange={(e) => setPlaintext(e.target.value)}
                    rows={5}
                    className="!font-sans"
                  />
                </Field>
                <div className="flex items-center gap-2 text-xs text-[var(--cl-text-secondary)] mb-4">
                  <Tag tone="info">{new Blob([plaintext]).size} 字节</Tag>
                  <Tag tone="neutral">接收方 KeyID c8f26274-…</Tag>
                </div>
                <PrimaryButton onClick={run} loading={running} disabled={!plaintext}>
                  <Send size={14} /> 加密并打包安全信封
                </PrimaryButton>
              </>
            ) : (
              <>
                <Field label="安全信封 JSON">
                  <TextArea
                    defaultValue={ENVELOPE}
                    rows={10}
                    className="font-mono text-[11.5px] leading-relaxed"
                  />
                </Field>
                <PrimaryButton onClick={run} loading={running}>
                  <ShieldCheck size={14} /> 验证并解密
                </PrimaryButton>
              </>
            )}
          </CryptoCard>

          <CryptoCard
            title={mode === "send" ? "2. 加密协议流程" : "2. 验证协议流程"}
            subtitle={mode === "send" ? "RSA-KEM + AES-GCM-DEM + ECDSA 签名" : "ECDSA 验签 → RSA 解封会话密钥 → AES-GCM 解密"}
            icon={<Lock size={14} />}
          >
            <FlowDiagram currentStep={currentStep} mode={mode} />
          </CryptoCard>
        </div>

        {/* Right panel - envelope output */}
        <div className="space-y-5">
          <CryptoCard
            title={mode === "send" ? "3. 输出安全信封" : "3. 解密结果"}
            icon={<Package size={14} />}
            extra={done && <Tag tone="success">完成</Tag>}
          >
            {!done && !running && (
              <div className="text-sm text-[var(--cl-text-placeholder)] py-12 text-center">
                {mode === "send" ? "执行后将在此显示信封" : "执行后将在此显示明文"}
              </div>
            )}
            {running && (
              <div className="flex items-center justify-center py-12">
                <div className="text-xs text-[var(--cl-text-secondary)] inline-flex items-center gap-2">
                  <span className="w-2 h-2 rounded-full bg-[var(--cl-primary)] cl-pulse" />
                  正在执行步骤 {Math.max(currentStep + 1, 1)} / {STEPS.length}…
                </div>
              </div>
            )}
            {done && mode === "send" && (
              <div className="space-y-3 cl-fade-up">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-[var(--cl-text-secondary)]">envelope.json</span>
                  <CopyButton value={ENVELOPE} />
                </div>
                <pre className="font-mono text-[11px] p-3 rounded bg-[var(--cl-bg-code)] leading-relaxed max-h-[420px] overflow-auto whitespace-pre-wrap break-all">
                  {ENVELOPE}
                </pre>
                <div className="flex flex-wrap gap-1.5">
                  <Tag tone="success">机密性 ✓</Tag>
                  <Tag tone="success">完整性 ✓</Tag>
                  <Tag tone="success">不可否认性 ✓</Tag>
                </div>
              </div>
            )}
            {done && mode === "receive" && (
              <div className="space-y-3 cl-fade-up">
                <div className="space-y-2">
                  {[
                    ["ECDSA 签名验证", true],
                    ["SHA-256 摘要匹配", true],
                    ["RSA 解封会话密钥", true],
                    ["AES-GCM 认证标签验证", true],
                  ].map(([label, ok]) => (
                    <div
                      key={label as string}
                      className="flex items-center justify-between px-3 py-2 rounded bg-[var(--cl-bg-page)]/60 text-sm"
                    >
                      <span>{label as string}</span>
                      <span className="inline-flex items-center gap-1 text-[var(--cl-success)]">
                        <CheckCircle2 size={14} /> 通过
                      </span>
                    </div>
                  ))}
                </div>
                <Field label="明文输出">
                  <div className="px-3 py-2.5 rounded bg-[var(--cl-bg-code)] font-mono text-xs whitespace-pre-wrap break-all">
                    机密文件内容 — 仅授权接收方可读。
                  </div>
                </Field>
              </div>
            )}
          </CryptoCard>

          {done && (
            <CryptoCard title="操作" bodyClassName="py-3">
              <div className="flex flex-col gap-2">
                <GhostButton>
                  <Download size={14} /> 下载 envelope.json
                </GhostButton>
                <GhostButton onClick={() => { setDone(false); setCurrentStep(-1); }}>
                  <ArrowRight size={14} /> 再次执行
                </GhostButton>
              </div>
            </CryptoCard>
          )}
        </div>
      </div>
    </>
  );
}

function FlowDiagram({ currentStep, mode }: { currentStep: number; mode: "send" | "receive" }) {
  const steps = mode === "send" ? STEPS : [...STEPS].reverse();
  return (
    <ol className="space-y-2">
      {steps.map((s, i) => {
        const Icon = s.icon;
        const active = i === currentStep;
        const done = i < currentStep;
        return (
          <li
            key={s.key}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-md border transition-all duration-300 ${
              active
                ? "border-[var(--cl-primary)] bg-[var(--cl-primary-light)]/60 cl-scale-pop"
                : done
                ? "border-[var(--cl-border-light)] bg-white"
                : "border-[var(--cl-border-light)] bg-[var(--cl-bg-page)]/30 opacity-60"
            }`}
          >
            <div
              className={`w-7 h-7 rounded-full inline-flex items-center justify-center text-xs flex-shrink-0 ${
                done
                  ? "bg-[var(--cl-success)] text-white"
                  : active
                  ? "bg-[var(--cl-primary)] text-white"
                  : "bg-[var(--cl-bg-page)] text-[var(--cl-text-secondary)]"
              }`}
            >
              {done ? <CheckCircle2 size={14} /> : i + 1}
            </div>
            <Icon
              size={14}
              className={
                active || done
                  ? "text-[var(--cl-primary)]"
                  : "text-[var(--cl-text-placeholder)]"
              }
            />
            <div className="flex-1 min-w-0">
              <div className="text-sm">{s.label}</div>
            </div>
            <Tag tone={active ? "primary" : done ? "success" : "neutral"}>{s.detail}</Tag>
          </li>
        );
      })}
    </ol>
  );
}
