import { useState, useMemo } from "react";
import { Database, Search, Trash2, Download, Key, ShieldCheck, KeyRound, Lock } from "lucide-react";
import { PageHeader } from "../shared/PageHeader";
import { CryptoCard } from "../shared/CryptoCard";
import { TextInput, GhostButton, Select, Tag } from "../shared/Field";
import { ROUTE_TITLES } from "../nav";

interface KeyItem {
  id: string;
  type: "symmetric" | "rsa_public" | "rsa_private" | "ecc_public" | "ecc_private";
  algo: string;
  label: string;
  pair: string | null;
  created: string;
}

const KEYS: KeyItem[] = [
  { id: "b7e15163-4aed-2b9e-9c87-53d8a2f77e1a", type: "symmetric", algo: "AES-256", label: "My AES-256 key", pair: null, created: "2026-06-07 14:30" },
  { id: "c8f26274-5bfe-3caf-ad98-64e9b3087f2b", type: "rsa_public", algo: "RSA-1024", label: "RSA #1", pair: "d9a37385-…", created: "2026-06-07 14:32" },
  { id: "d9a37385-6cfe-4dbf-be09-75fab4198e3c", type: "rsa_private", algo: "RSA-1024", label: "RSA #1", pair: "c8f26274-…", created: "2026-06-07 14:32" },
  { id: "ea048496-7d0f-5ec0-cf1a-86fbc52a9f4d", type: "ecc_public", algo: "ECC secp160r1", label: "ECC #1", pair: "fb1595a7-…", created: "2026-06-06 11:15" },
  { id: "fb1595a7-8e10-6fd1-d02b-97acd63ba05e", type: "ecc_private", algo: "ECC secp160r1", label: "ECC #1", pair: "ea048496-…", created: "2026-06-06 11:15" },
  { id: "0c26a6b8-9f21-70e2-e13c-a8bde74cb16f", type: "symmetric", algo: "SM4", label: "SM4 测试密钥", pair: null, created: "2026-06-05 09:42" },
];

const TYPE_LABEL: Record<KeyItem["type"], string> = {
  symmetric: "对称密钥",
  rsa_public: "RSA 公钥",
  rsa_private: "RSA 私钥",
  ecc_public: "ECC 公钥",
  ecc_private: "ECC 私钥",
};

const TYPE_TONE: Record<KeyItem["type"], any> = {
  symmetric: "info",
  rsa_public: "primary",
  rsa_private: "warn",
  ecc_public: "success",
  ecc_private: "warn",
};

const TYPE_ICON = {
  symmetric: Lock,
  rsa_public: KeyRound,
  rsa_private: KeyRound,
  ecc_public: ShieldCheck,
  ecc_private: ShieldCheck,
};

export function KeysView() {
  const meta = ROUTE_TITLES.keys;
  const [q, setQ] = useState("");
  const [type, setType] = useState("all");
  const [selected, setSelected] = useState<KeyItem | null>(KEYS[1]);

  const filtered = useMemo(
    () =>
      KEYS.filter(
        (k) =>
          (type === "all" || k.type === type) &&
          (q === "" || k.id.includes(q) || k.label.includes(q) || k.algo.toLowerCase().includes(q.toLowerCase()))
      ),
    [q, type]
  );

  return (
    <>
      <PageHeader
        title={meta.title}
        subtitle={meta.subtitle}
        breadcrumb={meta.breadcrumb}
        actions={
          <>
            <GhostButton>
              <Download size={14} /> 批量导出公钥
            </GhostButton>
          </>
        }
      />

      <CryptoCard className="mb-5" bodyClassName="py-3">
        <div className="flex flex-wrap items-center gap-3">
          <div className="relative">
            <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[var(--cl-text-placeholder)]" />
            <TextInput
              value={q}
              onChange={(e) => setQ(e.target.value)}
              placeholder="按 Key ID / 标签 / 算法搜索…"
              className="pl-8 w-72 font-mono text-xs"
            />
          </div>
          <Select
            value={type}
            onChange={setType}
            options={[
              { value: "all", label: "全部类型" },
              { value: "symmetric", label: "对称密钥" },
              { value: "rsa_public", label: "RSA 公钥" },
              { value: "rsa_private", label: "RSA 私钥" },
              { value: "ecc_public", label: "ECC 公钥" },
              { value: "ecc_private", label: "ECC 私钥" },
            ]}
          />
          <span className="ml-auto text-xs text-[var(--cl-text-secondary)]">
            共 <span className="text-[var(--cl-text-primary)]">{filtered.length}</span> 条 / 总 {KEYS.length}
          </span>
        </div>
      </CryptoCard>

      <div className="grid grid-cols-1 xl:grid-cols-[1fr_360px] gap-5">
        <CryptoCard bodyClassName="p-0" title="密钥列表" icon={<Database size={14} />}>
          <table className="w-full text-sm">
            <thead className="bg-[var(--cl-bg-page)]/60 text-[var(--cl-text-secondary)] text-xs">
              <tr>
                <th className="text-left font-normal px-4 py-2.5">Key ID</th>
                <th className="text-left font-normal px-4 py-2.5">类型</th>
                <th className="text-left font-normal px-4 py-2.5">算法</th>
                <th className="text-left font-normal px-4 py-2.5">标签</th>
                <th className="text-left font-normal px-4 py-2.5">配对密钥</th>
                <th className="text-left font-normal px-4 py-2.5">创建时间</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((k) => {
                const Icon = TYPE_ICON[k.type];
                const active = selected?.id === k.id;
                return (
                  <tr
                    key={k.id}
                    onClick={() => setSelected(k)}
                    className={`border-t border-[var(--cl-border-light)] cursor-pointer transition-colors ${
                      active ? "bg-[var(--cl-primary-light)]/60" : "hover:bg-[var(--cl-bg-page)]/60"
                    }`}
                  >
                    <td className="px-4 py-2.5 font-mono text-[11.5px]">{k.id.slice(0, 13)}…</td>
                    <td className="px-4 py-2.5">
                      <span className="inline-flex items-center gap-1.5">
                        <Icon size={12} className="text-[var(--cl-text-secondary)]" />
                        <Tag tone={TYPE_TONE[k.type]}>{TYPE_LABEL[k.type]}</Tag>
                      </span>
                    </td>
                    <td className="px-4 py-2.5 text-[var(--cl-text-regular)]">{k.algo}</td>
                    <td className="px-4 py-2.5">{k.label}</td>
                    <td className="px-4 py-2.5 font-mono text-xs text-[var(--cl-text-secondary)]">
                      {k.pair ?? "—"}
                    </td>
                    <td className="px-4 py-2.5 text-xs text-[var(--cl-text-secondary)]">{k.created}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
          <div className="px-4 py-2.5 flex items-center justify-between text-xs text-[var(--cl-text-secondary)] border-t border-[var(--cl-border-light)]">
            <span>显示 1 - {filtered.length} 条</span>
            <div className="inline-flex gap-1">
              {[1, 2, 3].map((n) => (
                <button
                  key={n}
                  className={`w-7 h-7 rounded ${n === 1 ? "bg-[var(--cl-primary)] text-white" : "hover:bg-[var(--cl-bg-page)]"}`}
                >
                  {n}
                </button>
              ))}
            </div>
          </div>
        </CryptoCard>

        {/* Detail */}
        {selected && (
          <CryptoCard
            title={selected.label}
            subtitle={selected.id}
            icon={<Key size={14} />}
            extra={<Tag tone={TYPE_TONE[selected.type]}>{TYPE_LABEL[selected.type]}</Tag>}
          >
            <dl className="space-y-2.5 text-sm">
              {[
                ["算法", selected.algo],
                ["创建时间", selected.created],
                ["过期时间", "永不过期"],
                ["配对密钥", selected.pair ?? "—"],
                ["KEK 包装", "已加密存储"],
              ].map(([k, v]) => (
                <div key={k as string} className="flex justify-between">
                  <dt className="text-[var(--cl-text-secondary)] text-xs">{k}</dt>
                  <dd className="text-[var(--cl-text-regular)] font-mono text-xs text-right max-w-[200px] break-all">
                    {v}
                  </dd>
                </div>
              ))}
            </dl>
            <div className="mt-5 pt-4 border-t border-[var(--cl-border-light)] flex flex-col gap-2">
              {(selected.type === "rsa_public" || selected.type === "ecc_public") && (
                <GhostButton>
                  <Download size={14} /> 导出公钥材料
                </GhostButton>
              )}
              <button className="h-9 px-3 rounded-md border border-[#FBC4C4] text-[var(--cl-danger)] text-sm hover:bg-[#FEF0F0] inline-flex items-center justify-center gap-1.5 transition-colors">
                <Trash2 size={14} /> 撤销该密钥
              </button>
            </div>
          </CryptoCard>
        )}
      </div>
    </>
  );
}
