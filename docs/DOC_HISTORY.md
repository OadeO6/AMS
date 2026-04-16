# DOC History

---

## About

A chronological log of all changes made to documentation files in this project.
One entry per meaningful change — no prose, just facts.

---

## Developer Instructions

> **How to update:** Every time you modify a file in `/docs/`, add a line at the top of the log below.
> Format: `YYYY-MM-DD | <file(s) changed> | <short description>`
> Do **not** delete old entries. Archive to `DOC_HISTORY_ARCHIVE.md` if the file exceeds 150 lines.
>
> **Files that require a log entry on change:**
> `ARCHITECTURE.md`, `ENDPOINTS.md`, `ENDPOINTS_DETAIL.md`, `DATABASE_SCHEMA.md`,
> `BUSINESS_RULES.md`, `TASK_HISTORY.md`

---

## Log

| Date | File(s) | Change |
|------|---------|--------|
| 2026-04-16 | `ENDPOINTS_DETAIL.md`, `DOC_HISTORY.md` | Phase 1 — Populated Auth section with full specs for all 11 auth endpoints (register/student, register/lecturer, login, logout, refresh, forgot-password, reset-password, GET/PATCH /me, PATCH /me/student, /me/lecturer, /me/password) |
| 2026-04-16 | `ARCHITECTURE.md`, `DOC_HISTORY.md` | Comprehensive update to architecture: stack versions, refined structure, and key design decisions |
| 2026-04-16 | `ARCHITECTURE.md`, `ENDPOINTS.md`, `ENDPOINTS_DETAIL.md`, `DOC_HISTORY.md` | Restructured docs: separated About from instructions, added sync requirements, created detailed endpoint spec file and this history log |
