PS> Select-String -Path README.md -Pattern 'Vue3|init|todo|React|FastAPI'

README.md:3:CryptoLab 是一个基于 **Rust PyO3 + FastAPI + React** 的密码算法实验平台，用手写 Rust 密码原语支撑可审计的 Web API、教学可视化界面、漏洞演示和综合安全文件传输场景。
README.md:8:[![Frontend](https://img.shields.io/badge/frontend-React%2018%20%2B%20Vite-61dafb)](#)
README.md:13:- **完整服务化链路**：FastAPI 将 Rust 扩展包装为 `/api/v1/*` REST API，包含 JWT、限流、审计、密钥存储和统一响应模型。
README.md:14:- **React 教学界面**：`frontend/` 是 React 18 + Vite + Tailwind + Radix UI 前端，包含 Dashboard、Symmetric、Hash、Encoding、RSA/ECC、Keys、Audit、Benchmark、Demos、Scenarios 等页面。
README.md:21:React 18 views
README.md:24:  -> FastAPI routers + Pydantic schemas
README.md:35:L6  React 18 + Vite + Tailwind + Radix UI / Swagger UI
README.md:37:L4  FastAPI + JWT + Pydantic + unified APIResponse
README.md:79:| API | Python 3.11，FastAPI 0.110，Pydantic 2.6，SQLAlchemy 2.0，Alembic，PyJWT，Redis，structlog |
README.md:80:| Frontend | React 18.3，Vite 6.3，TypeScript 5.7，Tailwind CSS 4.1，Radix UI，axios，Recharts |
README.md:98:├── api_server/                 # FastAPI 服务端
README.md:108:├── frontend/                   # React 18 + Vite + Tailwind + Radix UI


PS> Select-String -Path CLAUDE.md -Pattern 'React|Implementation Status|Remaining Rust|Benchmark note'

CLAUDE.md:7:CryptoLab is a BUPT secure-programming midterm project: hand-written cryptographic primitives in Rust, exposed through PyO3, served by FastAPI, and exercised from a React teaching UI.
CLAUDE.md:15:- **UI layer**: `frontend/` is a React 18 + Vite 6 + Tailwind 4 + Radix UI app with 12 API-backed views.
CLAUDE.md:38:├── frontend/                  # React 18 + Vite 6 + Tailwind 4
CLAUDE.md:78:| Frontend | React 18.3, Vite 6.3, TypeScript 5.7, Tailwind 4.1, Radix UI; 12 React views under `frontend/src/views/`. |
CLAUDE.md:83:## Implementation Status
CLAUDE.md:86:- Remaining Rust `todo!()`: none in algorithm modules.
CLAUDE.md:90:- Benchmark note: backend benchmark service currently supports SHA-256 only.
CLAUDE.md:112:- Frontend API calls belong in `frontend/src/api/`; React views should not use raw `axios`.
CLAUDE.md:119:- TypeScript: React function components, strict types where useful, no broad UI refactors during API fixes.


[exit=]
