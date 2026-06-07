# CryptoLab Frontend Design Overview

> Version 1.0 | 2026-06-07
> Target: Figma Make auto-generation + Element Plus component library

---

## 1. Project Background

CryptoLab is an academic cryptography experiment platform built for BUPT's Secure Programming course. The backend implements **15 hand-written cryptographic algorithms** in Rust (exposed via PyO3) behind a production-grade FastAPI service with JWT auth, audit logging, and key management.

The frontend is a **single-page application** serving two audiences:
- **Students**: interact with each algorithm, observe inputs/outputs, explore intermediate states
- **Instructors**: review audit logs, run benchmarks, demonstrate vulnerabilities

### Tech Stack (locked)

| Layer | Choice | Version |
|---|---|---|
| Framework | Vue 3 (Composition API, `<script setup>`) | ^3.4 |
| UI Library | Element Plus | ^2.6 |
| Icons | @element-plus/icons-vue | ^2.3 |
| Router | Vue Router 4 | ^4.3 |
| State | Pinia | ^2.1 |
| Charts | ECharts 5 + vue-echarts 7 | ^5.5 / ^7.0 |
| HTTP | Axios | ^1.6 |
| Build | Vite 5 | ^5.2 |
| Language | TypeScript ~5.4 | strict mode |

### API Proxy

Vite dev server proxies `/api` to `http://localhost:8000`. No CORS issues in development.

---

## 2. Information Architecture (Sitemap)

```
CryptoLab
├── /login              ← Public: Login & Register
│
├── [Authenticated Shell with Sidebar + Header]
│   ├── /dashboard      ← Home: algorithm catalog + quick stats
│   ├── /symmetric      ← AES / SM4 / RC6 encrypt & decrypt
│   ├── /hash           ← SHA-1/256/3, RIPEMD-160 hashing
│   ├── /hmac-pbkdf2    ← HMAC + PBKDF2 key derivation
│   ├── /encoding       ← Base64 / UTF-8 encode & decode
│   ├── /rsa            ← RSA keygen / encrypt / decrypt / sign / verify
│   ├── /ecc            ← ECC keygen + ECDSA sign / verify
│   ├── /keys           ← Key store management (list / export / revoke)
│   ├── /audit          ← Operation audit log viewer
│   ├── /benchmark      ← Algorithm throughput benchmark
│   ├── /demos          ← 4 vulnerability attack demonstrations
│   └── /scenarios      ← Secure file transfer (comprehensive scenario)
```

### Navigation Groups (Sidebar)

| Group | Icon | Pages |
|---|---|---|
| Algorithms | Lock | Symmetric, Hash, HMAC & PBKDF2, Encoding |
| Public Key | Key | RSA, ECC & ECDSA |
| Management | Setting | Key Store, Audit Logs, Benchmark |
| Labs | Warning | Security Demos, Secure File Transfer |

---

## 3. Design Language

### 3.1 Color Palette

| Token | Hex | Usage |
|---|---|---|
| `--cl-primary` | `#409EFF` | Element Plus primary blue, buttons, active nav |
| `--cl-primary-light` | `#ECF5FF` | Selected row, active nav background |
| `--cl-success` | `#67C23A` | Encrypt success, valid signature, checkmark |
| `--cl-warning` | `#E6A23C` | Demo banners, iteration warnings |
| `--cl-danger` | `#F56C6C` | Decrypt failure, invalid signature, errors |
| `--cl-info` | `#909399` | Disabled state, placeholder text |
| `--cl-bg-page` | `#F5F7FA` | Page background |
| `--cl-bg-card` | `#FFFFFF` | Card surface |
| `--cl-bg-code` | `#FAFAFA` | Code/hex output blocks |
| `--cl-border` | `#DCDFE6` | Card borders, dividers |
| `--cl-text-primary` | `#303133` | Headings, labels |
| `--cl-text-regular` | `#606266` | Body text |
| `--cl-text-secondary` | `#909399` | Captions, timestamps |
| `--cl-crypto-encrypt` | `#409EFF` | Encrypt flow color (blue gradient) |
| `--cl-crypto-decrypt` | `#67C23A` | Decrypt flow color (green gradient) |
| `--cl-crypto-sign` | `#9B59B6` | Signature flow color (purple) |

### 3.2 Typography

| Role | Font | Size | Weight |
|---|---|---|---|
| Page Title | Inter / "Microsoft YaHei" | 24px | 700 |
| Section Title | Inter / "Microsoft YaHei" | 18px | 600 |
| Body | Inter / "Microsoft YaHei" | 14px | 400 |
| Code / Hex | "JetBrains Mono", "Consolas", monospace | 13px | 400 |
| Caption | Inter / "Microsoft YaHei" | 12px | 400 |
| Badge | Inter | 11px | 600 |

### 3.3 Spacing System (8px grid)

| Token | Value | Usage |
|---|---|---|
| `--cl-gap-xs` | 4px | Icon-text gap |
| `--cl-gap-sm` | 8px | Inline element spacing |
| `--cl-gap-md` | 16px | Card padding, form gap |
| `--cl-gap-lg` | 24px | Section spacing |
| `--cl-gap-xl` | 32px | Page-level margin |

### 3.4 Border Radius

| Token | Value | Usage |
|---|---|---|
| `--cl-radius-sm` | 4px | Buttons, inputs |
| `--cl-radius-md` | 8px | Cards, dialogs |
| `--cl-radius-lg` | 12px | Feature cards on dashboard |
| `--cl-radius-round` | 20px | Tags, badges |

### 3.5 Shadow Levels

| Level | Value | Usage |
|---|---|---|
| `--cl-shadow-sm` | `0 1px 4px rgba(0,0,0,0.08)` | Cards at rest |
| `--cl-shadow-md` | `0 4px 12px rgba(0,0,0,0.10)` | Card hover, dropdowns |
| `--cl-shadow-lg` | `0 8px 24px rgba(0,0,0,0.12)` | Modals, floating panels |

### 3.6 Motion

| Animation | Duration | Easing | Trigger |
|---|---|---|---|
| Card hover lift | 200ms | ease-out | Mouse enter |
| Page transition | 300ms | ease-in-out | Route change (fade) |
| Result reveal | 400ms | cubic-bezier(.34,1.56,.64,1) | API response received |
| Progress bar | indeterminate | linear | API call in-flight |
| Copy flash | 150ms | ease | Click copy button |

---

## 4. Layout System

### 4.1 Authenticated Shell

```
┌─────────────────────────────────────────────────────┐
│  Header Bar (64px)                                  │
│  [Logo] CryptoLab     [SearchCmd+K] [User▾] [Logout]│
├──────────┬──────────────────────────────────────────┤
│ Sidebar  │  Main Content Area                       │
│ (220px)  │  ┌─────────────────────────────────────┐ │
│ collapsed│  │  Breadcrumb                         │ │
│ = 64px   │  │  Page Title + Description           │ │
│          │  │                                     │ │
│ [nav     │  │  Content Cards...                   │ │
│  groups] │  │                                     │ │
│          │  │                                     │ │
│          │  └─────────────────────────────────────┘ │
│          │  Footer: "Built with Rust + Python"      │
└──────────┴──────────────────────────────────────────┘
```

- **Breakpoint**: sidebar collapses to icon-only at viewport < 1200px
- **Max content width**: 1200px, centered in main area
- **Scroll**: main content area scrolls independently; sidebar fixed

### 4.2 Login Page

```
┌─────────────────────────────────────────────────────┐
│                                                     │
│              [Logo + "CryptoLab" title]              │
│              [Subtitle: 密码算法实验平台]             │
│                                                     │
│         ┌────────────────────────────┐              │
│         │  [Login] / [Register] tabs │              │
│         │                            │              │
│         │  Username ___________      │              │
│         │  Password ___________      │              │
│         │                            │              │
│         │  [    Login Button    ]    │              │
│         └────────────────────────────┘              │
│                                                     │
│              Animated crypto particle bg             │
└─────────────────────────────────────────────────────┘
```

---

## 5. Shared Component Library (14 components)

### C01: `CryptoCard`

**Purpose**: Wraps every functional section in a bordered card with optional header.

| Prop | Type | Default | Description |
|---|---|---|---|
| `title` | string | — | Card header title |
| `subtitle` | string | — | Gray subtitle below title |
| `icon` | Component | — | Element Plus icon in header |
| `loading` | boolean | false | Show skeleton overlay |
| `collapsible` | boolean | false | Allow content collapse |

**Slots**: `default` (content), `header-extra` (right side of header, e.g., action buttons)

### C02: `HexViewer`

**Purpose**: Display hex-encoded data with syntax highlighting, line numbers, and copy button. Used for ciphertext, hash digests, keys, signatures.

| Prop | Type | Default | Description |
|---|---|---|---|
| `value` | string | — | Hex string to display |
| `label` | string | — | Label above the viewer |
| `maxLines` | number | 4 | Collapse after N lines (16 chars/line) |
| `copyable` | boolean | true | Show copy-to-clipboard button |
| `highlight` | [number, number][] | [] | Byte ranges to highlight (e.g., GCM tag) |
| `compare` | string | — | Second hex string; diff coloring |

**Visual**: Monospace font, `--cl-bg-code` background, green/red diff highlighting.

### C03: `Base64Viewer`

**Purpose**: Display Base64 data with decode preview and copy. Similar to HexViewer but for Base64 payloads.

| Prop | Type | Default | Description |
|---|---|---|---|
| `value` | string | — | Base64 string |
| `label` | string | — | Label |
| `showDecoded` | boolean | false | Show decoded UTF-8 below if printable |
| `copyable` | boolean | true | Copy button |

### C04: `AlgorithmSelector`

**Purpose**: Dropdown or segmented control to pick algorithm + mode + padding.

| Prop | Type | Default | Description |
|---|---|---|---|
| `algorithms` | string[] | — | Available algorithms (e.g., ['aes','sm4','rc6']) |
| `modes` | string[] | — | Available modes (e.g., ['ECB','CBC','CTR','GCM']) |
| `paddings` | string[] | — | Available paddings |
| `showMode` | boolean | true | Show mode selector |
| `showPadding` | boolean | true | Show padding selector |

**Emits**: `update:algorithm`, `update:mode`, `update:padding`

### C05: `KeyIdPicker`

**Purpose**: Dropdown that lists user-owned keys from the key store, filtered by algorithm/type. Shows key_id, algorithm, label, creation date.

| Prop | Type | Default | Description |
|---|---|---|---|
| `keyType` | 'symmetric' \| 'rsa_public' \| 'rsa_private' \| 'ecc_public' \| 'ecc_private' | — | Filter by key type |
| `algorithm` | string | — | Further filter by algorithm |
| `placeholder` | string | 'Select a key...' | Placeholder text |

**Emits**: `update:keyId` (string UUID)

**Data source**: `GET /api/v1/keys` filtered client-side.

### C06: `OperationTimer`

**Purpose**: Animated duration display shown after an API operation completes. Pops in with the result animation.

| Prop | Type | Default | Description |
|---|---|---|---|
| `durationMs` | number | — | Milliseconds from API response |
| `operation` | string | — | Label like "Encryption" or "Key generation" |

**Visual**: Circular badge with millisecond count, pulsing green on < 100ms, yellow on < 1000ms, red on > 1000ms.

### C07: `StatusBanner`

**Purpose**: Full-width banner for demo pages showing security warnings (the `banner` field from demo responses).

| Prop | Type | Default | Description |
|---|---|---|---|
| `type` | 'warning' \| 'danger' \| 'info' | 'warning' | Banner style |
| `message` | string | — | Warning text |
| `icon` | Component | WarningFilled | Left icon |

### C08: `FlowDiagram`

**Purpose**: Visual step-by-step flow for composite scenarios (Secure File Transfer). Shows numbered steps with arrows, each step showing the algorithm used.

| Prop | Type | Default | Description |
|---|---|---|---|
| `steps` | FlowStep[] | — | Array of {label, algorithm, status, detail} |
| `direction` | 'horizontal' \| 'vertical' | 'horizontal' | Layout direction |

**Visual**: Connected nodes with icons per algorithm type, animated progress indicator on active step.

### C09: `InputPanel`

**Purpose**: Standardized left-side input form area used on all algorithm pages. Contains form fields, submit button, and optional file upload.

| Prop | Type | Default | Description |
|---|---|---|---|
| `submitLabel` | string | 'Execute' | Button text |
| `loading` | boolean | false | Disable form + show spinner |
| `resetable` | boolean | true | Show reset button |

**Slots**: `default` (form fields), `footer` (below submit button)

### C10: `OutputPanel`

**Purpose**: Standardized right-side result display area. Shows placeholder when empty, result content when populated, error state on failure.

| Prop | Type | Default | Description |
|---|---|---|---|
| `state` | 'empty' \| 'loading' \| 'success' \| 'error' | 'empty' | Current state |
| `errorMessage` | string | — | Error text when state = error |
| `errorCode` | number | — | Business error code |

**Slots**: `empty` (custom placeholder), `default` (result content)

**States**:
- **Empty**: Ghost illustration + "Run an operation to see results"
- **Loading**: Skeleton shimmer matching expected output shape
- **Success**: Animated reveal of content
- **Error**: Red border + error code badge + message

### C11: `CopyButton`

**Purpose**: Small icon button that copies text to clipboard with success feedback.

| Prop | Type | Default | Description |
|---|---|---|---|
| `text` | string | — | Text to copy |
| `size` | 'small' \| 'default' | 'small' | Button size |

**Visual**: DocumentCopy icon, flashes to green check for 1.5s after click.

### C12: `AuditTable`

**Purpose**: Reusable paginated table for audit log entries with filtering controls. Used on both the dedicated audit page and as an embedded mini-view on other pages.

| Prop | Type | Default | Description |
|---|---|---|---|
| `embedded` | boolean | false | Compact mode for embedding in other pages |
| `userId` | number | — | Pre-filter to specific user |
| `algorithm` | string | — | Pre-filter to specific algorithm |
| `limit` | number | 20 | Rows per page |

**Columns**: Trace ID, Operation, Algorithm, Key ID (truncated), Status, Duration, Timestamp

### C13: `KeygenButton`

**Purpose**: Combined button + dialog for one-click key generation. Used on RSA, ECC, and Symmetric pages to generate keys before using them.

| Prop | Type | Default | Description |
|---|---|---|---|
| `algorithm` | 'aes' \| 'sm4' \| 'rc6' \| 'rsa' \| 'ecc' | — | Algorithm to generate key for |
| `onSuccess` | (keyId: string) => void | — | Callback after successful keygen |

**Behavior**: Opens confirmation dialog with parameters (key size, curve, etc.), calls keygen endpoint, shows key_id on success, auto-selects in KeyIdPicker.

### C14: `ComparisonToggle`

**Purpose**: Toggle between input/output views, or between encrypt/decrypt modes. Animated swap with flip transition.

| Prop | Type | Default | Description |
|---|---|---|---|
| `leftLabel` | string | 'Encrypt' | Left option |
| `rightLabel` | string | 'Decrypt' | Right option |
| `modelValue` | 'left' \| 'right' | 'left' | Current selection |

---

## 6. Global State (Pinia Stores)

### `useAuthStore`

| State | Type | Description |
|---|---|---|
| `token` | string \| null | JWT access token (persisted to localStorage) |
| `user` | { user_id, username, role, created_at, last_login_at } \| null | Current user profile |
| `isLoggedIn` | computed boolean | `token !== null` |

**Actions**: `login(username, password)`, `register(username, password)`, `logout()`, `fetchMe()`

### `useKeysStore`

| State | Type | Description |
|---|---|---|
| `keys` | KeyListItem[] | Cached key list for current user |
| `loading` | boolean | Fetching keys |

**Actions**: `fetchKeys()`, `revokeKey(keyId)`, `invalidate()`

### `useAuditStore`

| State | Type | Description |
|---|---|---|
| `logs` | OperationLogItem[] | Current page of audit logs |
| `total` | number | Total count for pagination |
| `filters` | { algorithm, since, until } | Active filters |

**Actions**: `fetchLogs(page, filters)`, `resetFilters()`

---

## 7. API Client Architecture

```
src/api/
├── client.ts          # Axios instance with baseURL, interceptors (JWT header, error mapping)
├── auth.ts            # register, login, logout, me
├── symmetric.ts       # keygen, encrypt, decrypt
├── hash.ts            # hash, hmac, pbkdf2
├── encoding.ts        # base64Encode, base64Decode
├── pubkey.ts          # rsaKeygen, rsaEncrypt, rsaDecrypt, rsaSign, rsaVerify, eccKeygen, ecdsaSign, ecdsaVerify
├── keys.ts            # listKeys, getPublicMaterial, revokeKey
├── audit.ts           # listLogs
├── benchmark.ts       # runBenchmark
├── demos.ts           # ecbImageLeak, ecdsaKReuse, rsaLowExponent, pbkdf2IterationImpact
└── scenarios.ts       # secureFileSend, secureFileReceive
```

**Interceptors**:
- Request: inject `Authorization: Bearer <token>` from authStore
- Response: unwrap `APIResponse.data` on code=1000; throw typed error on other codes
- 401/4001/4002: auto-redirect to `/login`, clear token

---

## 8. Endpoint-to-Page Mapping (completeness check)

| Endpoint | Page |
|---|---|
| POST /api/v1/auth/register | Login (/login) |
| POST /api/v1/auth/login | Login (/login) |
| POST /api/v1/auth/logout | Header (global) |
| GET /api/v1/auth/me | Header (global) + Dashboard |
| POST /api/v1/symmetric/keygen | Symmetric (/symmetric) |
| POST /api/v1/symmetric/{algo}/encrypt | Symmetric (/symmetric) |
| POST /api/v1/symmetric/{algo}/decrypt | Symmetric (/symmetric) |
| POST /api/v1/hash/{algo} | Hash (/hash) |
| POST /api/v1/hash/hmac/{algo} | HMAC & PBKDF2 (/hmac-pbkdf2) |
| POST /api/v1/hash/pbkdf2 | HMAC & PBKDF2 (/hmac-pbkdf2) |
| POST /api/v1/encoding/base64/{op} | Encoding (/encoding) |
| POST /api/v1/pubkey/rsa/keygen | RSA (/rsa) |
| POST /api/v1/pubkey/rsa/encrypt | RSA (/rsa) |
| POST /api/v1/pubkey/rsa/decrypt | RSA (/rsa) |
| POST /api/v1/pubkey/rsa/sign | RSA (/rsa) |
| POST /api/v1/pubkey/rsa/verify | RSA (/rsa) |
| POST /api/v1/pubkey/ecc/keygen | ECC & ECDSA (/ecc) |
| POST /api/v1/pubkey/ecdsa/sign | ECC & ECDSA (/ecc) |
| POST /api/v1/pubkey/ecdsa/verify | ECC & ECDSA (/ecc) |
| GET /api/v1/keys | Key Store (/keys) |
| GET /api/v1/keys/{key_id}/public | Key Store (/keys) + RSA + ECC |
| DELETE /api/v1/keys/{key_id} | Key Store (/keys) |
| GET /api/v1/audit/logs | Audit (/audit) |
| GET /api/v1/benchmark/{algo} | Benchmark (/benchmark) |
| POST /api/v1/demos/ecb_image_leak | Demos (/demos) |
| POST /api/v1/demos/ecdsa_k_reuse | Demos (/demos) |
| POST /api/v1/demos/rsa_low_exponent | Demos (/demos) |
| POST /api/v1/demos/pbkdf2_iteration_impact | Demos (/demos) |
| POST /api/v1/scenarios/secure_file_transfer/send | Scenarios (/scenarios) |
| POST /api/v1/scenarios/secure_file_transfer/receive | Scenarios (/scenarios) |

**Coverage**: 30/30 endpoints mapped. Zero orphans.
