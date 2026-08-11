# Human review checklist

- [ ] The response detects local convention (lint config, tsconfig, touched
      files) before applying any default.
- [ ] Existing repository convention and lint configuration win over the
      skill's defaults, and divergence is noted rather than silently applied.
- [ ] Style migrations are proposed as separate, lint-driven changes, never
      mixed into a feature or bug-fix diff.
- [ ] New convention-free code uses `type` aliases, and `interface` appears
      only for declaration merging or class-hierarchy clarity.
- [ ] Properties and unmutated array/object parameters are `readonly`.
- [ ] Functions keep at most 3 parameters, overflow moves to a trailing typed
      options object, and booleans are named options.
- [ ] Pure TS/JS files use `kebab-case`; ecosystem-cased files (for example
      React `PascalCase.tsx` components) follow their ecosystem.
- [ ] Named exports are used unless a framework requires a default export.
- [ ] No `any`, unexplained suppressions, or weakened `tsconfig` strictness
      is introduced to make errors disappear.
- [ ] Machine-checkable rules are proposed as lint configuration, not prose.
- [ ] Review requests produce findings with citations, not unrequested edits.
- [ ] Output is materially equivalent on each claimed platform.
