import { AlertTriangle, Info, ShieldAlert } from "lucide-react";
import type { ReactNode } from "react";

interface StatusBannerProps {
  type?: "warning" | "danger" | "info";
  title?: string;
  message: ReactNode;
}

export function StatusBanner({ type = "warning", title, message }: StatusBannerProps) {
  const config = {
    warning: {
      bg: "bg-[#FDF6EC] border-[#F5DAB1]",
      icon: <AlertTriangle size={18} className="text-[var(--cl-warning)]" />,
      titleColor: "text-[#B88230]",
    },
    danger: {
      bg: "bg-[#FEF0F0] border-[#FBC4C4]",
      icon: <ShieldAlert size={18} className="text-[var(--cl-danger)]" />,
      titleColor: "text-[#C45656]",
    },
    info: {
      bg: "bg-[#ECF5FF] border-[#BFDFFF]",
      icon: <Info size={18} className="text-[var(--cl-primary)]" />,
      titleColor: "text-[var(--cl-primary-dark)]",
    },
  }[type];

  return (
    <div className={`flex items-start gap-3 px-4 py-3 rounded-md border ${config.bg}`}>
      <div className="mt-0.5 shrink-0">{config.icon}</div>
      <div className="text-sm text-[var(--cl-text-regular)] leading-relaxed">
        {title && <div className={`${config.titleColor} mb-0.5`}>{title}</div>}
        <div>{message}</div>
      </div>
    </div>
  );
}
