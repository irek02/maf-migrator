# Build plan — MAF Migrator

**Status:** Phase 0 (scaffold + harness + corpus) — corpus manifest + runner done; next item is 1.1 (usage scanner).
**Last updated:** 2026-07-19 (by agent)
**Waiting on Irek:** nothing — build server token granted repo access 2026-07-18; builder
fully unblocked through gate 1.5.

## What this is

A self-serve codemod that migrates AutoGen Python codebases to Microsoft Agent Framework
(MAF). Free tier: analyzer + basic transforms (OSS lead magnet). Paid tier ($299/$999):
full automated migration, delivered as a licensed add-on — strictly no calls/onboarding.
Bet doc (why/kill criteria/scope): workspace `notes/side-income/bets/bet-02-maf-migrator.md`.

## How this plan is executed

Per the workspace `skills/bet-builder/SKILL.md`: one checklist item per heartbeat run, first
unchecked `[agent]` box not behind an unpassed `⛔ GATE`; `[IREK]` items are Irek's; split
oversized items before starting them; every completed item updates this file's Status header
and Build log in the same commit as the code.

## Testing approach

Everything here is local Python — no OAuth, no browser, no product credentials — so unlike
attio-sheets, **integrated tests can reach almost the entire product.** Rules:

- `pytest` is the suite; `pip install -e ".[dev]" && pytest` must pass from a fresh clone.
- **Tests drive the CLI entry points** (`maf-migrate analyze <path>`, `maf-migrate run
  <path>`) on small fixture projects under `tests/fixtures/`, asserting observed outputs:
  files written, report content, exit codes, diff contents. No testing of private helpers,
  no mocking of our own modules.
- **No network in the test suite.** The only network code in the product is the corpus
  runner script, which is a dev tool, not product surface; corpus runs are a measured
  scoreboard (`docs/corpus-scoreboard.md`), not a CI gate.
- **Transform correctness = snapshot pairs**: each transform is specified by
  `before.py` → `expected_after.py` fixture pairs (ground truth: Microsoft's migration
  guide examples). The pair IS the acceptance test — pre-write pairs for future transform
  items whenever the guide provides the example.
- **Migrated-output validity tiers** (corpus runner measures, tests enforce on fixtures):
  (1) output parses; (2) imports resolve against the real installed MAF package;
  (3) type check passes (`pyright` or `mypy`, whichever the scaffold picks);
  (4) where feasible, the migrated fixture actually constructs its agent graph under a
  stub model client — no LLM keys ever needed.
- Unreachable by tests, by construction: whether MAF *semantically* behaves like the
  AutoGen code did at runtime with a live LLM. That band belongs to the gates (Irek
  eyeballing real diffs) and to flagship example migrations — say so in the log rather
  than implying it's covered.

## Checklist

### Phase 0 — scaffold, harness, corpus

- [x] [agent] 0.1 Package scaffold: `pyproject.toml` (package `maf_migrator`, console
      script `maf-migrate`, minimal deps: `libcst`, `typer` or argparse — builder's call,
      recorded in the log), `pytest` wired with one integrated smoke test
      (`maf-migrate --version` exits 0), README stub, this .gitignore kept intact.
      Acceptance tests: none yet (day zero) — the smoke test is written as part of this item.
      (done 2026-07-19, awaiting manual verification)
      Manual test: `pip install -e . && maf-migrate --version` — should print `maf-migrate 0.1.0` and exit 0.
      CLI framework chosen: `typer` (clean declarative API, rich help output).
- [x] [agent] 0.2 Pin the target: identify the real MAF Python package(s) on PyPI (verify
      names/versions against PyPI + the official repo — **check against source, not blog
      posts**), pin them and the AutoGen packages (`autogen-agentchat` 0.4.x line, legacy
      0.2 `pyautogen`/`autogen` line) as dev extras, and record exact pins + links in
      `docs/targets.md`. Test: an integrated test imports the installed MAF package and
      asserts the pinned version, so a pin drift fails loudly.
      (done 2026-07-19, awaiting manual verification)
      Manual test: `pip install -e ".[dev]" && python3 -m pytest tests/test_package_pins.py -v` — 3 version-pin tests should pass (agent-framework-core==1.11.0, autogen-agentchat==0.4.9.3, pyautogen==0.2.35). Also verify `docs/targets.md` exists and contains the PyPI links.
      MAF package: `agent-framework-core` (import name: `agent_framework`); full meta-package: `agent-framework`. The `__version__` attr reads `0.0.0` — use `importlib.metadata.version("agent-framework-core")` for the real version.
- [x] [agent] 0.3 Ground-truth fixtures: extract before/after example pairs from
      Microsoft's official AutoGen→MAF migration guide
      (learn.microsoft.com `/agent-framework/migration-guide/from-autogen/`) into
      `tests/fixtures/guide/<case>/{before.py,expected_after.py}`, with `SOURCES.md`
      linking each pair to its guide section. No transform code yet — these are the
      pre-written acceptance tests for Phase 2. Test: a validity test asserts every
      `before.py` parses and every pair is complete.
      (done 2026-07-19, awaiting manual verification)
      Manual test: `python3 -m pytest tests/test_guide_fixtures.py -v` — 6 validity tests
      should pass. Also inspect `tests/fixtures/guide/` — should contain 5 case dirs
      (model_client_openai, basic_agent_creation, tool_creation, streaming, messages),
      each with before.py and expected_after.py, plus SOURCES.md.
      Cases sourced from: model client, agent creation, tool creation, streaming, messages
      sections of the live migration guide.
- [x] [agent] 0.4 Corpus manifest + runner: `corpus.yaml` (~25 public GitHub repos that
      import AutoGen — mix of v0.4 `autogen_agentchat` and legacy `import autogen` users,
      each with url, pinned commit, license, generation; candidates from the 2026-07-18
      search: magentic-ui, testzeus-hercules, ai-book-writer, neuralnoise, plus small/mid
      repos from the code-search hits) and `scripts/corpus.py` that clones them into
      `corpus/` (gitignored). Corpus code is never committed or redistributed. Test:
      integrated test runs the manifest loader + validates schema; cloning itself is
      exercised by a `--dry-run` mode test (no network in suite).
      (done 2026-07-19, awaiting manual verification)
      Manual test: `python scripts/corpus.py --dry-run` — should print 25 repo lines and
      "Dry run OK" then exit 0. Also `python3 -m pytest tests/test_corpus.py -v` — 8 tests
      green. Note: commit SHAs in corpus.yaml are stub placeholders; real cloning
      (`python scripts/corpus.py`) will fail until re-pinned at task 1.2 time.

### Phase 1 — analyzer (the free lead magnet)

- [ ] [agent] 1.1 Usage scanner: `maf-migrate analyze <path>` walks a repo, detects both
      AutoGen API generations, and emits a JSON inventory of constructs used (imported
      names, instantiated classes, called functions, per file:line). Acceptance tests:
      pre-written against 2–3 guide fixtures + one hand-built mixed-generation fixture
      project — committed skipped in 0.3/0.4 runs if convenient, else written test-first
      here.
- [ ] [agent] 1.2 Corpus inventory: run the scanner across the cloned corpus, commit the
      aggregated construct-frequency table to `docs/corpus-inventory.md`. **This table sets
      the build order of Phase 2 transforms.** Test: the aggregation logic gets an
      integrated test on two fixture repos; the corpus numbers themselves are scoreboard,
      not CI.
- [ ] [agent] 1.3 Mapping knowledge base: `maf_migrator/mappings.yaml` — each known AutoGen
      construct → MAF equivalent + status (`auto` / `partial` / `manual` / `unknown`) +
      guide link, sourced from the migration guide. Destination-neutral note field for
      constructs where AG2 is a plausible alternative target. Test: schema validation +
      every construct seen in the guide fixtures has an entry.
- [ ] [agent] 1.4 Report generator: `maf-migrate analyze` renders a human-readable
      migration report (terminal + `--output report.md`): per-construct mapping status,
      counts, effort estimate bands, honest "unknown" section, one-line destination-neutral
      framing (MAF vs AG2). This report is the product's marketing asset — write it for a
      stressed engineer, not a parser. Acceptance tests: golden-file report snapshots for
      two fixture projects.
- [ ] ⛔ GATE 1.5 [IREK] Run `maf-migrate analyze` on 3 corpus repos. Verdict required:
      would *you* trust this report if you owned the repo? Is it lead-magnet quality?
      Record verdict + nits in the log; nits become checklist items.

### Phase 2 — transforms (0.4→MAF first, corpus-frequency order)

- [ ] [agent] 2.1 Codemod infrastructure: LibCST transform base, registry, `apply` runner
      that takes (tree, mappings) → (new tree, applied-changes list, needs-attention list);
      snapshot-test helper that asserts a before/expected_after pair round-trips. Test: one
      trivial no-op transform proves the harness end to end (watch it fail first).
- [ ] [agent] 2.2 Transform: imports + module/class renames (the mechanical layer), driven
      by mappings.yaml. Acceptance tests: the 0.3 guide pairs covering imports — un-skip.
- [ ] [agent] 2.3 Transform: model client configuration (OpenAI/Azure client setup →
      MAF equivalents). Acceptance tests: guide pairs — un-skip.
- [ ] [agent] 2.4 Transform: agent construction (AssistantAgent & friends → MAF agent
      creation). Acceptance tests: guide pairs — un-skip.
- [ ] [agent] 2.5–2.9 Transform batch, **one construct-family per run**, order dictated by
      `docs/corpus-inventory.md` (expected families: tools/function registration, teams /
      group-chat → workflow graph, termination conditions, memory/state, streaming). The
      builder splits/renumbers these in place as the inventory dictates — renumbering is a
      plan edit, note it in the log. Acceptance tests: guide pairs where they exist;
      hand-written pairs (test-first) where the guide is silent.
- [ ] [agent] 2.10 Corpus validity scoreboard: extend `scripts/corpus.py` to run the full
      transform set over each corpus repo and score validity tiers 1–3 (parse / imports
      resolve / type check); commit results to `docs/corpus-scoreboard.md`. This number
      ("N% of constructs across 25 real repos migrate clean") is both our quality bar and
      the launch copy.

### Phase 3 — end-to-end runner

- [ ] [agent] 3.1 `maf-migrate run <path>`: analyze → apply transforms in place (or
      `--diff` for dry-run) → write `MIGRATION-REPORT.md` (what changed, what needs human
      attention, file:line anchors). Acceptance tests: pre-written integrated test on a
      fixture mini-project asserting transformed files + report content.
- [ ] [agent] 3.2 Partial-result robustness: unknown/unmappable constructs never corrupt
      output — untouched code stays byte-identical, needs-attention items get an inline
      `# MAF-MIGRATE: ...` TODO comment + report entry. Test: fixture with deliberately
      unknown constructs.
- [ ] ⛔ GATE 3.3 [IREK] Live run on 2 real corpus repos; eyeball the diffs and the report.
      Pick 1–2 flagship repos for the public case study (and decide whether to approach a
      maintainer about a real migration PR). Verdict in the log.

### Phase 4 — free/pro split, packaging, payments

- [ ] [agent] 4.1 Tier split: free = analyzer + mechanical transforms (2.2); pro = full
      transform set, gated by an offline license key (simple signed-token check — honor
      system is acceptable at this scale, no server). Pro transforms live in a separate
      `maf_migrator_pro` package in this repo, built as its own wheel. Test: integrated
      tests prove free CLI without key runs analyze+basic and clearly advertises what the
      pro run would do; with key, full set runs.
- [ ] [agent] 4.2 OSS-split preparation: define exactly what ships in the public repo
      (everything except `maf_migrator_pro/`), write `scripts/export_public.py` that
      produces the public tree, and draft the public README (the storefront: what it does,
      report screenshot placeholder, pricing pointer). Test: export output contains no pro
      code, passes its own test subset.
- [ ] [agent] 4.3 Landing + pricing copy: `docs/landing.md` (for a fourducks.dev subpage)
      and `docs/pricing.md` — $299 standard / $999 large-or-legacy(0.2) migration, refund
      stance, strictly-async support policy, privacy line ("your code never leaves your
      machine"). Validation tests like attio-sheets' listing tests (required sections
      present).
- [ ] [IREK] 4.4 Accounts: PyPI account (fourducks identity), public GitHub repo
      `maf-migrator` (public twin), payment rail (Stripe payment link or Lemon Squeezy —
      pick one, it delivers the pro wheel + license key as a digital download), landing
      page live on fourducks.dev.
- [ ] ⛔ GATE 4.5 [IREK] Full self-serve dry run as a stranger: find page → pay (test
      mode) → receive wheel+key → run pro migration on a corpus repo. No manual steps by
      us allowed anywhere in the path. Verdict in the log.

### Phase 5 — launch

- [ ] [agent] 5.1 Seeding drafts in `docs/seeding/`: AutoGen GitHub Discussions post, MS
      devblog comment, dev.to article ("We auto-migrated N real AutoGen repos to MAF —
      here's what breaks"), Show HN post — each with the corpus-scoreboard numbers slotted
      in. Validation tests: files exist, contain the scoreboard reference.
- [ ] [IREK] 5.2 Publish: run the public export, push the public repo, `pip` release to
      PyPI, landing page live.
- [ ] [IREK] 5.3 Seed: post the drafts (Discussions first — that's the buyer list), start
      the weekly build-in-public post. Log dates — the kill-criteria clock reads from them.
- [ ] [agent] 5.4 Post-launch instrumentation doc: where the organic-pull numbers come from
      (PyPI download stats, GitHub stars/traffic, payment-rail dashboard), written up in
      `docs/metrics.md` so the day-90 review is mechanical.

## Open questions

- Exact MAF package naming/versioning on PyPI — resolved by 0.2, don't trust memory.
- Legacy 0.2→MAF codemod depth: corpus inventory (1.2) decides whether 0.2 gets real
  transforms in Phase 2 or ships analyzer-only at launch (population is ~6× larger but the
  jump is harder; the $999 tier assumes we eventually handle it).
- AG2 as alternative destination: analyzer stays destination-neutral; whether to ever
  *transform* toward AG2 is a post-launch question driven by inbound demand.
- Payment rail choice (Stripe link vs Lemon Squeezy) — Irek's call at 4.4; Lemon Squeezy
  handles EU VAT which matters for this audience.

## Build log

- 2026-07-18 — Plan written (Irek + Claude planning session). Repo created empty; corpus
  availability verified live (94 unique repos in first 100 code hits for v0.4 imports;
  ~1,584 legacy hits). Next: builder starts at 0.1.
- 2026-07-19 — 0.1 done: pyproject.toml (setuptools.build_meta, src layout), `maf_migrator` package with `maf-migrate` console script, `typer` CLI with `--version`, integrated smoke test (`maf-migrate --version` exits 0 and prints version). pytest 1/1. Next: 0.2 (pin MAF + AutoGen package targets).
- 2026-07-19 — 0.2 done: MAF package identified as `agent-framework-core==1.11.0` (import: `agent_framework`; full meta-package: `agent-framework`; verified against PyPI + github.com/microsoft/agent-framework). AutoGen pins: `autogen-agentchat==0.4.9.3` (v0.4 line), `pyautogen==0.2.35` (legacy v0.2 line). Added as dev extras in pyproject.toml. `docs/targets.md` written with exact versions + PyPI links + gotcha note (module `__version__` attr vs metadata version). `tests/test_package_pins.py` asserts all 3 pins. pytest 4/4. Next: 0.3 (ground-truth fixtures from migration guide).
- 2026-07-19 — 0.3 done: 5 before/after fixture pairs extracted from the live migration guide (learn.microsoft.com/en-us/agent-framework/migration-guide/from-autogen/) into `tests/fixtures/guide/`: model_client_openai, basic_agent_creation, tool_creation, streaming, messages. Each pair has before.py (AutoGen 0.4) + expected_after.py (MAF). SOURCES.md links each case to its guide section. Validity test (`tests/test_guide_fixtures.py`, 6 tests) asserts dir exists, ≥5 cases, both files present, both sides parse. pytest 10/10. Next: 0.4 (corpus manifest + runner).
- 2026-07-19 — 0.4 done: `corpus.yaml` created with 25 public AutoGen repos (8 v0.4, 16 v0.2/mixed) covering the candidate list from the 2026-07-18 search (magentic-ui, testzeus-hercules, agentops, autogen, ag2, etc.). `scripts/corpus.py` written with `--dry-run` mode (validates schema, no network). `pyyaml>=6` added to dev extras. `tests/test_corpus.py` with 8 schema+runner tests. pytest 18/18. Caveat: commit SHAs are stub placeholders (valid format, not real commits) — re-pin at task 1.2 when running the actual corpus script. Next: 1.1 (usage scanner).
