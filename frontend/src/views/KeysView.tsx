import { useState, useMemo, useEffect } from "react";
import { Database, Search, Trash2, Download, Key, ShieldCheck, KeyRound, Lock } from "lucide-react";
import { PageHeader } from "@/components/shared/PageHeader";
import { CryptoCard } from "@/components/shared/CryptoCard";
import { TextInput, GhostButton, Select, Tag } from "@/components/shared/Field";
import { ROUTE_TITLES } from "@/components/nav";
import { listKeys, deleteKey, getKeyPublic } from "@/api/keys";

interface KeyItem {
  id: string;
  type: "symmetric" | "rsa_public" | "rsa_private" | "ecc_public" | "ecc_private";
  algo: string;
  label: string;
  pair: string | null;
  pairId: string | null;
  created: string;
  expires: string;
}

interface BackendKey {
  id?: string;
  key_id?: string;
  key_type?: string;
  algorithm?: string;
  key_size?: number;
  label?: string | null;
  created_at?: string;
  expires_at?: string | null;
  status?: string;
  paired_key_id?: string | null;
  pair_id?: string | null;
  type?: string;
}

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

function deriveType(raw: BackendKey): KeyItem["type"] {
  if (raw.type === "symmetric" || raw.type === "rsa_public" || raw.type === "rsa_private" || raw.type === "ecc_public" || raw.type === "ecc_private") {
    return raw.type;
  }
  const keyType = (raw.key_type || raw.type || "").toLowerCase();
  const algo = (raw.algorithm || "").toLowerCase();
  if (keyType === "symmetric") return "symmetric";
  if (algo === "aes" || algo === "sm4" || algo === "rc6") return "symmetric";
  if (algo.startsWith("rsa")) {
    return keyType === "public" ? "rsa_public" : "rsa_private";
  }
  if (algo.startsWith("ecc") || algo.startsWith("ecdsa")) {
    return keyType === "public" ? "ecc_public" : "ecc_private";
  }
  return "symmetric";
}

function formatAlgo(raw: BackendKey): string {
  const a = (raw.algorithm || "").toUpperCase();
  if (raw.key_size) return `${a}-${raw.key_size}`;
  return a || "—";
}

function mapKey(raw: BackendKey): KeyItem {
  const keyId = raw.key_id ?? raw.id ?? "";
  const pairId = raw.pair_id ?? raw.paired_key_id ?? null;
  return {
    id: keyId,
    type: deriveType(raw),
    algo: formatAlgo(raw),
    label: raw.label || "未命名密钥",
    pair: pairId ? `${pairId.slice(0, 8)}…` : null,
    pairId,
    created: raw.created_at || "—",
    expires: raw.expires_at || "永不过期",
  };
}

export function KeysView() {
  const meta = ROUTE_TITLES.keys;
  const [q, setQ] = useState("");
  const [type, setType] = useState("all");
  const [keys, setKeys] = useState<KeyItem[]>([]);
  const [selected, setSelected] = useState<KeyItem | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [publicMaterial, setPublicMaterial] = useState<string | null>(null);
  const [publicLoading, setPublicLoading] = useState(false);

  const loadKeys = async () => {
    try {
      setLoading(true);
      setError(null);
      const resp = await listKeys();
      if (resp.code === 1000) {
        const arr = (resp.data ?? []) as BackendKey[];
        const mapped = arr.map(mapKey);
        setKeys(mapped);
        // Preserve selection if it still exists, else pick first
        setSelected((prev) => {
          if (prev && mapped.find((k) => k.id === prev.id)) return prev;
          return mapped[0] ?? null;
        });
      } else {
        setError(resp.message || "加载密钥列表失败");
      }
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || "网络错误");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadKeys();
  }, []);

  // Reset public material panel when selection changes
  useEffect(() => {
    setPublicMaterial(null);
  }, [selected?.id]);

  const filtered = useMemo(
    () =>
      keys.filter(
        (k) =>
          (type === "all" || k.type === type) &&
          (q === "" || k.id.includes(q) || k.label.includes(q) || k.algo.toLowerCase().includes(q.toLowerCase()))
      ),
    [q, type, keys]
  );

  const handleDelete = async (keyId: string) => {
    try {
      const resp = await deleteKey(keyId);
      if (resp.code === 1000) {
        await loadKeys();
      } else {
        setError(resp.message || "撤销密钥失败");
      }
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || "网络错误");
    }
  };

  const handleViewPublic = async (item: KeyItem) => {
    const keyId = item.type.endsWith("_private") ? item.pairId : item.id;
    if (!keyId) {
      setError("当前私钥没有配对公钥 ID");
      return;
    }
    try {
      setPublicLoading(true);
      setError(null);
      const resp = await getKeyPublic(keyId);
      if (resp.code === 1000) {
        const data: any = resp.data || {};
        const material = data.material ?? data.public_key_pem ?? data.public_key ?? data.public_material ?? data;
        setPublicMaterial(typeof material === "string" ? material : JSON.stringify(material, null, 2));
      } else {
        setError(resp.message || "获取公钥材料失败");
      }
    } catch (err: any) {
      setError(err?.response?.data?.message || err?.message || "网络错误");
    } finally {
      setPublicLoading(false);
    }
  };

  return (
    <>
      <PageHeader
        title={meta.title}
        subtitle={meta.subtitle}
        breadcrumb={meta.breadcrumb}
        actions={
          <>
            <GhostButton onClick={loadKeys} disabled={loading}>
              <Download size={14} /> {loading ? "刷新中…" : "批量导出公钥"}
            </GhostButton>
          </>
        }
      />

      {error && (
        <div className="mb-4 px-3 py-2 rounded-md bg-[#FEF0F0] border border-[#FBC4C4] text-xs text-[#C45656] cl-shake">
          {error}
        </div>
      )}

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
            共 <span className="text-[var(--cl-text-primary)]">{filtered.length}</span> 条 / 总 {keys.length}
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
              {filtered.length === 0 && !loading && (
                <tr>
                  <td colSpan={6} className="px-4 py-10 text-center text-xs text-[var(--cl-text-placeholder)]">
                    暂无密钥
                  </td>
                </tr>
              )}
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
                ["过期时间", selected.expires],
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

            {publicMaterial && (
              <div className="mt-4 p-3 rounded-md border border-[var(--cl-border-light)] bg-[var(--cl-bg-code)]">
                <div className="text-[10px] text-[var(--cl-text-secondary)] mb-1.5">公钥材料</div>
                <pre className="font-mono text-[10.5px] text-[var(--cl-text-regular)] whitespace-pre-wrap break-all max-h-48 overflow-auto">
                  {publicMaterial}
                </pre>
              </div>
            )}

            <div className="mt-5 pt-4 border-t border-[var(--cl-border-light)] flex flex-col gap-2">
              {(selected.type === "rsa_public" ||
                selected.type === "ecc_public" ||
                selected.type === "rsa_private" ||
                selected.type === "ecc_private") && (
                <GhostButton onClick={() => handleViewPublic(selected)} disabled={publicLoading}>
                  <Download size={14} /> {publicLoading ? "加载中…" : "导出公钥材料"}
                </GhostButton>
              )}
              <button
                onClick={() => handleDelete(selected.id)}
                className="h-9 px-3 rounded-md border border-[#FBC4C4] text-[var(--cl-danger)] text-sm hover:bg-[#FEF0F0] inline-flex items-center justify-center gap-1.5 transition-colors"
              >
                <Trash2 size={14} /> 撤销该密钥
              </button>
            </div>
          </CryptoCard>
        )}
      </div>
    </>
  );
}
