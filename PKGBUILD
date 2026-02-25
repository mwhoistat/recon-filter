# Maintainer: krvst
pkgname=recon-filter
pkgver=2.0.0
pkgrel=1
pkgdesc="Risk Intelligence Filtering Engine for System Logs & Recon Data"
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
    'python-pypdf: PDF processing support'
    'python-psutil: Performance monitoring'
)
makedepends=('python-build' 'python-installer' 'python-wheel' 'python-setuptools')
source=("$pkgname-$pkgver.tar.gz::https://github.com/mwhoistat/$pkgname/archive/refs/tags/v$pkgver.tar.gz")
sha256sums=('SKIP')

build() {
    cd "$pkgname-$pkgver"
    python -m build --wheel --no-isolation
}

package() {
    cd "$pkgname-$pkgver"
    python -m installer --destdir="$pkgdir" dist/*.whl
    install -Dm644 LICENSE "$pkgdir/usr/share/licenses/$pkgname/LICENSE"
}
