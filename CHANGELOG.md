# V1.0.1 - Arch Linux Native Support Integration
- **Improved Arch Linux Native Installation**: Global CLI availability without requiring a virtual environment.
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
