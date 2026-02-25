# V2.0.0 - Risk Intelligence Engine & Major Refactor

## Breaking Changes
- `--strict-performance`, `--enable-cache`, `--adaptive-mode` flags removed (auto-managed)
- `SmartScorer` class replaced by `IntelligenceEngine`
- Dead legacy modules (`cli.py`, `core.py`, `filters.py`) removed

## New Features
- **Risk Intelligence Engine**: Extension risk scoring, parameter sensitivity analysis, path depth evaluation, endpoint heuristics (admin/API/backup/dev detection)
- **Risk Tagging**: Output lines tagged `[HIGH]`, `[MEDIUM]`, `[LOW]` based on computed risk score
- **`--intelligent`**: Activate full risk scoring and endpoint heuristics
- **`--risk-threshold N`**: Filter output by minimum risk score
- **`--sort-by-risk`**: Sort output by risk score (highest first)
- **Bilingual Interface**: English and Bahasa Indonesia language selection at startup
- **AUR Publishing**: Valid PKGBUILD + .SRCINFO + step-by-step AUR push guide
- **Distro-Aware Update**: Auto-detects Linux distribution for upgrade instructions

## Improvements
- CLI flags simplified and help text rewritten
- `validate` command fixed to use proper `RuleCompiler` module
- Version check suppressed by default (only on `--force-update-check`)
- `doctor` command enhanced with dependency and environment checks

# V1.1.0 - Smart Filtering Engine & Full Code Audit
- **Smart Filtering Engine**: Context-aware scoring with priority keyword weights, fuzzy matching via `difflib`, and URL structure bonuses.
- **`--smart-mode`**: Single flag activating all intelligent filtering features at once.
- **`--priority-keyword`**: Boost specific keywords to maximum scoring weight (repeatable flag).
- **`--fuzzy-threshold`**: Configure similarity threshold for fuzzy keyword matching (default: 0.75).
- **Multi-Layer Chain Filtering**: keyword → URL → parameter → path cluster pipeline.
- **Update Mechanism**: Distro-specific upgrade instructions with automatic `/etc/os-release` detection (Arch/Debian/Fedora/openSUSE).
- **Full Code Audit**: Fixed stale `cli/__init__.py` imports, hardcoded version strings, dead code references, and legacy module imports.
- **Suppressed Startup Update Checks**: Version checks now only run on `--force-update-check` or `recon-filter update --check`.
- **PKGBUILD**: Updated to v1.1.0 for yay/pacman compatibility.

# V1.0.2 - Core Stability & Advanced Deduplication Update
- **Fixed `psutil` import crash**: Handled offline optional mapping gracefully globally.
- **Made performance monitoring optional**: Refactored concurrency bindings dynamically resolving CPU constraints without `psutil`.
- **Added built-in default keywords**: Auto-loads standard Bug Bounty targeting definitions when explicit keys aren't provided.
- **Added `doctor` command**: Introduces diagnostic checks analyzing RAM allocations, core counts, and installation integrity instantly.
- **Added advanced deduplication scoping**: Added `--dedupe-scope` mapping natively to `line`, `normalized`, or `url-normalized` matching behaviors.
- **Output Summary Footer**: Appends clean structural execution analytics directly onto the filtered file.
- **Improved Installation Robustness**: Cleanly executes offline inside `~/Tools/recon-filter` boundaries globally via native `pipx` or `pip .`.

# V1.0.1 - Arch Linux Native Support Integration- **Improved Arch Linux Native Installation**: Global CLI availability without requiring a virtual environment.
- **Added PKGBUILD**: Delivered standard PKGBUILD definition for seamless `makepkg` execution.
- **Dependency Refinement**: Segmented heavyweight dependencies (`psutil`, `pypdf`) into optional groups (`monitoring`, `pdf`), maximizing compatibility and enabling minimal installs.
- **Installation Stability Improvements**: Handled dependency absence gracefully gracefully natively parsing environments without crashing.

# V1.0.0 - Initial Stable Release

## High-Performance Streaming Architecture
- **Complete Re-write to Iterative Generators**: Eradicated `json.load()` and full file reads. Integrated `ijson` for true O(1) memory JSON Arrays/Object traversals internally.
- **Atomic Writer Bindings (`.tmp`)**: Destroying a running thread/process (SIGINT) cleanly unlinks the fragment securely leaving target binaries unharmed entirely natively.
- **Adaptive Native Concurrency**: Processes system Core-counts tying pool logic to max 70% CPU thresholds avoiding system lock-ups entirely. Enforces auto-streaming natively against huge file dimensions (measured >10% of local RAM).

## Format Extractions
- Full native format extraction and valid synthetic Output mappings for `.json`, `.csv`, `.txt`, `.log`, and `.pdf` entities. Natively maps CSV strict headers automatically.

## Intelligent Cache Management
- Calculates internal Checksum `SHA-256` footprint validations via `.recon_cache` cleanly bypassing untouched identical targets transparently via `--enable-cache`.

## Enterprise Validation Bounds
- `psutil` integration triggering exact Memory Limit thresholds via background `--memory-limit` checks effectively clearing System arrays (GC) preserving the OS kernel environments exactly.
- Implemented `/logs/audit.log` securely writing matching payloads internally (SHA256).

## User Diagnostics and Interactivity
- Native benchmarking subcommands measuring true Lines/sec hardware throughput dynamically: `recon-filter benchmark`.
- Native system diagnostic reports: `recon-filter doctor`.
- Interactive prompts for missing argument routing globally.
- Clean `pyproject.toml` distribution with GitHub update checks internally.
