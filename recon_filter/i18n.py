"""
Internationalization (i18n) system for recon-filter.
Simple dictionary-based translations supporting English and Bahasa Indonesia.
"""
from typing import Dict

_current_lang = "en"

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # Menu
    "select_language": {
        "en": "Select Language:",
        "id": "Pilih Bahasa:",
    },
    "menu_filter": {
        "en": "Filter File",
        "id": "Filter File",
    },
    "menu_intelligent": {
        "en": "Intelligent Analysis",
        "id": "Analisis Cerdas",
    },
    "menu_url": {
        "en": "URL Analysis",
        "id": "Analisis URL",
    },
    "menu_settings": {
        "en": "Settings",
        "id": "Pengaturan",
    },
    "menu_help": {
        "en": "Help",
        "id": "Bantuan",
    },
    "menu_exit": {
        "en": "Exit",
        "id": "Keluar",
    },
    "menu_select": {
        "en": "Select an option:",
        "id": "Pilih opsi:",
    },
    # Hints and messages
    "hint_url": {
        "en": "URL Analysis uses the filter engine with --extract-params.",
        "id": "Analisis URL menggunakan mesin filter dengan --extract-params.",
    },
    "hint_intelligent": {
        "en": "Intelligent mode activates risk scoring and endpoint heuristics.",
        "id": "Mode cerdas mengaktifkan penilaian risiko dan heuristik endpoint.",
    },
    "doctor_complete": {
        "en": "Diagnostic completed transparently.",
        "id": "Diagnostik selesai dengan transparan.",
    },
    "update_current": {
        "en": "Current Local Version:",
        "id": "Versi Lokal Saat Ini:",
    },
    "update_detected": {
        "en": "Detected Distribution:",
        "id": "Distribusi Terdeteksi:",
    },
    "risk_high": {
        "en": "HIGH RISK",
        "id": "RISIKO TINGGI",
    },
    "risk_medium": {
        "en": "MEDIUM RISK",
        "id": "RISIKO SEDANG",
    },
    "risk_low": {
        "en": "LOW RISK",
        "id": "RISIKO RENDAH",
    },
}


def set_language(lang: str):
    """Set the current language globally."""
    global _current_lang
    if lang in ("en", "id"):
        _current_lang = lang


def get_language() -> str:
    """Get the current language code."""
    return _current_lang


def t(key: str) -> str:
    """Translate a key to the current language. Falls back to English."""
    entry = TRANSLATIONS.get(key, {})
    return entry.get(_current_lang, entry.get("en", key))
