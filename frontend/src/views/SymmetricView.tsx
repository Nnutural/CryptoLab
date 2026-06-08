import { useEffect, useState } from "react";
import { BookOpen, Lock, Unlock, KeyRound, Dice5, Sparkles, ArrowLeftRight } from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { CryptoCard } from "@/components/shared/CryptoCard";
import { Field, TextInput, TextArea, Select, PrimaryButton, GhostButton, Tag } from "@/components/shared/Field";
import { HexViewer } from "@/components/shared/HexViewer";
import { OperationTimer } from "@/components/shared/OperationTimer";
import { EmptyState } from "@/components/shared/EmptyState";
import { ROUTE_TITLES } from "@/components/nav";
import { symmetricEncrypt, symmetricDecrypt, symmetricKeygen, type AesTrace } from "@/api/symmetric";
import { listKeys } from "@/api/keys";
import { AesTraceViewer } from "@/components/shared/AesTraceViewer";

const ALGS = [
  { value: "aes", label: "AES" },
  { value: "sm4", label: "SM4" },
  { value: "rc6", label: "RC6" },
];
const MODES = ["ECB", "CBC", "CTR", "GCM"].map((m) => ({ value: m, label: m }));
const PADS = [
  { value: "PKCS7", label: "PKCS7" },
  { value: "Zero", label: "ZeroPadding" },
  { value: "None", label: "None" },
];
const DEFAULT_IV_12 = "000102030405060708090a0b";
const DEFAULT_IV_16 = "000102030405060708090a0b0c0d0e0f";

// AES allows 128/192/256, SM4 fixed 128, RC6 typically 128/256
const KEY_SIZE_OPTIONS: Record<string, { value: string; label: string }[]> = {
  aes: [
    { value: "16", label: "AES-128" },
    { value: "24", label: "AES-192" },
    { value: "32", label: "AES-256" },
  ],
  sm4: [{ value: "16", label: "SM4-128" }],
  rc6: [{ value: "16", label: "RC6-128" }],
};

interface KeyEntry {
  key_id: string;
  algorithm: string;
  key_size?: number;
  label?: string;
  created_at?: string;
  status?: string;
}

function utf8ToBase64(value: string): string {
  const bytes = new TextEncoder().encode(value);
  let binary = "";
  bytes.forEach((b) => {
    binary += String.fromCharCode(b);
  });
  return btoa(binary);
}

function base64ToUtf8(value: string): string {
  try {
    const binary = atob(value);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return new TextDecoder().decode(bytes);
  } catch {
    return value;
  }
}

function base64ToHex(value: string): string {
  try {
    const binary = atob(value);
    let hex = "";
    for (let i = 0; i < binary.length; i++) {
      hex += binary.charCodeAt(i).toString(16).padStart(2, "0");
    }
    return hex;
  } catch {
    return "";
  }
}

function hexToBase64(value: string): string {
  const clean = value.replace(/\s+/g, "");
  const bytes = clean.match(/.{1,2}/g) || [];
  let binary = "";
  bytes.forEach((h) => {
    binary += String.fromCharCode(parseInt(h, 16));
  });
  return btoa(binary);
}

export function SymmetricView() {
  const meta = ROUTE_TITLES.symmetric;
  const [mode, setMode] = useState("GCM");
  const [alg, setAlg] = useState("aes");
  const [keySize, setKeySize] = useState("32");
  const [pad, setPad] = useState("PKCS7");
  const [dir, setDir] = useState<"encrypt" | "decrypt">("encrypt");
  const [keys, setKeys] = useState<KeyEntry[]>([]);
  const [keyId, setKeyId] = useState<string>("");
  const [iv, setIv] = useState(DEFAULT_IV_12);
  const [aad, setAad] = useState("");
  const [text, setText] = useState("Hello, World!");
  const [verbose, setVerbose] = useState(false);
  const [loading, setLoading] = useState(false);
  const [keygenLoading, setKeygenLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<
    | {
        b64: string;
        hex: string;
        ms: number;
        tagHex?: string;
        ivHex?: string;
        plaintext?: string;
        trace?: AesTrace | null;
      }
    | null
  >(null);

  const verboseAvailable = alg === "aes" && mode === "ECB" && dir === "encrypt";
  const plaintextByteLength = new TextEncoder().encode(text).length;
  const verboseBlockReady = plaintextByteLength === 16;

  // Load key list on mount and after keygen
  const loadKeys = async () => {
    try {
      const resp = await listKeys();
      if (resp.code === 1000) {
        const arr = (resp.data ?? []) as KeyEntry[];
        // Only symmetric algorithms relevant to this view
        const symKeys = arr.filter((k) => {
          const a = (k.algorithm || "").toLowerCase();
          return a === "aes" || a === "sm4" || a === "rc6";
        });
        setKeys(symKeys);
      }
    } catch {
      /* silent — selector will show empty */
    }
  };

  useEffect(() => {
    loadKeys();
  }, []);

  useEffect(() => {
    if (!verboseAvailable) {
      setVerbose(false);
    }
  }, [verboseAvailable]);

  // Reset keySize to a valid value when algorithm changes
  useEffect(() => {
    const opts = KEY_SIZE_OPTIONS[alg];
    if (opts && !opts.find((o) => o.value === keySize)) {
      setKeySize(opts[0].value);
    }
    if (alg === "rc6" && !["ECB", "CBC"].includes(mode)) {
      setMode("ECB");
    }
    if (pad === "Zero" && dir === "decrypt") {
      setPad("PKCS7");
    }
    const ivLen = iv.replace(/\s+/g, "").length;
    if (["CBC", "CTR"].includes(mode) && ivLen !== 32) {
      setIv(DEFAULT_IV_16);
    }
    if (mode === "GCM" && ivLen !== 24) {
      setIv(DEFAULT_IV_12);
    }
  }, [alg, keySize, mode, pad, dir, iv]);

  // Filter keys by selected algorithm
  const algKeys = keys.filter((k) => (k.algorithm || "").toLowerCase() === alg);
  const keyOptions = [
    { value: "", label: algKeys.length ? "请选择密钥…" : "暂无密钥,请生成" },
    ...algKeys.map((k) => ({
      value: k.key_id,
      label: `${k.label || k.algorithm} · ${k.key_id.slice(0, 8)}…`,
    })),
  ];

  const run = async () => {
    if (!keyId) {
      setError("请先选择或生成一个密钥");
      return;
    }
    try {
      setLoading(true);
      setError(null);
      setResult(null);
      if (dir === "encrypt") {
        const requestVerbose = verboseAvailable && verbose;
        const body: Record<string, any> = {
          algorithm: alg,
          plaintext_b64: utf8ToBase64(text),
          key_id: keyId,
          mode,
          padding: requestVerbose ? "None" : pad,
          verbose: requestVerbose,
        };
        if (mode !== "ECB" && mode !== "GCM" && iv) body.iv_hex = iv;
        if (mode === "GCM") {
          if (iv) body.iv_hex = iv;
          if (aad) body.aad_b64 = aad;
        }
        const resp = await symmetricEncrypt(alg, body);
        if (resp.code === 1000) {
          const data = resp.data || {};
          const b64: string = data.ciphertext_b64 || "";
          const hex = base64ToHex(b64);
          setResult({
            b64,
            hex,
            ms: data.duration_ms ?? 0,
            tagHex: mode === "GCM" && hex.length >= 32 ? hex.slice(-32) : undefined,
            ivHex: iv,
            trace: data.trace ?? null,
          });
        } else {
          setError(resp.message || "加密失败");
        }
      } else {
        const ciphertext = text.trim();
        const ciphertext_b64 = /^[0-9a-fA-F\s]+$/.test(ciphertext)
          ? hexToBase64(ciphertext)
          : ciphertext;
        const body: Record<string, any> = {
          algorithm: alg,
          ciphertext_b64,
          key_id: keyId,
          mode,
          padding: pad,
        };
        if (mode !== "ECB" && iv) body.iv_hex = iv;
        if (mode === "GCM") {
          if (aad) body.aad_b64 = aad;
        }
        const resp = await symmetricDecrypt(alg, body);
        if (resp.code === 1000) {
          const data = resp.data || {};
          const plaintextB64: string = data.plaintext_b64 || "";
          setResult({
            b64: "",
            hex: base64ToHex(ciphertext_b64),
            ms: data.duration_ms ?? 0,
            plaintext: base64ToUtf8(plaintextB64),
          });
        } else {
          setError(resp.message || "解密失败");
        }
      }
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || "网络错误");
    } finally {
      setLoading(false);
    }
  };

  const generateKey = async () => {
    try {
      setKeygenLoading(true);
      setError(null);
      const resp = await symmetricKeygen({
        algorithm: alg,
        key_size: Number(keySize),
        label: `${alg.toUpperCase()}-${Number(keySize) * 8} key`,
      });
      if (resp.code === 1000) {
        const data = resp.data || {};
        await loadKeys();
        if (data.key_id) setKeyId(data.key_id);
      } else {
        setError(resp.message || "生成密钥失败");
      }
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || "网络错误");
    } finally {
      setKeygenLoading(false);
    }
  };

  const randomIv = () => {
    const len = mode === "GCM" ? 12 : 16;
    const r = Array.from({ length: len }, () =>
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
            <span className="text-xs text-[var(--cl-text-secondary)]">密钥长度</span>
            <Select value={keySize} onChange={setKeySize} options={KEY_SIZE_OPTIONS[alg] || []} />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-[var(--cl-text-secondary)]">模式</span>
            <Select value={mode} onChange={setMode} options={alg === "rc6" ? MODES.filter((m) => ["ECB", "CBC"].includes(m.value)) : MODES} />
          </div>
          <div className="flex items-center gap-2">
            <span className="text-xs text-[var(--cl-text-secondary)]">填充</span>
            <Select value={pad} onChange={setPad} options={dir === "decrypt" ? PADS.filter((p) => p.value !== "Zero") : PADS} />
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
                <KeyRound size={10} /> {keyId ? "已选密钥" : "未选择"}
              </span>
            }
          >
            <div className="flex gap-2">
              <Select
                value={keyId}
                onChange={setKeyId}
                options={keyOptions}
                className="flex-1 font-mono text-xs"
              />
              <GhostButton onClick={generateKey} disabled={keygenLoading}>
                <Sparkles size={14} />
                {keygenLoading ? "生成中…" : "生成新密钥"}
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
            hint={
              dir === "encrypt"
                ? verbose
                  ? `UTF-8 ${plaintextByteLength}/16 字节`
                  : "提交时自动转 Base64"
                : undefined
            }
          >
            <TextArea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={5}
              placeholder={dir === "encrypt" ? (verbose ? "必须正好 16 字节" : "输入要加密的文本…") : "粘贴 Base64 密文…"}
            />
          </Field>

          {verboseAvailable && (
            <div className="mb-4 rounded-md border border-[var(--cl-border-light)] bg-[var(--cl-bg-page)]/55 px-3 py-2.5">
              <label className="flex items-center justify-between gap-3 cursor-pointer">
                <span className="inline-flex items-center gap-2 text-xs text-[var(--cl-text-regular)]">
                  <BookOpen size={14} className="text-[var(--cl-primary)]" />
                  教学模式 (Verbose)
                </span>
                <input
                  type="checkbox"
                  checked={verbose}
                  onChange={(event) => setVerbose(event.target.checked)}
                  className="h-4 w-4 accent-[var(--cl-primary)]"
                />
              </label>
              {verbose && (
                <div
                  className={`mt-2 text-[11px] ${
                    verboseBlockReady ? "text-[var(--cl-success)]" : "text-[var(--cl-warning)]"
                  }`}
                >
                  AES verbose 仅支持 ECB 单分组,明文必须正好 16 字节。
                </div>
              )}
            </div>
          )}

          {error && (
            <div className="mb-3 px-3 py-2 rounded-md bg-[#FEF0F0] border border-[#FBC4C4] text-xs text-[#C45656] cl-shake">
              {error}
            </div>
          )}

          <div className="flex items-center gap-2 mt-1">
            <PrimaryButton onClick={run} loading={loading}>
              {dir === "encrypt" ? <Lock size={14} /> : <Unlock size={14} />}
              {dir === "encrypt" ? "执行加密" : "执行解密"}
            </PrimaryButton>
            <GhostButton onClick={() => { setResult(null); setError(null); }}>
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
              {dir === "encrypt" ? (
                <>
                  <HexViewer value={result.b64} label="密文 (Base64)" variant="base64" />
                  <HexViewer value={result.hex} label="密文 (Hex 视图)" variant="hex" maxLines={3} />
                  {result.tagHex && (
                    <HexViewer value={result.tagHex} label="认证标签 Tag (hex)" variant="hex" maxLines={2} />
                  )}
                </>
              ) : (
                <>
                  <HexViewer value={result.plaintext || ""} label="明文" variant="base64" />
                </>
              )}
              <div className="flex items-center gap-2 flex-wrap pt-1">
                <Tag tone="success">运算成功</Tag>
                <Tag tone="info">算法 {alg.toUpperCase()}-{mode}</Tag>
                <Tag tone="neutral">填充 {pad}</Tag>
                <Tag tone="neutral">IV {mode === "ECB" ? "不使用" : `${iv.length / 2} 字节`}</Tag>
              </div>
              {result.trace && <AesTraceViewer trace={result.trace} />}
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
