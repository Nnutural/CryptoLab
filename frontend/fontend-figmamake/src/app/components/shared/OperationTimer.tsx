import { Clock, Zap } from "lucide-react";

interface OperationTimerProps {
  durationMs: number;
  operation?: string;
}

export function OperationTimer({ durationMs, operation }: OperationTimerProps) {
  const tier =
    durationMs < 1 ? "fast" : durationMs < 100 ? "good" : durationMs < 1000 ? "warn" : "slow";

  const styles = {
    fast: "bg-[#E8F8E1] text-[#3F9114] border-[#67C23A]",
    good: "bg-[#ECF5FF] text-[var(--cl-primary-dark)] border-[var(--cl-primary)]",
    warn: "bg-[#FDF6EC] text-[#B88230] border-[var(--cl-warning)]",
    slow: "bg-[#FEF0F0] text-[#C45656] border-[var(--cl-danger)]",
  }[tier];

  const display =
    durationMs < 1
      ? `${(durationMs * 1000).toFixed(1)} μs`
      : durationMs < 1000
      ? `${durationMs.toFixed(2)} ms`
      : `${(durationMs / 1000).toFixed(2)} s`;

  return (
    <div
      className={`inline-flex items-center gap-2 px-3 py-1.5 rounded-full border ${styles} cl-scale-pop`}
    >
      {tier === "fast" ? <Zap size={14} /> : <Clock size={14} />}
      <span className="font-mono text-xs">{display}</span>
      {operation && (
        <span className="text-xs opacity-80 pl-1.5 border-l border-current/30">
          {operation}
        </span>
      )}
    </div>
  );
}
