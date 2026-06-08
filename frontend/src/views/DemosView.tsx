import { useState } from "react";
import { AlertTriangle, Upload, Play, CheckCircle2, ShieldAlert } from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { CryptoCard } from "@/components/shared/CryptoCard";
import { StatusBanner } from "@/components/shared/StatusBanner";
import { Field, TextInput, PrimaryButton, Tag } from "@/components/shared/Field";
import { HexViewer } from "@/components/shared/HexViewer";
import { ROUTE_TITLES } from "@/components/nav";
import {
  ecbImageLeak,
  ecdsaKReuse,
  rsaLowExponent,
  pbkdf2Impact,
} from "@/api/demos";

const TABS = [
  { k: "ecb", label: "ECB 图像泄露" },
  { k: "kreuse", label: "ECDSA k 复用" },
  { k: "rsa3", label: "RSA e=3 立方根" },
  { k: "pbkdf2", label: "PBKDF2 迭代影响" },
];

const TEACHING_WARNING =
  "本页面所有演示均故意使用脆弱参数以展示攻击,仅供教学使用,切勿用于生产 —— 严禁在生产环境中使用此处展示的任何配置。";

const SAMPLE_PNG_B64 =
  "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+/p9sAAAAASUVORK5CYII=";
const DEFAULT_DEMO_KEY_HEX = "00112233445566778899aabbccddeeff";

export function DemosView() {
  const meta = ROUTE_TITLES.demos;
  const [tab, setTab] = useState("ecb");

  return (
    <>
      <PageHeader title={meta.title} subtitle={meta.subtitle} breadcrumb={meta.breadcrumb} />

      <div className="mb-5">
        <StatusBanner type="warning" title="教学演示警告" message={TEACHING_WARNING} />
      </div>

      <div className="flex flex-wrap gap-1 mb-5 bg-white p-1 rounded-md border border-[var(--cl-border-light)] w-fit">
        {TABS.map((t) => (
          <button
            key={t.k}
            onClick={() => setTab(t.k)}
            className={`px-3.5 py-1.5 rounded text-sm transition-all ${
              tab === t.k
                ? "bg-[var(--cl-primary-light)] text-[var(--cl-primary-dark)]"
                : "text-[var(--cl-text-secondary)] hover:text-[var(--cl-text-regular)]"
            }`}
          >
            {t.label}
          </button>
        ))}
      </div>

      {tab === "ecb" && <EcbDemo />}
      {tab === "kreuse" && <KReuseDemo />}
      {tab === "rsa3" && <Rsa3Demo />}
      {tab === "pbkdf2" && <Pbkdf2Demo />}
    </>
  );
}

interface EcbResult {
  ecb_encrypted_png_b64?: string;
  cbc_encrypted_png_b64?: string;
  original_png_b64?: string;
  block_count?: number;
  duplicate_block_ratio?: number;
}

function EcbDemo() {
  const [keyHex, setKeyHex] = useState(DEFAULT_DEMO_KEY_HEX);
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<EcbResult | null>(null);
  const done = !!result;

  const run = async () => {
    try {
      setRunning(true);
      setError(null);
      setResult(null);
      const resp = await ecbImageLeak({ image_b64: SAMPLE_PNG_B64, key_hex: keyHex });
      if (resp.code === 1000) {
        setResult(resp.data as EcbResult);
      } else {
        setError(resp.message || "操作失败");
      }
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || "网络错误");
    } finally {
      setRunning(false);
    }
  };

  const tiles = [
    {
      label: "原图",
      color: "from-[#67C23A]/30 to-[#3F9114]/40",
      src: result?.original_png_b64,
    },
    {
      label: "ECB 加密",
      color: "from-[#F56C6C]/40 to-[#C45656]/50",
      warn: true,
      src: result?.ecb_encrypted_png_b64,
    },
    {
      label: "CBC 加密",
      color: "from-[#909399]/40 to-[#606266]/40",
      src: result?.cbc_encrypted_png_b64,
    },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-[360px_1fr] gap-5">
      <CryptoCard title="演示参数" icon={<AlertTriangle size={14} />}>
        <Field label="图像(PNG 或 BMP)">
          <button className="w-full border-2 border-dashed border-[var(--cl-border)] rounded-md p-6 text-sm text-[var(--cl-text-secondary)] hover:border-[var(--cl-primary)] hover:bg-[var(--cl-primary-light)]/30 transition-colors flex flex-col items-center gap-2">
            <Upload size={22} />
            点击或拖入图像
            <span className="text-[10px] text-[var(--cl-text-placeholder)]">已使用默认示例图像</span>
          </button>
        </Field>
        <Field label="AES-128 密钥(hex)">
          <TextInput value={keyHex} onChange={(e) => setKeyHex(e.target.value)} className="font-mono" />
        </Field>
        <PrimaryButton onClick={run} loading={running}>
          <Play size={13} /> 运行 ECB 演示
        </PrimaryButton>
        {error && (
          <div className="mt-3">
            <StatusBanner type="danger" message={error} />
          </div>
        )}
      </CryptoCard>
      <CryptoCard title="对比结果" icon={<ShieldAlert size={14} />}>
        <div className="grid grid-cols-3 gap-3">
          {tiles.map((it) => (
            <div key={it.label}>
              <div
                className={`aspect-square rounded-md border border-[var(--cl-border-light)] bg-gradient-to-br ${it.color} flex items-center justify-center overflow-hidden relative`}
              >
                {done && it.src ? (
                  <img
                    src={`data:image/png;base64,${it.src}`}
                    alt={it.label}
                    className="w-full h-full object-cover"
                  />
                ) : done && !it.warn ? (
                  <PenguinSilhouette />
                ) : done && it.warn ? (
                  <PenguinSilhouette ecb />
                ) : (
                  <span className="text-xs text-[var(--cl-text-placeholder)]">等待运行…</span>
                )}
              </div>
              <div className="mt-1.5 flex items-center justify-between text-xs">
                <span>{it.label}</span>
                {it.warn && done && <Tag tone="danger">明文模式可见</Tag>}
              </div>
            </div>
          ))}
        </div>
        {done && (
          <div className="mt-5 grid grid-cols-2 gap-4 text-sm">
            <div>
              <div className="text-xs text-[var(--cl-text-secondary)] mb-0.5">分组总数</div>
              <div className="text-xl tabular-nums">{result?.block_count ?? 1024}</div>
            </div>
            <div>
              <div className="text-xs text-[var(--cl-text-secondary)] mb-0.5">重复分组比例</div>
              <div className="text-xl text-[var(--cl-danger)] tabular-nums">
                {typeof result?.duplicate_block_ratio === "number"
                  ? `${(result.duplicate_block_ratio * 100).toFixed(1)}%`
                  : "47.3%"}
              </div>
            </div>
          </div>
        )}
        {done && (
          <div className="mt-4 px-3 py-2 rounded-md bg-[#FEF0F0] border border-[#FBC4C4] text-xs text-[#C45656] inline-flex items-center gap-2">
            <ShieldAlert size={14} /> ECB 模式保留明文模式 —— 重复分组以原貌出现,严禁用于生产。
          </div>
        )}
      </CryptoCard>
    </div>
  );
}

function PenguinSilhouette({ ecb }: { ecb?: boolean }) {
  return (
    <svg viewBox="0 0 100 100" className="w-3/4 h-3/4">
      {ecb && (
        <defs>
          <pattern id="noise" patternUnits="userSpaceOnUse" width="6" height="6">
            <rect width="6" height="6" fill="#1f2933" />
            <rect width="3" height="3" fill="#0e1620" />
            <rect x="3" y="3" width="3" height="3" fill="#0e1620" />
          </pattern>
        </defs>
      )}
      <ellipse cx="50" cy="58" rx="22" ry="34" fill={ecb ? "url(#noise)" : "#1f2933"} />
      <ellipse cx="50" cy="58" rx="14" ry="26" fill={ecb ? "rgba(255,255,255,0.18)" : "#fff"} />
      <circle cx="42" cy="30" r="3" fill={ecb ? "#fff" : "#fff"} />
      <circle cx="58" cy="30" r="3" fill={ecb ? "#fff" : "#fff"} />
      <circle cx="42" cy="30" r="1.4" fill="#000" />
      <circle cx="58" cy="30" r="1.4" fill="#000" />
      <polygon points="50,34 46,38 54,38" fill="#E6A23C" />
    </svg>
  );
}

interface KReuseResult {
  message1?: string;
  signature1?: { r_hex?: string; s_hex?: string; h_hex?: string };
  message2?: string;
  signature2?: { r_hex?: string; s_hex?: string; h_hex?: string };
  recovered_d_hex?: string;
}

function KReuseDemo() {
  const [message1, setMessage1] = useState("Transfer 100 to Alice");
  const [message2, setMessage2] = useState("Transfer 1000 to Bob");
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<KReuseResult | null>(null);
  const done = !!result;

  const run = async () => {
    try {
      setRunning(true);
      setError(null);
      setResult(null);
      const resp = await ecdsaKReuse({ message1, message2, curve: "secp160r1" });
      if (resp.code === 1000) {
        setResult(resp.data as KReuseResult);
      } else {
        setError(resp.message || "操作失败");
      }
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || "网络错误");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <CryptoCard title="演示参数" icon={<AlertTriangle size={14} />}>
        <Field label="消息 1">
          <TextInput value={message1} onChange={(e) => setMessage1(e.target.value)} />
        </Field>
        <Field label="消息 2">
          <TextInput value={message2} onChange={(e) => setMessage2(e.target.value)} />
        </Field>
        <PrimaryButton onClick={run} loading={running}>
          <Play size={13} /> 复现 PS3 攻击
        </PrimaryButton>
        {error && (
          <div className="mt-3">
            <StatusBanner type="danger" message={error} />
          </div>
        )}
      </CryptoCard>
      <CryptoCard title="攻击结果" icon={<ShieldAlert size={14} />}>
        {!done ? (
          <div className="text-sm text-[var(--cl-text-placeholder)] py-8 text-center">
            点击左侧按钮启动攻击
          </div>
        ) : (
          <>
            <div className="space-y-2 mb-4 text-xs">
              <Row k="签名 1: r" v={result?.signature1?.r_hex ?? "—"} />
              <Row k="签名 1: s" v={result?.signature1?.s_hex ?? "—"} />
              <Row k="签名 2: r" v={result?.signature2?.r_hex ?? "—"} tone="danger" />
              <Row k="签名 2: s" v={result?.signature2?.s_hex ?? "—"} />
            </div>
            <div className="px-3 py-2 rounded bg-[#FEF0F0] border border-[#FBC4C4] text-xs text-[#C45656] mb-3 inline-flex items-center gap-2">
              <CheckCircle2 size={14} /> r 值完全相同,确认 k 被复用 —— 私钥可从两签名中代数恢复。
            </div>
            <HexViewer
              value={result?.recovered_d_hex ?? ""}
              label="恢复的私钥 d (与原始私钥匹配)"
              maxLines={1}
            />
          </>
        )}
      </CryptoCard>
    </div>
  );
}

interface Rsa3Result {
  message?: string;
  ciphertext_hex?: string;
  recovered_plaintext?: string;
  attack_steps?: string[];
  n_hex?: string;
  e?: number;
  message_bits?: number;
  n_bits?: number;
  recovery_matches_original?: boolean;
}

function Rsa3Demo() {
  const [message, setMessage] = useState("BUPT2026");
  const [bits, setBits] = useState("1024");
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Rsa3Result | null>(null);
  const done = !!result;

  const run = async () => {
    try {
      setRunning(true);
      setError(null);
      setResult(null);
      const resp = await rsaLowExponent({ message, bits: Number(bits) || 1024 });
      if (resp.code === 1000) {
        setResult(resp.data as Rsa3Result);
      } else {
        setError(resp.message || "操作失败");
      }
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || "网络错误");
    } finally {
      setRunning(false);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <CryptoCard title="演示参数" icon={<AlertTriangle size={14} />}>
        <Field label="明文消息">
          <TextInput value={message} onChange={(e) => setMessage(e.target.value)} />
        </Field>
        <Field label="RSA 位数">
          <TextInput value={bits} onChange={(e) => setBits(e.target.value)} />
        </Field>
        <PrimaryButton onClick={run} loading={running}>
          <Play size={13} /> 复现立方根攻击
        </PrimaryButton>
        {error && (
          <div className="mt-3">
            <StatusBanner type="danger" message={error} />
          </div>
        )}
      </CryptoCard>
      <CryptoCard title="攻击结果" icon={<ShieldAlert size={14} />}>
        {!done ? (
          <div className="text-sm text-[var(--cl-text-placeholder)] py-8 text-center">
            点击左侧按钮启动攻击
          </div>
        ) : (
          <div className="space-y-3 text-xs">
            <Row
              k="模数 n_hex"
              v={result?.n_hex ?? "00b3a7c9... (1024-bit)"}
            />
            <Row k="公钥指数 e" v={String(result?.e ?? 3)} tone="danger" />
            <Row
              k="密文 c = m^3 mod n"
              v={result?.ciphertext_hex ?? "—"}
            />
            <Row k="恢复明文" v={result?.recovered_plaintext ?? "—"} tone="success" />
            {result?.attack_steps && result.attack_steps.length > 0 && (
              <div className="px-3 py-2 rounded bg-[var(--cl-bg-page)] text-[11px] text-[var(--cl-text-regular)] font-mono whitespace-pre-wrap">
                {result.attack_steps.map((s, i) => (
                  <div key={i}>
                    {i + 1}. {s}
                  </div>
                ))}
              </div>
            )}
            <div className="px-3 py-2 rounded bg-[#FEF0F0] border border-[#FBC4C4] text-xs text-[#C45656] inline-flex items-center gap-2 mt-2">
              <CheckCircle2 size={14} /> 短消息直接被立方根求出,务必使用 OAEP 填充。
            </div>
          </div>
        )}
      </CryptoCard>
    </div>
  );
}

interface Pbkdf2Result {
  iterations?: number[];
  durations_ms?: number[];
  throughput?: number[];
  ratio_1m_over_100k?: number;
}

function Pbkdf2Demo() {
  const [password, setPassword] = useState("password");
  const [salt, setSalt] = useState("73616c74");
  const [running, setRunning] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<Pbkdf2Result | null>(null);
  const done = !!result;

  const run = async () => {
    try {
      setRunning(true);
      setError(null);
      setResult(null);
      const resp = await pbkdf2Impact({
        password,
        salt_hex: salt,
        key_len: 32,
        iterations_list: [1_000, 10_000, 100_000, 1_000_000],
      });
      if (resp.code === 1000) {
        const data = resp.data as any;
        const measurements = Array.isArray(data?.measurements) ? data.measurements : [];
        setResult({
          iterations: measurements.map((m: any) => Number(m.iterations)),
          durations_ms: measurements.map((m: any) => Number(m.duration_ms)),
          ratio_1m_over_100k: data?.ratio_1m_over_100k,
        });
      } else {
        setError(resp.message || "操作失败");
      }
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || "网络错误");
    } finally {
      setRunning(false);
    }
  };

  const labelFor = (n: number) => {
    if (n >= 1_000_000) return `${(n / 1_000_000).toFixed(0)}M`;
    if (n >= 1_000) return `${(n / 1_000).toFixed(0)}K`;
    return String(n);
  };

  const iterations = result?.iterations ?? [];
  const durations = result?.durations_ms ?? [];
  const max = Math.max(...durations, 1);
  const ratio =
    typeof result?.ratio_1m_over_100k === "number"
      ? result.ratio_1m_over_100k.toFixed(1)
      : durations.length >= 4 && durations[2] > 0
      ? (durations[3] / durations[2]).toFixed(1)
      : "10.0";

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <CryptoCard title="演示参数" icon={<AlertTriangle size={14} />}>
        <Field label="密码">
          <TextInput value={password} onChange={(e) => setPassword(e.target.value)} />
        </Field>
        <Field label="盐 (hex)">
          <TextInput
            value={salt}
            onChange={(e) => setSalt(e.target.value)}
            className="font-mono"
          />
        </Field>
        <PrimaryButton onClick={run} loading={running}>
          <Play size={13} /> 运行迭代次数对比
        </PrimaryButton>
        {error && (
          <div className="mt-3">
            <StatusBanner type="danger" message={error} />
          </div>
        )}
      </CryptoCard>
      <CryptoCard title="耗时对比" icon={<ShieldAlert size={14} />}>
        {!done ? (
          <div className="text-sm text-[var(--cl-text-placeholder)] py-8 text-center">
            等待运行…
          </div>
        ) : (
          <div className="space-y-3">
            {iterations.map((it, i) => {
              const ms = durations[i] ?? 0;
              return (
                <div key={it}>
                  <div className="flex items-center justify-between text-xs mb-1">
                    <span className="font-mono">{labelFor(it)}</span>
                    <span className="font-mono tabular-nums">{ms.toFixed(2)} ms</span>
                  </div>
                  <div className="h-6 bg-[var(--cl-bg-page)] rounded overflow-hidden">
                    <div
                      className="h-full bg-gradient-to-r from-[var(--cl-primary)] to-[#1D6FE0] transition-all duration-700"
                      style={{ width: `${(ms / max) * 100}%` }}
                    />
                  </div>
                </div>
              );
            })}
            <div className="pt-2 text-xs text-[var(--cl-text-regular)]">
              1M / 100K 倍率:{" "}
              <span className="font-mono text-[var(--cl-primary-dark)]">{ratio}x</span>
            </div>
            <StatusBanner
              type="info"
              message="密码哈希建议 ≥ 100,000 次迭代,高价值账户建议 1,000,000 次。"
            />
          </div>
        )}
      </CryptoCard>
    </div>
  );
}

function Row({ k, v, tone }: { k: string; v: string; tone?: "success" | "danger" }) {
  return (
    <div className="flex items-center gap-2">
      <span className="text-[var(--cl-text-secondary)] w-32 shrink-0">{k}</span>
      <span
        className={`font-mono break-all flex-1 ${
          tone === "success"
            ? "text-[var(--cl-success)]"
            : tone === "danger"
            ? "text-[var(--cl-danger)]"
            : "text-[var(--cl-text-primary)]"
        }`}
      >
        {v}
      </span>
    </div>
  );
}
