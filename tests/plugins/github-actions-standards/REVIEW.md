# Human review checklist

- [ ] Repository policy, required checks, delivery contract, and supported
      runtimes are discovered rather than invented.
- [ ] The main checks and required artifact handoffs are visible in `ci.yml`.
      Each extra file has a concrete caller or independent lifecycle, and
      step names identify failures in the run log.
- [ ] A restructure preserves the previous event-to-publication contract,
      including manual dry runs, approvals and trusted-publisher bindings.
- [ ] The primary CI uses explicit triggers, concurrency, runner job timeouts, stable job
      names, least-privilege permissions, and real dependency edges.
- [ ] String values in `with:`, `env:`, and runtime-version fields are quoted
      so YAML type coercion cannot change them; genuinely typed booleans and
      numbers stay unquoted.
- [ ] Untrusted PR code cannot access secrets, write tokens, OIDC, protected
      environments, or persistent runners.
- [ ] Checkout uses `persist-credentials: false` unless a later step in the
      same job must authenticate as the repository, in which case
      `persist-credentials: true` is declared explicitly and isolated in its
      own least-privilege job.
- [ ] Secrets do not appear in source, command arguments, or logs; derived
      values are masked before output and exposure response is documented.
- [ ] Official actions use exact release tags unless a stricter SHA policy
      applies. Third-party actions and external workflow calls use full
      upstream SHAs. An unverified action has specific user approval.
- [ ] Routine jobs need no stored secrets. Direct calls and safe defaults
      suffice unless additional setup or local reuse has a concrete consumer.
- [ ] Keys follow the documented order, simple values fit inline within 160
      columns and quoted step names are separated by one blank line.
- [ ] Dependency installation is lockfile-based and cache misses remain correct.
- [ ] Required outputs are built once and the distributable artifact is tested.
- [ ] Matrices, service jobs, retries, diagnostics, and cleanup have bounded
      failure behavior.
- [ ] Release and deployment work is isolated behind successful CI, trusted
      refs, protected environments, and a recovery plan.
- [ ] Any PR preview is per-PR, ephemeral, non-production, bounded, and
      deployed and cleaned up without privileged execution of contributor code.
- [ ] Path filtering cannot strand or bypass required checks.
- [ ] Repository settings and external side effects are not changed without
      authorization.
- [ ] Validation and observed workflow evidence are reported accurately.
- [ ] No language, vendor, runner, registry, task runner, secret, or branch is
      generalized from a project-specific example.
- [ ] No supply-chain, compliance, or production-readiness certification is
      claimed.
- [ ] Output is materially equivalent on each claimed platform.

After reviewing a scenario on a platform, record the outcome in
`acceptance.json` beside this file. Results are pinned to the plugin version,
so a version bump requires a fresh review.
