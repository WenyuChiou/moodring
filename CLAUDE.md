# MoodRing — repo-specific strategy

> Relocated from the global `~/.claude/CLAUDE.md` §Per-Repo Strategies on
> 2026-07-06 (REC-20260706-010): per-repo strategy belongs in the repo, not
> in every session's per-turn context. Global file keeps a two-line summary.

## Workflow — direct-to-main + pre-push validation

- **Direct-to-main** for data fixes, pipeline fixes, single-file UI tweaks.
- **Use a branch** only for multi-file dashboard refactors.
- **Guardrail:** validate `docs/` JSON/HTML before EVERY push — a bad push
  is a broken live dashboard.

## Reporting context

- Include the dashboard link in the morning briefing — Eric checks it on
  his phone (mobile rendering matters).
