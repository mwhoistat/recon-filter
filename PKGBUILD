# Maintainer: krvst
pkgname=recon-filter
pkgver=1.1.0
pkgrel=1
pkgdesc="Professional Stream Processing Engine for System Logs & Recon Data"
arch=('any')
url="https://github.com/mwhoistat/recon-filter"
license=('MIT')
depends=(
    'python>=3.9'
    'python-typer'
    'python-rich'
    'python-yaml'
    'python-questionary'
    'python-charset-normalizer'
    'python-ijson'
)
optdepends=(
    'python-pypdf: Advanced PDF processing support'
    'python-psutil: Performance monitoring limits'
)
makedepends=('python-build' 'python-installer' 'python-wheel' 'python-setuptools')
source=("$pkgname-$pkgver.tar.gz::https://github.com/mwhoistat/recon-filter/archive/refs/tags/v$pkgver.tar.gz")
sha256sums=('SKIP')

build() {
    export PIP_CONFIG_FILE=/dev/null
    cd "$pkgname-$pkgver"
    python -m build --wheel --no-isolation
}

package() {
    cd "$pkgname-$pkgver"
    python -m installer --destdir="$pkgdir" dist/*.whl
}
