# CryptoLab Figma Make Prompts

> 1 global design-system prompt + 12 per-page prompts.
> Each prompt is self-contained and can be pasted into Figma Make independently.

---

## Global Design System Prompt

```
Design a complete UI design system for "CryptoLab" — an academic cryptography
experiment platform built with Vue 3 and Element Plus. The application lets
university students interact with 15 hand-written cryptographic algorithms
through a clean, professional web interface.

BRAND IDENTITY:
- Name: CryptoLab (密码算法实验平台)
- Tone: Technical but approachable. Think "GitHub meets a university lab."
- Logo concept: A shield icon with a lock keyhole that subtly incorporates
  binary digits (0/1) in the shield pattern.

COLOR PALETTE:
- Primary: #409EFF (Element Plus blue) — buttons, active nav, links
- Primary Light: #ECF5FF — selected rows, active nav backgrounds
- Success: #67C23A — successful operations, valid signatures
- Warning: #E6A23C — demo banners, security warnings
- Danger: #F56C6C — errors, invalid signatures, failed decryption
- Info: #909399 — disabled states, placeholder text
- Page Background: #F5F7FA
- Card Background: #FFFFFF
- Code Background: #FAFAFA (for hex viewers and code blocks)
- Border: #DCDFE6
- Text Primary: #303133
- Text Regular: #606266
- Text Secondary: #909399
- Accent Purple: #9B59B6 — used for signature/signing flows

TYPOGRAPHY:
- Headings: Inter or system sans-serif, 24px/700 for page titles, 18px/600
  for section titles
- Body: 14px/400
- Code/Hex data: JetBrains Mono or Consolas, 13px/400, displayed on #FAFAFA
  background with 1px #DCDFE6 border
- Chinese text: Microsoft YaHei as fallback

SPACING: 8px grid. Card padding: 16px. Section gap: 24px. Page margin: 32px.

BORDER RADIUS: 4px for inputs/buttons, 8px for cards, 12px for feature cards,
20px for tags/badges.

SHADOWS:
- Cards at rest: 0 1px 4px rgba(0,0,0,0.08)
- Card hover: 0 4px 12px rgba(0,0,0,0.10)
- Modals: 0 8px 24px rgba(0,0,0,0.12)

LAYOUT:
- Authenticated shell: 64px fixed header bar + 220px collapsible sidebar +
  scrollable main content (max 1200px centered).
- Sidebar groups: "Algorithms" (Symmetric, Hash, HMAC & PBKDF2, Encoding),
  "Public Key" (RSA, ECC & ECDSA), "Management" (Key Store, Audit Logs,
  Benchmark), "Labs" (Security Demos, Secure File Transfer).
- Sidebar collapses to 64px icon-only at viewport < 1200px.

SHARED COMPONENTS TO DESIGN:
1. CryptoCard — bordered card with title, subtitle, icon, optional collapse
2. HexViewer — monospace hex display with copy button, line numbers, optional
   diff coloring (green = match, red = changed)
3. Base64Viewer — similar to HexViewer but for Base64 data
4. AlgorithmSelector — segmented control or dropdown for algo + mode + padding
5. KeyIdPicker — dropdown listing user's keys (UUID, algorithm, label, date)
6. OperationTimer — circular badge showing operation duration in milliseconds
   (green < 100ms, yellow < 1000ms, red > 1000ms)
7. StatusBanner — full-width warning banner for demo pages
8. FlowDiagram — connected node diagram showing protocol steps with progress
9. InputPanel — left-side form area with submit button
10. OutputPanel — right-side result area with 4 states: empty (ghost
    illustration), loading (skeleton), success (animated reveal), error (red
    border + code badge)
11. CopyButton — small icon button, flashes green checkmark after copy
12. AuditTable — paginated table for operation logs with filter controls
13. KeygenButton — button that opens a dialog, calls keygen, returns key_id
14. ComparisonToggle — animated toggle between Encrypt/Decrypt or Sign/Verify

Produce: a Figma component library with all 14 components in their various
states, plus the authenticated shell layout (sidebar + header + content area),
plus the login page layout. Use Element Plus styling as the base but add the
CryptoLab brand colors and typography. All components should have light mode
only (no dark mode).
```

---

## Page 1: Login & Register

```
Design the Login & Register page for CryptoLab.

LAYOUT: Full viewport, centered authentication card on a dark gradient
background (#1a1a2e → #16213e). Floating cryptographic symbol particles
(lock, key, shield icons) drift slowly in the background.

CENTER CARD (400px wide, white, 8px border radius, heavy shadow):
- Top: Shield Lock icon (48px), "CryptoLab" in 24px bold white on dark, with
  Chinese subtitle "密码算法实验平台" in 14px below.
- Tab bar with two tabs: "Login" and "Register" (Element Plus el-tabs style).
- Login tab:
  - Username input with User icon prefix (el-input, size large)
  - Password input with Lock icon prefix (el-input type=password, size large)
  - Full-width primary blue "Login" button (el-button type=primary size=large)
- Register tab:
  - Same fields plus a helper text: "Password must be at least 8 characters"
  - Full-width "Register" button

STATES TO SHOW:
1. Default (empty form, Login tab active)
2. Validation error (red border on password field, "Password must be at least
   8 characters" in red below)
3. Loading (button shows spinner, inputs disabled/grayed)
4. Login error (red toast at top: "Invalid credentials")
5. Success (green flash border on card, brief)
6. Rate limited (button disabled with countdown: "Try again in 45s")

FOOTER: "Powered by Rust + Python | BUPT 2026" in 12px light gray at page
bottom.

WOW DETAIL: Each password character briefly flashes as a hex code (e.g., "a"
→ "0x61") before masking to a bullet dot. Show this as a frame sequence.

Use the CryptoLab design system colors and typography.
```

---

## Page 2: Dashboard

```
Design the Dashboard page for CryptoLab, visible after login.

HEADER: "Welcome back, alice" with user role badge and "Last login: 2h ago"
in secondary text.

STATS ROW (4 equal-width metric cards):
- "15 Algorithms Available" with Lock icon
- "24 Keys Stored" with Key icon
- "156 Operations Today" with Document icon
- "0.8ms Avg Latency" with Timer icon
Each card: white, 12px radius, subtle shadow, icon in primary blue circle,
large number (32px bold), label below (14px regular).

ALGORITHM CATALOG (3-column grid of feature cards, 6 total):
Row 1:
- "Symmetric Encryption" — AES · SM4 · RC6, "ECB/CBC/CTR/GCM modes", Lock
  icon, blue accent bar top → links to /symmetric
- "Hash Functions" — SHA-1/256/3 · RIPEMD-160, "8 algorithms", Hash icon,
  green accent → /hash
- "Encoding" — Base64 · UTF-8, "Encode/Decode", Code icon, teal accent →
  /encoding
Row 2:
- "RSA Cryptography" — 1024-bit, "Encrypt/Sign", Key icon, purple accent →
  /rsa
- "ECC & ECDSA" — secp160r1, "Sign/Verify", Curve icon, purple accent → /ecc
- "Key Store" — "Manage keys", "KEK-wrapped storage", Setting icon, gray
  accent → /keys
Row 3 (optional, if space):
- "Security Demos" — 4 attack simulations, Warning icon, orange accent →
  /demos
- "Secure Transfer" — RSA + AES + ECDSA, Package icon, blue accent →
  /scenarios
- "Benchmark" — Throughput per algorithm, Chart icon, green accent →
  /benchmark

Each feature card: white, 12px radius, colored 4px top border, icon, title
(16px bold), description lines (13px regular), "Open →" link in card footer.
Hover: lift shadow + slight scale.

RECENT ACTIVITY (bottom section):
- Mini table: Time | Operation | Algorithm | Duration
- 5 rows of sample data (shown in PAGES.md)
- "View all audit logs →" link at bottom right

Show the dashboard inside the authenticated shell (sidebar + header).
```

---

## Page 3: Symmetric Encryption

```
Design the Symmetric Encryption workbench page for CryptoLab.

PAGE HEADER: "Symmetric Encryption" title, "AES / SM4 / RC6 — Block cipher
workbench" subtitle.

TOOLBAR ROW:
- AlgorithmSelector: three-part control — Algorithm dropdown (AES/SM4/RC6),
  Mode dropdown (ECB/CBC/CTR/GCM), Padding dropdown (PKCS7/Zero/X923/None).
  Use Element Plus el-select components in a horizontal row.
- ComparisonToggle: "Encrypt" / "Decrypt" toggle, pill-shaped, active side
  filled with primary blue.

MAIN AREA (two-column split, 45% / 55%):
Left — InputPanel:
- "Key" label + KeyIdPicker dropdown showing key UUID, algorithm, and label.
  A small "Generate Key" button (el-button size=small type=primary plain)
  next to the picker.
- "IV (hex)" input with a "Random" button that fills 24/32 hex chars.
  Show only when mode is CBC/CTR/GCM.
- "AAD (Base64)" input — show only when mode is GCM.
- "Plaintext" textarea (el-input type=textarea, 6 rows). In decrypt mode,
  this changes to "Ciphertext (Base64)" input.
- "Encrypt" button (primary, large) or "Decrypt" button (success, large).

Right — OutputPanel:
- Empty state: ghost lock illustration + "Run an operation to see results"
  in secondary text.
- Success state: Base64Viewer showing ciphertext, HexViewer showing hex
  representation below it, OperationTimer badge, algorithm+mode label.
- Error state: red border, error code badge (e.g., "3002"), error message.

STATES TO SHOW (as separate frames):
1. Empty (no key selected, output empty)
2. Key generated (KeyIdPicker shows new key, green check)
3. GCM mode selected (IV and AAD fields visible)
4. Encrypt result (ciphertext in both Base64 and hex views)
5. Decrypt result (plaintext in green-bordered text area)
6. Error: "GCM authentication tag mismatch" (code 3002)

WOW DETAIL: A "Compare Modes" collapsible section below the output shows 4
mini hex viewers side by side (ECB/CBC/CTR/GCM output of same plaintext+key).
ECB output has repeating blocks highlighted in red.

Show inside the authenticated shell layout.
```

---

## Page 4: Hash Functions

```
Design the Hash Functions page for CryptoLab.

PAGE HEADER: "Hash Functions" title, "One-way cryptographic digests" subtitle.

INPUT SECTION:
- Large textarea (el-input type=textarea, 4 rows) with placeholder "Enter
  text to hash..." and character count in bottom-right corner.
- Algorithm checkbox grid (2 rows x 4 columns):
  Row 1: SHA-1, SHA-224, SHA-256, SHA-384
  Row 2: SHA-512, SHA3-256, SHA3-512, RIPEMD-160
  Use Element Plus el-checkbox-group. Pre-check SHA-1, SHA-256, SHA3-256.
- "Compute Hashes" button (primary).

RESULTS SECTION:
- One CryptoCard per selected algorithm, stacked vertically.
- Each card contains: algorithm name as title, HexViewer with the full digest
  hex, "Digest length: N bits" in secondary text, CopyButton.
- If 2+ algorithms selected, show a "Comparison" summary below:
  "SHA-256 vs SHA3-256: 0/64 bytes match (0% — completely independent
  algorithms)"

AVALANCHE VISUALIZATION (key feature):
- When the user edits the input text, show the previous hash above the new
  hash in each card. Previous hash is 50% opacity.
- New hash has byte-level diff coloring: red for changed bytes, green for
  unchanged. A badge shows "52% changed" for each algorithm.

STATES:
1. Empty (no input, no results)
2. Input entered, algorithms checked, button ready
3. Loading (skeleton in each result card)
4. Results shown (3 algorithm cards)
5. Avalanche comparison (previous + new hashes with diff)

Show inside the authenticated shell.
```

---

## Page 5: HMAC & PBKDF2

```
Design the HMAC & PBKDF2 page for CryptoLab.

PAGE HEADER: "HMAC & Key Derivation" title, "Message authentication and
PBKDF2" subtitle.

TAB BAR: Two tabs — "HMAC" and "PBKDF2" (el-tabs).

HMAC TAB (two-column, 45/55):
Left — InputPanel:
- "Key" text input (el-input)
- "Message" textarea (3 rows)
- Algorithm radio group: SHA-1, SHA-256 (el-radio-group)
- "Compute HMAC" button (primary)
Right — OutputPanel:
- HexViewer showing mac_hex
- "Algorithm: HMAC-SHA256" label
- OperationTimer badge

PBKDF2 TAB (two-column, 45/55):
Left — InputPanel:
- "Password" text input
- "Salt" text input
- "Iterations" number input with an el-slider below (logarithmic scale:
  1,000 → 1,000,000, marks at 1K, 10K, 100K, 1M)
- "Key Length (bytes)" number input (1-64, default 32)
- "Derive Key" button (primary)
Right — OutputPanel:
- HexViewer showing derived_key_hex
- "Iterations: 100,000" and "Key length: 32 bytes" labels
- If iterations < 100,000: yellow warning banner from StatusBanner component
  with text from API warning field
- OperationTimer badge

STATES:
1. HMAC empty
2. HMAC result
3. PBKDF2 empty
4. PBKDF2 result (no warning)
5. PBKDF2 result with low-iteration warning (yellow banner)

WOW DETAIL: The PBKDF2 iterations slider shows a real-time timing estimate
label that updates as the user drags: "~0.5ms" at 1K, "~5ms" at 10K, "~45ms"
at 100K, "~450ms" at 1M. After computation, the actual time appears next to
the estimate.

Show inside the authenticated shell.
```

---

## Page 6: Encoding

```
Design the Encoding page for CryptoLab.

PAGE HEADER: "Encoding" title, "Base64 & UTF-8 data encoding" subtitle.

MAIN SECTION — Mirror layout:
Two equal-width textareas side by side (el-input type=textarea, 8 rows each):
- Left: "Plain Text" label, placeholder "Enter text..."
- Right: "Base64" label, placeholder "Enter Base64..."
- Between them: a circular swap button (⇄ icon) that swaps content.
- Below left: "Encode →" button (primary, arrow right icon)
- Below right: "← Decode" button (success, arrow left icon)
- Character counts below each textarea.

SIZE COMPARISON BAR:
- Below the buttons: "Original: 13 bytes → Encoded: 20 bytes (1.54x overhead)"
  with a simple bar chart showing the ratio visually.

BYTE VISUALIZATION (below textareas):
- Left side: ASCII byte grid showing each character's hex code (e.g., "H" =
  48, "e" = 65). One small colored box per byte.
- Right side: Base64 6-bit grouping visualization — color bands showing how
  3 input bytes map to 4 Base64 characters. Hover interaction: hovering a
  Base64 char highlights its source bytes.

UTF-8 SECTION (below, dimmed):
- Grayed-out card with "UTF-8 Encode/Decode" title and a "Coming Soon"
  el-tag (type=info). Disabled inputs inside at 50% opacity.

STATES:
1. Empty (both textareas blank)
2. Text entered on left, ready to encode
3. Encoded result on right
4. Base64 entered on right, ready to decode
5. Invalid Base64 error (right textarea red border, error text)
6. UTF-8 section always disabled

Show inside the authenticated shell.
```

---

## Page 7: RSA Cryptography

```
Design the RSA Cryptography page for CryptoLab.

PAGE HEADER: "RSA Cryptography" title, "1024-bit key generation, encryption
& signing" subtitle.

KEY GENERATION BAR (full-width CryptoCard):
- "Generate RSA-1024 Key Pair" button (primary) + optional "Label" input.
- After generation: show private_key_id and public_key_id as UUID badges.
- Expandable section: "View Public Key Material" — shows n_hex (128 hex chars,
  wrapped in HexViewer) and e_hex ("010001") with CopyButtons.

TAB BAR: "Encrypt / Decrypt" | "Sign / Verify" (el-tabs).

ENCRYPT/DECRYPT TAB (two-column):
Left — InputPanel:
- Mode radio: Encrypt / Decrypt
- KeyIdPicker for key (filters to rsa_public for encrypt, rsa_private for
  decrypt)
- "Plaintext" input (for encrypt) or "Ciphertext (hex)" input (for decrypt)
- Execute button
Right — OutputPanel:
- For encrypt: HexViewer showing ciphertext_hex (256 hex chars for 1024-bit)
- For decrypt: text display of recovered plaintext
- OperationTimer

SIGN/VERIFY TAB (two-column):
Left — InputPanel:
- Mode radio: Sign / Verify
- KeyIdPicker (rsa_private for sign, rsa_public for verify)
- "Message" textarea
- For verify mode: additional "Signature (hex)" input
- Execute button
Right — OutputPanel:
- For sign: HexViewer showing signature_hex
- For verify: large animated checkmark (green, valid) or X (red, invalid)
  with "Signature is VALID" / "Signature is INVALID" text

STATES:
1. No keys yet — prominent keygen card with explanation
2. Keygen in progress — progress bar: "Generating 1024-bit primes..."
3. Keygen success — key IDs shown with brief particle animation
4. Encrypt result — hex ciphertext
5. Decrypt result — plaintext text
6. Sign result — hex signature
7. Verify valid — large green checkmark
8. Verify invalid — large red X with shake animation
9. Key type mismatch error (code 4203)

WOW DETAIL: During RSA keygen, an animated visualization shows candidate
numbers being tested for primality — each candidate appears, gets crossed out
(composite) or confirmed (prime). When both primes are found, they visually
multiply into the modulus n.

Show inside the authenticated shell.
```

---

## Page 8: ECC & ECDSA

```
Design the ECC & ECDSA page for CryptoLab.

PAGE HEADER: "Elliptic Curve Cryptography" title, "ECDSA signatures on
secp160r1" subtitle.

CURVE INFO BANNER (full-width, info-type):
"Curve: secp160r1 | Field: 160-bit | Deterministic k (RFC 6979)"

KEY PAIR SECTION (CryptoCard):
- "Generate ECC Key Pair" button (primary) + "Label" input
- After generation: private_key_id and public_key_id UUID badges
- Public point display: Qx and Qy as HexViewers (40 hex chars each)
- VISUALIZATION: An ECharts scatter plot (300px tall) showing a simplified
  elliptic curve (y² = x³ + ax + b) with the public key point Q marked as a
  pulsing blue dot on the curve.

SIGN/VERIFY SECTION (two-column):
Left — InputPanel:
- Mode radio: Sign / Verify
- KeyIdPicker (ecc_private for sign, ecc_public for verify)
- "Message" textarea
- For verify: r_hex and s_hex inputs (40 hex chars each)
- Execute button
Right — OutputPanel:
- For sign: two HexViewers — r (40 hex) and s (40 hex), with "Copy r+s"
  combined copy button
- For verify: green checkmark or red X (same as RSA page style)
- "Curve: secp160r1" label
- OperationTimer

STATES:
1. No keys — keygen card
2. Key generated — public point shown, curve plot rendered
3. Sign result — r and s displayed
4. Verify valid — green checkmark
5. Verify invalid — red X
6. Wrong key type error

WOW DETAIL: On the elliptic curve plot, when signing, an animated dot traces
from the generator point G along the curve to the ephemeral point kG,
illustrating scalar multiplication visually.

Show inside the authenticated shell.
```

---

## Page 9: Key Store

```
Design the Key Store management page for CryptoLab.

PAGE HEADER: "Key Store" title, "Manage your cryptographic keys" subtitle.

TOOLBAR ROW:
- Filter dropdowns: "All Types" (symmetric/rsa_public/rsa_private/ecc_public/
  ecc_private), "All Algorithms" (AES/SM4/RC6/RSA/ECC)
- Search input (filters by label or key ID)
- Key count badge: "24 keys"

KEY RELATIONSHIP GRAPH (above table, 200px tall):
- ECharts force-directed graph visualization
- Symmetric keys = single circle nodes (blue)
- RSA key pairs = two connected nodes (public = green, private = red)
- ECC key pairs = same but with different shape (diamond)
- Hover a node → highlight its pair, show tooltip with key details

KEY TABLE (el-table, full width):
Columns: Key ID (truncated UUID + copy icon), Type (colored tag: symmetric=
blue, rsa_public=green, rsa_private=red, ecc_public=teal, ecc_private=
purple), Algorithm, Label, Paired Key ID, Created At.
Row click opens detail panel. Alternating row colors.
Pagination: 10 per page.

DETAIL PANEL (right-side slide-in, 400px wide):
- Full Key ID with copy
- Type, Algorithm, Label
- "Paired with: [key_id]" (clickable, scrolls to that row)
- Created / Expires dates
- For public keys: "Public Material" section with HexViewers for n_hex/e_hex
  (RSA) or qx_hex/qy_hex (ECC)
- "Revoke Key" button (danger, requires el-popconfirm)

STATES:
1. Loading (5 skeleton table rows)
2. Empty (vault illustration + "No keys yet — generate one from any
   algorithm page")
3. Loaded (table with data)
4. Detail panel open (right slide-in)
5. Revoke confirmation dialog
6. Revoke success (row fades out with strikethrough)
7. Export public material loading

Show inside the authenticated shell.
```

---

## Page 10: Audit Logs

```
Design the Audit Logs page for CryptoLab.

PAGE HEADER: "Audit Logs" title, "Cryptographic operation history" subtitle.

TIMELINE HEATMAP (above filters, 120px tall):
- ECharts heatmap showing operation density by hour for the past 7 days.
  X-axis: days, Y-axis: hours (0-23). Color intensity = operation count.
  Clicking a cell filters the table below to that time range.

FILTER BAR:
- Algorithm dropdown (All / AES / SM4 / SHA-256 / RSA / ECC / etc.)
- Since date picker (el-date-picker)
- Until date picker
- Status dropdown (All / Success / Client Error / Crypto Error / Server Error)
- "Search" button + "Reset" text link

LOG TABLE (el-table, full width, sortable columns):
Columns:
- Trace ID (truncated UUID, monospace, copyable)
- Operation (e.g., "aes_encrypt", "rsa_keygen")
- Algorithm (e.g., "AES-GCM", "RSA-1024")
- Key ID (truncated UUID or "—")
- Status (colored el-tag: 1000=green "OK", 2xxx=yellow "Param Error",
  3xxx=orange "Crypto Error", 4xxx=red "Auth Error", 5xxx=dark-red
  "Server Error")
- Duration (formatted: "0.42ms" or "234ms")
- Timestamp (relative: "2 min ago", absolute on hover)
Pagination: 20 per page, showing "1-20 of 156".

DETAIL DRAWER (right slide, 450px):
When a row is clicked, el-drawer slides in showing all fields:
- Trace ID (full, copyable)
- User ID
- Operation
- Algorithm
- Key ID (full UUID)
- Input Hash (SHA-256, 64 hex chars in HexViewer)
- Output Hash (SHA-256, 64 hex chars in HexViewer)
- Status Code with meaning
- Duration
- Client IP
- Created At (full ISO timestamp)

STATES:
1. Loading (skeleton rows + heatmap loading)
2. Loaded (heatmap + table with data)
3. Empty (no logs) — "No operations recorded yet"
4. Filtered empty — "No results for these filters"
5. Detail drawer open
6. Status color coding on tags

Show inside the authenticated shell.
```

---

## Page 11: Benchmark

```
Design the Benchmark page for CryptoLab.

PAGE HEADER: "Performance Benchmark" title, "Throughput and latency of
hand-written algorithms" subtitle.

ALGORITHM SELECTOR:
- Category filter buttons: [All] [Symmetric] [Hash] [Public Key]
  (el-radio-group, button style)
- Checkbox grid (3 columns) listing algorithms:
  Symmetric: AES-ECB, AES-GCM, SM4-ECB, RC6-ECB
  Hash: SHA-1, SHA-256, SHA-512, SHA3-256, SHA3-512, RIPEMD-160
  Public Key: RSA-Encrypt, ECDSA-Sign
- "Run Selected Benchmarks" button (primary, large)

RESULTS CHART (ECharts horizontal bar, 400px tall):
- Y-axis: algorithm names
- X-axis: throughput in MB/s
- Bars colored by category (blue=symmetric, green=hash, purple=pubkey)
- Value labels on bar ends: "820 MB/s"
- Sorted by throughput descending

RESULTS TABLE (el-table, below chart):
Columns: Algorithm, Data Size, Iterations, Total Time (ms), Throughput
(MB/s), Latency (ns/op)
Sample data:
| AES-ECB   | 1.00 MB | 100 | 121.5 | 823 MB/s  | 1.22 ms |
| AES-GCM   | 1.00 MB | 100 | 128.2 | 780 MB/s  | 1.28 ms |
| SHA-256   | 1.00 MB | 100 | 111.1 | 900 MB/s  | 1.11 ms |
| SM4-ECB   | 1.00 MB | 100 | 263.2 | 380 MB/s  | 2.63 ms |

STATES:
1. Empty — algorithm selector shown, no chart
2. Running — progress text: "Running benchmark 3/6: SM4-ECB...", each
   completed algo's bar appears and grows
3. Complete — full chart + table
4. Partial failure — completed algos show, failed show gray bar + error
   tooltip

WOW DETAIL: "Racing bars" animation — when all benchmarks complete, bars
briefly animate from 0 to their values simultaneously, creating a race
effect. Chart auto-sorts by throughput with smooth reorder transition.

Show inside the authenticated shell.
```

---

## Page 12: Security Demos

```
Design the Security Demos page for CryptoLab.

PAGE HEADER: "Security Demos" title, "Interactive vulnerability
demonstrations" subtitle.

GLOBAL WARNING BANNER (StatusBanner, type=warning):
"These demos intentionally use WEAK parameters to demonstrate attacks. NEVER
use these settings in production."

TAB BAR: 4 tabs with icons:
- "ECB Image Leak" (Image icon)
- "ECDSA k-Reuse" (Warning icon)
- "RSA e=3 Attack" (Unlock icon)
- "PBKDF2 Iterations" (Timer icon)

=== ECB IMAGE LEAK TAB ===
Left — InputPanel:
- "Upload Image" — el-upload component with drag-and-drop area, file preview
- "AES-128 Key (hex)" input with "Random Key" button
- "Run Demo" button (warning color)
Right — OutputPanel:
- Three images in a row: "Original" | "ECB Encrypted" | "CBC Encrypted"
  Each in a bordered frame with label above.
- Below images: "Block count: 1024" and "Duplicate block ratio: 47.3%"
  with a progress bar visualization.
- StatusBanner with the API banner text.

=== ECDSA k-REUSE TAB ===
Left — InputPanel:
- "Message 1" input (pre-filled: "Transfer $100")
- "Message 2" input (pre-filled: "Transfer $999")
- "Run Attack Demo" button (danger color)
Right — OutputPanel:
- "Private key (generated)" — hex, initially hidden behind a "Reveal" button
- "Signature 1" — r_hex and s_hex
- "Signature 2" — r_hex and s_hex (same r value highlighted in red)
- "r values equal? YES" with red warning badge
- "Recovered private key" — hex in red-bordered HexViewer
- "Matches original? YES" — red "ATTACK SUCCESSFUL" badge

=== RSA LOW EXPONENT TAB ===
Left — InputPanel:
- "Message" input (default: "BUPT2026")
- "Run Attack Demo" button (danger color)
Right — OutputPanel:
- n_hex in HexViewer
- "e = 3" with danger tag
- "Ciphertext = m³ mod n" formula display
- "∛c = recovered message" formula
- "Recovered: BUPT2026" in red-bordered box
- "Matches original? YES" — red "ATTACK SUCCESSFUL" badge

=== PBKDF2 ITERATIONS TAB ===
Left — InputPanel:
- "Password" input (default: "password")
- "Salt (hex)" input (default: "73616c747361")
- Iteration checkboxes: [✓]1K [✓]10K [✓]100K [✓]1M
- "Run Comparison" button (primary)
Right — OutputPanel:
- ECharts horizontal bar chart showing duration per iteration count.
  Bars color-graded: green (1K, fast) → yellow (100K) → red (1M, slow).
- "1M / 100K ratio: 10.0x" statistic.
- Verdict text: "Use at least 100,000 iterations for password hashing."

STATES:
1. Tab selected, empty (brief vulnerability explanation + illustration)
2. Loading (appropriate message per demo)
3. Result shown
4. ECB: three images with curtain reveal animation
5. Attack successful (red badges, highlighted recovered data)

WOW DETAIL: ECB Image Leak — the three images are revealed with a left-to-
right curtain animation. The ECB-encrypted image clearly shows the original
pattern, creating a dramatic visual contrast with the CBC noise. The
duplicate block ratio bar fills with red.

Show inside the authenticated shell.
```

---

## Page 13: Secure File Transfer

```
Design the Secure File Transfer page for CryptoLab.

PAGE HEADER: "Secure File Transfer" title, "RSA + AES-GCM + SHA-256 + ECDSA
combined" subtitle.

FLOW DIAGRAM (FlowDiagram component, full width, 100px tall):
7 connected nodes in a horizontal chain:
1. "Get RSA Public Key" (Key icon)
2. "Generate AES Session Key" (Lock icon)
3. "RSA Encrypt Key" (Shield icon)
4. "AES-GCM Encrypt File" (Lock icon)
5. "SHA-256 File Hash" (Hash icon)
6. "ECDSA Sign Hash" (Pen icon)
7. "Send Envelope" (Send icon)
Nodes are circles connected by arrows. Default: all gray. During send: each
step lights up blue → green sequentially with an animated "data packet" icon
traveling along the arrows.

TAB BAR: "Send" (Upload icon) | "Receive" (Download icon)

=== SEND TAB === (two-column)
Left — InputPanel:
- "Receiver's RSA Public Key" — KeyIdPicker (filter: rsa_public) + "Generate
  RSA Pair" small button
- "Your ECDSA Private Key" — KeyIdPicker (filter: ecc_private) + "Generate
  ECC Pair" small button
- "File" — el-upload drag-and-drop area OR "Paste Base64" textarea toggle
- "Send Securely" button (primary, large, with Send icon)
Right — OutputPanel:
- Empty: ghost illustration + "Select keys and upload a file"
- Success: JSON envelope in a code viewer (syntax-highlighted, scrollable,
  max 300px), CopyButton, summary stats below:
  - File size: 1.2 KB
  - Encrypted size: 1.3 KB
  - Signature time: 3.5ms
  - Total time: 18.2ms

=== RECEIVE TAB === (two-column)
Left — InputPanel:
- "Your RSA Private Key" — KeyIdPicker (filter: rsa_private)
- "Sender's ECDSA Public Key" — KeyIdPicker (filter: ecc_public)
- "Envelope" — large textarea (auto-filled if switching from Send tab)
- "Receive & Verify" button (success, large, with Download icon)
Right — OutputPanel:
- "Decrypted Content" — text/file display
- Verification badges:
  - "GCM Tag: VALID" (green check) or "INVALID" (red X)
  - "ECDSA Signature: VALID" (green check) or "INVALID" (red X)
- Duration badge

STATES:
1. Empty (flow diagram all gray)
2. Keys selected (first nodes in flow turn blue)
3. File uploaded (file info shown, more nodes turn blue)
4. Sending (flow diagram animates step by step, 200ms per step)
5. Send success (envelope JSON shown, all flow nodes green)
6. Receiving (reverse flow animation)
7. Receive success, all valid (both check marks green, plaintext shown)
8. Receive: signature invalid (red X on ECDSA node, warning message)
9. Receive: GCM tag invalid (red X on AES node, error message)

WOW DETAIL: The flow diagram is not static — during the send operation, a
small data-packet icon animates along the arrows between nodes. The packet
icon morphs at each step: plaintext document → encrypted block → signed
envelope. The receiving animation plays in reverse: envelope → block →
document. This creates a cinematic protocol visualization.

Show inside the authenticated shell.
```

---

## Usage Notes

1. **Each prompt is self-contained**: paste any single prompt into Figma Make without needing the others.
2. **Global prompt first**: generate the component library and layout shell first, then generate individual pages referencing those components.
3. **States are explicit**: each prompt lists the distinct UI states to generate as separate frames/variants.
4. **Example data is concrete**: all hex values, UUIDs, and response structures match the actual backend API contracts.
5. **Wow moments**: each page has a specific interactive/animated detail described for the designer to include as a special frame or annotation.
