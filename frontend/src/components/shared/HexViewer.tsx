import { useMemo, useState } from "react";
import { CopyButton } from "./CopyButton";
import { ChevronDown } from "lucide-react";

interface HexViewerProps {
  value: string;
  label?: string;
  maxLines?: number;
  bytesPerLine?: number;
  copyable?: boolean;
  variant?: "hex" | "base64";
}

export function HexViewer({
  value,
  label,
  maxLines = 4,
  bytesPerLine = 16,
  copyable = true,
  variant = "hex",
}: HexViewerProps) {
  const [expanded, setExpanded] = useState(false);

  const lines = useMemo(() => {
    if (variant === "hex") {
      const clean = value.replace(/\s+/g, "");
      const chunks: string[] = [];
      for (let i = 0; i < clean.length; i += bytesPerLine * 2) {
        const line = clean.slice(i, i + bytesPerLine * 2);
        const formatted = line.match(/.{1,2}/g)?.join(" ") ?? "";
        chunks.push(formatted);
      }
      return chunks;
    } else {
      const charsPerLine = bytesPerLine * 4;
      const chunks: string[] = [];
      for (let i = 0; i < value.length; i += charsPerLine) {
        chunks.push(value.slice(i, i + charsPerLine));
      }
      return chunks;
    }
  }, [value, bytesPerLine, variant]);

  const visibleLines = expanded ? lines : lines.slice(0, maxLines);
  const hasOverflow = lines.length > maxLines;

  return (
    <div className="cl-fade-up">
      {label && (
        <div className="flex items-center justify-between mb-2">
          <div className="flex items-center gap-2">
            <span className="text-xs text-[var(--cl-text-secondary)]">{label}</span>
            <span className="text-[10px] text-[var(--cl-text-placeholder)] font-mono">
              {variant === "hex" ? `${value.replace(/\s+/g, "").length / 2} 字节` : `${value.length} 字符`}
            </span>
          </div>
          {copyable && <CopyButton text={value} />}
        </div>
      )}
      <div className="rounded-md border border-[var(--cl-border-light)] bg-[var(--cl-bg-code)] overflow-hidden">
        <div className="font-mono text-[12.5px] leading-[1.7] text-[var(--cl-text-primary)] p-3">
          {visibleLines.length === 0 ? (
            <span className="text-[var(--cl-text-placeholder)]">—</span>
          ) : (
            visibleLines.map((line, i) => (
              <div key={i} className="flex">
                <span className="text-[var(--cl-text-placeholder)] select-none w-8 shrink-0">
                  {String(i * bytesPerLine).padStart(4, "0")}
                </span>
                <span className="break-all">{line}</span>
              </div>
            ))
          )}
        </div>
        {hasOverflow && (
          <button
            onClick={() => setExpanded((e) => !e)}
            className="w-full flex items-center justify-center gap-1 py-1.5 text-xs text-[var(--cl-text-secondary)] hover:text-[var(--cl-primary)] hover:bg-white border-t border-[var(--cl-border-light)] transition-colors"
          >
            <ChevronDown
              size={14}
              className={`transition-transform duration-200 ${expanded ? "rotate-180" : ""}`}
            />
            {expanded ? "收起" : `展开剩余 ${lines.length - maxLines} 行`}
          </button>
        )}
      </div>
    </div>
  );
}
