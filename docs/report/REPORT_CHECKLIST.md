# CryptoLab 最终报告自检清单

生成时间：2026-06-29 Asia/Shanghai  
项目根目录：`D:\Nnutural\Desktop\BUPT_6\SecureProgrammingTechnologyandCaseDevelopment\期中作业\CryptoLab`  
当前 `HEAD`：`0861103477a7126599bde0fafafb1a3ed602a9d3`  

## 1. 本轮交付物

| 文件 | 状态 | 说明 |
|---|---|---|
| `docs/report/source_index.md` | 已生成 | 章节到源码、行号、CSV、日志、截图的索引 |
| `docs/report/REPORT_ASSET_MAP.md` | 已生成 | 章节到图表、截图、数据表、日志证据的映射 |
| `docs/report/outline.md` | 已生成 | 三级标题、字数预算、引用、公式、伪码、代码节选规划 |
| `docs/report/FINAL_REPORT.md` | 已生成 | Markdown 主稿，含摘要、正文、参考文献、附录 |
| `docs/report/REPORT_CHECKLIST.md` | 已生成 | 本自检清单 |

## 2. 格式与范围自检

| 检查项 | 结果 | 备注 |
|---|---|---|
| 只生成 Markdown 主稿 | 通过 | 未要求 LaTeX，本轮未创建 `main.tex` |
| 未创建 `.tex` 文件 | 通过 | 已用文件扫描确认 `docs/report` 下无 `.tex` 文件 |
| 章节编号至三级标题 | 基本通过 | 正文使用 `# / ## / ###`，附录也用 `#` 标题 |
| 图片使用 Markdown 语法 | 通过 | 第 3、4 章已引用图表和前端截图 |
| 图表标题与说明 | 通过 | `FINAL_REPORT.md` 中 30 个图注和 36 个表注均已设置独立标题段 |
| Mermaid 使用源码嵌入 | 通过 | 包含章节关系、架构、ER、信任边界、鉴权、数据流、场景时序 |
| 公式编号 | 通过 | 含 (3-1) 至 (3-19)、(4-1) |
| 算法伪码 | 通过 | 含 Algorithm 3-1 至 3-8、Algorithm 4-1 |
| Rust 源码节选 | 通过 | 含 FFI、HMAC、PBKDF2、AES、RSA、ECC、ECDSA 7 段 |
| 引用条目 | 通过 | 第 7 章列出 54 条参考文献 |
| 附录 | 通过 | 含 API、状态码、测试向量、图表、截图、构建运行说明 |

## 3. 事实边界自检

| 风险点 | 处理结果 |
|---|---|
| RC6 当前状态 | 已写为 ECB/CBC 已实现、GCM 不暴露，未写成全模式完成 |
| Docker build | 已写明 compose config 通过、build 存在失败日志，未写成成功 |
| AES verbose 前端截图 | 已写明 `P0_03_frontend_symmetric_aes_verbose_trace.png` 未发现，并用 JSON/文档/Fig.5 替代 |
| 裸 pytest | 已写明裸 pytest 缺 `jwt`，项目 `.venv` 下 pytest 通过 |
| metrics 数据 | 已写明本地数据可能稀疏，未夸大长期监控能力 |
| demos response_model | 已写明 4 个 demos 路由未显式声明 `response_model`，状态为 部分完成 (Partial) |
| 当前 Git 状态 | 当前核对时 `docs/report/` 为本轮新增未跟踪目录；历史材料内记录的 dirty 状态已在索引中区分 |

## 4. 已使用的核心图表与截图

| 类型 | 已进入正文 |
|---|---|
| 实验图 | Fig.1 测试验证、Fig.2 算法覆盖、Fig.3 交叉验证、Fig.4 benchmark、Fig.5 AES verbose、Fig.6 安全 demo |
| 前端截图 | Dashboard、AES-GCM、Hash、HMAC、PBKDF2、RSA、ECDSA、Encoding、Keys、Audit logs、Audit detail、ECB demo、ECDSA k 复用 demo、PBKDF2 迭代影响 demo、Benchmark、Secure file transfer 发送/接收/验证 |
| Mermaid 图 | 报告组织结构、六层架构、ER 图、请求信任边界、文件传输时序、JWT 鉴权、请求响应数据流 |

## 5. 仍需人工补图或可选增强

| 编号 | 缺口 | 当前证据 | 建议 |
|---|---|---|---|
| M-01 | AES verbose 前端截图 | `fig5_aes_verbose_trace.png`、`verbose_mode.md`、JSON | 在 `/symmetric` 页面启用教学模式后补拍 `P0_03_frontend_symmetric_aes_verbose_trace.png` |
| M-02 | Swagger UI 总览截图 | `api_probe_noproxy.txt` | 打开 `http://127.0.0.1:8000/docs` 补拍 |
| M-03 | API 成功响应截图 | `api_probe_noproxy.txt` | 用 Swagger 或 HTTP 客户端执行 `POST /api/v1/hash/sha256` 后补拍 |
| M-04 | Rust 测试通过截图 | `cargo_test_full.txt` | 如需 PNG，重新运行测试或截图历史通过日志 |
| M-05 | API pytest / npm test 截图 | `pytest_venv_full.txt`、`npm_test_full.txt` | 当前有日志，PNG 可选补拍 |
| M-06 | 数据库审计快照截图 | `database_snapshot.txt` | 打开脱敏日志或重新查询后截图 |
| M-07 | Docker build 成功证据 | 当前只有失败日志 | 修复网络/镜像源/依赖版本后重跑 build |
| M-08 | 更严格段落红线 | 主稿已尽量使用长段落 | 若后续排版前逐段审查，可进一步调整短 caption 或短表格说明 |

## 6. 可选转换命令

本轮不要求生成 PDF，也不创建 LaTeX 文件。若后续需要从 Markdown 转换 PDF，可在人工确认图片路径、字体和页面样式后选择类似命令：

```powershell
pandoc docs\report\FINAL_REPORT.md -o docs\report\FINAL_REPORT.pdf --toc --number-sections
```

该命令仅作为后续排版参考，不属于本轮交付要求。





