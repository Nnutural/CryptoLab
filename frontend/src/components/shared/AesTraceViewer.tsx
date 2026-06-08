import { useEffect, useMemo, useState, type ButtonHTMLAttributes } from "react";
import {
  ArrowRight,
  BookOpen,
  ChevronLeft,
  ChevronRight,
  Pause,
  Play,
  RotateCcw,
  Timer,
} from "lucide-react";
import type { AesRoundTrace, AesTrace } from "@/api/symmetric";
import { StateMatrixGrid } from "./StateMatrixGrid";
import { RoundStepIndicator, type AesStepName } from "./RoundStepIndicator";
import { TimingBarChart } from "./TimingBarChart";

interface TraceStep {
  round: AesRoundTrace;
  phase: AesStepName;
  before: string;
  after: string;
}

function changedIndices(before: string, after: string): number[] {
  const cleanBefore = before.replace(/\s+/g, "");
  const cleanAfter = after.replace(/\s+/g, "");
  const indices: number[] = [];
  for (let i = 0; i < 16; i += 1) {
    if (cleanBefore.slice(i * 2, i * 2 + 2) !== cleanAfter.slice(i * 2, i * 2 + 2)) {
      indices.push(i);
    }
  }
  return indices;
}

function makeSteps(trace: AesTrace): TraceStep[] {
  return trace.rounds.flatMap((round, index) => {
    const roundStart = index === 0 ? trace.initial_add_round_key : trace.rounds[index - 1].after_add_round_key;
    const steps: TraceStep[] = [
      {
        round,
        phase: "SubBytes",
        before: roundStart,
        after: round.after_sub_bytes,
      },
      {
        round,
        phase: "ShiftRows",
        before: round.after_sub_bytes,
        after: round.after_shift_rows,
      },
    ];
    if (round.after_mix_columns) {
      steps.push({
        round,
        phase: "MixColumns",
        before: round.after_shift_rows,
        after: round.after_mix_columns,
      });
    }
    steps.push({
      round,
      phase: "AddRoundKey",
      before: round.after_mix_columns ?? round.after_shift_rows,
      after: round.after_add_round_key,
    });
    return steps;
  });
}

function IconButton({
  title,
  children,
  ...props
}: ButtonHTMLAttributes<HTMLButtonElement> & { title: string }) {
  return (
    <button
      type="button"
      title={title}
      aria-label={title}
      className="h-8 w-8 rounded-md border border-[var(--cl-border)] bg-white text-[var(--cl-text-regular)] hover:border-[var(--cl-primary)] hover:bg-[var(--cl-primary-light)] hover:text-[var(--cl-primary)] disabled:opacity-40 disabled:cursor-not-allowed inline-flex items-center justify-center transition-all"
      {...props}
    >
      {children}
    </button>
  );
}

export function AesTraceViewer({ trace }: { trace: AesTrace }) {
  const steps = useMemo(() => makeSteps(trace), [trace]);
  const [stepIndex, setStepIndex] = useState(0);
  const [playing, setPlaying] = useState(false);

  useEffect(() => {
    setStepIndex(0);
    setPlaying(false);
  }, [trace]);

  useEffect(() => {
    if (!playing || steps.length === 0) return;
    const id = window.setInterval(() => {
      setStepIndex((current) => (current + 1 >= steps.length ? 0 : current + 1));
    }, 600);
    return () => window.clearInterval(id);
  }, [playing, steps.length]);

  const current = steps[Math.min(stepIndex, steps.length - 1)];
  const highlight = current ? changedIndices(current.before, current.after) : [];
  const progressLabel = current
    ? `Round ${current.round.round_index} / ${trace.total_rounds} · ${current.phase}`
    : "Ready";

  const goPrev = () => setStepIndex((value) => Math.max(0, value - 1));
  const goNext = () => setStepIndex((value) => Math.min(steps.length - 1, value + 1));
  const reset = () => {
    setPlaying(false);
    setStepIndex(0);
  };

  return (
    <div className="mt-5 bg-white rounded-lg border border-[var(--cl-border-light)] shadow-[0_1px_4px_rgba(0,0,0,0.04)] overflow-hidden cl-fade-up">
      <div className="px-5 py-3.5 border-b border-[var(--cl-border-light)]">
        <div className="flex flex-wrap items-center gap-3">
          <div className="inline-flex items-center gap-2 min-w-0 mr-auto">
            <span className="inline-flex h-8 w-8 items-center justify-center rounded-md bg-[var(--cl-primary-light)] text-[var(--cl-primary)]">
              <BookOpen size={16} />
            </span>
            <div className="min-w-0">
              <div className="text-[15px] text-[var(--cl-text-primary)]">
                AES-{trace.key_size_bits} 加密过程
              </div>
              <div className="text-xs text-[var(--cl-text-secondary)]">{progressLabel}</div>
            </div>
          </div>

          <div className="flex items-center gap-1.5">
            <IconButton title={playing ? "暂停" : "播放"} onClick={() => setPlaying((v) => !v)}>
              {playing ? <Pause size={15} /> : <Play size={15} />}
            </IconButton>
            <IconButton title="上一步" onClick={goPrev} disabled={stepIndex === 0}>
              <ChevronLeft size={16} />
            </IconButton>
            <IconButton title="下一步" onClick={goNext} disabled={stepIndex >= steps.length - 1}>
              <ChevronRight size={16} />
            </IconButton>
            <IconButton title="重置" onClick={reset}>
              <RotateCcw size={14} />
            </IconButton>
          </div>
        </div>
      </div>

      <div className="p-5 space-y-6">
        <section>
          <div className="mb-3 flex items-center justify-between gap-3">
            <div>
              <h3 className="text-[14px] text-[var(--cl-text-primary)]">Round 0 · Initial AddRoundKey</h3>
              <p className="text-xs text-[var(--cl-text-secondary)] mt-0.5">
                Plaintext XOR Round Key 0 = State
              </p>
            </div>
          </div>
          <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr_auto_1fr] gap-4 items-start">
            <StateMatrixGrid label="Plaintext" state={trace.plaintext_hex} />
            <div className="hidden md:flex h-full items-center justify-center text-[var(--cl-text-placeholder)] pt-8">
              XOR
            </div>
            <StateMatrixGrid label="Round Key 0" state={trace.round_keys_hex[0] ?? ""} />
            <div className="hidden md:flex h-full items-center justify-center text-[var(--cl-text-placeholder)] pt-8">
              =
            </div>
            <StateMatrixGrid label="State" state={trace.initial_add_round_key} />
          </div>
        </section>

        {current && (
          <section className="rounded-md border border-[var(--cl-border-light)] bg-[var(--cl-bg-page)]/35 p-4">
            <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
              <div>
                <h3 className="text-[14px] text-[var(--cl-text-primary)]">
                  Round {current.round.round_index}
                </h3>
                <p className="text-xs text-[var(--cl-text-secondary)] mt-0.5">
                  {highlight.length} byte(s) changed in this step
                </p>
              </div>
              <RoundStepIndicator
                current={current.phase}
                finalRound={current.round.after_mix_columns === null}
              />
            </div>

            <div className="grid grid-cols-1 md:grid-cols-[1fr_auto_1fr] gap-4 items-start">
              <StateMatrixGrid label="Before" state={current.before} />
              <div className="hidden md:flex h-full items-center justify-center text-[var(--cl-text-placeholder)] pt-8">
                <ArrowRight size={18} />
              </div>
              <StateMatrixGrid label="After" state={current.after} highlight={highlight} />
            </div>
          </section>
        )}

        <section>
          <div className="mb-3 flex items-center gap-2">
            <Timer size={15} className="text-[var(--cl-primary)]" />
            <h3 className="text-[14px] text-[var(--cl-text-primary)]">每轮耗时(纳秒)</h3>
            <span className="text-[11px] text-[var(--cl-text-secondary)] font-mono">
              key expansion {trace.timings_ns.key_expansion_ns} ns · total {trace.timings_ns.total_ns} ns
            </span>
          </div>
          <TimingBarChart perRoundNs={trace.timings_ns.per_round_ns} />
        </section>
      </div>
    </div>
  );
}
