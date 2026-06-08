import { useEffect, useState } from "react";
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
import { PageHeader } from "@/components/shared/PageHeader";
import { CryptoCard } from "@/components/shared/CryptoCard";
import { StatusBanner } from "@/components/shared/StatusBanner";
import { Field, TextArea, PrimaryButton, GhostButton, Tag } from "@/components/shared/Field";
import { CopyButton } from "@/components/shared/CopyButton";
import { ROUTE_TITLES } from "@/components/nav";
import { secureFileSend, secureFileReceive } from "@/api/scenarios";
import { listKeys } from "@/api/keys";

const STEPS = [
  { key: "pub", icon: KeyRound, label: "获取接收方 RSA 公钥", detail: "RSA-1024", timingKey: "fetch_pubkey_ms" },
  { key: "gen", icon: Lock, label: "生成随机 AES-256 会话密钥", detail: "256-bit", timingKey: "session_key_gen_ms" },
  { key: "wrap", icon: KeyRound, label: "RSA 加密会话密钥", detail: "RSA-OAEP", timingKey: "rsa_wrap_ms" },
  { key: "enc", icon: Lock, label: "AES-GCM 加密文件", detail: "AEAD", timingKey: "aes_encrypt_ms" },
  { key: "hash", icon: Hash, label: "计算文件 SHA-256 摘要", detail: "256-bit", timingKey: "sha256_ms" },
  { key: "sign", icon: FileSignature, label: "ECDSA 对摘要签名", detail: "secp160r1", timingKey: "ecdsa_sign_ms" },
  { key: "pack", icon: Package, label: "打包安全信封", detail: "JSON", timingKey: "pack_ms" },
] as const;

const RECEIVE_STEPS = [
  { key: "verify_sig", icon: FileSignature, label: "ECDSA 验签", detail: "secp160r1", timingKey: "ecdsa_verify_ms" },
  { key: "verify_hash", icon: Hash, label: "SHA-256 摘要匹配", detail: "256-bit", timingKey: "sha256_ms" },
  { key: "unwrap", icon: KeyRound, label: "RSA 解封会话密钥", detail: "RSA-OAEP", timingKey: "rsa_unwrap_ms" },
  { key: "decrypt", icon: Lock, label: "AES-GCM 解密文件", detail: "AEAD", timingKey: "aes_decrypt_ms" },
] as const;

const DEFAULT_ENVELOPE = `{
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

interface SendResult {
  envelope: any;
  envelopeJson: string;
  step_timings?: Record<string, number>;
}

interface ReceiveResult {
  verified: boolean;
  decrypted_file_base64?: string;
  decrypted_text?: string;
  step_timings?: Record<string, number>;
}

interface ScenarioKeyIds {
  rsaPublicId?: string;
  rsaPrivateId?: string;
  eccPublicId?: string;
  eccPrivateId?: string;
}

function toBase64(text: string): string {
  try {
    const bytes = new TextEncoder().encode(text);
    let binary = "";
    bytes.forEach((b) => (binary += String.fromCharCode(b)));
    return btoa(binary);
  } catch {
    return btoa(text);
  }
}

function fromBase64(b64: string): string {
  try {
    const binary = atob(b64);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return new TextDecoder().decode(bytes);
  } catch {
    return b64;
  }
}

export function ScenariosView() {
  const meta = ROUTE_TITLES.scenarios;
  const [mode, setMode] = useState<"send" | "receive">("send");
  const [plaintext, setPlaintext] = useState("机密文件内容 — 仅授权接收方可读。");
  const [envelopeInput, setEnvelopeInput] = useState(DEFAULT_ENVELOPE);
  const [running, setRunning] = useState(false);
  const [currentStep, setCurrentStep] = useState(-1);
  const [error, setError] = useState<string | null>(null);
  const [sendResult, setSendResult] = useState<SendResult | null>(null);
  const [receiveResult, setReceiveResult] = useState<ReceiveResult | null>(null);
  const [keyIds, setKeyIds] = useState<ScenarioKeyIds>({});

  const activeSteps = mode === "send" ? STEPS : RECEIVE_STEPS;
  const done = mode === "send" ? !!sendResult : !!receiveResult;

  const resetState = () => {
    setSendResult(null);
    setReceiveResult(null);
    setCurrentStep(-1);
    setError(null);
  };

  useEffect(() => {
    const loadScenarioKeys = async () => {
      try {
        const resp = await listKeys();
        if (resp.code !== 1000 || !Array.isArray(resp.data)) return;
        const rows = resp.data as any[];
        const findKey = (algorithm: string, type: string) =>
          rows.find(
            (k) =>
              String(k.algorithm || "").toLowerCase() === algorithm &&
              String(k.key_type ?? k.type ?? "").toLowerCase() === type,
          )?.key_id;
        setKeyIds({
          rsaPublicId: findKey("rsa", "public"),
          rsaPrivateId: findKey("rsa", "private"),
          eccPublicId: findKey("ecc", "public"),
          eccPrivateId: findKey("ecc", "private"),
        });
      } catch {
        /* scenario can still report a missing-key error when executed */
      }
    };
    loadScenarioKeys();
  }, []);

  const animateSteps = async (count: number) => {
    for (let i = 0; i < count; i++) {
      setCurrentStep(i);
      // Small visual delay between step highlights so the user sees the flow.
      await new Promise((r) => setTimeout(r, 180));
    }
  };

  const runSend = async () => {
    if (!keyIds.rsaPublicId || !keyIds.eccPrivateId) {
      setError("请先在 RSA 页面生成密钥对,并在 ECC 页面生成密钥对。发送需要 RSA 公钥和 ECC 私钥。");
      return;
    }
    try {
      setRunning(true);
      resetState();
      const animation = animateSteps(STEPS.length);
      const resp = await secureFileSend({
        file_b64: toBase64(plaintext),
        receiver_rsa_public_key_id: keyIds.rsaPublicId,
        sender_ecdsa_private_key_id: keyIds.eccPrivateId,
        sender_ecdsa_curve: "secp160r1",
      });
      await animation;
      if (resp.code === 1000) {
        const data = resp.data as any;
        const envelope = data?.envelope ?? data;
        setSendResult({
          envelope,
          envelopeJson: JSON.stringify(envelope, null, 2),
          step_timings: {
            pack_ms: data?.sender_summary?.duration_ms ?? 0,
          },
        });
      } else {
        setError(resp.message || "操作失败");
      }
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || "网络错误");
    } finally {
      setRunning(false);
    }
  };

  const runReceive = async () => {
    if (!keyIds.rsaPrivateId || !keyIds.eccPublicId) {
      setError("请先在 RSA 页面生成密钥对,并在 ECC 页面生成密钥对。接收需要 RSA 私钥和 ECC 公钥。");
      return;
    }
    try {
      setRunning(true);
      resetState();
      let envelope: any;
      try {
        envelope = JSON.parse(envelopeInput);
      } catch {
        setError("信封 JSON 解析失败,请检查格式。");
        setRunning(false);
        return;
      }
      const animation = animateSteps(RECEIVE_STEPS.length);
      const resp = await secureFileReceive({
        envelope,
        receiver_rsa_private_key_id: keyIds.rsaPrivateId,
        sender_ecdsa_public_key_id: keyIds.eccPublicId,
      });
      await animation;
      if (resp.code === 1000) {
        const data = resp.data as any;
        const plaintextB64 = data?.plaintext_b64;
        const verification = data?.verification ?? {};
        const verified =
          Object.keys(verification).length > 0 && Object.values(verification).every(Boolean);
        const decrypted =
          typeof plaintextB64 === "string"
            ? fromBase64(plaintextB64)
            : undefined;
        setReceiveResult({
          verified,
          decrypted_file_base64: plaintextB64,
          decrypted_text: decrypted,
          step_timings: {
            aes_decrypt_ms: data?.duration_ms ?? 0,
          },
        });
      } else {
        setError(resp.message || "验证或解密失败");
      }
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || "网络错误");
    } finally {
      setRunning(false);
    }
  };

  const run = () => (mode === "send" ? runSend() : runReceive());

  const timings = mode === "send" ? sendResult?.step_timings : receiveResult?.step_timings;

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
                resetState();
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

      {error && (
        <div className="mb-5">
          <StatusBanner type="danger" title="执行失败" message={error} />
        </div>
      )}

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
                  <Tag tone="neutral">
                    接收方 KeyID {keyIds.rsaPublicId ? `${keyIds.rsaPublicId.slice(0, 8)}…` : "未就绪"}
                  </Tag>
                </div>
                <PrimaryButton onClick={run} loading={running} disabled={!plaintext}>
                  <Send size={14} /> 加密并打包安全信封
                </PrimaryButton>
              </>
            ) : (
              <>
                <Field label="安全信封 JSON">
                  <TextArea
                    value={envelopeInput}
                    onChange={(e) => setEnvelopeInput(e.target.value)}
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
            subtitle={
              mode === "send"
                ? "RSA-KEM + AES-GCM-DEM + ECDSA 签名"
                : "ECDSA 验签 → RSA 解封会话密钥 → AES-GCM 解密"
            }
            icon={<Lock size={14} />}
          >
            <FlowDiagram
              steps={activeSteps as unknown as ReadonlyArray<(typeof STEPS)[number]>}
              currentStep={currentStep}
              timings={timings}
              done={done}
            />
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
                  正在执行步骤 {Math.max(currentStep + 1, 1)} / {activeSteps.length}…
                </div>
              </div>
            )}
            {done && mode === "send" && sendResult && (
              <div className="space-y-3 cl-fade-up">
                <div className="flex items-center justify-between">
                  <span className="text-xs text-[var(--cl-text-secondary)]">envelope.json</span>
                  <CopyButton text={sendResult.envelopeJson} />
                </div>
                <pre className="font-mono text-[11px] p-3 rounded bg-[var(--cl-bg-code)] leading-relaxed max-h-[420px] overflow-auto whitespace-pre-wrap break-all">
                  {sendResult.envelopeJson}
                </pre>
                <div className="flex flex-wrap gap-1.5">
                  <Tag tone="success">机密性 ✓</Tag>
                  <Tag tone="success">完整性 ✓</Tag>
                  <Tag tone="success">不可否认性 ✓</Tag>
                </div>
              </div>
            )}
            {done && mode === "receive" && receiveResult && (
              <div className="space-y-3 cl-fade-up">
                <div className="space-y-2">
                  {[
                    ["ECDSA 签名验证", receiveResult.verified],
                    ["SHA-256 摘要匹配", receiveResult.verified],
                    ["RSA 解封会话密钥", receiveResult.verified],
                    ["AES-GCM 认证标签验证", receiveResult.verified],
                  ].map(([label, ok]) => (
                    <div
                      key={label as string}
                      className="flex items-center justify-between px-3 py-2 rounded bg-[var(--cl-bg-page)]/60 text-sm"
                    >
                      <span>{label as string}</span>
                      <span
                        className={`inline-flex items-center gap-1 ${
                          ok ? "text-[var(--cl-success)]" : "text-[var(--cl-danger)]"
                        }`}
                      >
                        <CheckCircle2 size={14} /> {ok ? "通过" : "失败"}
                      </span>
                    </div>
                  ))}
                </div>
                <Field label="明文输出">
                  <div className="px-3 py-2.5 rounded bg-[var(--cl-bg-code)] font-mono text-xs whitespace-pre-wrap break-all">
                    {receiveResult.decrypted_text ?? "(无解密结果)"}
                  </div>
                </Field>
              </div>
            )}
          </CryptoCard>

          {done && (
            <CryptoCard title="操作" bodyClassName="py-3">
              <div className="flex flex-col gap-2">
                {mode === "send" && sendResult && (
                  <GhostButton
                    onClick={() => {
                      const blob = new Blob([sendResult.envelopeJson], {
                        type: "application/json",
                      });
                      const url = URL.createObjectURL(blob);
                      const a = document.createElement("a");
                      a.href = url;
                      a.download = "envelope.json";
                      a.click();
                      URL.revokeObjectURL(url);
                    }}
                  >
                    <Download size={14} /> 下载 envelope.json
                  </GhostButton>
                )}
                <GhostButton onClick={resetState}>
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

function FlowDiagram({
  steps,
  currentStep,
  timings,
  done,
}: {
  steps: ReadonlyArray<{ key: string; icon: any; label: string; detail: string; timingKey: string }>;
  currentStep: number;
  timings?: Record<string, number>;
  done: boolean;
}) {
  return (
    <ol className="space-y-2">
      {steps.map((s, i) => {
        const Icon = s.icon;
        const active = i === currentStep;
        const isDone = done || i < currentStep;
        const timing = timings?.[s.timingKey];
        return (
          <li
            key={s.key}
            className={`flex items-center gap-3 px-3 py-2.5 rounded-md border transition-all duration-300 ${
              active
                ? "border-[var(--cl-primary)] bg-[var(--cl-primary-light)]/60 cl-scale-pop"
                : isDone
                ? "border-[var(--cl-border-light)] bg-white"
                : "border-[var(--cl-border-light)] bg-[var(--cl-bg-page)]/30 opacity-60"
            }`}
          >
            <div
              className={`w-7 h-7 rounded-full inline-flex items-center justify-center text-xs flex-shrink-0 ${
                isDone
                  ? "bg-[var(--cl-success)] text-white"
                  : active
                  ? "bg-[var(--cl-primary)] text-white"
                  : "bg-[var(--cl-bg-page)] text-[var(--cl-text-secondary)]"
              }`}
            >
              {isDone ? <CheckCircle2 size={14} /> : i + 1}
            </div>
            <Icon
              size={14}
              className={
                active || isDone
                  ? "text-[var(--cl-primary)]"
                  : "text-[var(--cl-text-placeholder)]"
              }
            />
            <div className="flex-1 min-w-0">
              <div className="text-sm">{s.label}</div>
              {typeof timing === "number" && (
                <div className="text-[11px] text-[var(--cl-text-secondary)] font-mono tabular-nums">
                  {timing.toFixed(2)} ms
                </div>
              )}
            </div>
            <Tag tone={active ? "primary" : isDone ? "success" : "neutral"}>{s.detail}</Tag>
          </li>
        );
      })}
    </ol>
  );
}
