"""Service layer — business orchestration sits between routers and models.

Routers MUST NOT import from `app.models` directly. All persistence, KEK
wrapping, and audit-emission go through one of these services so the
algorithm layer has a single place to find them.
"""
