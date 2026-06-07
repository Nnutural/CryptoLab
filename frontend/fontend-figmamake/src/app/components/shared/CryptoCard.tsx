import type { ReactNode } from "react";

interface CryptoCardProps {
  title?: ReactNode;
  subtitle?: ReactNode;
  icon?: ReactNode;
  extra?: ReactNode;
  children: ReactNode;
  className?: string;
  bodyClassName?: string;
}

export function CryptoCard({
  title,
  subtitle,
  icon,
  extra,
  children,
  className = "",
  bodyClassName = "",
}: CryptoCardProps) {
  return (
    <div
      className={`bg-white rounded-lg border border-[var(--cl-border-light)] shadow-[0_1px_4px_rgba(0,0,0,0.04)] hover:shadow-[0_4px_12px_rgba(0,0,0,0.06)] transition-shadow duration-200 ${className}`}
    >
      {(title || extra) && (
        <div className="flex items-center justify-between px-5 py-3.5 border-b border-[var(--cl-border-light)]">
          <div className="flex items-center gap-2.5 min-w-0">
            {icon && (
              <span className="inline-flex items-center justify-center w-7 h-7 rounded-md bg-[var(--cl-primary-light)] text-[var(--cl-primary)]">
                {icon}
              </span>
            )}
            <div className="min-w-0">
              {title && (
                <div className="text-[15px] text-[var(--cl-text-primary)] truncate">{title}</div>
              )}
              {subtitle && (
                <div className="text-xs text-[var(--cl-text-secondary)] mt-0.5 truncate">
                  {subtitle}
                </div>
              )}
            </div>
          </div>
          {extra && <div className="shrink-0 ml-3">{extra}</div>}
        </div>
      )}
      <div className={`p-5 ${bodyClassName}`}>{children}</div>
    </div>
  );
}
