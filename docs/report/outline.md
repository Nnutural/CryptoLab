# CryptoLab 最终技术报告详细大纲

题目：CryptoLab：基于 Rust × Python 异构架构的密码算法工程实现与安全分析  
阶段：阶段 1 规划稿，等待用户确认后再进入正文写作  
当前 `HEAD`：`0861103477a7126599bde0fafafb1a3ed602a9d3`  
正文目标体量：约 31,000-34,500 字，不含参考文献和附录。  

## 1. 写作总约束

正文采用客观第三人称叙述，不使用“我”“我们”。每个一级、二级章节开头设置 1-2 段总览性文字，结尾设置 1 段小结并过渡至下章。段落长度控制在 200-450 字，段内使用显式连接词，例如“首先、其次、进而、然而、与此相对、由此可见、具体而言、值得注意的是、在此基础上”。列表和表格用于结构化信息，不替代论述。

技术事实优先级为：`docs/report_assets/STATS.md`、`docs/PROGRESS.md`、`docs/PROGRESS_DELTA.md`、CSV 数据、源码扫描、日志证据、截图索引、旧设计方案。遇到冲突时，旧设计方案只作为背景，不作为最终事实。正文不得把 RC6 写成全模式完成，不得把 Docker build 写成成功，不得把 AES verbose 前端截图写成已采集，不得把裸 pytest 写成通过。

## 2. 引用编号预案

本预案为正文阶段统一引用编号。阶段 2-5 写作时，所有条目至少在正文出现一次，最终第 7 章按 IEEE 数字编号制展开完整条目。

### 2.1 国际标准与 RFC

| 编号 | 文献 |
|---|---|
| [1] | NIST, FIPS 197, Advanced Encryption Standard (AES), updated 2023. |
| [2] | NIST, FIPS 180-4, Secure Hash Standard (SHS), 2015. |
| [3] | NIST, FIPS 202, SHA-3 Standard: Permutation-Based Hash and Extendable-Output Functions, 2015. |
| [4] | NIST, FIPS 186-5, Digital Signature Standard (DSS), 2023. |
| [5] | NIST SP 800-38A, Recommendation for Block Cipher Modes of Operation, 2001. |
| [6] | NIST SP 800-38D, Recommendation for Galois/Counter Mode (GCM) and GMAC, 2007. |
| [7] | NIST SP 800-132, Recommendation for Password-Based Key Derivation, 2010. |
| [8] | IETF RFC 8017, PKCS #1: RSA Cryptography Specifications Version 2.2, 2016. |
| [9] | IETF RFC 2104, HMAC: Keyed-Hashing for Message Authentication, 1997. |
| [10] | IETF RFC 4231, Identifiers and Test Vectors for HMAC-SHA-224/256/384/512, 2005. |
| [11] | IETF RFC 8018, PKCS #5: Password-Based Cryptography Specification Version 2.1, 2017. |
| [12] | IETF RFC 4648, The Base16, Base32, and Base64 Data Encodings, 2006. |
| [13] | IETF RFC 3629, UTF-8, a transformation format of ISO 10646, 2003. |
| [14] | IETF RFC 6979, Deterministic Usage of DSA and ECDSA, 2013. |
| [15] | Certicom Research, SEC 2: Recommended Elliptic Curve Domain Parameters, Version 2.0, 2010. |
| [16] | GB/T 32907-2016, 信息安全技术 SM4 分组密码算法, 2016. |

### 2.2 学术经典、安全事件、教材与工程实践

| 编号 | 文献 |
|---|---|
| [17] | R. L. Rivest, A. Shamir, and L. Adleman, A Method for Obtaining Digital Signatures and Public-Key Cryptosystems, Communications of the ACM, 1978. |
| [18] | W. Diffie and M. Hellman, New Directions in Cryptography, IEEE Transactions on Information Theory, 1976. |
| [19] | N. Koblitz, Elliptic Curve Cryptosystems, Mathematics of Computation, 1987. |
| [20] | V. S. Miller, Use of Elliptic Curves in Cryptography, CRYPTO 1985. |
| [21] | D. Johnson, A. Menezes, and S. Vanstone, The Elliptic Curve Digital Signature Algorithm (ECDSA), International Journal of Information Security, 2001. |
| [22] | M. Bellare, R. Canetti, and H. Krawczyk, Keying Hash Functions for Message Authentication, CRYPTO 1996. |
| [23] | J. Daemen and V. Rijmen, The Design of Rijndael, Springer, 2002. |
| [24] | G. Bertoni, J. Daemen, M. Peeters, and G. Van Assche, The Keccak Reference / Sponge Function Family, 2011. |
| [25] | X. Wang, Y. L. Yin, and H. Yu, Finding Collisions in the Full SHA-1, CRYPTO 2005. |
| [26] | M. Stevens et al., The first collision for full SHA-1, CRYPTO 2017. |
| [27] | A. K. Lenstra et al., Ron was wrong, Whit is right, IACR ePrint, 2012. |
| [28] | CVE-2014-0160, OpenSSL Heartbleed vulnerability, 2014. |
| [29] | Cloudflare, Cloudbleed incident analysis, 2017. |
| [30] | M. Nemec et al., The Return of Coppersmith's Attack: Practical Factorization of Widely Used RSA Moduli, ACM CCS 2017. |
| [31] | fail0verflow, Console Hacking 2010 / PS3 ECDSA nonce reuse discussion, 27C3, 2010. |
| [32] | D. Brumley and D. Boneh, Remote Timing Attacks are Practical, USENIX Security, 2003. |
| [33] | B. Schneier, Applied Cryptography, 2nd ed., Wiley, 1996. |
| [34] | A. Menezes, P. van Oorschot, and S. Vanstone, Handbook of Applied Cryptography, CRC Press, 1996. |
| [35] | J. Katz and Y. Lindell, Introduction to Modern Cryptography, 3rd ed., CRC Press, 2020. |
| [36] | N. Ferguson, B. Schneier, and T. Kohno, Cryptography Engineering, Wiley, 2010. |
| [37] | W. Stallings, Cryptography and Network Security, Pearson, latest available edition. |
| [38] | OpenSSL Project Documentation. |
| [39] | BoringSSL Project Documentation. |
| [40] | RustCrypto Project Documentation and repositories. |
| [41] | PyO3 User Guide. |
| [42] | FastAPI Documentation. |
| [43] | SQLAlchemy Documentation. |
| [44] | React Documentation. |
| [45] | Vite Documentation. |
| [46] | Docker Compose Documentation. |
| [47] | OWASP API Security Top 10, 2023. |
| [48] | B. Beyer et al., Site Reliability Engineering, O'Reilly / Google, 2016. |
| [49] | AWS Well-Architected Framework. |
| [50] | Cloudflare, Why we built BoringTun in Rust, engineering blog, 2019. |

## 3. 公式、伪码与代码节选总计划

| 类型 | 编号或数量 | 安排 |
|---|---|---|
| 编号公式 | 至少 15 条 | 主体集中于第 3 章，性能公式放第 4 章 |
| 算法伪码 | 至少 9 段 | Base64、SHA-256、HMAC、PBKDF2、AES、SM4、RSA、ECDSA、交叉验证 |
| Rust 源码节选 | 至少 6 段 | 优先选 `ffi.rs`、`hmac.rs`、`pbkdf2.rs`、`aes.rs`、`rsa.rs`、`ecdsa.rs` |
| Mermaid 图 | 至少 4 张 | 报告组织、六层架构、认证时序、请求-响应数据流，可补 ER/STRIDE |
| 前端截图 | 主文至少 14 张 | 第 4 章覆盖 Dashboard、AES、Hash、HMAC、PBKDF2、RSA、ECDSA、Demo、Benchmark、Audit、Keys、Encoding、Scenario |

### 3.1 公式编号预案

| 编号 | 内容 | 章节 |
|---|---|---|
| (3-1) | Base64 输出长度 `L = 4 * ceil(n / 3)` | 3.2.1 |
| (3-2) | SHA 类 padding 后长度 `l + 1 + k ≡ 448 (mod 512)` | 3.3.1 |
| (3-3) | HMAC 定义 `H((K' xor opad) || H((K' xor ipad) || m))` | 3.3.5 |
| (3-4) | PBKDF2 块函数 `F(P,S,c,i)=U_1 xor ... xor U_c` | 3.3.6 |
| (3-5) | AES `GF(2^8)` 模多项式 `x^8+x^4+x^3+x+1` | 3.4.1 |
| (3-6) | AES MixColumns 矩阵乘法 | 3.4.1 |
| (3-7) | SM4 轮函数 `X_{i+4}=X_i xor T(X_{i+1} xor X_{i+2} xor X_{i+3} xor rk_i)` | 3.4.2 |
| (3-8) | CTR 模式 `C_i=P_i xor E_K(Nonce||i)` | 3.4.4 |
| (3-9) | GCM 认证标签 `T=E_K(J_0) xor GHASH_H(A,C)` | 3.4.4 |
| (3-10) | RSA 参数 `n=pq, phi(n)=(p-1)(q-1), ed≡1 mod phi(n)` | 3.5.2 |
| (3-11) | RSA 运算 `c=m^e mod n, m=c^d mod n` | 3.5.2 |
| (3-12) | 椭圆曲线 `y^2=x^3+ax+b mod p` | 3.5.3 |
| (3-13) | 点加斜率与坐标更新 | 3.5.3 |
| (3-14) | ECDSA 签名 `r=(kG)_x mod n, s=k^{-1}(z+rd) mod n` | 3.5.4 |
| (3-15) | ECDSA 验签 `u_1=zs^{-1}, u_2=rs^{-1}, R=u_1G+u_2Q` | 3.5.4 |
| (4-1) | 吞吐量 `MB/s = bytes / duration_s / 2^20` | 4.5 |

### 3.2 伪码编号预案

| 编号 | 标题 | 章节 |
|---|---|---|
| Algorithm 3-1 | Strict Base64 Decode | 3.2.1 |
| Algorithm 3-2 | SHA-256 Compression Loop | 3.3.2 |
| Algorithm 3-3 | HMAC-SHA256 | 3.3.5 |
| Algorithm 3-4 | PBKDF2-HMAC-SHA256 | 3.3.6 |
| Algorithm 3-5 | AES Block Encryption | 3.4.1 |
| Algorithm 3-6 | SM4 32-Round Transform | 3.4.2 |
| Algorithm 3-7 | RSA Key Generation and CRT Private Operation | 3.5.2 |
| Algorithm 3-8 | ECDSA Signing with RFC 6979 Nonce | 3.5.4 |
| Algorithm 4-1 | Three-Layer Cross Validation | 4.1 |

### 3.3 源码节选预案

| 编号 | 文件与行段 | 章节 | 用途 |
|---|---|---|---|
| Code 3-1 | `rust_core/src/ffi.rs:19-87` | 3.1 | PyO3 注册和 FFI 边界 |
| Code 3-2 | `rust_core/src/hash/hmac.rs:10-60` | 3.3.5 | HMAC 构造与常时间验证 |
| Code 3-3 | `rust_core/src/hash/pbkdf2.rs:16-64` | 3.3.6 | PBKDF2 迭代派生 |
| Code 3-4 | `rust_core/src/symmetric/aes.rs:355-456` | 3.4.1 | AES key expansion、SubBytes、MixColumns、GF 乘法 |
| Code 3-5 | `rust_core/src/symmetric/sm4.rs:98-184` | 3.4.2 | SM4 轮函数和 T 变换 |
| Code 3-6 | `rust_core/src/pubkey/rsa.rs:48-145` | 3.5.2 | RSA keygen、CRT 和盲化 |
| Code 3-7 | `rust_core/src/pubkey/ecc.rs:124-163` | 3.5.3 | Montgomery ladder 风格标量乘 |
| Code 3-8 | `rust_core/src/pubkey/ecdsa.rs:107-162` | 3.5.4 | RFC 6979 确定性 nonce |

## 4. 章节详细大纲

### 第 1 章 引言

预计正文：3,200-3,600 字。章节任务是从真实安全事件导入密码算法工程实现的风险，再把课程要求落到 CryptoLab 的四类算法、接口调用和教学可视化目标。全章引用重点为 [28]-[32]、[1]-[16]、[38]-[42]，并穿插课程评分细则与 `STATS.md`。

#### 1.1 研究背景与意义

预计 850-950 字。首先从 Heartbleed 的越界读、Cloudbleed 的内存泄漏、ROCA 的 RSA 密钥生成缺陷、PS3 ECDSA `k` 重用切入，说明密码系统失败往往并非算法数学本身被完全攻破，而是工程实现、随机数、边界检查、密钥生命周期和可观测性失效共同造成。其次引入 Rust 内存安全、常时间比较和审计追踪等工程措施，说明 CryptoLab 报告不只评价“能否算出密文”，还评价“能否以可验证、可追溯、可维护方式暴露密码能力”。引用 [28][29][30][31][32][36]。

必备资产：无项目截图，引用安全事件与 `STATS.md` 总览数字。  
公式：无。  
图表：无。

#### 1.2 国内外现状

预计 900-1,050 字。首先综述 OpenSSL、BoringSSL、RustCrypto 和 PyO3/Rust 生态在密码工程中的定位，说明工业界通常把密码原语隔离在边界清晰的库中，通过稳定 API、持续测试和审计来降低调用风险。其次综述 NIST/FIPS/RFC 与国密标准化进程，突出 AES、SHA、RSA、ECDSA、SM4 等算法的标准来源以及实现者必须面对的兼容性和安全边界。引用 [1]-[16][38][39][40][41][50]，至少覆盖 6 篇文献。

必备资产：无项目图。  
表格：国内外生态对比表。  
公式：无。

#### 1.3 课题任务与挑战

预计 650-750 字。首先按课程要求拆解 4 大类别和 15 种算法，说明对称加密、哈希/认证/KDF、编码、公钥密码之间的工程差异。其次结合 `algorithm_implementation.csv` 说明当前 15/15 均有实现证据，14 项为 已完成 (Complete)，RC6 为 部分完成 (Partial)，原因是 ECB/CBC 已实现但 GCM 不暴露。进而说明接口调用、状态码、执行过程可见与 35 页以上报告是本任务的交付约束。引用课程评分细则、`STATS.md`、[1]-[16]。

必备资产：`docs/report_assets/data/algorithm_implementation.csv`。  
表格：课程要求与项目实现对应表。  
公式：无。

#### 1.4 本报告主要工作

预计 350-450 字。以 5 条点列概括贡献，每条 30-50 字，分别覆盖 Rust 核心算法、PyO3/FastAPI 服务化、三重验证、前端可视化与漏洞 demo、密钥保护与审计。正文前后仍需段落式引导和总结，避免列表替代论述。引用 `STATS.md`、`source_index.md`。

必备资产：无。  
表格：可选贡献列表。  
公式：无。

#### 1.5 报告组织结构

预计 350-450 字。用 Mermaid 流程图表示第 1 章到第 7 章的逻辑关系：背景与任务、系统设计、算法实现、执行与展示、接口调用、总结展望、参考文献与附录。段落需说明第 2 章服务于架构评分点，第 3 章服务于代码开发评分点，第 4-5 章服务于结果与接口评分点，第 7 章服务于参考文献评分点。

必备资产：Mermaid `flowchart TD`。  
公式：无。  
小结：承接第 2 章需求与架构。

### 第 2 章 系统设计

预计正文：6,200-7,000 字。章节任务是把课程需求转化为可追溯的架构决策，采用 ADR 风格说明 Rust、PyO3、FastAPI/SQLAlchemy、KEK 信封加密等选型。全章以 `source_index.md` 第 2 节、`STATS.md`、源码模型、日志证据为主，不照搬旧设计方案中的理想状态。

#### 2.1 需求分析

预计 850-1,000 字。首先分表列出功能性需求（FR）：15 种算法、API 调用、执行状态码、可视化过程、漏洞演示、综合安全文件传输。其次列出非功能性需求（NFR）：性能、安全、可观测性、可维护性、可移植性和可复现性。进而说明这些需求如何映射到 Rust core、FastAPI、React、数据库、Redis/内存缓存和报告资产。引用课程评分细则、`STATS.md`、`code_lines_summary.csv`、[47][48][49]。

必备表格：FR 表、NFR 表。  
图表：可引用图 3-1 的算法覆盖矩阵。  
公式：无。

#### 2.2 总体架构

预计 850-1,000 字。首先用 Mermaid 展示六层架构：表示层、网关层、接口层、服务层、算法层、数据层。其次按层解释职责与依赖，说明 React 只负责交互，FastAPI 负责契约和权限，Python service 负责业务编排，PyO3 绑定隔离 Rust 算法，DB/Redis 负责持久化和限流。引用 `api_server/app/main.py`、`rust_core/src/ffi.rs`、`api_server/app/db/session.py`、[41][42][43][44][45]。

必备图表：Mermaid 六层架构图。  
表格：分层职责表。  
公式：无。

#### 2.3 关键技术选型

预计 2,600-3,000 字。每个 ADR 至少 300 字，并含候选方案 × 评估维度权衡矩阵。ADR-001 解释 Rust core 对比 C/Go/纯 Python，在内存安全、性能、生态、学习成本方面的取舍，引用 Heartbleed 和 RustCrypto。ADR-002 解释 PyO3 对比 `ctypes/cffi`，重点是类型安全、错误映射和构建复杂度。ADR-003 解释 FastAPI + SQLAlchemy，以及当前 SQLite/PostgreSQL 适配事实，不夸大生产数据库状态。ADR-004 解释 master key、HKDF-SHA256 派生 KEK、AES-GCM 信封加密入库，对比明文入库、用户口令直接加密和外部 KMS。引用 [28][38][40][41][42][43]，项目证据见 `ffi.rs`、`kek.py`、`models/key_store.py`。

必备表格：ADR-001 至 ADR-004 权衡矩阵。  
图表：可选 ADR 决策流 Mermaid。  
公式：可引用 HKDF 概念但不强制编号。

#### 2.4 数据库设计

预计 850-1,000 字。首先基于 `models/*.py` 和迁移证据总结 `users`、`key_store`、`operation_logs`、`algorithm_metrics` 四张核心表，明确 SQLite 适配导致的字段类型差异。其次解释审计表只存 hash 与元数据，密钥表保存 GCM 加密材料、IV 和 tag，metrics 表当前模型存在但本地数据可能稀疏。引用 `database_snapshot.txt` 和 `PROGRESS.md`，避免照搬 PostgreSQL 理想 DDL。

必备表格：四张表 DDL 摘要。  
图表：Mermaid ER 图。  
公式：无。

#### 2.5 安全设计

预计 1,050-1,250 字。首先用 STRIDE 框架列出 Spoofing、Tampering、Repudiation、Information Disclosure、Denial of Service、Elevation of Privilege 风险，并逐项映射 JWT、GCM AAD、审计日志、KEK、限流和权限边界。其次说明密钥生命周期：生成、信封加密、取用解包、导出限制、撤销、审计。进而说明 trace_id 如何贯穿响应、日志和 DB。引用 `auth.py`、`rate_limit.py`、`audit.py`、`trace.py`、`kek.py`、[47]。

必备表格：STRIDE 风险与缓解措施。  
图表：信任边界 Mermaid。  
公式：无。

#### 2.6 设计原则与权衡

预计 500-650 字。首先总结 fail-closed、最小信任、职责分离在项目中的具体落地：错误状态码、受保护路径、私钥不可导出、Rust 算法不感知 HTTP。其次承认设计代价：异构构建复杂、FFI 边界需要测试、Docker 构建受环境影响、metrics 需要长期采集。引用 `status_codes.csv`、`test_summary.csv`、[48][49]。

必备表格：原则-实现-代价表。  
小结：承接第 3 章算法实现。

### 第 3 章 算法实现

预计正文：12,800-14,500 字。章节任务是按课程评分点展示代码开发深度。每个算法小节采用“五段式”：算法原理与数学基础、标准与规范溯源、实现要点、安全工程考量、自实现与权威库差异。全章至少 12 条公式、8 段伪码、6 段 Rust 源码节选，状态以 `algorithm_implementation.csv` 为准。

#### 3.1 工程结构与构建系统

预计 900-1,050 字。首先说明 Cargo workspace/Rust crate、PyO3 绑定和 Python service 的边界，引用 `traits.rs` 与 `ffi.rs`。其次说明测试和依赖隔离策略，包括 Rust `cargo test`、API `.venv` pytest、前端 TypeScript smoke。进而插入 Code 3-1，解释 `register` 如何把 Rust 函数暴露为 Python 模块。引用 [40][41]。

必备图表：图 3-1 算法覆盖矩阵。  
源码：Code 3-1。  
公式：无。  
差异表：手写 Rust core 与直接 Python 调库对比。

#### 3.2 编码算法

预计 1,250-1,450 字。3.2.1 Base64 用 RFC 4648 解释 3 字节到 4 字符映射、`=` padding 和严格解码，给出公式 (3-1)、Algorithm 3-1，并在差异表中对比 Python `base64`。3.2.2 UTF-8 用 RFC 3629 解释 Unicode scalar value 到 1-4 字节序列的转换，强调拒绝 overlong、surrogate 和非法 tail byte，引用 `utf8.rs` 测试。引用 [12][13]。

必备表格：Base64/UTF-8 自实现与权威库差异表。  
公式：(3-1)。  
伪码：Algorithm 3-1。  
源码：可不放长节选，或在版面允许时节选 `utf8.rs:36-139`。

#### 3.3 哈希算法、消息认证与密钥派生

预计 3,100-3,600 字。3.3.1 SHA-1 说明 Merkle-Damgard、padding、80 轮压缩，并讨论 SHAttered 后只能用于教学或兼容；引用 [2][25][26]。3.3.2 SHA-256 展开消息调度和压缩函数，给出公式 (3-2)，Algorithm 3-2，并可选节选 `sha2.rs`。3.3.3 SHA-3/Keccak 说明海绵结构和项目实现边界，引用 [3][24]。3.3.4 RIPEMD-160 说明双线结构和用途边界。3.3.5 HMAC 给出公式 (3-3)、Algorithm 3-3、Code 3-2，引用 [9][10][22]。3.3.6 PBKDF2 给出公式 (3-4)、Algorithm 3-4、Code 3-3，并讨论迭代次数与暴力破解成本关系，引用 [7][11][36]。

必备表格：SHA-1、SHA-256、SHA-3、RIPEMD-160、HMAC、PBKDF2 差异表。  
公式：(3-2)、(3-3)、(3-4)。  
伪码：Algorithm 3-2、3-3、3-4。  
源码：Code 3-2、Code 3-3；可选 SHA-256 压缩函数节选。

#### 3.4 对称加密

预计 3,200-3,700 字。3.4.1 AES 解释 SPN、S 盒、ShiftRows、MixColumns、KeyExpansion，给出公式 (3-5)、(3-6)、Algorithm 3-5、Code 3-4，并引用 FIPS 197、SP 800-38A/38D、图 4-15。3.4.2 SM4 解释 32 轮结构、S 盒、线性变换、与 AES 设计哲学差异，给出公式 (3-7)、Algorithm 3-6、Code 3-5，引用 GB/T 32907-2016。3.4.3 RC6 必须标注 ECB/CBC 已实现、GCM 不暴露，引用 `algorithm_implementation.csv`。3.4.4 工作模式解释 ECB/CBC/CTR/GCM 的数学定义、应用场景和安全性差异，给出公式 (3-8)、(3-9)，并联系第 4 章 ECB 泄露 demo。引用 [1][5][6][16][23]。

必备表格：AES、SM4、RC6 差异表；工作模式安全性表。  
公式：(3-5) 至 (3-9)。  
伪码：Algorithm 3-5、3-6。  
源码：Code 3-4、Code 3-5，可选 RC6 片段。

#### 3.5 公钥密码

预计 3,150-3,650 字。3.5.1 大数运算说明 Miller-Rabin、扩展欧几里得、模幂与随机素数生成，引用 `bigint/mod.rs`。3.5.2 RSA-1024 给出公式 (3-10)、(3-11)、Algorithm 3-7、Code 3-6，比较 PKCS#1 v1.5 与 OAEP/PSS，并说明盲化抗时序攻击，引用 [8][17][27][32]。3.5.3 ECC-160 给出公式 (3-12)、(3-13)，说明 secp160r1、点加、点倍、Montgomery ladder，引用 [15][19][20]。3.5.4 ECDSA 给出公式 (3-14)、(3-15)、Algorithm 3-8、Code 3-8，说明 RFC 6979 确定性 `k` 与 PS3 事件，引用 [4][14][21][31]。

必备表格：RSA、ECC、ECDSA 自实现与权威库差异表。  
公式：(3-10) 至 (3-15)。  
伪码：Algorithm 3-7、3-8。  
源码：Code 3-6、Code 3-8；可选 Code 3-7。

#### 3.6 安全工程横切关注点

预计 1,100-1,300 字。3.6.1 论证 Rust 内存安全如何降低 Heartbleed 类 OOB 读风险，但也承认逻辑错误和侧信道仍需测试与审计。3.6.2 说明常时间执行：Rust `subtle::ConstantTimeEq`、Python `hmac.compare_digest`，并联系 HMAC、GCM tag、digest 校验。3.6.3 说明密钥生命周期和零化边界：正文前需再次核对 `zeroize` 实际使用范围，避免夸大；服务端以 KEK 信封加密、私钥不导出、审计脱敏作为主证据。引用 [28][32][36][40]。

必备表格：安全关注点-实现证据-剩余风险。  
图表：可引用 STRIDE 表。  
公式：无。  
小结：承接第 4 章测试和展示。

### 第 4 章 执行结果、系统展示与性能分析

预计正文：5,200-6,100 字。章节任务是把测试、前端实际展示、性能和安全 demo 合并呈现，避免只有后端日志。全部数字来自 `test_summary.csv`、benchmark CSV、日志和截图索引。

#### 4.1 测试体系概述

预计 600-750 字。首先说明三重验证体系：自实现 vs 标准测试向量、自实现 vs 主流库、跨语言/HTTP/前端一致性。其次插入图 4-1 和图 4-2，解释它们如何覆盖算法族和证据层。引用 `cross_validation_matrix.md`、`FIGURE_QA.md`、[1]-[16]。

必备图：图 4-1、图 4-2。  
伪码：Algorithm 4-1。  
公式：无。

#### 4.2 正确性验证

预计 850-1,000 字。首先列标准测试向量覆盖表，说明 Base64、UTF-8、SHA、HMAC、PBKDF2、AES、SM4、RC6、RSA、ECC、ECDSA 分别引用哪些来源。其次列 Rust `53 passed, 0 failed, 3 ignored`、API `.venv` `254 passed, 1 deselected`、前端 `npm test` TypeScript smoke 通过。与此相对，裸 pytest 缺 `jwt`，Docker build 失败，应作为局限而不是失败掩盖。引用 `test_vector_sources.csv`、`test_summary.csv`、日志。

必备表：测试向量覆盖表、测试结果表。  
图：图 4-1。  
公式：无。

#### 4.3 前端密码算法过程与结果展示

预计 1,500-1,800 字。按 4.3.1 至 4.3.5 展示主工作台、AES-GCM、Hash/HMAC/PBKDF2、RSA/ECDSA、编码/密钥/审计。每张截图后写 80-150 字，说明输入、输出、算法意义和支撑结论。引用 `FRONT_SCREENSHOT_CLASSIFICATION.md`，使用 P0_01、P0_02、P0_04、P0_05、P0_06、P0_07、P1_04、P1_05、P1_03、P0_09、P1_06。

必备截图：至少 11 张前端图。  
表：截图说明表。  
公式：无。

#### 4.4 AES verbose / 教学模式中间过程

预计 650-800 字。首先明确前端截图 `P0_03_frontend_symmetric_aes_verbose_trace.png` 当前未发现，不能写成已采集。其次使用 `verbose_mode.md`、`aes_verbose_trace_fips197.json` 和图 4-15 作为替代证据，说明 FIPS 197 AES-128 向量每轮 state 对照。引用 [1]。

必备图：图 4-15。  
必备缺口说明：前端 P0-03 待补拍。  
公式：可回引 (3-5)、(3-6)。

#### 4.5 性能基准测试

预计 800-950 字。首先插入图 4-16，说明吞吐型算法、KDF/HMAC、公钥操作处在不同数量级，因此使用分面而非单一坐标轴。其次引用 `fig4_benchmark_summary.csv` 中 AES ECB 平均约 101.58 MB/s、AES GCM 约 13.81 MB/s、SM4 ECB 约 87.13 MB/s、RC6 ECB 约 222.78 MB/s、SHA256 约 218.27 MB/s、PBKDF2 约 14.01 ms/op、ECDSA verify 约 34.79 ms/op 等数据，保留合理有效位数。引用公式 (4-1)。

必备图：图 4-16、P1_01 benchmark 前端截图。  
公式：(4-1)。  
表：benchmark 摘要表。

#### 4.6 安全漏洞演示模块

预计 850-1,000 字。首先说明 ECB 模式信息泄露，插入 P0_08 和图 4-17；其次说明 ECDSA k 值重用如何恢复私钥、RSA 小指数攻击边界、PBKDF2 迭代次数对成本的影响。进而强调 demo 与生产路径隔离，demo 是教学材料而非推荐配置。引用 `demos_service.py`、`fig6` CSV、[31][36]。

必备图：图 4-17、P0_08、可选 extra demo 图。  
公式：可回引 (3-14)。  
表：漏洞-成因-演示证据-防护表。

#### 4.7 综合应用场景

预计 650-800 字。展示安全文件传输端到端流程：RSA-OAEP 包装会话密钥、AES-GCM 加密文件、SHA-256 计算摘要、ECDSA 签名。插入 P1_02，说明 envelope JSON、协议步骤与机密性/完整性/不可否认性标签。引用 `scenario_service.py`、[1][6][8][14]。

必备图：P1_02。  
图表：Mermaid 发送/接收流程图。  
小结：承接第 5 章接口调用。

### 第 5 章 接口设计与调用

预计正文：4,100-4,800 字。章节任务是证明第三方程序可以通过接口调用算法并获得状态码。全章以 `api_endpoints.csv`、`status_codes.csv`、API 探测日志、路由源码、前端 API 集成为主。

#### 5.1 接口设计原则

预计 600-750 字。说明 RESTful 约束、`/api/v1` 版本化、端点按功能域分组、幂等性边界、统一错误码。引用 [42][47]、`api_endpoints.csv`。

必备表：接口设计原则表。  
公式：无。

#### 5.2 端点全景

预计 700-850 字。按 auth、symmetric、hash、encoding、pubkey、keys、audit、benchmark、demos、scenarios、metrics 分类展示 32 个端点。必须说明 4 个 demos 路由有 handler/service/test 证据，但未显式声明 `response_model`，状态为 部分完成 (Partial)。引用 `api_endpoints.csv`，附录 A 放完整表。

必备表：端点分类表。  
图：无。

#### 5.3 统一响应结构与状态码体系

预计 650-800 字。说明 `APIResponse` 的 `code/message/data/trace_id` 结构，解释 1000、200x、300x、410x、420x、500x 分段。引用 `schemas/common.py`、`status_codes.csv`、`status_codes.py`。

必备表：状态码分段表。  
图：无。

#### 5.4 鉴权、限流与审计

预计 850-1,000 字。首先用 Mermaid 时序图描述注册/登录、JWT 签发、访问受保护端点、黑名单登出。其次说明 Redis 或 memory cache 的 `rate_limit:{ip}:{path_prefix}` 和 `jwt_blacklist:{jti}` key 模式。进而列审计日志字段表，说明不存明文，只存 hash、trace、状态和耗时。引用 `auth.py`、`rate_limit.py`、`audit.py`、`operation_log.py`。

必备图：鉴权流程 Mermaid sequenceDiagram。  
必备表：审计字段表。  
公式：无。

#### 5.5 第三方调用范式

预计 750-900 字。给出 curl 调用 `POST /api/v1/hash/sha256` 的示例和日志路径，给出 Python `requests/httpx` 客户端示例，说明 Swagger UI 当前缺 PNG 截图但有 OpenAPI 日志，说明前端 React 通过 API 模块将算法过程和结果渲染到页面。引用 `api_probe_noproxy.txt`、`SCREENSHOT_INDEX.md`。

必备代码块：curl 示例、Python 示例。  
缺口：Swagger 截图待补拍。  
图：可选 Swagger 待补说明。

#### 5.6 错误处理与可观测性

预计 650-800 字。说明 `trace_id` 如何从中间件进入响应头、统一异常处理和审计日志；说明 metrics 表和 `/metrics` 端点存在，但本地运行数据可能稀疏，不能夸大长期观测能力。插入 Mermaid 数据流图，展示 request -> middleware -> router -> service -> Rust core/DB -> response。引用 `trace.py`、`exceptions.py`、`metrics_service.py`、`database_snapshot.txt`。

必备图：请求-响应数据流 Mermaid。  
表：错误场景与状态码表。  
小结：承接总结。

### 第 6 章 总结与展望

预计正文：2,300-2,800 字。章节任务是回扣第 1 章目标，突出主要创新，同时诚实承认局限。不得用夸大形容词，不得掩盖 Docker、RC6、AES verbose 前端截图、裸 pytest、metrics、demos response_model 问题。

#### 6.1 工作总结

预计 750-900 字，4-5 段。分别总结算法覆盖、异构架构、测试验证、前端展示和安全工程。引用 `STATS.md`、图 3-1、图 4-1。

#### 6.2 主要创新点

预计 800-1,000 字，5 项创新，每项 150-200 字。建议创新点：Rust × Python 异构密码核心、三重验证体系、AES verbose 教学模式、漏洞 demo 与综合场景、KEK/审计/状态码工程化。引用 [40][41][42][47][48] 和项目资产。

#### 6.3 局限性与不足

预计 550-700 字，至少 6 项。必须列 RC6 部分完成、Docker build 失败、AES verbose 前端截图缺失、裸 pytest 缺 `jwt`、metrics 数据稀疏、demos route 未显式 `response_model`。可补充 ECDSA secp160r1 第三方库交叉验证限制、前端 `npm test` 只是 TypeScript smoke。

#### 6.4 未来工作

预计 350-450 字。包括完整模式覆盖、Docker 构建稳定性、UI 自动化测试、长期 metrics 采集、更多漏洞 demo、最终排版完善。小结过渡到参考文献和附录。

### 第 7 章 参考文献

预计不计入正文页数。按 [1]-[50] 统一编号，正文阶段确保每条至少出现一次。分类组织但编号连续，包含国际标准与 RFC、国家标准、学术经典、安全事件、教材专著和工程实践。

## 5. 附录规划

| 附录 | 标题 | 数据来源 |
|---|---|---|
| 附录 A | 完整 API 端点列表 | `docs/report_assets/data/api_endpoints.csv` |
| 附录 B | 完整状态码表 | `docs/report_assets/data/status_codes.csv` |
| 附录 C | 测试向量来源汇总 | `docs/report_assets/data/test_vector_sources.csv` |
| 附录 D | 图表资产索引 | `docs/report_assets/data/figure_assets_summary.csv`、`FIGURE_INDEX.md`、`FIGURE_QA.md` |
| 附录 E | 截图资产索引 | `SCREENSHOT_INDEX.md`、`FRONT_SCREENSHOT_CLASSIFICATION.md` |
| 附录 F | 构建与运行说明 | `STATS.md` 复现命令、logs、Docker config/build 日志 |

## 6. 阶段交付节奏

阶段 2 写第 1、2 章和参考文献初稿，重点先定引用编号和 ADR 叙事。阶段 3 独立写第 3 章，需要逐段检查公式、伪码、源码节选和差异表。阶段 4 写第 4、5 章，重点插入前端截图并承认缺口。阶段 5 写第 6、7 章、附录和 `REPORT_CHECKLIST.md`，重点做红线自检。

