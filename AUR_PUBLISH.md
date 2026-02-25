# Publishing recon-filter to AUR

## Prerequisites
- AUR account at https://aur.archlinux.org
- SSH key uploaded to your AUR account
- `git`, `makepkg` installed

## Step 1: Create GitHub Release Tag
```bash
cd ~/Tools/recon-filter
git add -A
git commit -m "release: v2.0.0"
git tag v2.0.0
git push origin main --tags
```

## Step 2: Clone AUR Repository
```bash
# First time only — clone empty AUR package repo
git clone ssh://aur@aur.archlinux.org/recon-filter.git /tmp/aur-recon-filter
```

## Step 3: Copy Package Files
```bash
cp ~/Tools/recon-filter/PKGBUILD /tmp/aur-recon-filter/
cp ~/Tools/recon-filter/.SRCINFO /tmp/aur-recon-filter/
```

## Step 4: Regenerate .SRCINFO (Recommended)
```bash
cd /tmp/aur-recon-filter
makepkg --printsrcinfo > .SRCINFO
```

## Step 5: Commit and Push to AUR
```bash
cd /tmp/aur-recon-filter
git add PKGBUILD .SRCINFO
git commit -m "Update recon-filter to v2.0.0"
git push origin master
```

## Step 6: Verify
```bash
# Search AUR for the package
yay -Ss recon-filter

# Install via yay
yay -S recon-filter

# Update when new version is available
yay -Syu recon-filter
```

## Updating to a New Version
1. Update `pkgver` in `PKGBUILD`
2. Update `sha256sums` (or keep `SKIP` during development)
3. Run `makepkg --printsrcinfo > .SRCINFO`
4. Commit and push to AUR repo
5. Create matching GitHub release tag

## Debian PPA (Future)
For Debian/Ubuntu distribution, create a PPA at https://launchpad.net:
1. Create a `debian/` directory with `control`, `rules`, `changelog` files
2. Build with `debuild -S`
3. Upload with `dput ppa:krvst/recon-filter *.changes`

## Fedora COPR (Future)
For Fedora distribution via COPR (https://copr.fedorainfracloud.org):
1. Create a `.spec` file for RPM packaging
2. Upload to COPR project
3. Users install with `dnf copr enable krvst/recon-filter && dnf install recon-filter`
