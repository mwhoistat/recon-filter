<div align="center">
  <h1>Recon-Filter Professional Enterprise Engine</h1>
  <p>A high-performance, structurally intelligent stream processor designed for precise mapping over unstructured lines, JSON Arrays, massive CSV tables, and PDF targets.</p>

  [![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)]()
  [![Release](https://img.shields.io/badge/release-v1.1.0-green.svg)]()
  [![License](https://img.shields.io/badge/license-MIT-blue.svg)]()
</div>

## Native Installation

Recon-Filter V1.0.1 is cleanly distributed as a compliant Python CLI structure. It is strictly optimized to support global installation without forcing users into virtual environments.

### Arch Linux (via makepkg / AUR)
For Arch users, we provide a `PKGBUILD` that bundles the CLI natively directly into `/usr/bin/recon-filter`.
```bash
git clone https://github.com/mwhoistat/recon-filter.git
cd recon-filter
makepkg -si
```

### Global Install (via pip)
Install globally to ensure the CLI is available directly on your terminal.
```bash
pip install recon-filter
# or from source:
pip install .
```

*(Optional)* Minimal install bypassing heavyweight packages (PDFs, PSUtil Monitoring):
```bash
pip install recon-filter --no-deps
```
Or to install with optional feature groups:
```bash
pip install .[pdf,monitoring]
```

### Verification
```bash
recon-filter self-test
# > All Core Subsystems Operational. The Pipeline is ready for Distribution.

recon-filter --version
# > recon-filter version: 1.0.2
```

### Running from ~/Tools/recon-filter
If installing strictly from an external tools directory mapped globally without virtual environments:
```bash
git clone https://github.com/mwhoistat/recon-filter.git ~/Tools/recon-filter
cd ~/Tools/recon-filter

# Install directly bypassing environments safely
pip install . --user
# Ensure ~/.local/bin is structurally in your $PATH
```

## Arch Linux Compatibility Testing

**Tested on:**
- Arch Linux (Rolling Release)
- Latest Linux Kernel
- Python System Version natively mapping bounds

### Troubleshooting Arch Linux
- **If pip refuses global install**: Use `makepkg -si` via the bundled `PKGBUILD`, or deploy using `pipx install recon-filter`. Arch strictly enforces PEP 668 managed boundaries.
- **If `recon-filter` command is not found**: Ensure `~/.local/bin` is added to your `$PATH`. 
- **If conflicting permission errors emerge**: Confirm `.pkg` execution via AUR bindings instead of running pip globally via `sudo`.

## Core Enhancements (v1.1.0)

### Smart Filtering Engine (`--smart-mode`)
Activate intelligent context-aware filtering with a single flag:
```bash
recon-filter filter ./targets.txt --smart-mode
```
- **Priority Keyword Scoring**: High-value keywords (`apikey=10`, `secret=9`, `token=8`) are weighted above generic terms
- **Fuzzy Matching**: Catches near-miss keywords using `difflib.SequenceMatcher` (e.g., `pasword` matches `password`)
- **URL Structure Bonuses**: URLs with query parameters automatically score higher
- **Chain Filtering**: keyword → URL → parameter → path cluster pipeline

Custom priority keywords:
```bash
recon-filter filter ./data --smart-mode --priority-keyword "jwt" --priority-keyword "bearer"
```

Adjust fuzzy sensitivity:
```bash
recon-filter filter ./data --smart-mode --fuzzy-threshold 0.8
```

### Updating via Package Manager
```bash
# Arch Linux / CachyOS / Manjaro
yay -Syu recon-filter
# or local PKGBUILD
cd ~/Tools/recon-filter && makepkg -si

# Debian / Ubuntu
pip install --upgrade recon-filter

# Check for updates
recon-filter update --check
```

### Optional Dependencies & Running Without `psutil`
Recon-Filter defaults to using Python Standard Libraries. It cleanly handles the absence of heavyweight monitoring dependencies natively:
- **`psutil`** (Performance Limits): If absent, the engine bypasses `MemoryError` tracking natively, gracefully executing structural filtering without crashing.
- **`pypdf`** (PDF parsing): Optional handler execution.
Install with: `pip install recon-filter[monitoring,pdf]`

### Built-in Default Keyword Behavior
When executing without strict `--regex` or `-k keywords.txt` logic, Recon-Filter instantly routes against an internal suite of 25+ standard Bug Bounty keys (e.g., `api`, `token`, `password`, `config`). To suppress this, use `--no-default-keyword`.

### Smart Detection & Output Diagnostics
The pipeline accurately compares structural `mimetypes` alerting outputs against conflicting mappings. Resulting text files automatically render standard diagnostic footers natively outlining matches tracked explicitly (opt-out utilizing `--no-footer`).

## Quick Start
Run the pipeline pointing it natively towards logs or recon data. It will automatically back them up, parse them, extract exact hits, and safely replace them locally.
```bash
recon-filter ./data --recursive --regex "^CRITICAL|^FATAL" --generate-hash-report
```

## The "V1.0.0" Engineering Philosophy

Recon-Filter differs from `grep` or standard parsing scripts precisely because it respects the **structure** of the payload natively while providing extreme execution safeguards entirely. 

### Format Preservation
When mapping a JSON payload, removing arbitrary strings causes downstream API breaks entirely. Recon-Filter dynamically executes iterative parsing (`ijson`), isolating targeted structs recursively, generating cleanly valid `.json` arrays representing exclusively matched signatures securely. It repeats this pattern for CSV and Text cleanly.

### Ultra-Performance Constraints
Digesting a 10GB target traditionally explodes the python interpreter raising `MemoryError`. Recon-Filter monitors CPU counts and Local RAM bindings natively using `psutil`. It adapts threading pools mapped at < 70% capacity preventing system crash overrides. All writers are strictly Iterative; objects never accumulate memory streams natively.

### Architecture Security
All targets process within strict `engine/handlers`. Writing logic routes purely into an `.tmp` atomic payload. If the system drops connection or a Regex DoS limit trips halting the target natively, the canonical binaries are never overwritten corruptly preventing fragmented destructions natively.

All inputs check Path Traversal constraints securely blocking mapped injection routing to `/etc/passwd`.

## Extended Functionality

### Generating Statistics
A powerful mapping tool generating output diagnostics reflecting extraction ratios completely.
```bash
recon-filter ./logs -k keywords.txt --export-stats audit.json
recon-filter stats audit.json
```

### Advanced URL Analysis & Clustering
Integrate natively into Bug Bounty payloads generating active parameter dictionaries mapped securely from raw data hits.
```bash
recon-filter ./data --strict-url --extract-params --param-report
```
By utilizing clustering flags, targets resolve elegantly into respective depth directories splitting bulk data efficiently:
```bash
recon-filter ./endpoints.txt --group-by-extension --group-by-depth --depth-limit 3
```

### Safe Caching
Averts redundant cycles strictly bypassing targeted extractions seamlessly using internal SHA256 limits securely.
```bash
recon-filter ./logs -r "token=" --enable-cache
```

### Measuring Bounds
Determine your local systems performance constraints mapping synthetic load extractions dynamically natively.
```bash
recon-filter benchmark --size 500
# Expected Throughput: 40,000+ L/s 
```

## Security Contributions

Contributions are completely encouraged protecting enterprise IO constraints natively.
Please run `recon-filter self-test` validating downstream components before pulling cleanly mapped code limits. The engine defaults internal logging mapping `logger.warning` silencing verbose clutter for professional deployments.

---
### License
Licensed under the strict MIT binding definition perfectly mapping limits safely securely.
