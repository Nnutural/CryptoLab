import { useEffect, useState } from "react";
import { KeyRound, Lock, FileSignature, CheckCircle2, XCircle, Sparkles, ShieldCheck } from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { CryptoCard } from "@/components/shared/CryptoCard";
import { Field, TextInput, TextArea, PrimaryButton, Tag } from "@/components/shared/Field";
import { HexViewer } from "@/components/shared/HexViewer";
import { OperationTimer } from "@/components/shared/OperationTimer";
import { ROUTE_TITLES } from "@/components/nav";
import { rsaKeygen, rsaEncrypt, rsaDecrypt, rsaSign, rsaVerify } from "@/api/pubkey";
import { getKeyPublic, listKeys } from "@/api/keys";

interface RsaKey {
  key_id: string;
  private_key_id: string;
  public_key_id: string;
  label?: string;
  algorithm?: string;
  public_key_pem?: string;
  n_hex?: string;
  e_hex?: string;
  bits?: number;
}

function getKeyType(row: any): string {
  return String(row?.key_type ?? row?.type ?? "").toLowerCase();
}

async function fetchRsaPublicMaterial(publicKeyId: string): Promise<Partial<RsaKey>> {
  try {
    const resp = await getKeyPublic(publicKeyId);
    if (resp.code !== 1000) return {};
    const material = (resp.data as any)?.material ?? {};
    return {
      n_hex: material.n_hex,
      e_hex: material.e_hex,
      public_key_pem: material.public_key_pem,
    };
  } catch {
    return {};
  }
}

export function RsaView() {
  const meta = ROUTE_TITLES.rsa;
  const [hasKey, setHasKey] = useState(false);
  const [generating, setGenerating] = useState(false);
  const [tab, setTab] = useState<"enc" | "sign">("enc");
  const [keyInfo, setKeyInfo] = useState<RsaKey | null>(null);
  const [keyError, setKeyError] = useState<string | null>(null);

  const loadKeys = async () => {
    try {
      const resp = await listKeys();
      if (resp.code === 1000 && Array.isArray(resp.data)) {
        const rsaKeys = resp.data.filter((k: any) => String(k.algorithm || "").toLowerCase() === "rsa");
        const privateKey = rsaKeys.find((k: any) => getKeyType(k) === "private");
        const publicKey = rsaKeys.find((k: any) => getKeyType(k) === "public");
        if (privateKey && publicKey) {
          const publicMaterial = await fetchRsaPublicMaterial(publicKey.key_id);
          setKeyInfo({
            key_id: privateKey.key_id,
            private_key_id: privateKey.key_id,
            public_key_id: publicKey.key_id,
            label: privateKey.label,
            algorithm: privateKey.algorithm,
            bits: privateKey.bits,
            ...publicMaterial,
          });
          setHasKey(true);
        } else {
          setHasKey(false);
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
      const resp = await rsaKeygen({ bits: 1024, e: 65537, label: `rsa-${Date.now()}` });
      if (resp.code === 1000) {
        const data = resp.data;
        const publicMaterial = await fetchRsaPublicMaterial(data.public_key_id);
        setKeyInfo({
          key_id: data.private_key_id,
          private_key_id: data.private_key_id,
          public_key_id: data.public_key_id,
          bits: data.bits,
          algorithm: "RSA",
          ...publicMaterial,
        });
        setHasKey(true);
      } else {
        setKeyError(resp.message || "生成密钥失败");
      }
    } catch (err: any) {
      setKeyError(err?.response?.data?.message || err?.message || "网络错误");
    } finally {
      setGenerating(false);
    }
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
        ) : hasKey && keyInfo ? (
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <div className="text-xs text-[var(--cl-text-secondary)] mb-1.5">密钥 ID</div>
              <div className="font-mono text-xs px-3 py-2 rounded bg-[var(--cl-bg-code)] border border-[var(--cl-border-light)] break-all">
                {keyInfo.key_id}
              </div>
              {keyInfo.label && (
                <>
                  <div className="text-xs text-[var(--cl-text-secondary)] mt-3 mb-1.5">标签</div>
                  <div className="font-mono text-xs px-3 py-2 rounded bg-[var(--cl-bg-code)] border border-[var(--cl-border-light)]">
                    {keyInfo.label}
                  </div>
                </>
              )}
            </div>
            <div>
              {keyInfo.n_hex && (
                <HexViewer value={keyInfo.n_hex} label={`模数 n_hex (${keyInfo.bits || 1024} bit)`} maxLines={2} />
              )}
              <div className="mt-3 inline-flex items-center gap-2 text-xs text-[var(--cl-text-regular)]">
                <span className="text-[var(--cl-text-secondary)]">公钥指数 e</span>
                <span className="font-mono px-2 py-0.5 rounded bg-[var(--cl-bg-code)] border border-[var(--cl-border-light)]">
                  {keyInfo.e_hex ? `0x${keyInfo.e_hex} (${parseInt(keyInfo.e_hex, 16)})` : "0x010001 (65537)"}
                </span>
              </div>
            </div>
          </div>
        ) : keyError ? (
          <div className="text-sm text-[var(--cl-danger)] py-2">{keyError}</div>
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

      {tab === "enc" ? (
        <EncPanel privateKeyId={keyInfo?.private_key_id || ""} publicKeyId={keyInfo?.public_key_id || ""} />
      ) : (
        <SignPanel privateKeyId={keyInfo?.private_key_id || ""} publicKeyId={keyInfo?.public_key_id || ""} />
      )}
    </>
  );
}

function EncPanel({ privateKeyId, publicKeyId }: { privateKeyId: string; publicKeyId: string }) {
  const [dir, setDir] = useState<"enc" | "dec">("enc");
  const [text, setText] = useState("Secret message");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<{ hex: string; ms: number } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const run = async () => {
    const keyId = dir === "enc" ? publicKeyId : privateKeyId;
    if (!keyId) {
      setError("请先生成 RSA 密钥对");
      return;
    }
    try {
      setLoading(true);
      setError(null);
      setResult(null);
      if (dir === "enc") {
        const resp = await rsaEncrypt({ plaintext: text, key_id: keyId });
        if (resp.code === 1000) {
          setResult({ hex: resp.data.ciphertext_hex, ms: resp.data.duration_ms ?? 0 });
        } else {
          setError(resp.message || "加密失败");
        }
      } else {
        const resp = await rsaDecrypt({ ciphertext_hex: text, key_id: keyId });
        if (resp.code === 1000) {
          setResult({ hex: resp.data.plaintext, ms: resp.data.duration_ms ?? 0 });
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
            value={(dir === "enc" ? publicKeyId : privateKeyId) || "(尚未生成密钥)"}
            readOnly
            className="font-mono"
          />
        </Field>
        <Field label={dir === "enc" ? "明文" : "密文 (hex)"}>
          <TextArea value={text} onChange={(e) => setText(e.target.value)} rows={3} className={dir === "enc" ? "!font-sans" : ""} />
        </Field>
        {error && (
          <div className="mb-3 px-3 py-2 rounded-md bg-[#FEF0F0] border border-[#FBC4C4] text-xs text-[#C45656] cl-shake">
            {error}
          </div>
        )}
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
          <HexViewer value={result.hex} label={dir === "enc" ? "密文 (hex)" : "明文"} maxLines={4} />
        ) : (
          <div className="text-sm text-[var(--cl-text-placeholder)] py-8 text-center">
            选择方向并执行运算
          </div>
        )}
      </CryptoCard>
    </div>
  );
}

function SignPanel({ privateKeyId, publicKeyId }: { privateKeyId: string; publicKeyId: string }) {
  const [dir, setDir] = useState<"sign" | "verify">("sign");
  const [msg, setMsg] = useState("Important document content");
  const [sig, setSig] = useState("");
  const [tamper, setTamper] = useState(false);
  const [loading, setLoading] = useState(false);
  const [signResult, setSignResult] = useState<{ hex: string; ms: number } | null>(null);
  const [verifyResult, setVerifyResult] = useState<{ valid: boolean; ms: number } | null>(null);
  const [error, setError] = useState<string | null>(null);

  const run = async () => {
    const keyId = dir === "sign" ? privateKeyId : publicKeyId;
    if (!keyId) {
      setError("请先生成 RSA 密钥对");
      return;
    }
    try {
      setLoading(true);
      setError(null);
      setSignResult(null);
      setVerifyResult(null);
      if (dir === "sign") {
        const resp = await rsaSign({ message: msg, key_id: keyId });
        if (resp.code === 1000) {
          setSignResult({ hex: resp.data.signature_hex, ms: resp.data.duration_ms ?? 0 });
          setSig(resp.data.signature_hex);
        } else {
          setError(resp.message || "签名失败");
        }
      } else {
        const messageToVerify = tamper ? `${msg}_tampered` : msg;
        const resp = await rsaVerify({ message: messageToVerify, signature_hex: sig, key_id: keyId });
        if (resp.code === 1000) {
          setVerifyResult({ valid: !!resp.data.valid, ms: resp.data.duration_ms ?? 0 });
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
        {error && (
          <div className="mb-3 px-3 py-2 rounded-md bg-[#FEF0F0] border border-[#FBC4C4] text-xs text-[#C45656] cl-shake">
            {error}
          </div>
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
