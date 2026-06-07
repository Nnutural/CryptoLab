import type { ReactNode } from "react";
import { Sparkles } from "lucide-react";

export function EmptyState({
  icon,
  title,
  description,
  action,
}: {
  icon?: ReactNode;
  title: string;
  description?: string;
  action?: ReactNode;
}) {
  return (
    <div className="flex flex-col items-center justify-center text-center py-10 px-6">
      <div className="w-14 h-14 rounded-full bg-[var(--cl-bg-page)] inline-flex items-center justify-center text-[var(--cl-text-placeholder)] mb-3">
        {icon ?? <Sparkles size={22} />}
      </div>
      <div className="text-sm text-[var(--cl-text-regular)]">{title}</div>
      {description && (
        <div className="text-xs text-[var(--cl-text-secondary)] mt-1.5 max-w-sm">{description}</div>
      )}
      {action && <div className="mt-4">{action}</div>}
    </div>
  );
}
