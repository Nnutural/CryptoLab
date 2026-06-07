import { useState } from "react";
import { AlertTriangle, Upload, Play, CheckCircle2, ShieldAlert } from "lucide-react";
import { PageHeader } from "../shared/PageHeader";
import { CryptoCard } from "../shared/CryptoCard";
import { StatusBanner } from "../shared/StatusBanner";
import { Field, TextInput, PrimaryButton, Tag } from "../shared/Field";
import { HexViewer } from "../shared/HexViewer";
import { ROUTE_TITLES } from "../nav";

const TABS = [
  { k: "ecb", label: "ECB 图像泄露" },
  { k: "kreuse", label: "ECDSA k 复用" },
  { k: "rsa3", label: "RSA e=3 立方根" },
  { k: "pbkdf2", label: "PBKDF2 迭代影响" },
];

export function DemosView() {
  const meta = ROUTE_TITLES.demos;
  const [tab, setTab] = useState("ecb");

  return (
    <>
      <PageHeader title={meta.title} subtitle={meta.subtitle} breadcrumb={meta.breadcrumb} />

      <div className="mb-5">
        <StatusBanner
          type="warning"
          title="教学演示警告"
          message="本页面所有演示均故意使用脆弱参数以展示攻击,严禁在生产环境中使用此处展示的任何配置。"
        />
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

function EcbDemo() {
  const [done, setDone] = useState(false);
  const [running, setRunning] = useState(false);
  const run = () => {
    setRunning(true);
    setDone(false);
    setTimeout(() => {
      setRunning(false);
      setDone(true);
    }, 900);
  };
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
          <TextInput defaultValue="00112233445566778899aabbccddeeff" className="font-mono" />
        </Field>
        <PrimaryButton onClick={run} loading={running}>
          <Play size={13} /> 运行 ECB 演示
        </PrimaryButton>
      </CryptoCard>
      <CryptoCard title="对比结果" icon={<ShieldAlert size={14} />}>
        <div className="grid grid-cols-3 gap-3">
          {[
            { label: "原图", color: "from-[#67C23A]/30 to-[#3F9114]/40" },
            { label: "ECB 加密", color: "from-[#F56C6C]/40 to-[#C45656]/50", warn: true },
            { label: "CBC 加密", color: "from-[#909399]/40 to-[#606266]/40" },
          ].map((it) => (
            <div key={it.label}>
              <div
                className={`aspect-square rounded-md border border-[var(--cl-border-light)] bg-gradient-to-br ${it.color} flex items-center justify-center overflow-hidden relative`}
              >
                {done && !it.warn && <PenguinSilhouette />}
                {done && it.warn && <PenguinSilhouette ecb />}
                {!done && (
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
              <div className="text-xl tabular-nums">1024</div>
            </div>
            <div>
              <div className="text-xs text-[var(--cl-text-secondary)] mb-0.5">重复分组比例</div>
              <div className="text-xl text-[var(--cl-danger)] tabular-nums">47.3%</div>
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

function KReuseDemo() {
  const [done, setDone] = useState(false);
  const [running, setRunning] = useState(false);
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <CryptoCard title="演示参数" icon={<AlertTriangle size={14} />}>
        <Field label="消息 1">
          <TextInput defaultValue="Transfer 100 to Alice" />
        </Field>
        <Field label="消息 2">
          <TextInput defaultValue="Transfer 1000 to Bob" />
        </Field>
        <PrimaryButton
          onClick={() => {
            setRunning(true);
            setTimeout(() => {
              setRunning(false);
              setDone(true);
            }, 800);
          }}
          loading={running}
        >
          <Play size={13} /> 复现 PS3 攻击
        </PrimaryButton>
      </CryptoCard>
      <CryptoCard title="攻击结果" icon={<ShieldAlert size={14} />}>
        {!done ? (
          <div className="text-sm text-[var(--cl-text-placeholder)] py-8 text-center">
            点击左侧按钮启动攻击
          </div>
        ) : (
          <>
            <div className="space-y-2 mb-4 text-xs">
              <Row k="签名 1: r" v="aabbccdd11223344..." />
              <Row k="签名 1: s" v="ccdd5566aabbeeff..." />
              <Row k="签名 2: r" v="aabbccdd11223344..." tone="danger" />
              <Row k="签名 2: s" v="eeff7788aabbccdd..." />
            </div>
            <div className="px-3 py-2 rounded bg-[#FEF0F0] border border-[#FBC4C4] text-xs text-[#C45656] mb-3 inline-flex items-center gap-2">
              <CheckCircle2 size={14} /> r 值完全相同,确认 k 被复用 —— 私钥可从两签名中代数恢复。
            </div>
            <HexViewer
              value="0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b"
              label="恢复的私钥 d (与原始私钥匹配)"
              maxLines={1}
            />
          </>
        )}
      </CryptoCard>
    </div>
  );
}

function Rsa3Demo() {
  const [done, setDone] = useState(false);
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <CryptoCard title="演示参数" icon={<AlertTriangle size={14} />}>
        <Field label="明文消息">
          <TextInput defaultValue="BUPT2026" />
        </Field>
        <Field label="RSA 位数">
          <TextInput defaultValue="1024" />
        </Field>
        <PrimaryButton onClick={() => setDone(true)}>
          <Play size={13} /> 复现立方根攻击
        </PrimaryButton>
      </CryptoCard>
      <CryptoCard title="攻击结果" icon={<ShieldAlert size={14} />}>
        {!done ? (
          <div className="text-sm text-[var(--cl-text-placeholder)] py-8 text-center">
            点击左侧按钮启动攻击
          </div>
        ) : (
          <div className="space-y-3 text-xs">
            <Row k="模数 n_hex" v="00b3a7c9... (1024-bit)" />
            <Row k="公钥指数 e" v="3" tone="danger" />
            <Row k="密文 c = m^3 mod n" v="2f8a1c…" />
            <Row k="∛c 立方根" v="42 55 50 54 32 30 32 36" />
            <Row k="恢复明文" v="BUPT2026" tone="success" />
            <div className="px-3 py-2 rounded bg-[#FEF0F0] border border-[#FBC4C4] text-xs text-[#C45656] inline-flex items-center gap-2 mt-2">
              <CheckCircle2 size={14} /> 短消息直接被立方根求出,务必使用 OAEP 填充。
            </div>
          </div>
        )}
      </CryptoCard>
    </div>
  );
}

function Pbkdf2Demo() {
  const [done, setDone] = useState(false);
  const data = [
    { it: "1K", ms: 0.5 },
    { it: "10K", ms: 4.8 },
    { it: "100K", ms: 45.2 },
    { it: "1M", ms: 452.1 },
  ];
  const max = 452.1;
  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-5">
      <CryptoCard title="演示参数" icon={<AlertTriangle size={14} />}>
        <Field label="密码">
          <TextInput defaultValue="password" />
        </Field>
        <Field label="盐 (hex)">
          <TextInput defaultValue="73616c74" className="font-mono" />
        </Field>
        <PrimaryButton onClick={() => setDone(true)}>
          <Play size={13} /> 运行迭代次数对比
        </PrimaryButton>
      </CryptoCard>
      <CryptoCard title="耗时对比" icon={<ShieldAlert size={14} />}>
        {!done ? (
          <div className="text-sm text-[var(--cl-text-placeholder)] py-8 text-center">
            等待运行…
          </div>
        ) : (
          <div className="space-y-3">
            {data.map((d) => (
              <div key={d.it}>
                <div className="flex items-center justify-between text-xs mb-1">
                  <span className="font-mono">{d.it}</span>
                  <span className="font-mono tabular-nums">{d.ms} ms</span>
                </div>
                <div className="h-6 bg-[var(--cl-bg-page)] rounded overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-[var(--cl-primary)] to-[#1D6FE0] transition-all duration-700"
                    style={{ width: `${(d.ms / max) * 100}%` }}
                  />
                </div>
              </div>
            ))}
            <div className="pt-2 text-xs text-[var(--cl-text-regular)]">
              1M / 100K 倍率: <span className="font-mono text-[var(--cl-primary-dark)]">10.0x</span>
            </div>
            <StatusBanner type="info" message="密码哈希建议 ≥ 100,000 次迭代,高价值账户建议 1,000,000 次。" />
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
