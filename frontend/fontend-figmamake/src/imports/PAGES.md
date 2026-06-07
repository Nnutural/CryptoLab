# CryptoLab Page Specifications

> 12 pages x 7 subsections each. Every backend endpoint is mapped to at least one page.

---

## Page 1: Login & Register (`/login`)

### 1.1 Route & Permissions

| Field | Value |
|---|---|
| Path | `/login` |
| Auth required | No (redirects to `/dashboard` if already logged in) |
| Vue component | `LoginView.vue` |
| Guard | Reverse auth guard: redirect authenticated users away |

### 1.2 Purpose

Combined authentication page. Users register a new account or log in to an existing one. This is the entry point for all authenticated functionality. The page establishes CryptoLab's visual identity and sets the tone for the cryptographic experience.

### 1.3 Data Sources

| Action | Endpoint | Request | Response |
|---|---|---|---|
| Register | `POST /api/v1/auth/register` | `{ username: string, password: string }` | `{ user_id: number, created_at: string }` |
| Login | `POST /api/v1/auth/login` | `{ username: string, password: string }` | `{ access_token: string, token_type: "Bearer", expires_in: number }` |

### 1.4 Layout Structure

```
┌──────────────────────────────────────────────────────────┐
│  Full viewport, centered card, animated background       │
│                                                          │
│  Background: dark gradient (#1a1a2e → #16213e) with     │
│  floating cryptographic symbol particles (lock, key,     │
│  shield icons, slowly drifting)                          │
│                                                          │
│         ┌──────────────────────────────┐                 │
│         │  [Shield Lock Icon, 48px]    │                 │
│         │  "CryptoLab"  (24px, white)  │                 │
│         │  "密码算法实验平台" (14px)    │                 │
│         │                              │                 │
│         │  ┌─[Login]──[Register]─┐     │  ← el-tabs     │
│         │  │                     │     │                 │
│         │  │  Username           │     │                 │
│         │  │  ┌────────────────┐ │     │                 │
│         │  │  │  👤            │ │     │  ← el-input    │
│         │  │  └────────────────┘ │     │    with prefix  │
│         │  │  Password           │     │    icon         │
│         │  │  ┌────────────────┐ │     │                 │
│         │  │  │  🔒            │ │     │                 │
│         │  │  └────────────────┘ │     │                 │
│         │  │                     │     │                 │
│         │  │  [ ● Login / Register ]   │  ← el-button   │
│         │  │                     │     │    type=primary │
│         │  └─────────────────────┘     │    size=large   │
│         │                              │                 │
│         │  Password rules (register):  │                 │
│         │  "8+ characters required"    │                 │
│         └──────────────────────────────┘                 │
│                                                          │
│  Footer: "Powered by Rust + Python | BUPT 2026"         │
└──────────────────────────────────────────────────────────┘
```

**Card**: 400px width, white, `--cl-radius-md`, `--cl-shadow-lg`, centered vertically and horizontally.

### 1.5 Example Data

**Login Request:**
```json
{ "username": "alice", "password": "Str0ngPass!" }
```

**Login Response (success):**
```json
{
  "code": 1000,
  "message": "操作成功",
  "data": {
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOjEsInVzZXJuYW1lIjoiYWxpY2UiLCJyb2xlIjoidXNlciIsImV4cCI6MTcxOTMwMDAwMH0.abc123",
    "token_type": "Bearer",
    "expires_in": 3600
  },
  "trace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
}
```

**Register Response (success):**
```json
{
  "code": 1000,
  "data": { "user_id": 1, "created_at": "2026-06-07T14:30:00Z" }
}
```

**Login Error (wrong password):**
```json
{
  "code": 4001,
  "message": "Invalid credentials",
  "data": null
}
```

### 1.6 State Specification

| State | Trigger | Visual |
|---|---|---|
| **Default** | Page load | Empty form, Login tab active |
| **Validating** | Input blur | Red border on invalid field, inline error text below |
| **Loading** | Form submit | Button shows spinner, inputs disabled |
| **Success** | 200 + code 1000 | Green flash on card border, redirect to /dashboard after 300ms |
| **Error (credentials)** | code 4001 | el-message error toast at top, form remains editable, password field cleared |
| **Error (username taken)** | code 2001 on register | Inline error under username field: "Username already exists" |
| **Error (rate limited)** | code 4029 | el-message warning: "Too many attempts, try again in 60s", countdown timer on button |

### 1.7 Wow Moment

**Typing cipher effect**: As the user types their password, each character briefly shows as a random hex byte (e.g., typing "a" flashes "0x61") before masking to "●". This subtle animation reinforces the cryptographic theme and demonstrates encoding awareness without compromising security.

---

## Page 2: Dashboard (`/dashboard`)

### 2.1 Route & Permissions

| Field | Value |
|---|---|
| Path | `/dashboard` |
| Auth required | Yes |
| Vue component | `DashboardView.vue` |
| Redirect from | `/` |

### 2.2 Purpose

Landing page after login. Provides an at-a-glance overview of the platform's capabilities: algorithm catalog, recent operation stats, and quick-launch cards for each algorithm category. Functions as both a navigation hub and a feature showcase.

### 2.3 Data Sources

| Action | Endpoint | Request | Response |
|---|---|---|---|
| User profile | `GET /api/v1/auth/me` | — | `{ user_id, username, role, created_at, last_login_at }` |
| Key count | `GET /api/v1/keys` | — | `KeyListItem[]` (count client-side) |
| Recent audit | `GET /api/v1/audit/logs?limit=5` | — | `OperationLogItem[]` |

### 2.4 Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│ Welcome Banner                                          │
│ "Welcome back, alice"   Role: user   Last: 2h ago       │
├─────────────────────────────────────────────────────────┤
│ Stats Row (4 metric cards, equal width)                  │
│ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐               │
│ │  15   │ │  24   │ │  156  │ │ 0.8ms │               │
│ │Algos  │ │Keys   │ │Ops    │ │Avg    │               │
│ │Avail  │ │Stored │ │Today  │ │Latency│               │
│ └───────┘ └───────┘ └───────┘ └───────┘               │
├─────────────────────────────────────────────────────────┤
│ Algorithm Catalog (3-column grid of feature cards)      │
│                                                         │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│ │ 🔐 Symmetric │ │ # Hash      │ │ </> Encoding │    │
│ │ AES·SM4·RC6  │ │ SHA·RIPEMD  │ │ Base64·UTF-8 │    │
│ │ ECB/CBC/CTR/ │ │ 8 algorithms │ │ Encode/Decode│    │
│ │ GCM modes    │ │              │ │              │    │
│ │ [Open →]     │ │ [Open →]     │ │ [Open →]     │    │
│ └──────────────┘ └──────────────┘ └──────────────┘    │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│ │ 🔑 RSA      │ │ 📐 ECC      │ │ 🗄 Key Store │    │
│ │ 1024-bit    │ │ secp160r1   │ │ Manage keys  │    │
│ │ Encrypt/Sign │ │ ECDSA Sign  │ │ KEK wrapped  │    │
│ │ [Open →]     │ │ [Open →]     │ │ [Open →]     │    │
│ └──────────────┘ └──────────────┘ └──────────────┘    │
│ ┌──────────────┐ ┌──────────────┐ ┌──────────────┐    │
│ │ ⚠ Demos     │ │ 📦 Transfer │ │ 📊 Benchmark │    │
│ │ 4 attack    │ │ Secure File │ │ Throughput   │    │
│ │ simulations │ │ Send/Receive│ │ per algorithm│    │
│ │ [Open →]     │ │ [Open →]     │ │ [Open →]     │    │
│ └──────────────┘ └──────────────┘ └──────────────┘    │
├─────────────────────────────────────────────────────────┤
│ Recent Activity (last 5 operations)                     │
│ ┌───────────────────────────────────────────────────┐  │
│ │ Time     │ Operation    │ Algorithm │ Duration    │  │
│ │ 14:32    │ aes_encrypt  │ AES-GCM   │ 0.42ms     │  │
│ │ 14:31    │ rsa_keygen   │ RSA-1024  │ 234.5ms    │  │
│ │ 14:28    │ sha256       │ SHA-256   │ 0.08ms     │  │
│ │ ...      │              │           │            │  │
│ └───────────────────────────────────────────────────┘  │
│ [View all audit logs →]                                 │
└─────────────────────────────────────────────────────────┘
```

### 2.5 Example Data

**User profile:**
```json
{
  "user_id": 1,
  "username": "alice",
  "role": "user",
  "created_at": "2026-06-05T10:00:00Z",
  "last_login_at": "2026-06-07T12:30:00Z"
}
```

**Stats computed from API:**
```json
{
  "algorithmsAvailable": 15,
  "keysStored": 24,
  "opsToday": 156,
  "avgLatencyMs": 0.83
}
```

### 2.6 State Specification

| State | Trigger | Visual |
|---|---|---|
| **Loading** | Initial page load | All 4 stat cards show skeleton, catalog cards show gray placeholders |
| **Loaded** | API responses received | Stats count up from 0 to actual value (animated number), cards fade in staggered |
| **Empty** | New user, no operations | Stats all 0, recent activity shows "No operations yet — try encrypting something!" with arrow to Symmetric page |
| **Error** | API failure | Error banner above stats, catalog cards still show (static content) |

### 2.7 Wow Moment

**Animated number counters**: Each stat card counts up from 0 to its real value over 800ms with an easing curve. The "Algorithms Available" card has a subtle lock-icon animation that "unlocks" as the count completes. The feature cards appear with a staggered 50ms delay cascade.

---

## Page 3: Symmetric Encryption (`/symmetric`)

### 3.1 Route & Permissions

| Field | Value |
|---|---|
| Path | `/symmetric` |
| Auth required | Yes |
| Vue component | `SymmetricView.vue` |

### 3.2 Purpose

Interactive workbench for AES, SM4, and RC6 symmetric encryption/decryption. Users select an algorithm, mode, padding, and key (from key store), then encrypt or decrypt data. Results show ciphertext/plaintext with timing information.

### 3.3 Data Sources

| Action | Endpoint | Request | Response |
|---|---|---|---|
| Generate key | `POST /api/v1/symmetric/keygen` | `{ algorithm, key_size, label? }` | `{ key_id, algorithm, key_type }` |
| Encrypt | `POST /api/v1/symmetric/{algo}/encrypt` | `{ algorithm, mode, padding, key_id, iv_hex?, aad_b64?, plaintext_b64 }` | `{ ciphertext_b64, algorithm, mode, duration_ms }` |
| Decrypt | `POST /api/v1/symmetric/{algo}/decrypt` | `{ algorithm, mode, padding, key_id, iv_hex?, aad_b64?, ciphertext_b64 }` | `{ plaintext_b64, algorithm, mode, duration_ms }` |
| List keys | `GET /api/v1/keys` | — | `KeyListItem[]` |

### 3.4 Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│ Page Title: "Symmetric Encryption"                      │
│ Subtitle: "AES / SM4 / RC6 — Block cipher workbench"   │
├─────────────────────────────────────────────────────────┤
│ Toolbar Row                                             │
│ ┌───────────────────────────────────────────────────┐  │
│ │ AlgorithmSelector [AES ▾] [GCM ▾] [PKCS7 ▾]     │  │
│ │                                                   │  │
│ │ ComparisonToggle [Encrypt | Decrypt]              │  │
│ └───────────────────────────────────────────────────┘  │
├──────────────────────┬──────────────────────────────────┤
│ InputPanel (left)    │ OutputPanel (right)              │
│                      │                                  │
│ Key:                 │ [empty / loading / result]       │
│ ┌──────────────────┐ │                                  │
│ │ KeyIdPicker      │ │ When result:                    │
│ │ [key-a1b2... ▾]  │ │ ┌────────────────────────────┐ │
│ │  + [Generate Key]│ │ │ Ciphertext (Base64)        │ │
│ └──────────────────┘ │ │ ┌────────────────────────┐ │ │
│                      │ │ │ YWJjZGVmZ2hpamtsbW5v │ │ │
│ IV (hex):            │ │ │ cHFyc3R1dnd4eXo=     │ │ │
│ ┌──────────────────┐ │ │ └───────────────[Copy]──┘ │ │
│ │ 000102030405...  │ │ │                            │ │
│ │ [Random IV btn]  │ │ │ Hex View:                  │ │
│ └──────────────────┘ │ │ ┌────────────────────────┐ │ │
│                      │ │ │ 61 62 63 64 65 66 67  │ │ │
│ AAD (for GCM):       │ │ │ 68 69 6a 6b 6c 6d 6e  │ │ │
│ ┌──────────────────┐ │ │ └───────────────[Copy]──┘ │ │
│ │ optional b64     │ │ │                            │ │
│ └──────────────────┘ │ │ OperationTimer: 0.42ms     │ │
│                      │ │ Algorithm: AES-256-GCM      │ │
│ Plaintext:           │ └────────────────────────────┘ │
│ ┌──────────────────┐ │                                  │
│ │ el-input textarea│ │                                  │
│ │ "Hello, World!"  │ │                                  │
│ │ (auto base64)    │ │                                  │
│ └──────────────────┘ │                                  │
│                      │                                  │
│ [🔒 Encrypt]        │                                  │
└──────────────────────┴──────────────────────────────────┘
```

**Key behavior**: Plaintext textarea auto-encodes to Base64 on submit. When in Decrypt mode, the left panel swaps: ciphertext input on left, plaintext output on right.

### 3.5 Example Data

**Encrypt request (user fills form, sent as):**
```json
{
  "algorithm": "aes",
  "mode": "GCM",
  "padding": "None",
  "key_id": "b7e15163-4aed-2b9e-9c87-53d8a2f77e1a",
  "iv_hex": "000102030405060708090a0b",
  "plaintext_b64": "SGVsbG8sIFdvcmxkIQ=="
}
```

**Encrypt response:**
```json
{
  "ciphertext_b64": "kL3RfXpXMJvG7Y6qHzU8D9RNH5I6DJKzATKweA==",
  "algorithm": "AES",
  "mode": "GCM",
  "duration_ms": 0.42
}
```

**Keygen request:**
```json
{ "algorithm": "aes", "key_size": 32, "label": "My AES-256 key" }
```

**Keygen response:**
```json
{ "key_id": "b7e15163-4aed-2b9e-9c87-53d8a2f77e1a", "algorithm": "aes", "key_type": "symmetric" }
```

### 3.6 State Specification

| State | Trigger | Visual |
|---|---|---|
| **Initial** | Page load | Empty InputPanel, OutputPanel shows ghost: "Select an algorithm and key, then encrypt" |
| **No keys** | User has no symmetric keys | KeyIdPicker shows empty state: "No keys found — generate one first", KeygenButton prominent |
| **Key selected** | Pick key from dropdown | Green check next to key picker, IV field auto-focuses |
| **Loading** | Submit encrypt/decrypt | InputPanel disabled, OutputPanel shows skeleton shimmer |
| **Success** | API 200 | OutputPanel reveals result with slide-down animation, timer pops in |
| **Decrypt success** | Decrypted plaintext | Plaintext shown in green-bordered box, auto-decoded from Base64 to readable text |
| **Error (GCM tag fail)** | code 3002 | OutputPanel error state: "Decryption failed — GCM authentication tag mismatch" with danger icon |
| **Error (key not found)** | code 4202 | KeyIdPicker border turns red, tooltip: "Key not found or revoked" |
| **Error (wrong key type)** | code 4203 | Error message: "This key is for RSA, not AES" |

### 3.7 Wow Moment

**Mode comparison strip**: Below the main output, a collapsible "Compare Modes" panel lets the user encrypt the same plaintext with the same key across all 4 modes (ECB/CBC/CTR/GCM) simultaneously. The results display side-by-side with visual block coloring — ECB's repeating blocks are highlighted in red to visually demonstrate the pattern-leakage vulnerability. This is pedagogically powerful: students see the ECB weakness without needing the separate demo page.

---

## Page 4: Hash Computation (`/hash`)

### 4.1 Route & Permissions

| Field | Value |
|---|---|
| Path | `/hash` |
| Auth required | No (hash endpoints have no auth) |
| Vue component | `HashView.vue` |

### 4.2 Purpose

Compute cryptographic hash digests using SHA-1, SHA-224, SHA-256, SHA-384, SHA-512, SHA3-256, SHA3-512, and RIPEMD-160. Users input text and see the digest in real-time. Supports multi-algorithm comparison to show how different hashes produce different outputs from the same input.

### 4.3 Data Sources

| Action | Endpoint | Request | Response |
|---|---|---|---|
| Compute hash | `POST /api/v1/hash/{algo}` | `{ data: string }` | `{ digest_hex: string, algorithm: string }` |

`{algo}` is one of: `sha1`, `sha224`, `sha256`, `sha384`, `sha512`, `sha3_256`, `sha3_512`, `ripemd160`

### 4.4 Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│ Page Title: "Hash Functions"                            │
│ Subtitle: "One-way cryptographic digests"               │
├─────────────────────────────────────────────────────────┤
│ Input Section                                           │
│ ┌───────────────────────────────────────────────────┐  │
│ │ el-input textarea, 4 rows                         │  │
│ │ Placeholder: "Enter text to hash..."              │  │
│ │ Character count: 13 / ∞                           │  │
│ └───────────────────────────────────────────────────┘  │
│                                                         │
│ Algorithm Checkboxes (multi-select):                    │
│ [✓] SHA-1  [✓] SHA-256  [ ] SHA-384  [ ] SHA-512      │
│ [ ] SHA-224  [✓] SHA3-256  [ ] SHA3-512  [ ] RIPEMD-160│
│                                                         │
│ [🔍 Compute Hashes]                                    │
├─────────────────────────────────────────────────────────┤
│ Results (one card per selected algorithm)                │
│                                                         │
│ ┌─ SHA-1 ──────────────────────────────────────────┐   │
│ │ aaf4c61d...cc1b       (40 hex chars)    [Copy]   │   │
│ │ Digest length: 160 bits                           │   │
│ └──────────────────────────────────────────────────┘   │
│                                                         │
│ ┌─ SHA-256 ────────────────────────────────────────┐   │
│ │ 2cf24dba...2e2ba      (64 hex chars)    [Copy]   │   │
│ │ Digest length: 256 bits                           │   │
│ └──────────────────────────────────────────────────┘   │
│                                                         │
│ ┌─ SHA3-256 ───────────────────────────────────────┐   │
│ │ 3338be69...8c7e3      (64 hex chars)    [Copy]   │   │
│ │ Digest length: 256 bits                           │   │
│ └──────────────────────────────────────────────────┘   │
│                                                         │
│ Comparison Bar:                                         │
│ "SHA-256 vs SHA3-256: 0/64 bytes match (0%)"           │
└─────────────────────────────────────────────────────────┘
```

### 4.5 Example Data

**Request (SHA-256):**
```json
{ "data": "hello" }
```

**Response:**
```json
{
  "digest_hex": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
  "algorithm": "sha256"
}
```

**Multi-hash results for "hello":**
```
SHA-1:      aaf4c61ddcc5e8a2dabede0f3b482cd9aea9434d
SHA-256:    2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824
SHA3-256:   3338be694f50c5f338814986cdf0686453a888b84f424d792af4b9202398f392
RIPEMD-160: 108f07b8382412612c048d07d13f814118445acd
```

### 4.6 State Specification

| State | Trigger | Visual |
|---|---|---|
| **Empty** | Page load | Textarea empty, no results shown, placeholder: "Enter text and select algorithms" |
| **Ready** | Text entered + algorithms checked | Compute button becomes primary blue |
| **Loading** | Submit | Each result card shows skeleton in parallel (API calls fire simultaneously) |
| **Success** | All responses received | Cards appear with stagger animation (50ms between each) |
| **Partial** | Some algorithms fail | Successful cards show normally; failed card shows error icon + message |
| **Avalanche demo** | User changes 1 character | Previous hashes dim, new hashes appear below with diff-highlighting |
| **Error** | Network failure | Global error toast, results area unchanged |

### 4.7 Wow Moment

**Avalanche visualization**: When the user modifies even one character, the page shows the previous hash grayed out above the new hash, with byte-level diff coloring. Changed bytes highlighted in red, unchanged in green. For SHA-256, changing "hello" to "hallo" results in ~50% byte change — visually dramatic, pedagogically essential. A small "% changed" badge reinforces the avalanche effect concept.

---

## Page 5: HMAC & PBKDF2 (`/hmac-pbkdf2`)

### 5.1 Route & Permissions

| Field | Value |
|---|---|
| Path | `/hmac-pbkdf2` |
| Auth required | No |
| Vue component | `HmacPbkdf2View.vue` |

### 5.2 Purpose

Two related operations: HMAC (keyed-hash message authentication) and PBKDF2 (password-based key derivation). These are grouped because both build on hash functions and represent "hash + secret" workflows.

### 5.3 Data Sources

| Action | Endpoint | Request | Response |
|---|---|---|---|
| HMAC | `POST /api/v1/hash/hmac/{algo}` | `{ key, message, algorithm }` | `{ mac_hex, algorithm }` |
| PBKDF2 | `POST /api/v1/hash/pbkdf2` | `{ password, salt, iterations, key_len }` | `{ derived_key_hex, iterations, warning? }` |

`{algo}` for HMAC: `sha1`, `sha256`

### 5.4 Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│ Page Title: "HMAC & Key Derivation"                     │
│ Subtitle: "Message authentication and PBKDF2"           │
├─────────────────────────────────────────────────────────┤
│ el-tabs: [HMAC] [PBKDF2]                               │
├─────────────────────────────────────────────────────────┤
│ === HMAC Tab ===                                        │
│ ┌────────────────────┬──────────────────────────────┐  │
│ │ Key:               │ Result:                      │  │
│ │ [______________]   │                              │  │
│ │                    │ MAC (hex):                   │  │
│ │ Message:           │ ┌──────────────────────────┐ │  │
│ │ [______________]   │ │ b0344c61d8db38535ca8...  │ │  │
│ │ [______________]   │ └─────────────────[Copy]──┘ │  │
│ │                    │                              │  │
│ │ Algorithm:         │ Algorithm: HMAC-SHA256       │  │
│ │ ○ SHA-1  ● SHA-256 │                              │  │
│ │                    │ OperationTimer: 0.05ms       │  │
│ │ [Compute HMAC]     │                              │  │
│ └────────────────────┴──────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ === PBKDF2 Tab ===                                      │
│ ┌────────────────────┬──────────────────────────────┐  │
│ │ Password:          │ Derived Key (hex):           │  │
│ │ [______________]   │ ┌──────────────────────────┐ │  │
│ │                    │ │ 120fb6cffcf8b32c43e7...  │ │  │
│ │ Salt:              │ └─────────────────[Copy]──┘ │  │
│ │ [______________]   │                              │  │
│ │                    │ Iterations: 100,000          │  │
│ │ Iterations:        │ Key length: 32 bytes         │  │
│ │ [___100000___]     │                              │  │
│ │ (el-slider below)  │ ⚠ Warning:                  │  │
│ │ 1K ──────── 1M     │ "iterations < 100000 is     │  │
│ │                    │  weak for password storage"  │  │
│ │ Key length (bytes):│                              │  │
│ │ [___32___]         │ OperationTimer: 45.2ms       │  │
│ │                    │                              │  │
│ │ [Derive Key]       │                              │  │
│ └────────────────────┴──────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 5.5 Example Data

**HMAC request:**
```json
{ "key": "secret-key", "message": "Hello, HMAC!", "algorithm": "sha256" }
```

**HMAC response:**
```json
{
  "mac_hex": "b0344c61d8db38535ca8afcedb13f1ca4d0cf48126f1bfb8a8b3cd9ab0c2918c",
  "algorithm": "sha256"
}
```

**PBKDF2 request:**
```json
{ "password": "my-password", "salt": "random-salt-value", "iterations": 100000, "key_len": 32 }
```

**PBKDF2 response:**
```json
{
  "derived_key_hex": "120fb6cffcf8b32c43e7225256c4f837a86548c92ccc35480805987cb70be17b",
  "iterations": 100000,
  "warning": null
}
```

**PBKDF2 with low iterations:**
```json
{
  "derived_key_hex": "...",
  "iterations": 1000,
  "warning": "iterations below 100000 is considered weak for password hashing"
}
```

### 5.6 State Specification

| State | Trigger | Visual |
|---|---|---|
| **Empty** | Page load | Form empty, result panel shows ghost |
| **Loading** | Submit | Button spinner; for PBKDF2 with high iterations, show progress estimate |
| **Success** | Response received | MAC/derived key revealed with animation |
| **Warning** | PBKDF2 iterations < 100000 | Yellow warning banner in result area with `warning` text from API |
| **Error (empty key)** | HMAC with empty key field | Inline validation: "Key is required" |
| **Error (iterations too low)** | iterations < 1000 | Pydantic validation error shown inline |

### 5.7 Wow Moment

**PBKDF2 timing slider**: The iterations field has an el-slider (1K to 1M, logarithmic scale). As the user drags the slider, a real-time estimate of computation time appears: "~0.5ms" at 1K, "~45ms" at 100K, "~450ms" at 1M. After computing, the actual time displays next to the estimate for comparison. This viscerally demonstrates why iteration count matters for password security.

---

## Page 6: Encoding (`/encoding`)

### 6.1 Route & Permissions

| Field | Value |
|---|---|
| Path | `/encoding` |
| Auth required | No |
| Vue component | `EncodingView.vue` |

### 6.2 Purpose

Base64 encoding and decoding. Simple tool-style page for converting between raw text and Base64 representation. UTF-8 encoding is listed but marked as "coming soon" since it's not implemented in the current backend phase.

### 6.3 Data Sources

| Action | Endpoint | Request | Response |
|---|---|---|---|
| Base64 encode | `POST /api/v1/encoding/base64/encode` | `{ data: string }` | `{ encoded: string }` |
| Base64 decode | `POST /api/v1/encoding/base64/decode` | `{ encoded: string }` | `{ data: string }` |

### 6.4 Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│ Page Title: "Encoding"                                  │
│ Subtitle: "Base64 & UTF-8 data encoding"                │
├─────────────────────────────────────────────────────────┤
│ Two-panel mirror layout with swap button                │
│                                                         │
│ ┌──────────────┐   [⇄]   ┌──────────────┐             │
│ │ Plain Text   │  swap    │ Base64       │             │
│ │              │  button  │              │             │
│ │ el-input     │         │ el-input     │             │
│ │ textarea     │         │ textarea     │             │
│ │ rows=8       │         │ rows=8       │             │
│ │              │         │              │             │
│ │ "Hello,      │         │ "SGVsbG8s    │             │
│ │  World!"     │         │  IFdvcmxk   │             │
│ │              │         │  IQ=="       │             │
│ │              │         │              │             │
│ │ Chars: 13    │         │ Chars: 20    │             │
│ └──────────────┘         └──────────────┘             │
│                                                         │
│ [Encode →]              [← Decode]                      │
│                                                         │
│ Size comparison:                                        │
│ "Original: 13 bytes → Encoded: 20 bytes (1.54x)"       │
├─────────────────────────────────────────────────────────┤
│ UTF-8 Section (dimmed, "Coming Soon" badge)             │
│ ┌───────────────────────────────────────────────────┐  │
│ │ UTF-8 encode/decode — not available in this phase │  │
│ │ [Disabled inputs with placeholder text]           │  │
│ └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 6.5 Example Data

**Encode request:**
```json
{ "data": "Hello, World!" }
```

**Encode response:**
```json
{ "encoded": "SGVsbG8sIFdvcmxkIQ==" }
```

**Decode request:**
```json
{ "encoded": "SGVsbG8sIFdvcmxkIQ==" }
```

**Decode response:**
```json
{ "data": "Hello, World!" }
```

**Invalid Base64 decode error:**
```json
{ "code": 2003, "message": "encoded must be standard Base64" }
```

### 6.6 State Specification

| State | Trigger | Visual |
|---|---|---|
| **Empty** | Page load | Both textareas empty, buttons disabled |
| **Ready** | Text entered in either panel | Corresponding encode/decode button activates |
| **Loading** | Submit | Tiny spinner on button |
| **Success** | Response received | Output panel fills with smooth character-by-character typing animation |
| **Error (invalid base64)** | Decode with bad input | Right panel border turns red, error tooltip: "Invalid Base64 string" |
| **UTF-8 disabled** | Always | Bottom section 50% opacity, "Coming Soon" el-tag |

### 6.7 Wow Moment

**Live byte visualization**: Below each textarea, a byte-grid shows the raw bytes of the text. Plain text side shows ASCII codes (72 65 6C 6C 6F...), Base64 side shows the 6-bit grouping with color bands showing how 3 input bytes map to 4 output characters. Hovering over a Base64 character highlights the corresponding source bytes and vice versa.

---

## Page 7: RSA (`/rsa`)

### 7.1 Route & Permissions

| Field | Value |
|---|---|
| Path | `/rsa` |
| Auth required | Yes |
| Vue component | `RsaView.vue` |

### 7.2 Purpose

RSA-1024 public key cryptography workbench. Supports key generation (stored in key store with KEK wrapping), encryption/decryption, and digital signature/verification. All operations use key_id references to the server-side key store.

### 7.3 Data Sources

| Action | Endpoint | Request | Response |
|---|---|---|---|
| Keygen | `POST /api/v1/pubkey/rsa/keygen` | `{ bits: 1024, e: 65537, label? }` | `{ private_key_id, public_key_id, algorithm, bits }` |
| Encrypt | `POST /api/v1/pubkey/rsa/encrypt` | `{ plaintext, key_id }` | `{ ciphertext_hex }` |
| Decrypt | `POST /api/v1/pubkey/rsa/decrypt` | `{ ciphertext_hex, key_id }` | `{ plaintext }` |
| Sign | `POST /api/v1/pubkey/rsa/sign` | `{ message, key_id }` | `{ signature_hex }` |
| Verify | `POST /api/v1/pubkey/rsa/verify` | `{ message, signature_hex, key_id }` | `{ valid: boolean }` |
| Export pub | `GET /api/v1/keys/{key_id}/public` | — | `{ key_id, algorithm, material: { n_hex, e_hex } }` |
| List keys | `GET /api/v1/keys` | — | `KeyListItem[]` |

### 7.4 Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│ Page Title: "RSA Cryptography"                          │
│ Subtitle: "1024-bit key generation, encryption & signing"│
├─────────────────────────────────────────────────────────┤
│ Key Generation Bar                                      │
│ ┌───────────────────────────────────────────────────┐  │
│ │ [Generate RSA-1024 Key Pair]  Label: [_________]  │  │
│ │                                                   │  │
│ │ Active keys: private_key_id = b7e15...            │  │
│ │              public_key_id  = c8f26...            │  │
│ │              [View Public Key Material ▾]         │  │
│ │              n_hex: 00b3a7c9... (128 hex chars)   │  │
│ │              e_hex: 010001                        │  │
│ └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ el-tabs: [Encrypt/Decrypt] [Sign/Verify]                │
├─────────────────────────────────────────────────────────┤
│ === Encrypt/Decrypt Tab ===                             │
│ ┌────────────────────┬──────────────────────────────┐  │
│ │ Mode: ○Encrypt ○Dec│ Output:                      │  │
│ │                    │                              │  │
│ │ Key:               │ Ciphertext (hex):            │  │
│ │ [KeyIdPicker ▾]    │ ┌──────────────────────────┐ │  │
│ │ (public for enc,   │ │ 4a3f8b2c1d5e6f7a8b...  │ │  │
│ │  private for dec)  │ │ (256 hex chars)          │ │  │
│ │                    │ └─────────────────[Copy]──┘ │  │
│ │ Plaintext:         │                              │  │
│ │ [______________]   │ OperationTimer: 12.3ms       │  │
│ │                    │                              │  │
│ │ [Execute]          │                              │  │
│ └────────────────────┴──────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ === Sign/Verify Tab ===                                 │
│ ┌────────────────────┬──────────────────────────────┐  │
│ │ Mode: ○Sign ○Verify│ Output:                      │  │
│ │                    │                              │  │
│ │ Key:               │ Signature (hex):             │  │
│ │ [KeyIdPicker ▾]    │ ┌──────────────────────────┐ │  │
│ │ (private for sign, │ │ 7d2f3a8c...             │ │  │
│ │  public for verify)│ └─────────────────[Copy]──┘ │  │
│ │                    │                              │  │
│ │ Message:           │ — OR for verify —            │  │
│ │ [______________]   │                              │  │
│ │                    │ ✅ Signature is VALID        │  │
│ │ Signature (verify):│    (green big checkmark)     │  │
│ │ [______________]   │ — OR —                       │  │
│ │                    │ ❌ Signature is INVALID      │  │
│ │ [Execute]          │    (red X with shake anim)   │  │
│ └────────────────────┴──────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 7.5 Example Data

**Keygen response:**
```json
{
  "private_key_id": "b7e15163-4aed-2b9e-9c87-53d8a2f77e1a",
  "public_key_id": "c8f26274-5bfe-3caf-ad98-64e9b3087f2b",
  "algorithm": "rsa",
  "bits": 1024
}
```

**Encrypt request:**
```json
{ "plaintext": "Secret message", "key_id": "c8f26274-5bfe-3caf-ad98-64e9b3087f2b" }
```

**Encrypt response:**
```json
{ "ciphertext_hex": "4a3f8b2c1d5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f..." }
```

**Sign response:**
```json
{ "signature_hex": "7d2f3a8c9b1e4d5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e..." }
```

**Verify response (valid):**
```json
{ "valid": true }
```

**Public key export:**
```json
{
  "key_id": "c8f26274-5bfe-3caf-ad98-64e9b3087f2b",
  "algorithm": "rsa",
  "material": {
    "n_hex": "00b3a7c9e1f5d2a8b6c4e3f7d1a9b5c8e2f6d4a0b7c3e9f5d1a8b4c6e0f2d7...",
    "e_hex": "010001"
  }
}
```

### 7.6 State Specification

| State | Trigger | Visual |
|---|---|---|
| **No key** | Page load, no RSA keys exist | Prominent keygen card: "Generate your first RSA key pair to get started" |
| **Keygen loading** | Click generate | Full-width progress bar: "Generating 1024-bit primes... (typically 100-500ms)" |
| **Keygen success** | Response received | Key IDs appear with confetti-like particle burst, auto-selected in picker |
| **Ready** | Key selected + input filled | Execute button active |
| **Encrypting** | Submit encrypt | Spinner with "Encrypting with RSA..." |
| **Encrypt success** | Ciphertext received | Hex viewer reveals ciphertext, byte count shown |
| **Verify valid** | `valid: true` | Large animated green checkmark, "Signature Valid" in green |
| **Verify invalid** | `valid: false` | Large red X with shake animation, "Signature Invalid" in red |
| **Error (key type mismatch)** | code 4203 | Error: "Cannot encrypt with a private key — select the public key" |
| **Error (private access denied)** | code 4204 | Error: "Cannot export private key material" |

### 7.7 Wow Moment

**Key generation progress**: During RSA keygen (which takes 100-500ms due to prime generation), an animated visualization shows the Miller-Rabin primality testing process: a stream of candidate numbers appearing and being crossed out (composite) or confirmed (prime). When both primes are found, they visually "multiply" into the modulus n. This demystifies the key generation process that is usually a black box.

---

## Page 8: ECC & ECDSA (`/ecc`)

### 8.1 Route & Permissions

| Field | Value |
|---|---|
| Path | `/ecc` |
| Auth required | Yes |
| Vue component | `EccView.vue` |

### 8.2 Purpose

Elliptic Curve Cryptography on secp160r1. Supports key pair generation and ECDSA digital signatures (sign + verify). Unlike RSA, ECC here only supports signing — no encryption endpoint is exposed.

### 8.3 Data Sources

| Action | Endpoint | Request | Response |
|---|---|---|---|
| Keygen | `POST /api/v1/pubkey/ecc/keygen` | `{ curve: "secp160r1", label? }` | `{ private_key_id, public_key_id, algorithm, curve }` |
| Sign | `POST /api/v1/pubkey/ecdsa/sign` | `{ message, key_id, curve }` | `{ r_hex, s_hex, curve }` |
| Verify | `POST /api/v1/pubkey/ecdsa/verify` | `{ message, r_hex, s_hex, key_id, curve }` | `{ valid: boolean, curve }` |
| Export pub | `GET /api/v1/keys/{key_id}/public` | — | `{ material: { qx_hex, qy_hex, curve } }` |

### 8.4 Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│ Page Title: "Elliptic Curve Cryptography"               │
│ Subtitle: "ECDSA signatures on secp160r1"               │
├─────────────────────────────────────────────────────────┤
│ Curve Info Banner                                       │
│ ┌───────────────────────────────────────────────────┐  │
│ │ Curve: secp160r1  |  Field: 160-bit  |  Group     │  │
│ │ order: 2^160 approx  |  RFC 6979 deterministic k  │  │
│ └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ Key Pair Section                                        │
│ ┌───────────────────────────────────────────────────┐  │
│ │ [Generate ECC Key Pair]  Label: [_________]       │  │
│ │                                                   │  │
│ │ Public Point (when generated):                    │  │
│ │ Qx: 0a1b2c3d4e5f... (40 hex)                    │  │
│ │ Qy: 9f8e7d6c5b4a... (40 hex)                    │  │
│ │                                                   │  │
│ │ [Elliptic Curve Point Visualization]              │  │
│ │ (ECharts scatter plot of Q on the curve)          │  │
│ └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ ┌────────────────────┬──────────────────────────────┐  │
│ │ Mode: ○Sign ○Verify│ Output:                      │  │
│ │                    │                              │  │
│ │ Key:               │ Signature:                   │  │
│ │ [KeyIdPicker ▾]    │ r: 0a1b2c3d... (40 hex)     │  │
│ │                    │ s: 5e6f7a8b... (40 hex)     │  │
│ │ Message:           │                  [Copy r+s]  │  │
│ │ [______________]   │                              │  │
│ │                    │ — OR for verify —            │  │
│ │ (Verify mode:)     │ ✅ Signature VALID           │  │
│ │ r_hex: [________]  │ ❌ Signature INVALID         │  │
│ │ s_hex: [________]  │                              │  │
│ │                    │ OperationTimer: 3.5ms        │  │
│ │ [Execute]          │                              │  │
│ └────────────────────┴──────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 8.5 Example Data

**Keygen response:**
```json
{
  "private_key_id": "d9a37385-6cfe-4dbf-be09-75fab4198e3c",
  "public_key_id": "ea048496-7d0f-5ec0-cf1a-86fbc52a9f4d",
  "algorithm": "ecc",
  "curve": "secp160r1"
}
```

**Sign response:**
```json
{
  "r_hex": "0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b",
  "s_hex": "5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f",
  "curve": "secp160r1"
}
```

**Verify response:**
```json
{ "valid": true, "curve": "secp160r1" }
```

**Public key export:**
```json
{
  "key_id": "ea048496-7d0f-5ec0-cf1a-86fbc52a9f4d",
  "algorithm": "ecc",
  "material": {
    "qx_hex": "0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b",
    "qy_hex": "9f8e7d6c5b4a39281706f5e4d3c2b1a09f8e7d6c",
    "curve": "secp160r1"
  }
}
```

### 8.6 State Specification

| State | Trigger | Visual |
|---|---|---|
| **No key** | No ECC keys | Keygen card: "Generate an ECC key pair on secp160r1" |
| **Keygen success** | Key pair created | Public point coordinates appear, curve visualization renders |
| **Signing** | Submit sign | Spinner: "Computing ECDSA signature (RFC 6979)..." |
| **Sign success** | (r, s) received | Two hex viewers for r and s, both with copy buttons |
| **Verify valid** | `valid: true` | Green checkmark animation |
| **Verify invalid** | `valid: false` | Red X with shake |
| **Error (wrong key type)** | code 4203 | "This key is RSA, not ECC" |

### 8.7 Wow Moment

**Elliptic curve point plot**: An ECharts scatter plot shows the secp160r1 curve (simplified to a visible field for demonstration). The generated public key point Q is plotted on the curve with a pulsing marker. When signing, an animated dot traces the scalar multiplication path from the generator point G to the ephemeral point kG, illustrating the ECDSA signing process visually.

---

## Page 9: Key Store (`/keys`)

### 9.1 Route & Permissions

| Field | Value |
|---|---|
| Path | `/keys` |
| Auth required | Yes |
| Vue component | `KeysView.vue` |

### 9.2 Purpose

Central key management page. Lists all keys owned by the current user, shows metadata (algorithm, type, creation date, paired key relationship), and supports key revocation (soft delete). Public key material can be exported. This is the "KMS lite" view that demonstrates secure key lifecycle management.

### 9.3 Data Sources

| Action | Endpoint | Request | Response |
|---|---|---|---|
| List keys | `GET /api/v1/keys` | — | `KeyListItem[]` |
| Export public | `GET /api/v1/keys/{key_id}/public` | — | `{ key_id, algorithm, material }` |
| Revoke | `DELETE /api/v1/keys/{key_id}` | — | `null` |

### 9.4 Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│ Page Title: "Key Store"                                 │
│ Subtitle: "Manage your cryptographic keys"              │
├─────────────────────────────────────────────────────────┤
│ Toolbar                                                 │
│ ┌───────────────────────────────────────────────────┐  │
│ │ Filter: [All Types ▾] [All Algorithms ▾]          │  │
│ │ Search: [___________]  Key count: 24              │  │
│ └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ Key Table (el-table)                                    │
│ ┌────────┬────────┬──────┬────────┬──────┬──────────┐  │
│ │ Key ID │ Type   │ Algo │ Label  │ Pair │ Created  │  │
│ ├────────┼────────┼──────┼────────┼──────┼──────────┤  │
│ │ b7e1.. │ sym    │ AES  │ My key │  —   │ 06-07    │  │
│ │ c8f2.. │ rsa_pub│ RSA  │ RSA #1 │d9a3..│ 06-07    │  │
│ │ d9a3.. │ rsa_pri│ RSA  │ RSA #1 │c8f2..│ 06-07    │  │
│ │ ea04.. │ ecc_pub│ ECC  │ ECC #1 │fb15..│ 06-06    │  │
│ │ fb15.. │ ecc_pri│ ECC  │ ECC #1 │ea04..│ 06-06    │  │
│ ├────────┴────────┴──────┴────────┴──────┴──────────┤  │
│ │ Pagination: < 1 2 3 > (10 per page)              │  │
│ └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ Key Detail Panel (when row selected)                    │
│ ┌───────────────────────────────────────────────────┐  │
│ │ Key ID: c8f26274-5bfe-3caf-ad98-64e9b3087f2b     │  │
│ │ Type: rsa_public  Algorithm: RSA  Bits: 1024      │  │
│ │ Label: "RSA #1"                                   │  │
│ │ Paired with: d9a37385... (private key)            │  │
│ │ Created: 2026-06-07 14:30:00                      │  │
│ │ Expires: never                                    │  │
│ │                                                   │  │
│ │ Public Material:                                  │  │
│ │ n: 00b3a7c9e1f5d2a8b6c4e3f7d1a9b5c8...  [Copy]  │  │
│ │ e: 010001                                [Copy]  │  │
│ │                                                   │  │
│ │ [Revoke Key]  (red, requires confirmation)        │  │
│ └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 9.5 Example Data

**Key list response:**
```json
[
  {
    "id": "b7e15163-4aed-2b9e-9c87-53d8a2f77e1a",
    "key_type": "symmetric",
    "algorithm": "aes",
    "paired_key_id": null,
    "label": "My AES-256 key",
    "created_at": "2026-06-07T14:30:00Z",
    "expires_at": null
  },
  {
    "id": "c8f26274-5bfe-3caf-ad98-64e9b3087f2b",
    "key_type": "rsa_public",
    "algorithm": "rsa",
    "paired_key_id": "d9a37385-6cfe-4dbf-be09-75fab4198e3c",
    "label": "RSA #1",
    "created_at": "2026-06-07T14:32:00Z",
    "expires_at": null
  }
]
```

### 9.6 State Specification

| State | Trigger | Visual |
|---|---|---|
| **Loading** | Page load | Table skeleton with 5 shimmer rows |
| **Empty** | No keys | Empty state illustration: locked vault, "No keys yet — generate one from any algorithm page" |
| **Loaded** | Keys fetched | Table populated, row click opens detail panel |
| **Detail open** | Row click | Right-side panel slides in with key details |
| **Export loading** | Click "View Material" on public key | Spinner in detail panel |
| **Revoke confirm** | Click "Revoke Key" | el-popconfirm: "Are you sure? This key will be soft-deleted and cannot be used for operations." |
| **Revoke success** | 200 | Row fades out with strikethrough animation, count decrements |
| **Error (not owned)** | code 4201 | Error: "You don't own this key" (should not happen in normal UI flow) |

### 9.7 Wow Moment

**Key relationship graph**: Above the table, a small node-link diagram (ECharts graph) visualizes key pair relationships. Symmetric keys appear as single nodes; RSA/ECC pairs appear as connected node pairs (public ↔ private). Nodes are colored by algorithm type. Hovering a node highlights its pair. This makes the "paired_key_id" relationship tangible and demonstrates key lifecycle visually.

---

## Page 10: Audit Logs (`/audit`)

### 10.1 Route & Permissions

| Field | Value |
|---|---|
| Path | `/audit` |
| Auth required | Yes |
| Vue component | `AuditView.vue` |
| Note | Regular users see only their own logs; admin sees all |

### 10.2 Purpose

Searchable, filterable view of all cryptographic operation logs. Demonstrates the platform's observability and compliance capabilities. Each log entry shows trace_id, operation, algorithm, key reference (by ID, never raw material), input/output SHA-256 fingerprints, status, timing, and timestamp.

### 10.3 Data Sources

| Action | Endpoint | Request (query params) | Response |
|---|---|---|---|
| List logs | `GET /api/v1/audit/logs` | `?user_id=&algorithm=&since=&until=&limit=&offset=` | `OperationLogItem[]` |

### 10.4 Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│ Page Title: "Audit Logs"                                │
│ Subtitle: "Cryptographic operation history"             │
├─────────────────────────────────────────────────────────┤
│ Filter Bar                                              │
│ ┌───────────────────────────────────────────────────┐  │
│ │ Algorithm: [All ▾]  Since: [📅_____]              │  │
│ │ Until: [📅_____]   Status: [All ▾]               │  │
│ │ [Search]  [Reset Filters]                         │  │
│ └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ Log Table (el-table, sortable columns)                  │
│ ┌─────────┬──────────┬────────┬────────┬──────┬──────┐ │
│ │Trace ID │Operation │Algo    │Key ID  │Status│Time  │ │
│ ├─────────┼──────────┼────────┼────────┼──────┼──────┤ │
│ │a1b2c3.. │aes_enc   │AES-GCM │b7e1.. │1000  │0.4ms │ │
│ │d4e5f6.. │rsa_kgen  │RSA-1024│c8f2.. │1000  │234ms │ │
│ │g7h8i9.. │sha256    │SHA-256 │ —     │1000  │0.1ms │ │
│ │j0k1l2.. │aes_dec   │AES-GCM │b7e1.. │3002  │0.3ms │ │
│ ├─────────┴──────────┴────────┴────────┴──────┴──────┤ │
│ │ Showing 1-20 of 156    < 1 2 3 ... 8 >             │ │
│ └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ Log Detail Drawer (when row clicked)                    │
│ ┌───────────────────────────────────────────────────┐  │
│ │ Trace ID: a1b2c3d4-e5f6-7890-abcd-ef1234567890   │  │
│ │ User ID: 1                                        │  │
│ │ Operation: aes_encrypt                            │  │
│ │ Algorithm: AES-GCM                                │  │
│ │ Key ID: b7e15163-4aed-2b9e-9c87-53d8a2f77e1a     │  │
│ │ Input Hash (SHA-256):                             │  │
│ │   2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1f...  │  │
│ │ Output Hash (SHA-256):                            │  │
│ │   9b74c9897bac770ffc029ffd720d2b6b0a5f5e15e2...  │  │
│ │ Status Code: 1000 (Success)                       │  │
│ │ Duration: 0.42ms                                  │  │
│ │ Client IP: 127.0.0.1                              │  │
│ │ Created: 2026-06-07T14:32:15.123Z                 │  │
│ └───────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 10.5 Example Data

**Audit log entry:**
```json
{
  "id": 42,
  "trace_id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "user_id": 1,
  "operation": "aes_encrypt",
  "algorithm": "AES-GCM",
  "key_id": "b7e15163-4aed-2b9e-9c87-53d8a2f77e1a",
  "input_hash": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
  "output_hash": "9b74c9897bac770ffc029ffd720d2b6b0a5f5e15e21ad45fde6a78ac7e51e2f3",
  "status_code": 1000,
  "duration_ms": 0.42,
  "client_ip": "127.0.0.1",
  "created_at": "2026-06-07T14:32:15.123Z"
}
```

### 10.6 State Specification

| State | Trigger | Visual |
|---|---|---|
| **Loading** | Page load or filter change | Table body replaced with skeleton rows |
| **Loaded** | Response received | Table populated, pagination active |
| **Empty** | No logs match filters | "No operations recorded yet" with illustration |
| **Filtered empty** | Filters active but no matches | "No results for these filters — try broadening your search" |
| **Detail open** | Row click | Right drawer slides in with full log detail |
| **Error** | API failure | Error banner above table |
| **Status color coding** | Always | 1000 = green tag, 2xxx = yellow, 3xxx = orange, 4xxx = red, 5xxx = dark red |

### 10.7 Wow Moment

**Timeline heatmap**: Above the table, an ECharts calendar heatmap (or hour-of-day heatmap for today) shows operation density. Darker cells = more operations. Clicking a cell filters the table to that time range. This gives an instant visual overview of platform activity and demonstrates the "observability" design principle.

---

## Page 11: Benchmark (`/benchmark`)

### 11.1 Route & Permissions

| Field | Value |
|---|---|
| Path | `/benchmark` |
| Auth required | Yes |
| Vue component | `BenchmarkView.vue` |

### 11.2 Purpose

Run and compare throughput benchmarks for all algorithms. Generates ECharts bar charts showing MB/s throughput and ns/op latency. Allows comparing hand-written implementations' performance.

### 11.3 Data Sources

| Action | Endpoint | Request | Response |
|---|---|---|---|
| Run benchmark | `GET /api/v1/benchmark/{algo}` | — | `{ algorithm, data_size_bytes, iterations, total_ms, throughput_mb_per_s, ns_per_op }` |

`{algo}` examples: `sha256`, `sha3_256`, `aes_ecb`, `aes_gcm`, `sm4_ecb`, `rc6_ecb`, `rsa_encrypt`, `ecdsa_sign`

### 11.4 Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│ Page Title: "Performance Benchmark"                     │
│ Subtitle: "Throughput and latency of hand-written algos"│
├─────────────────────────────────────────────────────────┤
│ Algorithm Selector                                      │
│ ┌───────────────────────────────────────────────────┐  │
│ │ Category: [All] [Symmetric] [Hash] [Public Key]   │  │
│ │                                                   │  │
│ │ Algorithms (checkbox grid):                       │  │
│ │ [✓] AES-ECB  [✓] AES-GCM  [✓] SM4-ECB           │  │
│ │ [✓] RC6-ECB  [✓] SHA-256  [✓] SHA3-256           │  │
│ │ [ ] SHA-1    [ ] SHA-512  [ ] RIPEMD-160          │  │
│ │ [ ] RSA-Enc  [ ] ECDSA-Sign                       │  │
│ │                                                   │  │
│ │ [Run Selected Benchmarks]                         │  │
│ └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ Results Chart (ECharts horizontal bar)                   │
│ ┌───────────────────────────────────────────────────┐  │
│ │ Throughput (MB/s)                                 │  │
│ │                                                   │  │
│ │ AES-ECB    ████████████████████  820 MB/s         │  │
│ │ AES-GCM    ███████████████████   780 MB/s         │  │
│ │ SM4-ECB    █████████            380 MB/s          │  │
│ │ RC6-ECB    ██████████           420 MB/s          │  │
│ │ SHA-256    ██████████████████████ 900 MB/s        │  │
│ │ SHA3-256   █████████████          520 MB/s        │  │
│ └───────────────────────────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ Results Table                                           │
│ ┌──────────┬──────────┬──────┬─────────┬─────────────┐ │
│ │Algorithm │Data Size │Iters │Total ms │Throughput   │ │
│ ├──────────┼──────────┼──────┼─────────┼─────────────┤ │
│ │AES-ECB   │1.00 MB   │100   │121.5    │820 MB/s     │ │
│ │AES-GCM   │1.00 MB   │100   │128.2    │780 MB/s     │ │
│ │SHA-256   │1.00 MB   │100   │111.1    │900 MB/s     │ │
│ └──────────┴──────────┴──────┴─────────┴─────────────┘ │
└─────────────────────────────────────────────────────────┘
```

### 11.5 Example Data

**Benchmark response (AES-ECB):**
```json
{
  "algorithm": "aes_ecb",
  "data_size_bytes": 1048576,
  "iterations": 100,
  "total_ms": 121.5,
  "throughput_mb_per_s": 823.05,
  "ns_per_op": 1215000.0
}
```

**Benchmark response (SHA-256):**
```json
{
  "algorithm": "sha256",
  "data_size_bytes": 1048576,
  "iterations": 100,
  "total_ms": 111.1,
  "throughput_mb_per_s": 900.09,
  "ns_per_op": 1111000.0
}
```

### 11.6 State Specification

| State | Trigger | Visual |
|---|---|---|
| **Empty** | Page load | No chart, algorithm selector ready, "Select algorithms and run" |
| **Running** | Click run | Progress indicator: "Running benchmark 2/6: SM4-ECB..." Each completed algo appears as its bar grows in real-time |
| **Complete** | All benchmarks done | Full chart + table displayed |
| **Partial** | Some fail | Completed ones show; failed ones show gray bar with error tooltip |
| **Error** | Network failure | Error toast, partial results preserved |

### 11.7 Wow Moment

**Live racing bars**: As each benchmark completes, its bar in the chart animates from 0 to its throughput value. When all are done, a brief "race" animation replays all bars growing simultaneously, making it visually obvious which algorithms are fastest. The chart auto-sorts by throughput with a smooth reorder animation.

---

## Page 12: Security Demos (`/demos`)

### 12.1 Route & Permissions

| Field | Value |
|---|---|
| Path | `/demos` |
| Auth required | No (demo_access_dependency handles access) |
| Vue component | `DemosView.vue` |

### 12.2 Purpose

Four interactive vulnerability demonstrations, each showing a real cryptographic attack and its mitigation. Educational purpose: students see WHY certain practices (ECB mode, k-reuse, small exponents, low iteration counts) are dangerous.

### 12.3 Data Sources

| Demo | Endpoint | Request | Key Response Fields |
|---|---|---|---|
| ECB Image Leak | `POST /api/v1/demos/ecb_image_leak` | `{ image_b64, key_hex }` | `{ banner, original_png_b64, ecb_encrypted_png_b64, cbc_encrypted_png_b64, block_count, duplicate_block_ratio }` |
| ECDSA k-Reuse | `POST /api/v1/demos/ecdsa_k_reuse` | `{ message1, message2, curve }` | `{ banner, private_key_hex, reused_k_hex, signature1, signature2, r_equal, recovered_d_hex, recovery_matches_original }` |
| RSA Low Exponent | `POST /api/v1/demos/rsa_low_exponent` | `{ message, bits }` | `{ banner, n_hex, e, ciphertext_hex, cube_safe, recovered_plaintext, recovery_matches_original }` |
| PBKDF2 Impact | `POST /api/v1/demos/pbkdf2_iteration_impact` | `{ password, salt_hex, key_len, iterations_list }` | `{ banner, measurements[], ratio_1m_over_100k, verdict }` |

### 12.4 Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│ Page Title: "Security Demos"                            │
│ Subtitle: "Interactive vulnerability demonstrations"    │
│                                                         │
│ ⚠ StatusBanner: "These demos intentionally use WEAK    │
│   parameters to demonstrate attacks. NEVER use these    │
│   settings in production."                              │
├─────────────────────────────────────────────────────────┤
│ Demo Tabs: [ECB Image] [ECDSA k-Reuse] [RSA e=3]      │
│            [PBKDF2 Iterations]                          │
├─────────────────────────────────────────────────────────┤
│ === ECB Image Leak Tab ===                              │
│ ┌────────────────────┬──────────────────────────────┐  │
│ │ Upload Image:      │ Results:                     │  │
│ │ [📁 Drop or Click]│                              │  │
│ │                    │ Original │ ECB-Enc │ CBC-Enc │  │
│ │ AES-128 Key (hex): │ ┌─────┐  ┌─────┐  ┌─────┐  │  │
│ │ [00112233...]      │ │ img │  │ img │  │ img │  │  │
│ │ [Random Key]       │ └─────┘  └─────┘  └─────┘  │  │
│ │                    │                              │  │
│ │ [Run Demo]         │ Block count: 1024            │  │
│ │                    │ Duplicate ratio: 47.3%       │  │
│ │                    │ "ECB preserves patterns!"    │  │
│ └────────────────────┴──────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ === ECDSA k-Reuse Tab ===                               │
│ ┌────────────────────┬──────────────────────────────┐  │
│ │ Message 1:         │ Attack Result:               │  │
│ │ [______________]   │                              │  │
│ │ Message 2:         │ Private key (generated):     │  │
│ │ [______________]   │ d = 0a1b2c... [hidden ▾]     │  │
│ │                    │                              │  │
│ │ [Run Attack Demo]  │ Sig 1: r=AAA..., s=BBB...   │  │
│ │                    │ Sig 2: r=AAA..., s=CCC...   │  │
│ │                    │ r values equal? ✅ YES       │  │
│ │                    │                              │  │
│ │                    │ Recovered d = 0a1b2c...      │  │
│ │                    │ Matches original? ✅ YES     │  │
│ │                    │                              │  │
│ │                    │ ⚠ "The attacker recovered   │  │
│ │                    │ the private key!"            │  │
│ └────────────────────┴──────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ === RSA Low Exponent Tab ===                            │
│ ┌────────────────────┬──────────────────────────────┐  │
│ │ Message:           │ Attack Result:               │  │
│ │ [__BUPT2026__]     │                              │  │
│ │                    │ n (1024-bit): 00b3a7...      │  │
│ │ [Run Attack Demo]  │ e = 3  ⚠                    │  │
│ │                    │ Ciphertext: m^3 = ...        │  │
│ │                    │ Cube root ∛c = ...           │  │
│ │                    │ Recovered: "BUPT2026"        │  │
│ │                    │ Matches? ✅ YES              │  │
│ └────────────────────┴──────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ === PBKDF2 Iterations Tab ===                           │
│ ┌────────────────────┬──────────────────────────────┐  │
│ │ Password:          │ Results:                     │  │
│ │ [__password__]     │                              │  │
│ │ Salt (hex):        │ ECharts bar chart:           │  │
│ │ [__73616c74__]     │ 1K    ████  0.5ms            │  │
│ │ Iterations:        │ 10K   ████████  4.8ms        │  │
│ │ [✓]1K [✓]10K      │ 100K  █████████████  45ms    │  │
│ │ [✓]100K [✓]1M     │ 1M    ██████████████████ 450ms│  │
│ │                    │                              │  │
│ │ [Run Comparison]   │ 1M/100K ratio: 10.0x         │  │
│ │                    │ Verdict: "Use ≥100K iters"   │  │
│ └────────────────────┴──────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 12.5 Example Data

**ECB Image Leak response:**
```json
{
  "banner": "WARNING: ECB mode leaks plaintext patterns. This demo uses intentionally weak encryption to illustrate the vulnerability.",
  "original_png_b64": "iVBORw0KGgo...",
  "ecb_encrypted_png_b64": "iVBORw0KGgo...",
  "cbc_encrypted_png_b64": "iVBORw0KGgo...",
  "block_count": 1024,
  "duplicate_block_ratio": 0.473
}
```

**ECDSA k-Reuse response:**
```json
{
  "banner": "WARNING: Reusing nonce k in ECDSA allows full private key recovery (PS3 hack, 2010).",
  "private_key_hex": "0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b",
  "public_key": { "qx_hex": "...", "qy_hex": "..." },
  "reused_k_hex": "1234567890abcdef1234567890abcdef12345678",
  "signature1": { "r_hex": "aabb...", "s_hex": "ccdd..." },
  "signature2": { "r_hex": "aabb...", "s_hex": "eeff..." },
  "r_equal": true,
  "recovered_d_hex": "0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b",
  "recovery_matches_original": true
}
```

**RSA Low Exponent response:**
```json
{
  "banner": "WARNING: RSA with e=3 and no padding allows plaintext recovery via cube root for short messages.",
  "n_hex": "00b3a7c9...",
  "e": 3,
  "ciphertext_hex": "...",
  "message_bits": 64,
  "n_bits": 1024,
  "cube_safe": false,
  "recovered_plaintext": "BUPT2026",
  "recovery_matches_original": true
}
```

**PBKDF2 Impact response:**
```json
{
  "banner": "This demo compares PBKDF2 computation time at various iteration counts.",
  "measurements": [
    { "iterations": 1000, "derived_key_hex": "...", "duration_ms": 0.5 },
    { "iterations": 10000, "derived_key_hex": "...", "duration_ms": 4.8 },
    { "iterations": 100000, "derived_key_hex": "...", "duration_ms": 45.2 },
    { "iterations": 1000000, "derived_key_hex": "...", "duration_ms": 452.1 }
  ],
  "ratio_1m_over_100k": 10.0,
  "verdict": "Use at least 100,000 iterations for password hashing. 1,000,000 recommended for high-value accounts."
}
```

### 12.6 State Specification

| State | Trigger | Visual |
|---|---|---|
| **Empty** | Tab selected, no demo run | Brief explanation of the vulnerability, illustration, "Run Demo" button |
| **Loading (ECB)** | Submit | "Encrypting image with ECB and CBC..." with progress |
| **Loading (ECDSA)** | Submit | "Generating keys, signing with reused k, recovering private key..." |
| **Loading (RSA)** | Submit | "Generating RSA key with e=3, encrypting, computing cube root..." |
| **Loading (PBKDF2)** | Submit | "Running PBKDF2 at 4 iteration counts..." with progress per iteration |
| **Result** | Response received | Full result panel with highlighted attack success |
| **ECB visual** | Image results | Three images side by side; ECB image still shows recognizable pattern |
| **Attack success** | recovery_matches_original = true | Red "ATTACK SUCCESSFUL" badge with explanation |
| **Error** | API failure | Error message in result area |

### 12.7 Wow Moment

**ECB penguin reveal**: For the ECB Image Leak demo, when the results load, the three images (original, ECB-encrypted, CBC-encrypted) are revealed left-to-right with a curtain animation. The ECB image clearly shows the original pattern through the "encryption" — a visual gut-punch that makes the ECB weakness unforgettable. A percentage badge shows the duplicate block ratio, and an animated highlight pulses on matching blocks.

---

## Page 13: Secure File Transfer (`/scenarios`)

### 13.1 Route & Permissions

| Field | Value |
|---|---|
| Path | `/scenarios` |
| Auth required | Yes |
| Vue component | `ScenariosView.vue` |

### 13.2 Purpose

End-to-end secure file transfer demonstration combining RSA (key exchange), AES-GCM (encryption), SHA-256 (integrity), and ECDSA (digital signature). This is the "capstone" page that ties all algorithms together in a realistic workflow. Split into Send and Receive tabs.

### 13.3 Data Sources

| Action | Endpoint | Request | Response |
|---|---|---|---|
| Send | `POST /api/v1/scenarios/secure_file_transfer/send` | `{ file_b64, receiver_rsa_public_key_id?, receiver_rsa_public_pem?, sender_ecdsa_private_key_id?, sender_ecdsa_private_hex?, sender_ecdsa_curve }` | `{ envelope: {...}, sender_summary: { encrypted_size, signature_ms, total_ms } }` |
| Receive | `POST /api/v1/scenarios/secure_file_transfer/receive` | `{ envelope, receiver_rsa_private_key_id?, receiver_rsa_private?, sender_ecdsa_public_key_id?, sender_ecdsa_public? }` | `{ plaintext_b64, verification: { signature_valid, tag_valid }, duration_ms }` |
| RSA keygen | `POST /api/v1/pubkey/rsa/keygen` | `{ bits: 1024 }` | `{ private_key_id, public_key_id }` |
| ECC keygen | `POST /api/v1/pubkey/ecc/keygen` | `{ curve: "secp160r1" }` | `{ private_key_id, public_key_id }` |
| Export pub | `GET /api/v1/keys/{key_id}/public` | — | `{ material }` |

### 13.4 Layout Structure

```
┌─────────────────────────────────────────────────────────┐
│ Page Title: "Secure File Transfer"                      │
│ Subtitle: "RSA + AES-GCM + SHA-256 + ECDSA combined"   │
├─────────────────────────────────────────────────────────┤
│ FlowDiagram (horizontal, 7 steps):                      │
│ [RSA PubKey] → [Gen AES Key] → [RSA Encrypt Key] →     │
│ [AES-GCM Encrypt] → [SHA-256 Hash] → [ECDSA Sign] →   │
│ [Send Envelope]                                         │
├─────────────────────────────────────────────────────────┤
│ el-tabs: [📤 Send] [📥 Receive]                        │
├─────────────────────────────────────────────────────────┤
│ === Send Tab ===                                        │
│ ┌────────────────────┬──────────────────────────────┐  │
│ │ Step 1: Keys       │ Envelope Output:             │  │
│ │                    │                              │  │
│ │ Receiver RSA pub:  │ [empty until sent]           │  │
│ │ [KeyIdPicker ▾]    │                              │  │
│ │ or [Generate RSA]  │ When sent:                   │  │
│ │                    │ ┌──────────────────────────┐ │  │
│ │ Sender ECDSA priv: │ │ {                        │ │  │
│ │ [KeyIdPicker ▾]    │ │   "encrypted_key": "..." │ │  │
│ │ or [Generate ECC]  │ │   "ciphertext_b64": "..."│ │  │
│ │                    │ │   "iv": "...",            │ │  │
│ │ Step 2: File       │ │   "tag": "...",           │ │  │
│ │ [📁 Upload file]  │ │   "signature": {...},     │ │  │
│ │ or paste Base64    │ │   "file_hash": "..."      │ │  │
│ │                    │ │ }                         │ │  │
│ │ [📤 Send Securely] │ └──────────────[Copy]──────┘ │  │
│ │                    │                              │  │
│ │                    │ Summary:                     │  │
│ │                    │ File size: 1.2 KB            │  │
│ │                    │ Encrypted size: 1.3 KB       │  │
│ │                    │ Signature time: 3.5ms        │  │
│ │                    │ Total time: 18.2ms           │  │
│ └────────────────────┴──────────────────────────────┘  │
├─────────────────────────────────────────────────────────┤
│ === Receive Tab ===                                     │
│ ┌────────────────────┬──────────────────────────────┐  │
│ │ Step 1: Keys       │ Decrypted Output:            │  │
│ │                    │                              │  │
│ │ Receiver RSA priv: │ [empty until received]       │  │
│ │ [KeyIdPicker ▾]    │                              │  │
│ │                    │ When received:               │  │
│ │ Sender ECDSA pub:  │ ┌──────────────────────────┐ │  │
│ │ [KeyIdPicker ▾]    │ │ Plaintext (decoded):     │ │  │
│ │                    │ │ "Hello, secure world!"   │ │  │
│ │ Step 2: Envelope   │ └──────────────────────────┘ │  │
│ │ [Paste envelope ▾] │                              │  │
│ │ (auto-fill from    │ Verification:                │  │
│ │  send tab)         │ ✅ GCM tag valid             │  │
│ │                    │ ✅ ECDSA signature valid     │  │
│ │ [📥 Receive & Verify]│ Total time: 15.8ms         │  │
│ └────────────────────┴──────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
```

### 13.5 Example Data

**Send request (key_id mode):**
```json
{
  "file_b64": "SGVsbG8sIHNlY3VyZSB3b3JsZCE=",
  "receiver_rsa_public_key_id": "c8f26274-5bfe-3caf-ad98-64e9b3087f2b",
  "sender_ecdsa_private_key_id": "d9a37385-6cfe-4dbf-be09-75fab4198e3c",
  "sender_ecdsa_curve": "secp160r1"
}
```

**Send response:**
```json
{
  "envelope": {
    "encrypted_session_key_hex": "4a3f8b2c1d5e6f7a...",
    "ciphertext_b64": "kL3RfXpXMJvG7Y6q...",
    "iv_hex": "000102030405060708090a0b",
    "tag_hex": "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6",
    "file_hash_hex": "2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824",
    "signature": {
      "r_hex": "0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b",
      "s_hex": "5e6f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f"
    },
    "sender_curve": "secp160r1"
  },
  "sender_summary": {
    "encrypted_size": 1312,
    "signature_ms": 3.5,
    "total_ms": 18.2
  }
}
```

**Receive response:**
```json
{
  "plaintext_b64": "SGVsbG8sIHNlY3VyZSB3b3JsZCE=",
  "verification": {
    "signature_valid": true,
    "tag_valid": true
  },
  "duration_ms": 15.8
}
```

### 13.6 State Specification

| State | Trigger | Visual |
|---|---|---|
| **Empty** | Page load | FlowDiagram shows all steps gray, "Start by selecting keys and uploading a file" |
| **Keys selected** | Both key pickers filled | Steps 1 in FlowDiagram turn blue |
| **File ready** | File uploaded or Base64 pasted | File info shown (name, size), step 2 turns blue |
| **Sending** | Submit send | FlowDiagram animates step by step: RSA → AES → SHA → ECDSA, each turns green on completion |
| **Send success** | Envelope received | Full envelope JSON in output, copy button, summary stats |
| **Receiving** | Submit receive | Reverse FlowDiagram animation |
| **Receive success (all valid)** | plaintext + both verifications pass | Green double-check marks, decoded plaintext shown |
| **Receive partial (sig invalid)** | signature_valid = false | Red X on ECDSA step, warning: "File may have been tampered with" |
| **Error (GCM fail)** | tag_valid = false | Red X on AES step: "Ciphertext integrity check failed" |

### 13.7 Wow Moment

**Animated protocol walkthrough**: The FlowDiagram at the top is not just a static diagram — during the send operation, each step lights up in sequence with a 200ms delay, showing an animated data packet traveling between steps. The packet icon changes shape at each step: plaintext → encrypted block → signed envelope. On receive, the animation plays in reverse. This makes the multi-algorithm protocol visually tangible and is the most impressive demo for the course presentation.
