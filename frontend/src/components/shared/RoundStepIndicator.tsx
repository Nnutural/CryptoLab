import { Check } from "lucide-react";

export type AesStepName = "SubBytes" | "ShiftRows" | "MixColumns" | "AddRoundKey";

const STEPS: AesStepName[] = ["SubBytes", "ShiftRows", "MixColumns", "AddRoundKey"];

export function RoundStepIndicator({
  current,
  finalRound,
}: {
  current: AesStepName;
  finalRound?: boolean;
}) {
  const currentIndex = STEPS.indexOf(current);

  return (
    <div className="flex flex-wrap items-center gap-2">
      {STEPS.map((step, index) => {
        const omitted = finalRound && step === "MixColumns";
        const done = index < currentIndex && !omitted;
        const active = step === current;
        return (
          <div key={step} className="flex items-center gap-2">
            <span
              className={`inline-flex items-center gap-1.5 rounded-full border px-2.5 py-1 text-[11px] transition-all duration-300 ${
                omitted
                  ? "border-dashed border-[var(--cl-border)] text-[var(--cl-text-placeholder)]"
                  : active
                  ? "border-[var(--cl-primary)] bg-[var(--cl-primary-light)] text-[var(--cl-primary-dark)] cl-pulse"
                  : done
                  ? "border-[var(--cl-border-light)] bg-[var(--cl-bg-page)] text-[var(--cl-text-secondary)]"
                  : "border-dashed border-[var(--cl-border)] text-[var(--cl-text-placeholder)]"
              }`}
            >
              {done && <Check size={12} />}
              <span>{step}</span>
            </span>
            {index < STEPS.length - 1 && (
              <span className="text-[var(--cl-text-placeholder)]">→</span>
            )}
          </div>
        );
      })}
    </div>
  );
}
