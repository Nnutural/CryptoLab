import { useEffect, useState } from "react";
import { Lock, Unlock, KeyRound, Dice5, Sparkles, ArrowLeftRight } from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { CryptoCard } from "@/components/shared/CryptoCard";
import { Field, TextInput, TextArea, Select, PrimaryButton, GhostButton, Tag } from "@/components/shared/Field";
import { HexViewer } from "@/components/shared/HexViewer";
import { OperationTimer } from "@/components/shared/OperationTimer";
import { EmptyState } from "@/components/shared/EmptyState";
import { ROUTE_TITLES } from "@/components/nav";
import { symmetricEncrypt, symmetricDecrypt, symmetricKeygen } from "@/api/symmetric";
import { listKeys } from "@/api/keys";

const ALGS = [
  { value: "aes", label: "AES" },
  { value: "sm4", label: "SM4" },
  { value: "rc6", label: "RC6" },
];
const MODES = ["ECB", "CBC", "CTR", "GCM"].map((m) => ({ value: m, label: m }));
const PADS = ["PKCS7", "ZeroPadding", "None"].map((p) => ({ value: p, label: p }));

// AES allows 128/192/256, SM4 fixed 128, RC6 typically 128/256
const KEY_SIZE_OPTIONS: Record<string, { value: string; label: string }[]> = {
  aes: [
    { value: "128", label: "AES-128" },
    { value: "192", label: "AES-192" },
    { value: "256", label: "AES-256" },
  ],
  sm4: [{ value: "128", label: "SM4-128" }],
  rc6: [
    { value: "128", label: "RC6-128" },
    { value: "256", label: "RC6-256" },
  ],
};

interface KeyEntry {
  key_id: string;
  algorithm: string;
  key_size?: number;
  label?: string;
  created_at?: string;
  status?: string;
}

export function SymmetricView() {
  const meta = ROUTE_TITLES.symmetric;
  const [mode, setMode] = useState("GCM");
  const [alg, setAlg] = useState("aes");
  const [keySize, setKeySize] = useState("256");
  const [pad, setPad] = useState("PKCS7");
  const [dir, setDir] = useState<"encrypt" | "decrypt">("encrypt");
  const [keys, setKeys] = useState<KeyEntry[]>([]);
  const [keyId, setKeyId] = useState<string>("");
  const [iv, setIv] = useState("000102030405060708090a0b");
  const [aad, setAad] = useState("");
  const [text, setText] = useState("Hello, World!");
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
      }
    | null
  >(null);

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

  // Reset keySize to a valid value when algorithm changes
  useEffect(() => {
    const opts = KEY_SIZE_OPTIONS[alg];
    if (opts && !opts.find((o) => o.value === keySize)) {
      setKeySize(opts[0].value);
    }
  }, [alg, keySize]);

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
        const body: Record<string, any> = {
          plaintext: text,
          key_id: keyId,
          mode,
        };
        if (mode !== "ECB" && mode !== "GCM" && iv) body.iv_hex = iv;
        if (mode === "GCM") {
          if (iv) body.iv_hex = iv;
          if (aad) body.aad = aad;
        }
        const resp = await symmetricEncrypt(alg, body);
        if (resp.code === 1000) {
          const data = resp.data || {};
          const hex: string = data.ciphertext_hex || "";
          // Convert hex to Base64 for display
          let b64 = "";
          try {
            const bytes = new Uint8Array(
              (hex.match(/.{1,2}/g) || []).map((h) => parseInt(h, 16))
            );
            let bin = "";
            for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
            b64 = typeof btoa !== "undefined" ? btoa(bin) : "";
          } catch {
            b64 = hex;
          }
          setResult({
            b64,
            hex,
            ms: data.duration_ms ?? 0,
            tagHex: data.tag_hex,
            ivHex: data.iv_hex,
          });
          if (data.iv_hex) setIv(data.iv_hex);
        } else {
          setError(resp.message || "加密失败");
        }
      } else {
        // decrypt: input field holds ciphertext (Base64). Try to convert to hex.
        let cipherHex = text.trim();
        // If the text is not pure hex, treat as Base64 and convert
        if (!/^[0-9a-fA-F\s]+$/.test(cipherHex)) {
          try {
            const bin = typeof atob !== "undefined" ? atob(cipherHex) : "";
            let h = "";
            for (let i = 0; i < bin.length; i++) {
              h += bin.charCodeAt(i).toString(16).padStart(2, "0");
            }
            cipherHex = h;
          } catch {
            /* keep as-is */
          }
        } else {
          cipherHex = cipherHex.replace(/\s+/g, "");
        }
        const body: Record<string, any> = {
          ciphertext_hex: cipherHex,
          key_id: keyId,
          mode,
        };
        if (mode !== "ECB" && iv) body.iv_hex = iv;
        if (mode === "GCM") {
          if (aad) body.aad = aad;
          // tag_hex may be supplied via the AAD-adjacent flow; if user pasted a separate field we don't have here.
        }
        const resp = await symmetricDecrypt(alg, body);
        if (resp.code === 1000) {
          const data = resp.data || {};
          setResult({
            b64: "",
            hex: cipherHex,
            ms: data.duration_ms ?? 0,
            plaintext: data.plaintext,
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
        label: `${alg.toUpperCase()}-${keySize} key`,
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
            hint={dir === "encrypt" ? "提交时自动转 Base64" : undefined}
          >
            <TextArea
              value={text}
              onChange={(e) => setText(e.target.value)}
              rows={5}
              placeholder={dir === "encrypt" ? "输入要加密的文本…" : "粘贴 Base64 密文…"}
            />
          </Field>

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
