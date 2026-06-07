import type { ReactNode } from "react";
import { ChevronRight, Home } from "lucide-react";

interface PageHeaderProps {
  title: string;
  subtitle?: string;
  breadcrumb?: string[];
  actions?: ReactNode;
  badge?: ReactNode;
}

export function PageHeader({ title, subtitle, breadcrumb = [], actions, badge }: PageHeaderProps) {
  return (
    <div className="mb-6 cl-fade-up">
      {breadcrumb.length > 0 && (
        <nav className="flex items-center gap-1.5 text-xs text-[var(--cl-text-secondary)] mb-3">
          <Home size={12} />
          {breadcrumb.map((item, i) => (
            <span key={i} className="inline-flex items-center gap-1.5">
              <ChevronRight size={12} className="text-[var(--cl-text-placeholder)]" />
              <span className={i === breadcrumb.length - 1 ? "text-[var(--cl-text-regular)]" : ""}>
                {item}
              </span>
            </span>
          ))}
        </nav>
      )}
      <div className="flex items-start justify-between gap-4 flex-wrap">
        <div>
          <div className="flex items-center gap-2.5">
            <h1 className="text-[24px] leading-tight tracking-tight text-[var(--cl-text-primary)]">
              {title}
            </h1>
            {badge}
          </div>
          {subtitle && (
            <p className="text-sm text-[var(--cl-text-secondary)] mt-1.5 max-w-2xl">{subtitle}</p>
          )}
        </div>
        {actions && <div className="flex items-center gap-2">{actions}</div>}
      </div>
    </div>
  );
}
