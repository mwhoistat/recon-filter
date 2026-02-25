<div align="center">
  <h1>Recon-Filter — Risk Intelligence Filtering Engine</h1>
  <p>High-performance stream processor for extracting URLs, credentials, and high-risk targets from massive datasets with risk scoring and endpoint heuristics.</p>

  [![Python Version](https://img.shields.io/badge/python-3.9+-blue.svg)]()
  [![Release](https://img.shields.io/badge/release-v2.0.0-green.svg)]()
  [![License](https://img.shields.io/badge/license-MIT-blue.svg)]()
  [![AUR](https://img.shields.io/badge/AUR-recon--filter-blue.svg)]()
</div>

## Installation

### Arch Linux (AUR)
```bash
yay -S recon-filter
```

### From Source (All Distributions)
```bash
git clone https://github.com/mwhoistat/recon-filter.git
cd recon-filter
pip install .
```

### Via pipx (Recommended)
```bash
pipx install recon-filter
```

### Local Build (Arch)
```bash
cd ~/Tools/recon-filter
makepkg -si
```

## Quick Start
```bash
# Basic filtering
recon-filter filter ./targets.txt --regex "admin|password"

# Intelligent risk analysis
recon-filter filter ./urls.txt --intelligent --sort-by-risk

# Risk threshold filtering (only HIGH risk)
recon-filter filter ./data.txt --intelligent --risk-threshold 15

# Fuzzy matching with priority keywords
recon-filter filter ./logs.txt --smart-mode --priority-keyword "jwt" --priority-keyword "bearer"

# Interactive mode with language selection
recon-filter
```

## Risk Intelligence Engine (`--intelligent`)

The intelligence engine scores each line based on multiple risk factors:

| Factor | Example | Score Impact |
|--------|---------|-------------|
| Keyword weight | `apikey`, `secret`, `password` | 8-10 |
| Extension risk | `.env`, `.bak`, `.sql`, `.php` | 7-10 |
| Parameter sensitivity | `?password=`, `?token=`, `?redirect=` | 7-10 |
| Endpoint heuristics | `/admin`, `/api/v1/`, `/wp-admin` | 3-6 |
| Path depth | `/a/b/c/d/secret.php` | 1-4 |

### Risk Tags
- `[HIGH]` — Score ≥ 15 (critical findings)
- `[MEDIUM]` — Score 8-14 (notable targets)
- `[LOW]` — Score < 8 (low priority)

### Example Output
```
[HIGH] [score:24] https://target.com/admin/config.php?password=test&token=abc123
[HIGH] [score:19] https://target.com/api/v1/users?apikey=sk_live_xxx
[MEDIUM] [score:12] https://target.com/backup/db.sql.bak
[LOW] [score:5] https://target.com/about.html
```

## Bilingual Interface

Running `recon-filter` without arguments opens the interactive menu:

**English:**
```
Recon Filter v2.0.0

Select Language / Pilih Bahasa:
> English

Select an option:
> Filter File
  Intelligent Analysis
  URL Analysis
  Settings
  Help
  Exit
```

**Bahasa Indonesia:**
```
Recon Filter v2.0.0

Select Language / Pilih Bahasa:
> Bahasa Indonesia

Pilih opsi:
> Filter File
  Analisis Cerdas
  Analisis URL
  Pengaturan
  Bantuan
  Keluar
```

## Updating

```bash
# Check for updates
recon-filter update --check

# Arch Linux
yay -Syu recon-filter

# pip / pipx
pip install --upgrade recon-filter
pipx upgrade recon-filter
```

For AUR publishing instructions, see [AUR_PUBLISH.md](AUR_PUBLISH.md).

## CLI Reference

### Core Commands
| Command | Description |
|---------|-------------|
| `filter` | Process and filter files |
| `stats` | Generate statistics from data |
| `validate` | Test regex patterns and keyword files |
| `doctor` | System diagnostics and dependency check |
| `update` | Show upgrade instructions for your distro |
| `benchmark` | Performance load testing |
| `config` | Initialize configuration file |

### Intelligence Flags
| Flag | Description |
|------|-------------|
| `--intelligent` | Enable risk scoring and endpoint heuristics |
| `--smart-mode` | Enable fuzzy matching and keyword scoring |
| `--risk-threshold N` | Minimum risk score to include (default: 0) |
| `--sort-by-risk` | Sort output by risk score descending |
| `--priority-keyword KW` | Boost keyword to max weight (repeatable) |
| `--fuzzy-threshold N` | Fuzzy match sensitivity 0.0-1.0 (default: 0.75) |

### Filter Flags
| Flag | Description |
|------|-------------|
| `--regex PATTERN` | Regex matching pattern |
| `-k FILE` | Keyword file path |
| `--extract-params` | Extract URL parameter distributions |
| `--group-by-extension` | Cluster output by file extension |
| `--group-by-depth` | Cluster output by URL depth |
| `--dedupe-scope` | Deduplication mode: `line`, `normalized`, `url-normalized` |
| `--no-default-keyword` | Disable default recon keyword dictionary |

## Optional Dependencies
```bash
pip install recon-filter[monitoring]  # psutil for RAM tracking
pip install recon-filter[pdf]         # pypdf for PDF processing
```

## License
MIT License — see [LICENSE](LICENSE)
