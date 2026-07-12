# Versioning Policy

The TruAgents SDK ships from a shared repository but each language package
carries its own version. This document explains the guarantees you can rely on
and the guarantees you cannot rely on yet.

## The `0.x` phase — where we are today

The Python SDK ships at `0.1.0`. Semver treats the `0.x` range as pre-stable,
and we treat it the same way.

- **Minor bumps (`0.1.0` -> `0.2.0`) may introduce breaking changes.** They will
  not do so silently.
- **Patch bumps (`0.1.0` -> `0.1.1`) will not break.** Only bug fixes,
  documentation updates, and additive changes safe under semver.
- Every breaking change ships with:
  - A CHANGELOG entry describing the migration.
  - A GitHub Release note with the same content.
  - Where feasible, a `DeprecationWarning` in the previous minor version so
    partners get one release of runway.
- We do **not** backport fixes to older minors while at `0.x`. Upgrade to the
  latest minor to get security and behavioural fixes.

## Promotion to `1.0.0`

We will publish `1.0.0` once **either** of the following holds:

- **Field usage**: three external partners have run a `0.x` release in
  production for 30 consecutive days without a breaking change against them, OR
- **Internal stability**: two consecutive minor releases have shipped with no
  breaking changes.

Whichever condition fires last is the promotion trigger.

## The `1.0.0+` phase — what changes

Once `1.0.0` ships, semver becomes strict:

- **No breaking changes in minor releases.** Breaking changes require a major
  bump.
- **Deprecation windows are at least 3 months** from the introduction of a
  `DeprecationWarning` to the removal of the API surface. We may revisit the
  length based on partner adoption feedback.
- **LTS coverage: the latest two majors.** Security fixes land on both; feature
  work only on the current major.

## API-version compatibility

The SDK version tracks the SDK's own contract. It does **not** encode the
TruAgents API version. When the API introduces its own versioning story, we
will publish a compatibility matrix here.

## Release channels

- **Stable** — `pip install truagents` picks the latest published release.
- **Pre-release** — pre-releases are tagged as `sdk-python-vX.Y.Z-rcN` and are
  installable via `pip install truagents==X.Y.ZrcN`.

## Support policy (pre-`1.0.0`)

While at `0.x`, only the latest minor receives security or behavioural fixes.
Once at `1.0.0`, we will publish an explicit LTS window and coverage table
alongside the release.
