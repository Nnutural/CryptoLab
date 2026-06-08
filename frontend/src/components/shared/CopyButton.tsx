import { useState } from "react";
import { Copy, Check } from "lucide-react";

interface CopyButtonProps {
  text: string;
  label?: string;
  size?: "sm" | "md";
}

export function CopyButton({ text, label, size = "sm" }: CopyButtonProps) {
  const [copied, setCopied] = useState(false);

  const handle = async () => {
    try {
      await navigator.clipboard.writeText(text);
    } catch {
      /* ignore */
    }
    setCopied(true);
    setTimeout(() => setCopied(false), 1400);
  };

  const dims = size === "sm" ? "h-7 px-2 text-xs" : "h-8 px-3 text-sm";

  return (
    <button
      onClick={handle}
      className={`inline-flex items-center gap-1.5 rounded-md border border-[var(--cl-border)] ${dims} bg-white text-[var(--cl-text-regular)] hover:bg-[var(--cl-primary-light)] hover:text-[var(--cl-primary)] hover:border-[var(--cl-primary)] transition-colors`}
      type="button"
    >
      <span className="relative inline-flex w-3.5 h-3.5">
        <Copy
          className={`absolute inset-0 transition-all duration-200 ${copied ? "opacity-0 scale-50" : "opacity-100 scale-100"}`}
          size={14}
        />
        <Check
          className={`absolute inset-0 text-[var(--cl-success)] transition-all duration-200 ${copied ? "opacity-100 scale-100" : "opacity-0 scale-50"}`}
          size={14}
        />
      </span>
      <span>{copied ? "已复制" : label ?? "复制"}</span>
    </button>
  );
}
