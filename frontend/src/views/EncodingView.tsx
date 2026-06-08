import { useState } from "react";
import { Code2, ArrowRightLeft, ArrowRight, ArrowLeft, Lock } from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { CryptoCard } from "@/components/shared/CryptoCard";
import { TextArea, PrimaryButton, GhostButton, Tag } from "@/components/shared/Field";
import { ROUTE_TITLES } from "@/components/nav";
import { base64Encode, base64Decode } from "@/api/encoding";
import client, { type APIResponse } from "@/api/client";

type Mode = "base64" | "utf8";

function decodeBase64Text(value: string): string {
  try {
    const binary = atob(value);
    const bytes = new Uint8Array(binary.length);
    for (let i = 0; i < binary.length; i++) bytes[i] = binary.charCodeAt(i);
    return new TextDecoder().decode(bytes);
  } catch {
    return value;
  }
}

export function EncodingView() {
  const meta = ROUTE_TITLES.encoding;
  const [mode, setMode] = useState<Mode>("base64");
  const [plain, setPlain] = useState("Hello, World!");
  const [encoded, setEncoded] = useState("SGVsbG8sIFdvcmxkIQ==");
  const [loading, setLoading] = useState<"encode" | "decode" | null>(null);
  const [error, setError] = useState<string | null>(null);

  const callApi = async <T,>(fn: () => Promise<APIResponse<T>>): Promise<T | null> => {
    try {
      const resp = await fn();
      if (resp.code === 1000) {
        return resp.data;
      }
      setError(resp.message || "操作失败");
      return null;
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || "网络错误");
      return null;
    }
  };

  const utf8Call = (
    op: "encode" | "decode",
    payload: Record<string, unknown>,
  ): Promise<APIResponse<any>> =>
    client.post(`/encoding/utf8/${op}`, payload) as unknown as Promise<APIResponse<any>>;

  const doEncode = async () => {
    setError(null);
    setLoading("encode");
    try {
      const data = await callApi<any>(() =>
        mode === "base64" ? base64Encode(plain) : utf8Call("encode", { data: plain }),
      );
      if (data) {
        // backend may return `encoded` for base64 or `result` for utf8
        const result = data.encoded ?? data.result ?? data.output ?? "";
        setEncoded(String(result));
      }
    } finally {
      setLoading(null);
    }
  };

  const doDecode = async () => {
    setError(null);
    setLoading("decode");
    try {
      const data = await callApi<any>(() =>
        mode === "base64" ? base64Decode(encoded) : utf8Call("decode", { data: encoded }),
      );
      if (data) {
        const raw = data.decoded ?? data.data ?? data.result ?? data.output ?? "";
        const result = mode === "base64" ? decodeBase64Text(String(raw)) : raw;
        setPlain(String(result));
      }
    } finally {
      setLoading(null);
    }
  };

  const swap = () => {
    const tmp = plain;
    setPlain(encoded);
    setEncoded(tmp);
  };

  const plainBytes = new Blob([plain]).size;
  const encBytes = new Blob([encoded]).size;
  const ratio = plainBytes ? (encBytes / plainBytes).toFixed(2) : "—";

  const rightTitle = mode === "base64" ? "Base64 编码" : "UTF-8 字节";
  const rightSubtitle = mode === "base64" ? "Base64 · ASCII safe" : "UTF-8 · 字节序列";
  const encodeLabel = mode === "base64" ? "编码为 Base64" : "编码为 UTF-8";
  const decodeLabel = mode === "base64" ? "解码为文本" : "解码为文本";

  return (
    <>
      <PageHeader title={meta.title} subtitle={meta.subtitle} breadcrumb={meta.breadcrumb} />

      {/* Mode tabs */}
      <div className="mb-5 inline-flex items-center p-1 rounded-md bg-white border border-[var(--cl-border-light)]">
        {(["base64", "utf8"] as Mode[]).map((m) => {
          const active = mode === m;
          return (
            <button
              key={m}
              onClick={() => {
                setMode(m);
                setError(null);
              }}
              className={`px-3 h-7 rounded text-xs transition-colors ${
                active
                  ? "bg-[var(--cl-primary)] text-white"
                  : "text-[var(--cl-text-secondary)] hover:text-[var(--cl-text-regular)]"
              }`}
            >
              {m === "base64" ? "Base64" : "UTF-8"}
            </button>
          );
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-[1fr_auto_1fr] gap-4 items-stretch">
        <CryptoCard title="原始文本" subtitle="Plain Text · UTF-8" icon={<Code2 size={14} />}>
          <TextArea
            rows={8}
            value={plain}
            onChange={(e) => setPlain(e.target.value)}
            placeholder="输入要编码的内容…"
            className="!font-sans"
          />
          <div className="flex items-center justify-between mt-2 text-[11px] text-[var(--cl-text-placeholder)] font-mono">
            <span>字符 {plain.length}</span>
            <span>{plainBytes} 字节</span>
          </div>
          <div className="mt-3">
            <PrimaryButton onClick={doEncode} loading={loading === "encode"} disabled={!plain}>
              <ArrowRight size={14} /> {encodeLabel}
            </PrimaryButton>
          </div>
        </CryptoCard>

        <div className="flex lg:flex-col items-center justify-center">
          <button
            onClick={swap}
            className="w-10 h-10 rounded-full bg-white border border-[var(--cl-border)] text-[var(--cl-text-secondary)] hover:bg-[var(--cl-primary-light)] hover:text-[var(--cl-primary)] hover:border-[var(--cl-primary)] transition-all shadow-sm inline-flex items-center justify-center"
            title="互换两侧内容"
          >
            <ArrowRightLeft size={16} />
          </button>
        </div>

        <CryptoCard title={rightTitle} subtitle={rightSubtitle} icon={<Lock size={14} />}>
          <TextArea
            rows={8}
            value={encoded}
            onChange={(e) => setEncoded(e.target.value)}
            placeholder={mode === "base64" ? "或粘贴 Base64…" : "或粘贴 UTF-8 字节…"}
          />
          <div className="flex items-center justify-between mt-2 text-[11px] text-[var(--cl-text-placeholder)] font-mono">
            <span>字符 {encoded.length}</span>
            <span>{encBytes} 字节</span>
          </div>
          <div className="mt-3">
            <GhostButton onClick={doDecode} disabled={loading === "decode" || !encoded}>
              <ArrowLeft size={14} /> {decodeLabel}
            </GhostButton>
          </div>
        </CryptoCard>
      </div>

      <div className="mt-5 flex items-center gap-2 px-4 py-2.5 rounded-md bg-[var(--cl-primary-light)] border border-[#BFDFFF] text-xs text-[var(--cl-primary-dark)] inline-flex">
        <ArrowRightLeft size={14} />
        原始 {plainBytes} 字节 → 编码后 {encBytes} 字节 (比率 {ratio}x)
      </div>

      {error && (
        <div className="mt-3 px-4 py-2.5 rounded-md bg-[#FEF0F0] border border-[#FBC4C4] text-xs text-[#C45656] inline-flex items-center gap-2">
          {error}
        </div>
      )}

      <CryptoCard
        className="mt-5"
        title="说明"
        icon={<Code2 size={14} />}
        extra={<Tag tone="neutral">{mode === "base64" ? "Base64" : "UTF-8"}</Tag>}
      >
        <div className="text-sm text-[var(--cl-text-secondary)] leading-relaxed">
          {mode === "base64"
            ? "Base64 将任意二进制数据编码为 64 个 ASCII 字符,常用于在文本协议(JSON、HTTP Header、邮件)中安全传输二进制内容。每 3 字节输入扩展为 4 字节输出,膨胀率约 1.33x。"
            : "UTF-8 是 Unicode 的变长字节编码:ASCII 字符仍占 1 字节,中日韩等常见字符占 3 字节,扩展符号最多占 4 字节,兼容 ASCII 又能表示全部 Unicode 字符。"}
        </div>
      </CryptoCard>
    </>
  );
}
