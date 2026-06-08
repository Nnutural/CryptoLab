interface StateMatrixGridProps {
  state: string;
  highlight?: number[];
  label?: string;
}

function byteAt(state: string, index: number): string {
  const clean = state.replace(/\s+/g, "").toUpperCase();
  return clean.slice(index * 2, index * 2 + 2).padEnd(2, "-");
}

export function StateMatrixGrid({ state, highlight = [], label }: StateMatrixGridProps) {
  const highlighted = new Set(highlight);
  const cells = Array.from({ length: 16 }, (_, visualIndex) => {
    const row = Math.floor(visualIndex / 4);
    const col = visualIndex % 4;
    const byteIndex = row + 4 * col;
    const active = highlighted.has(byteIndex);
    return { byteIndex, value: byteAt(state, byteIndex), active };
  });

  return (
    <div className="min-w-0">
      {label && <div className="mb-2 text-[11px] text-[var(--cl-text-secondary)]">{label}</div>}
      <div className="grid grid-cols-4 gap-1.5 w-full max-w-[220px]">
        {cells.map((cell) => (
          <div
            key={cell.byteIndex}
            className={`aspect-square min-w-0 rounded border bg-[var(--cl-bg-code)] font-mono text-[12px] sm:text-[13px] flex items-center justify-center transition-all duration-300 ease-out ${
              cell.active
                ? "border-[var(--cl-warning)] bg-[#FDF6EC] text-[#B88230] shadow-[0_0_0_2px_rgba(230,162,60,0.16)] cl-scale-pop"
                : "border-[var(--cl-border-light)] text-[var(--cl-text-primary)]"
            }`}
            title={`state[${cell.byteIndex}]`}
          >
            {cell.value}
          </div>
        ))}
      </div>
    </div>
  );
}
