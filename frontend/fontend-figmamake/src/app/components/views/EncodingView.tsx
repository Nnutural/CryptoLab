import { useState } from "react";
import { Code2, ArrowRightLeft, ArrowRight, ArrowLeft, Lock } from "lucide-react";
import { PageHeader } from "../shared/PageHeader";
import { CryptoCard } from "../shared/CryptoCard";
import { TextArea, PrimaryButton, GhostButton, Tag } from "../shared/Field";
import { ROUTE_TITLES } from "../nav";

function utf8Encode(s: string): string {
  try {
    return btoa(unescape(encodeURIComponent(s)));
  } catch {
    return "";
  }
}
function utf8Decode(s: string): string {
  try {
    return decodeURIComponent(escape(atob(s)));
  } catch {
    return "[解码错误:无效的 Base64 字符串]";
  }
}

export function EncodingView() {
  const meta = ROUTE_TITLES.encoding;
  const [plain, setPlain] = useState("Hello, World!");
  const [encoded, setEncoded] = useState("SGVsbG8sIFdvcmxkIQ==");

  const doEncode = () => setEncoded(utf8Encode(plain));
  const doDecode = () => setPlain(utf8Decode(encoded));
  const swap = () => {
    const tmp = plain;
    setPlain(encoded);
    setEncoded(tmp);
  };

  const plainBytes = new Blob([plain]).size;
  const encBytes = new Blob([encoded]).size;
  const ratio = plainBytes ? (encBytes / plainBytes).toFixed(2) : "—";

  return (
    <>
      <PageHeader title={meta.title} subtitle={meta.subtitle} breadcrumb={meta.breadcrumb} />

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
            <PrimaryButton onClick={doEncode}>
              <ArrowRight size={14} /> 编码为 Base64
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

        <CryptoCard title="Base64 编码" subtitle="Base64 · ASCII safe" icon={<Lock size={14} />}>
          <TextArea
            rows={8}
            value={encoded}
            onChange={(e) => setEncoded(e.target.value)}
            placeholder="或粘贴 Base64…"
          />
          <div className="flex items-center justify-between mt-2 text-[11px] text-[var(--cl-text-placeholder)] font-mono">
            <span>字符 {encoded.length}</span>
            <span>{encBytes} 字节</span>
          </div>
          <div className="mt-3">
            <GhostButton onClick={doDecode}>
              <ArrowLeft size={14} /> 解码为文本
            </GhostButton>
          </div>
        </CryptoCard>
      </div>

      <div className="mt-5 flex items-center gap-2 px-4 py-2.5 rounded-md bg-[var(--cl-primary-light)] border border-[#BFDFFF] text-xs text-[var(--cl-primary-dark)] inline-flex">
        <ArrowRightLeft size={14} />
        原始 {plainBytes} 字节 → 编码后 {encBytes} 字节 (比率 {ratio}x)
      </div>

      <CryptoCard className="mt-5 opacity-60" title="UTF-8 编码 / 解码" icon={<Code2 size={14} />} extra={<Tag tone="neutral">即将上线</Tag>}>
        <div className="text-sm text-[var(--cl-text-secondary)]">
          UTF-8 单独编码工具尚未在当前阶段提供,Base64 已内置 UTF-8 兼容处理。
        </div>
      </CryptoCard>
    </>
  );
}
