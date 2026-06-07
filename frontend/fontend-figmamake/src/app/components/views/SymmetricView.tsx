import { useState } from "react";
import { Lock, Unlock, KeyRound, Dice5, Sparkles, ArrowLeftRight } from "lucide-react";
import { PageHeader } from "../shared/PageHeader";
import { CryptoCard } from "../shared/CryptoCard";
import { Field, TextInput, TextArea, Select, PrimaryButton, GhostButton, Tag } from "../shared/Field";
import { HexViewer } from "../shared/HexViewer";
import { OperationTimer } from "../shared/OperationTimer";
import { EmptyState } from "../shared/EmptyState";
import { ROUTE_TITLES } from "../nav";

const ALGS = [
  { value: "aes", label: "AES" },
  { value: "sm4", label: "SM4" },
  { value: "rc6", label: "RC6" },
];
const MODES = ["ECB", "CBC", "CTR", "GCM"].map((m) => ({ value: m, label: m }));
const PADS = ["PKCS7", "ZeroPadding", "None"].map((p) => ({ value: p, label: p }));

const SAMPLE_CIPHER = "kL3RfXpXMJvG7Y6qHzU8D9RNH5I6DJKzATKweA==";
const SAMPLE_HEX = "90bdd17d7a57309bc6ed8eaa1f353c0fd44d1f923a0c92b3013297";

export function SymmetricView() {
  const meta = ROUTE_TITLES.symmetric;
  const [mode, setMode] = useState("GCM");
  const [alg, setAlg] = useState("aes");
  const [pad, setPad] = useState("PKCS7");
  const [dir, setDir] = useState<"encrypt" | "decrypt">("encrypt");
  const [keyId] = useState("b7e15163-4aed-2b9e-9c87-53d8a2f77e1a");
  const [iv, setIv] = useState("000102030405060708090a0b");
  const [aad, setAad] = useState("");
  const [text, setText] = useState("Hello, World!");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ b64: string; hex: string; ms: number } | null>(null);

  const run = () => {
    setLoading(true);
    setResult(null);
    setTimeout(() => {
      setLoading(false);
      setResult({
        b64: SAMPLE_CIPHER,
        hex: SAMPLE_HEX,
        ms: 0.42 + Math.random() * 0.6,
      });
    }, 700);
  };

  const randomIv = () => {
    const r = Array.from({ length: 12 }, () =>
      Math.floor(Math.random() * 256).toString(16).padStart(2, "0")
    ).join("");
    setIv(r);
  };

  return (
    <>
      <PageHeader title={meta.title} subtitle={meta.subtitle} breadcrumb={meta.breadcrumb} />

      {/* Toolbar */}
      <CryptoCard className="mb-5" bodyClassName="py-3.5">
        <div className="flex items-center gap-3 flex-wrap">
          <div className="flex items-center gap-2">
            <span className="text-xs text-[var(--cl-text-secondary)]">算法</span>
            <Select value={alg} onChange={setAlg} options={ALGS} />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-[var(--cl-text-secondary)]">模式</span>
            <Select value={mode} onChange={setMode} options={MODES} />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-[var(--cl-text-secondary)]">填充</span>
            <Select value={pad} onChange={setPad} options={PADS} />
          </div>
          <div className="ml-auto flex items-center bg-[var(--cl-bg-page)] rounded-md p-0.5">
            {(["encrypt", "decrypt"] as const).map((d) => (
              <button
                key={d}
                onClick={() => setDir(d)}
                className={`px-3 py-1.5 rounded text-xs inline-flex items-center gap-1.5 transition-all ${
                  dir === d
                    ? "bg-white shadow-sm text-[var(--cl-primary-dark)]"
                    : "text-[var(--cl-text-secondary)]"
                }`}
              >
                {d === "encrypt" ? <Lock size={12} /> : <Unlock size={12} />}
                {d === "encrypt" ? "加密" : "解密"}
              </button>
            ))}
          </div>
        </div>
      </CryptoCard>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
        {/* Input */}
        <CryptoCard
          title={dir === "encrypt" ? "输入明文" : "输入密文"}
          subtitle={`${alg.toUpperCase()}-${mode} · ${pad}`}
          icon={<Lock size={14} />}
        >
          <Field
            label="密钥(从密钥库选择)"
            hint={
              <span className="inline-flex items-center gap-1">
                <KeyRound size={10} /> 已选密钥
              </span>
            }
          >
            <div className="flex gap-2">
              <TextInput value={keyId} readOnly className="font-mono text-xs" />
              <GhostButton>
                <Sparkles size={14} />
                生成新密钥
              </GhostButton>
            </div>
          </Field>

          <Field
            label="初始向量 IV (hex)"
            hint={`${mode === "GCM" ? "GCM 推荐 12 字节" : "CBC/CTR 推荐 16 字节"}`}
          >
            <div className="flex gap-2">
              <TextInput
                value={iv}
                onChange={(e) => setIv(e.target.value)}
                className="font-mono"
                placeholder="00 01 02 …"
              />
              <GhostButton onClick={randomIv}>
                <Dice5 size={14} />
                随机
              </GhostButton>
            </div>
          </Field>

          {mode === "GCM" && (
            <Field label="附加认证数据 AAD (可选 Base64)">
              <TextInput
                value={aad}
                onChange={(e) => setAad(e.target.value)}
                placeholder="留空即不使用 AAD"
                className="font-mono"
              />
            </Field>
          )}

          <Field
            label={dir === "encrypt" ? "明文" : "密文 (Base64)"}
            hint={dir === "encrypt" ? "提交时自动转 Base64" : undefined}
          >
            <TextArea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={5}
              placeholder={dir === "encrypt" ? "输入要加密的文本…" : "粘贴 Base64 密文…"}
            />
          </Field>

          <div className="flex items-center gap-2 mt-1">
            <PrimaryButton onClick={run} loading={loading}>
              {dir === "encrypt" ? <Lock size={14} /> : <Unlock size={14} />}
              {dir === "encrypt" ? "执行加密" : "执行解密"}
            </PrimaryButton>
            <GhostButton onClick={() => setResult(null)}>
              <ArrowLeftRight size={14} />
              清空结果
            </GhostButton>
          </div>
        </CryptoCard>

        {/* Output */}
        <CryptoCard
          title="运算结果"
          subtitle={result ? `${alg.toUpperCase()}-${mode} · ${pad}` : "尚未执行任何运算"}
          icon={<Sparkles size={14} />}
          extra={result && <OperationTimer durationMs={result.ms} operation={`${dir === "encrypt" ? "加密" : "解密"}`} />}
        >
          {loading ? (
            <div className="space-y-3">
              <div className="h-3 rounded bg-[var(--cl-bg-page)] overflow-hidden relative">
                <div className="cl-marquee-bar absolute inset-y-0 w-1/3 bg-[var(--cl-primary)]/30" />
              </div>
              <div className="h-24 rounded bg-[var(--cl-bg-page)]/70 animate-pulse" />
              <div className="h-16 rounded bg-[var(--cl-bg-page)]/70 animate-pulse" />
              <div className="text-xs text-[var(--cl-text-secondary)] text-center">
                正在执行 {alg.toUpperCase()}-{mode} {dir === "encrypt" ? "加密" : "解密"}…
              </div>
            </div>
          ) : result ? (
            <div className="space-y-4">
              <HexViewer value={result.b64} label="密文 (Base64)" variant="base64" />
              <HexViewer value={result.hex} label="密文 (Hex 视图)" variant="hex" maxLines={3} />
              <div className="flex items-center gap-2 flex-wrap pt-1">
                <Tag tone="success">运算成功</Tag>
                <Tag tone="info">算法 {alg.toUpperCase()}-{mode}</Tag>
                <Tag tone="neutral">填充 {pad}</Tag>
                <Tag tone="neutral">IV {iv.length / 2} 字节</Tag>
              </div>
            </div>
          ) : (
            <EmptyState
              icon={<Lock size={22} />}
              title="选择密钥并填写参数后执行运算"
              description="输入明文或密文后,点击左侧按钮即可看到运算结果与耗时信息。"
            />
          )}
        </CryptoCard>
      </div>

      {/* Mode comparison teaser */}
      <CryptoCard
        className="mt-5"
        title="模式对比 · ECB 模式弱点演示"
        subtitle="同一明文在不同分组模式下的密文表现,用于直观理解 ECB 的明文模式泄露问题。"
        icon={<ArrowLeftRight size={14} />}
      >
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {["ECB", "CBC", "CTR", "GCM"].map((m) => (
            <div
              key={m}
              className={`rounded-md p-3 border ${
                m === "ECB"
                  ? "bg-[#FEF0F0]/60 border-[#FBC4C4]"
                  : "bg-[var(--cl-bg-code)] border-[var(--cl-border-light)]"
              }`}
            >
              <div className="flex items-center justify-between mb-2">
                <span className="text-xs">{m}</span>
                {m === "ECB" && <Tag tone="danger">⚠ 泄露</Tag>}
              </div>
              <div className="font-mono text-[10.5px] text-[var(--cl-text-regular)] break-all leading-relaxed">
                {m === "ECB"
                  ? "a3f9 a3f9 a3f9 a3f9\n7e2c 7e2c 7e2c 7e2c"
                  : "kL3R fXpX MJvG 7Y6q\nHzU8 D9RN H5I6 DJKz"}
              </div>
            </div>
          ))}
        </div>
      </CryptoCard>
    </>
  );
}
