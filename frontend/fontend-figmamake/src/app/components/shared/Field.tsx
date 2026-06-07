import type { ReactNode } from "react";

export function Field({
  label,
  hint,
  children,
  required,
  error,
}: {
  label: ReactNode;
  hint?: ReactNode;
  children: ReactNode;
  required?: boolean;
  error?: string;
}) {
  return (
    <div className="mb-4">
      <div className="flex items-baseline justify-between mb-1.5">
        <label className="text-xs text-[var(--cl-text-regular)]">
          {label}
          {required && <span className="text-[var(--cl-danger)] ml-0.5">*</span>}
        </label>
        {hint && <span className="text-[10px] text-[var(--cl-text-placeholder)]">{hint}</span>}
      </div>
      {children}
      {error && <div className="text-[11px] text-[var(--cl-danger)] mt-1 cl-shake">{error}</div>}
    </div>
  );
}

export function TextInput(props: React.InputHTMLAttributes<HTMLInputElement>) {
  const { className = "", ...rest } = props;
  return (
    <input
      className={`w-full h-9 px-3 rounded-md border border-[var(--cl-border)] bg-white text-sm focus:border-[var(--cl-primary)] focus:ring-2 focus:ring-[var(--cl-primary)]/15 outline-none transition-all placeholder:text-[var(--cl-text-placeholder)] ${className}`}
      {...rest}
    />
  );
}

export function TextArea(props: React.TextareaHTMLAttributes<HTMLTextAreaElement>) {
  const { className = "", ...rest } = props;
  return (
    <textarea
      className={`w-full px-3 py-2 rounded-md border border-[var(--cl-border)] bg-white text-sm focus:border-[var(--cl-primary)] focus:ring-2 focus:ring-[var(--cl-primary)]/15 outline-none transition-all resize-y placeholder:text-[var(--cl-text-placeholder)] font-mono ${className}`}
      {...rest}
    />
  );
}

export function Select({
  value,
  onChange,
  options,
  className = "",
}: {
  value: string;
  onChange: (v: string) => void;
  options: { value: string; label: string }[];
  className?: string;
}) {
  return (
    <select
      value={value}
      onChange={(e) => onChange(e.target.value)}
      className={`h-9 px-3 pr-8 rounded-md border border-[var(--cl-border)] bg-white text-sm focus:border-[var(--cl-primary)] focus:ring-2 focus:ring-[var(--cl-primary)]/15 outline-none transition-all appearance-none bg-[url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'><path fill='%23909399' d='M6 8L2 4h8z'/></svg>")] bg-no-repeat bg-[right_8px_center] ${className}`}
    >
      {options.map((o) => (
        <option key={o.value} value={o.value}>
          {o.label}
        </option>
      ))}
    </select>
  );
}

export function PrimaryButton({
  children,
  loading,
  ...props
}: React.ButtonHTMLAttributes<HTMLButtonElement> & { loading?: boolean }) {
  const { className = "", disabled, ...rest } = props;
  return (
    <button
      disabled={disabled || loading}
      className={`h-9 px-4 rounded-md bg-[var(--cl-primary)] text-white text-sm hover:bg-[var(--cl-primary-hover)] disabled:bg-[var(--cl-primary)]/50 disabled:cursor-not-allowed inline-flex items-center justify-center gap-1.5 shadow-[0_2px_8px_rgba(64,158,255,0.25)] hover:shadow-[0_4px_12px_rgba(64,158,255,0.4)] transition-all ${className}`}
      {...rest}
    >
      {loading && (
        <span className="w-3.5 h-3.5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
      )}
      {children}
    </button>
  );
}

export function GhostButton(props: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  const { className = "", ...rest } = props;
  return (
    <button
      className={`h-9 px-3 rounded-md border border-[var(--cl-border)] bg-white text-sm text-[var(--cl-text-regular)] hover:border-[var(--cl-primary)] hover:text-[var(--cl-primary)] hover:bg-[var(--cl-primary-light)] inline-flex items-center justify-center gap-1.5 transition-all ${className}`}
      {...rest}
    />
  );
}

export function Tag({
  children,
  tone = "info",
}: {
  children: ReactNode;
  tone?: "info" | "success" | "warn" | "danger" | "primary" | "neutral";
}) {
  const map = {
    info: "bg-[#ECF5FF] text-[var(--cl-primary-dark)]",
    primary: "bg-[var(--cl-primary)] text-white",
    success: "bg-[#E8F8E1] text-[#3F9114]",
    warn: "bg-[#FDF6EC] text-[#B88230]",
    danger: "bg-[#FEF0F0] text-[#C45656]",
    neutral: "bg-[var(--cl-bg-page)] text-[var(--cl-text-secondary)]",
  };
  return (
    <span className={`inline-flex items-center px-2 py-0.5 rounded text-[10.5px] tracking-wide ${map[tone]}`}>
      {children}
    </span>
  );
}
