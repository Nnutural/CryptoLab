import {
  LayoutDashboard,
  Lock,
  Hash,
  KeyRound,
  Code2,
  ShieldCheck,
  Sigma,
  Database,
  ScrollText,
  Gauge,
  AlertTriangle,
  Send,
  type LucideIcon,
} from "lucide-react";

export type RouteKey =
  | "dashboard"
  | "symmetric"
  | "hash"
  | "hmac-pbkdf2"
  | "encoding"
  | "rsa"
  | "ecc"
  | "keys"
  | "audit"
  | "benchmark"
  | "demos"
  | "scenarios";

export interface NavItem {
  key: RouteKey;
  label: string;
  icon: LucideIcon;
  desc?: string;
}

export interface NavGroup {
  label: string;
  items: NavItem[];
}

export const NAV_GROUPS: NavGroup[] = [
  {
    label: "概览",
    items: [{ key: "dashboard", label: "控制台", icon: LayoutDashboard, desc: "平台概览" }],
  },
  {
    label: "算法实验",
    items: [
      { key: "symmetric", label: "对称加密", icon: Lock, desc: "AES · SM4 · RC6" },
      { key: "hash", label: "哈希函数", icon: Hash, desc: "SHA · RIPEMD" },
      { key: "hmac-pbkdf2", label: "消息认证与密钥派生", icon: Sigma, desc: "HMAC · PBKDF2" },
      { key: "encoding", label: "编码转换", icon: Code2, desc: "Base64 · UTF-8" },
    ],
  },
  {
    label: "公钥密码",
    items: [
      { key: "rsa", label: "RSA 密码算法", icon: KeyRound, desc: "加密 · 签名" },
      { key: "ecc", label: "ECC 与 ECDSA", icon: ShieldCheck, desc: "secp160r1" },
    ],
  },
  {
    label: "管理功能",
    items: [
      { key: "keys", label: "密钥管理", icon: Database, desc: "密钥仓库" },
      { key: "audit", label: "审计日志", icon: ScrollText, desc: "操作追踪" },
      { key: "benchmark", label: "性能测试", icon: Gauge, desc: "吞吐量基准" },
    ],
  },
  {
    label: "综合实验",
    items: [
      { key: "demos", label: "安全演示", icon: AlertTriangle, desc: "漏洞复现" },
      { key: "scenarios", label: "安全文件传输", icon: Send, desc: "端到端流程" },
    ],
  },
];

export const ROUTE_TITLES: Record<RouteKey, { title: string; subtitle: string; breadcrumb: string[] }> =
  {
    dashboard: { title: "控制台", subtitle: "欢迎回到 CryptoLab,这里汇集了你最近的实验数据。", breadcrumb: ["概览", "控制台"] },
    symmetric: { title: "对称加密", subtitle: "AES / SM4 / RC6 — 分组密码工作台,支持 ECB / CBC / CTR / GCM 模式。", breadcrumb: ["算法实验", "对称加密"] },
    hash: { title: "哈希函数", subtitle: "单向密码学摘要 — SHA-1 / SHA-2 / SHA-3 / RIPEMD-160。", breadcrumb: ["算法实验", "哈希函数"] },
    "hmac-pbkdf2": { title: "消息认证与密钥派生", subtitle: "HMAC 消息认证码与 PBKDF2 密码派生函数。", breadcrumb: ["算法实验", "消息认证与密钥派生"] },
    encoding: { title: "编码转换", subtitle: "Base64 / UTF-8 数据编码转换工具。", breadcrumb: ["算法实验", "编码转换"] },
    rsa: { title: "RSA 密码算法", subtitle: "RSA-1024 公钥密码体制,支持密钥生成、加解密、数字签名。", breadcrumb: ["公钥密码", "RSA 密码算法"] },
    ecc: { title: "ECC 与 ECDSA", subtitle: "基于 secp160r1 椭圆曲线的 ECDSA 数字签名。", breadcrumb: ["公钥密码", "ECC 与 ECDSA"] },
    keys: { title: "密钥管理", subtitle: "管理你拥有的全部密钥(KEK 包装存储)。", breadcrumb: ["管理功能", "密钥管理"] },
    audit: { title: "审计日志", subtitle: "查看全部密码运算的可追溯审计记录。", breadcrumb: ["管理功能", "审计日志"] },
    benchmark: { title: "性能测试", subtitle: "手写算法的吞吐量与延迟基准测试。", breadcrumb: ["管理功能", "性能测试"] },
    demos: { title: "安全演示", subtitle: "四个交互式安全漏洞演示。仅供教学使用,切勿用于生产。", breadcrumb: ["综合实验", "安全演示"] },
    scenarios: { title: "安全文件传输", subtitle: "RSA + AES-GCM + SHA-256 + ECDSA 端到端综合实验。", breadcrumb: ["综合实验", "安全文件传输"] },
  };
