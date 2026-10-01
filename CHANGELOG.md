# Changelog

## [Unreleased]

### Added
- Bauer v0.1.0 security-audit skill from canonical revision `213f085dcd316923aab78324c8ea6a3e58713c34`, including all four helpers, five references, license and third-party notice.
- Ten-skill inventory, Bauer pinned-source byte-parity checks and local helper CLI checks; independent provenance in `SOURCE.json` preserves the original collection checksums.

### Known limitations
- Bauer is an agent-driven evidence workflow, not an autonomous scanner or security certification. No live OWASP, OSV or TypeSafe/Jev queries or Bauer installation were exercised. Its OSV helper fails closed on RFC3339 leap-second timestamps.
- Hannah’s normal community-source installation remains scanner-blocked; no override or trust bypass was applied.

## [0.1.0] — 2026-09-29

### Added
- Initial Hermes skill tap with nine Lux Solari ports and their references, scripts, curricula, licenses, and 53 visual reference PNGs.
- Hannah's bundled Python recommendation engine; offline helper and packaging checks.
- Whiting commit-message and default-branch push guards, semantic-version bump suggestions, and changelog-first release discipline.
- Tag-driven GitHub Releases with version/changelog validation, tests before publishing, a full-repository source archive, and SHA-256 checksums. Manual dispatch can republish an existing tag.

### Verified
- Eight default skill installs were checked in disposable Hermes homes with 184 files matching the checkout by checksum.
- Packaging and helper tests run locally and in GitHub Actions. They do not establish live image-generation, teaching, or rendered-design parity.

### Known limitations
- Hannah's community-source installation remains blocked by a `caution` scan verdict. No scan override or trust bypass was applied.
- These are on-demand skills, not native lifecycle hooks or a separately registered historical command suite.
- Tap collection versions are independent of retained upstream skill and engine versions.
