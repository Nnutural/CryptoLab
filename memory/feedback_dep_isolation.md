---
name: feedback-dep-isolation
description: All toolchains and dependencies in CryptoLab (and similar user projects) must be installed under the project directory, never into user-global locations.
metadata:
  type: feedback
---

Never install Rust toolchains/crates, Python packages, or npm packages into user-global locations (`~/.cargo`, `~/.rustup`, global Python site-packages, global npm). Always use project-local paths: `./.cargo-home/`, `./.rustup-home/`, `./.venv/`, `./node_modules/`, `./.npm-cache/`, `./.npm-global/`.

**Why:** the user is a student running multiple coursework projects on a personal Windows machine — polluting user-global state would cause version conflicts between courses and leave artifacts that are hard to clean up. They explicitly required this isolation in the CryptoLab init brief.

**How to apply:** before running `cargo`, `rustup`, `pip`, `uv`, or `npm` commands, ensure project-local env is sourced (`scripts/env.sh` exports `CARGO_HOME`, `RUSTUP_HOME`, activates `.venv`). Reflect this rule in any new project's CLAUDE.md / README / setup scripts unless the user opts out. See [[cryptolab-project]].
