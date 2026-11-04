"""
Bright Tech International - Lead Intelligence Dashboard
Design system: "Precision Enterprise SaaS" (Plus Jakarta Sans + Inter)

THEME: sirf neeche ACTIVE_THEME ka naam badlo (ya PALETTES mein hex colors edit karo)
aur poora dashboard (buttons, chips, bars, badges, shadows, rings) automatically
naye colors mein change ho jayega.

Requires: streamlit >= 1.40
"""
import os
import re
import csv
import time
import hashlib
from datetime import datetime
from html import escape as esc

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

# Import qualification and discovery engine functions
from app import (
    analyze_prospect,
    fetch_live_website,
    generate_infinite_target_candidates,
    get_already_processed_domains,
)

st.set_page_config(
    page_title="Bright Tech - Lead Intelligence Engine",
    page_icon="⚜️",
    layout="wide",
    initial_sidebar_state="expanded",
)

CSV_FILE = "bright_tech_qualified_leads.csv"
EXCEL_FILE = "Bright_Tech_Clean_Leads.xlsx"

# =====================================================================
#  1. THEME  (yahin se colors change karo)
# =====================================================================
ACTIVE_THEME = "rose"   # default theme (neeche PALETTES mein jo naam hai wahi likho)
THEME_SWITCHER = True     # True = sidebar ke bottom mein live theme dropdown dikhega

PALETTES = {
    # primary = buttons/links/selection, secondary = accent chips/charts, success = positive status
    "cobalt":   {"primary": "#2563EB", "secondary": "#6366F1", "success": "#10B981"},
    "emerald":  {"primary": "#059669", "secondary": "#0D9488", "success": "#16A34A"},
    "violet":   {"primary": "#7C3AED", "secondary": "#DB2777", "success": "#10B981"},
    "rose":     {"primary": "#E11D48", "secondary": "#F97316", "success": "#10B981"},
    "midnight": {"primary": "#0F172A", "secondary": "#475569", "success": "#10B981"},
    "ocean":    {"primary": "#0284C7", "secondary": "#6366F1", "success": "#10B981"},
    "teal":     {"primary": "#0D9488", "secondary": "#0284C7", "success": "#16A34A"},
    "amber":    {"primary": "#D97706", "secondary": "#7C3AED", "success": "#10B981"},
    "graphite": {"primary": "#334155", "secondary": "#6366F1", "success": "#10B981"},
    # ---- NAYI THEME ADD KARNI HO? bas ek line aur copy karo:
    # "mytheme": {"primary": "#HEX", "secondary": "#HEX", "success": "#HEX"},
    # phir ACTIVE_THEME = "mytheme" kar do (ya sidebar dropdown se select karo).
}

# Neutral slate foundation from DESIGN.md (palette ke andar override bhi kar sakte ho)
NEUTRALS = {
    "canvas": "#F8FAFC",
    "muted": "#F1F5F9",
    "surface": "#FFFFFF",
    "border": "#E2E8F0",
    "border-strong": "#CBD5E1",
    "text": "#0F172A",
    "text-2": "#475569",
    "text-3": "#94A3B8",
    "danger": "#DC2626",
    "warning": "#D97706",
    "info": "#0891B2",
}

# Branding / copy
BRAND = {
    "name": "BrightTech",
    "sub": "INTERNATIONAL",
    "tier": "PRO",
    "footer_name": "Built by Sehar Tahir - Team Lead",
    "footer_role": "Full Stack Developer | GHL CRM Automation Specialist",
}
TELEMETRY = {
    "Engine": "v2.4-active",
    "Coverage": "UK / US Only",
    "Standard": "Strict GDPR",
}
PAGE_SIZE = 10


def _rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def mix(c1, c2, w):
    """Blend c1 with c2 (w = share of c2)."""
    a, b = _rgb(c1), _rgb(c2)
    return "#%02x%02x%02x" % tuple(round(a[i] * (1 - w) + b[i] * w) for i in range(3))


def rgba(c, a):
    r, g, b = _rgb(c)
    return f"rgba({r},{g},{b},{a})"


def build_theme(name):
    p = {**NEUTRALS, **PALETTES[name]}
    prim, sec, suc, dan = p["primary"], p["secondary"], p["success"], p["danger"]
    t = {
        "canvas": p["canvas"], "muted": p["muted"], "surface": p["surface"],
        "border": p["border"], "border-strong": p["border-strong"],
        "text": p["text"], "text-2": p["text-2"], "text-3": p["text-3"],
        "primary": prim,
        "primary-hover": mix(prim, "#000000", 0.12),
        "primary-active": mix(prim, "#000000", 0.26),
        "primary-soft": mix(prim, "#FFFFFF", 0.92),
        "primary-soft-2": mix(prim, "#FFFFFF", 0.78),
        "primary-mid": mix(prim, "#FFFFFF", 0.5),
        "primary-ring": rgba(prim, 0.12),
        "primary-row": rgba(prim, 0.05),
        "accent-bg": mix(sec, "#FFFFFF", 0.93),
        "accent-text": mix(sec, "#000000", 0.3),
        "accent-border": mix(sec, "#FFFFFF", 0.72),
        "success": suc,
        "success-bg": mix(suc, "#FFFFFF", 0.92),
        "success-text": mix(suc, "#000000", 0.58),
        "success-border": mix(suc, "#FFFFFF", 0.65),
        "success-strong": mix(suc, "#000000", 0.25),
        "danger": dan,
        "danger-bg": mix(dan, "#FFFFFF", 0.94),
        "danger-border": mix(dan, "#FFFFFF", 0.82),
        "shadow-1": "0 1px 2px 0 rgba(15,23,42,.04), 0 1px 3px 0 rgba(15,23,42,.03)",
        "shadow-2": "0 4px 6px -1px rgba(15,23,42,.05), 0 2px 4px -2px rgba(15,23,42,.05)",
        "shadow-3": "0 20px 25px -5px rgba(15,23,42,.08), 0 8px 10px -6px rgba(15,23,42,.04)",
    }
    return t, p


THEME_NAME = st.session_state.get("theme", ACTIVE_THEME)
if THEME_NAME not in PALETTES:
    THEME_NAME = ACTIVE_THEME
THEME, BASE = build_theme(THEME_NAME)

# =====================================================================
#  2. ICONS + SMALL HELPERS
# =====================================================================
ICONS = {
    "network": '<rect x="16" y="16" width="6" height="6" rx="1"/><rect x="2" y="16" width="6" height="6" rx="1"/><rect x="9" y="2" width="6" height="6" rx="1"/><path d="M5 16v-3a1 1 0 0 1 1-1h12a1 1 0 0 1 1 1v3"/><path d="M12 12V8"/>',
    "grid": '<rect width="7" height="9" x="3" y="3" rx="1"/><rect width="7" height="5" x="14" y="3" rx="1"/><rect width="7" height="9" x="14" y="12" rx="1"/><rect width="7" height="5" x="3" y="16" rx="1"/>',
    "sliders": '<line x1="21" x2="14" y1="4" y2="4"/><line x1="10" x2="3" y1="4" y2="4"/><line x1="21" x2="12" y1="12" y2="12"/><line x1="8" x2="3" y1="12" y2="12"/><line x1="21" x2="16" y1="20" y2="20"/><line x1="12" x2="3" y1="20" y2="20"/><line x1="14" x2="14" y1="2" y2="6"/><line x1="8" x2="8" y1="10" y2="14"/><line x1="16" x2="16" y1="18" y2="22"/>',
    "check-circle": '<circle cx="12" cy="12" r="10"/><path d="m9 12 2 2 4-4"/>',
    "map-pin": '<path d="M20 10c0 6-8 12-8 12s-8-6-8-12a8 8 0 0 1 16 0Z"/><circle cx="12" cy="10" r="3"/>',
    "code": '<polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/>',
    "external": '<path d="M15 3h6v6"/><path d="M10 14 21 3"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/>',
    "file": '<path d="M15 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7Z"/><path d="M14 2v4a2 2 0 0 0 2 2h4"/><path d="M10 9H8"/><path d="M16 13H8"/><path d="M16 17H8"/>',
    "table": '<rect width="18" height="18" x="3" y="3" rx="2"/><path d="M3 9h18"/><path d="M9 21V9"/>',
    "refresh": '<path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/><path d="M21 3v5h-5"/>',
    "scan": '<path d="M3 7V5a2 2 0 0 1 2-2h2"/><path d="M17 3h2a2 2 0 0 1 2 2v2"/><path d="M21 17v2a2 2 0 0 1-2 2h-2"/><path d="M7 21H5a2 2 0 0 1-2-2v-2"/><circle cx="12" cy="12" r="3"/><path d="m16 16-1.9-1.9"/>',
    "shield": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="m9 12 2 2 4-4"/>',
    "shield-alert": '<path d="M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z"/><path d="M12 8v4"/><path d="M12 16h.01"/>',
}


def icon(name, size=16, stroke=2):
    return (
        f'<svg class="ic" width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
        f'stroke="currentColor" stroke-width="{stroke}" stroke-linecap="round" '
        f'stroke-linejoin="round">{ICONS[name]}</svg>'
    )


def compact(s):
    """Remove blank lines / indentation so Markdown never treats HTML as a code block."""
    return "\n".join(line.strip() for line in s.strip().splitlines() if line.strip())


def html_block(s):
    st.markdown(compact(s), unsafe_allow_html=True)


ACRONYMS = {"saas": "SaaS", "sme": "SME", "smb": "SMB", "ai": "AI", "it": "IT", "b2b": "B2B", "crm": "CRM"}


def pretty(s):
    words = str(s).replace("_", " ").split()
    return " ".join(ACRONYMS.get(w.lower(), w[:1].upper() + w[1:]) for w in words)


def sentence(s):
    s = str(s).strip()
    return s[:1].upper() + s[1:]


def fmt_num(v):
    try:
        f = float(v)
        return str(int(f)) if f == int(f) else f"{f:.1f}"
    except Exception:
        return str(v)


def pct(part, total):
    return round(100 * part / total, 1) if total else 0


def band_class(b):
    s = str(b).lower()
    if "high" in s:
        return "ok"
    if "low" in s or "<" in s:
        return "bad"
    return "neu"


def score_class(v):
    try:
        v = float(v)
    except Exception:
        return ""
    return "sc-ok" if v >= 80 else ("sc-bad" if v < 60 else "")


# =====================================================================
#  3. CSS
# =====================================================================
FONT_IMPORT = (
    "@import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@500;600;700"
    "&family=Inter:wght@400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap');"
)

STATIC_CSS = r"""
:root{--font-head:'Plus Jakarta Sans','Inter',system-ui,sans-serif;--font-body:'Inter',system-ui,sans-serif;--font-mono:'JetBrains Mono',ui-monospace,Menlo,monospace;--r-card:12px;--r-ctl:8px;}
html, body, .stApp, .stApp p, .stApp label, .stApp input, .stApp textarea, .stApp button, .stApp li, .stApp a, [data-testid="stMarkdownContainer"] {font-family:var(--font-body) !important;}
.stApp{background:var(--canvas);color:var(--text);}
#MainMenu, footer, [data-testid="stMainMenu"], [data-testid="stAppDeployButton"], [data-testid="stDecoration"]{display:none !important;}
header[data-testid="stHeader"]{background:transparent;height:3rem;}
.block-container{max-width:1600px;padding:2rem 2.75rem 4rem;}
.block-container > [data-testid="stVerticalBlock"]{gap:2rem;}
.block-container [data-testid="stHorizontalBlock"]{gap:1.25rem;}
.st-key-live_js{position:fixed;bottom:0;right:0;width:2px;height:2px;opacity:0;pointer-events:none;overflow:hidden;z-index:-1;margin:0;}
.ic{flex:none;}

/* ---------- Compact Filters Redesign ---------- */

.st-key-filters_card {
    padding: 20px 24px !important;
    border-radius: 12px;
    gap: 10px !important;
}

.st-key-filters_card [data-testid="stHorizontalBlock"] {
    gap: 10px !important;
    align-items: center !important;
}

.st-key-filters_card [data-testid="stHorizontalBlock"] 
[data-testid="stHorizontalBlock"] {
    gap: 8px !important;
}

.f-label {
    font-size: 11px !important;
    font-weight: 600;
    white-space: nowrap;
    letter-spacing: .04em;
}

.st-key-filters_card [data-testid="stMultiSelect"] {
    margin: 0 !important;
}

.st-key-filters_card [data-testid="stMultiSelect"] 
[data-baseweb="select"] > div {
    min-height: 40px !important;
    padding: 3px 7px !important;
    border-radius: 8px !important;
}

.st-key-filters_card span[data-baseweb="tag"] {
    margin: 2px !important;
    padding: 3px 7px !important;
    font-size: 11px !important;
}

.st-key-filters_card button {
    min-height: 38px !important;
    padding: 0 14px !important;
    white-space: nowrap;
}

.st-key-clear_all button {
    font-size: 12px !important;
    font-weight: 600 !important;
}

@media(max-width: 900px) {
    .st-key-filters_card {
        padding: 16px !important;
    }
}
/* Prospect selector spacing fix */
.selector-heading {
    display: block !important;
    margin-bottom: 14px !important;
    position: relative !important;
    z-index: 2 !important;
}

.selector-title {
    display: block !important;
    line-height: 1.5 !important;
    margin-bottom: 5px !important;
}

.selector-subtitle {
    display: block !important;
    line-height: 1.5 !important;
    margin-bottom: 12px !important;
}

.st-key-selector {
    overflow: visible !important;
}

.st-key-selector [data-baseweb="select"] {
    margin-top: 5px !important;
}



/* Dropdown selected options */
[data-baseweb="menu"] [aria-selected="true"] {
    background-color: var(--primary-color) !important;
    color: white !important;
}

/* ---------- Sidebar ---------- */
section[data-testid="stSidebar"]{background:var(--surface);border-right:1px solid var(--border);}
section[data-testid="stSidebar"][aria-expanded="true"]{min-width:272px !important;width:272px !important;}
[data-testid="stSidebarHeader"]{height:2.75rem;min-height:0;padding:.75rem 1rem 0;justify-content:flex-end;}
[data-testid="stSidebarHeader"] button, [data-testid="stExpandSidebarButton"], [data-testid="stSidebarCollapsedControl"] button{color:var(--text-2) !important;border-radius:8px;}
[data-testid="stSidebarHeader"] button:hover, [data-testid="stExpandSidebarButton"]:hover{background:var(--muted) !important;}
[data-testid="stSidebarUserContent"]{padding:.5rem 1rem 1.25rem;}
[data-testid="stSidebarUserContent"] > [data-testid="stVerticalBlock"]{min-height:calc(100vh - 6rem);gap:1.25rem;}
.st-key-theme_box{margin-top:auto;border-top:1px solid var(--border);padding-top:16px;}
.st-key-theme_box label p{font:600 11px var(--font-body) !important;letter-spacing:.06em;text-transform:uppercase;color:var(--text-2) !important;}
.brand{display:flex;align-items:center;gap:12px;padding:0 4px 4px;}
.logo{width:36px;height:36px;border-radius:8px;background:var(--primary);color:#fff;display:flex;align-items:center;justify-content:center;box-shadow:inset 0 1px 0 rgba(255,255,255,.15);}
.brand-txt{flex:1;line-height:1.15;}
.b1{font:600 17px/1.1 var(--font-head);letter-spacing:-.02em;color:var(--text);}
.b2{font:600 11px/1.4 var(--font-body);letter-spacing:.06em;color:var(--text-2);}
.pro{font:700 10px var(--font-body);letter-spacing:.04em;padding:3px 8px;border-radius:6px;background:var(--primary-soft);color:var(--primary);}
.side-label{font:600 11px var(--font-body);letter-spacing:.06em;text-transform:uppercase;color:var(--text-2);padding:8px 4px 10px;}
.nav-item{display:flex;align-items:center;gap:10px;padding:10px 12px;border-radius:8px;font:600 15px var(--font-body);color:var(--text-2);}
.nav-item.active{background:var(--primary);color:#fff;box-shadow:inset 0 1px 0 rgba(255,255,255,.15);}
.st-key-discovery_card{background:var(--muted);border:1px solid var(--border);border-radius:12px;padding:18px;margin-top:28px;gap:1rem !important;}
.disc-head{display:flex;justify-content:space-between;align-items:center;font:600 14px var(--font-body);color:var(--text);}
.disc-head span{display:inline-flex;align-items:center;gap:8px;}
.disc-head .cap{font:400 12px var(--font-body);color:var(--text-2);}
.disc-row{display:flex;justify-content:space-between;font:500 13px var(--font-body);color:var(--text-2);}
.disc-row b{color:var(--primary);font-weight:600;}
.telemetry{font:400 12px/1.9 var(--font-body);color:var(--text-2);}
.t-row{display:flex;justify-content:space-between;}
.t-row b{font-weight:500;color:var(--text);}
.t-row .ok{color:var(--success-strong);font-weight:600;}

/* ---------- Top bar ---------- */
.live-pill{display:inline-flex;align-items:center;gap:8px;font:600 12px var(--font-body);color:var(--success-text);background:var(--surface);border:1px solid var(--border);border-radius:9999px;padding:5px 12px;box-shadow:var(--shadow-1);}
.live-pill .dot{width:7px;height:7px;border-radius:50%;background:var(--success);box-shadow:0 0 0 0 var(--success);animation:pulse 2s infinite;}
@keyframes pulse{0%{box-shadow:0 0 0 0 var(--success-border);}70%{box-shadow:0 0 0 6px transparent;}100%{box-shadow:0 0 0 0 transparent;}}
@media (prefers-reduced-motion: reduce){.live-pill .dot{animation:none;}}
.st-key-q [data-baseweb="input"]{position:relative;}
.st-key-q [data-baseweb="input"] input{padding-left:38px !important;}
.st-key-q [data-baseweb="input"]::before{content:"";position:absolute;left:13px;top:50%;width:16px;height:16px;transform:translateY(-50%);background:url("data:image/svg+xml;utf8,<svg xmlns='http://www.w3.org/2000/svg' width='16' height='16' viewBox='0 0 24 24' fill='none' stroke='%2394A3B8' stroke-width='2' stroke-linecap='round'><circle cx='11' cy='11' r='8'/><path d='m21 21-4.3-4.3'/></svg>") no-repeat center;pointer-events:none;z-index:2;}
[data-testid="InputInstructions"]{display:none;}

/* ---------- Title ---------- */
.page-title{font:700 32px/1.15 var(--font-head);letter-spacing:-.03em;color:var(--text);margin:0;}
.page-sub{font:400 14px/20px var(--font-body);color:var(--text-2);margin-top:6px;}
.st-key-force_refresh{display:flex;justify-content:flex-end;}
.sync{text-align:right;font:400 12px var(--font-body);color:var(--text-3);white-space:nowrap;}
.sync b{font-weight:500;color:var(--text-2);}
@keyframes spin{to{transform:rotate(360deg);}}
.ic.spin{animation:spin .9s linear infinite;color:var(--primary);}
.kpi.loading .kpi-num, .kpi.loading .kpi-foot, .kpi.loading .kpi-unit, .kpi.loading .badge{opacity:.3;filter:blur(1.5px);}
.kpi.loading .lbl::after{content:" · refreshing";color:var(--primary);text-transform:none;letter-spacing:0;font-weight:500;}
.new-badge{font:700 10px var(--font-body);background:var(--success-bg);color:var(--success-text);border:1px solid var(--success-border);border-radius:4px;padding:1px 6px;margin-left:8px;letter-spacing:.04em;vertical-align:middle;}

/* ---------- Cards / KPI ---------- */
.card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-card);box-shadow:var(--shadow-1);padding:24px;}
.card.detail{padding:32px;}
.kpi{display:flex;flex-direction:column;gap:20px;min-height:196px;padding:28px;transition:box-shadow 120ms ease;}
.kpi:hover{box-shadow:var(--shadow-2);}
.kpi-top{display:flex;justify-content:space-between;align-items:center;color:var(--text-3);}
.lbl{font:600 11px var(--font-body);letter-spacing:.06em;text-transform:uppercase;color:var(--text-2);}
.kpi-val{display:flex;align-items:center;gap:10px;}
.kpi-num{font:700 40px/1 var(--font-head);letter-spacing:-.03em;font-variant-numeric:tabular-nums;color:var(--text);}
.kpi-unit{font:400 14px var(--font-body);color:var(--text-2);}
.kpi-foot{display:flex;justify-content:space-between;align-items:flex-end;gap:12px;font:400 13px/1.45 var(--font-body);color:var(--text-2);margin-top:auto;}
.kpi-foot .r{text-align:right;font-weight:500;}
.kpi-foot .r.ok{color:var(--success-strong);}
.kpi-foot .r.pri{color:var(--primary);}
.tag{font:700 10px var(--font-body);letter-spacing:.04em;padding:2px 8px;border-radius:6px;background:var(--accent-bg);color:var(--accent-text);}
.badge{display:inline-flex;align-items:center;gap:6px;height:22px;padding:0 9px;border-radius:9999px;font:600 11px var(--font-body);border:1px solid;white-space:nowrap;}
.badge.ok{background:var(--success-bg);color:var(--success-text);border-color:var(--success-border);}

/* ---------- Filters ---------- */
.st-key-filters_card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-card);box-shadow:var(--shadow-1);padding:28px 32px;gap:1rem !important;}
.st-key-filters_card [data-testid="stHorizontalBlock"]{gap:.75rem;}
.f-label{font:600 11px var(--font-body);letter-spacing:.06em;text-transform:uppercase;color:var(--text-2);}
[data-testid="stMultiSelect"] [data-baseweb="select"] > div{min-height:36px;background:var(--muted) !important;border:1px solid var(--border) !important;border-radius:8px !important;}


/* ---------- Inputs ---------- */
[data-testid="stTextInput"] [data-baseweb="input"], [data-testid="stSelectbox"] [data-baseweb="select"] > div{background:var(--surface) !important;border:1px solid var(--border) !important;border-radius:8px !important;min-height:38px;box-shadow:none;}
[data-testid="stTextInput"] [data-baseweb="input"]:focus-within, [data-testid="stSelectbox"] [data-baseweb="select"] > div:focus-within, [data-testid="stMultiSelect"] [data-baseweb="select"] > div:focus-within{border-color:var(--primary) !important;box-shadow:0 0 0 3px var(--primary-ring) !important;}
[data-testid="stTextInput"] input{font:400 14px var(--font-body) !important;color:var(--text) !important;background:transparent !important;}
[data-testid="stTextInput"] input::placeholder{color:var(--text-3) !important;}

/* ---------- Buttons ---------- */
[data-testid="stBaseButton-primary"], button[kind="primary"]{background:var(--primary) !important;color:#fff !important;border:1px solid var(--primary) !important;border-radius:8px !important;min-height:40px;font:500 14px var(--font-body) !important;box-shadow:inset 0 1px 0 rgba(255,255,255,.15), var(--shadow-1) !important;transition:background 120ms ease;}
[data-testid="stBaseButton-primary"]:hover, button[kind="primary"]:hover{background:var(--primary-hover) !important;border-color:var(--primary-hover) !important;}
[data-testid="stBaseButton-primary"]:active, button[kind="primary"]:active{background:var(--primary-active) !important;}
[data-testid="stBaseButton-secondary"], button[kind="secondary"], [data-testid="stPopover"] > button{background:var(--surface) !important;color:var(--text) !important;border:1px solid var(--border) !important;border-radius:8px !important;min-height:36px;font:500 13px var(--font-body) !important;box-shadow:var(--shadow-1) !important;}
[data-testid="stBaseButton-secondary"]:hover, button[kind="secondary"]:hover, [data-testid="stPopover"] > button:hover{background:var(--canvas) !important;border-color:var(--border-strong) !important;}
.st-key-discover, .st-key-discover .stButton, .st-key-discover button{width:100%;}
.st-key-force_refresh button, .st-key-clear_all button{background:transparent !important;border:none !important;box-shadow:none !important;color:var(--primary) !important;font-weight:600 !important;}
.st-key-force_refresh button:hover, .st-key-clear_all button:hover{background:var(--primary-soft) !important;}
.st-key-pg_prev button, .st-key-pg_next button{background:var(--primary-soft) !important;color:var(--primary) !important;border:none !important;box-shadow:none !important;min-height:30px;width:32px;padding:0;}
.st-key-pg_prev button:disabled, .st-key-pg_next button:disabled{opacity:.45;}
[class*="st-key-pgn_"] button{background:transparent !important;border:1px solid transparent !important;box-shadow:none !important;color:var(--text-2) !important;min-height:34px;width:34px;padding:0;border-radius:8px !important;font:600 13px var(--font-body) !important;font-variant-numeric:tabular-nums;transition:background 120ms ease;}
[class*="st-key-pgn_"] button:hover{background:var(--primary-soft) !important;color:var(--primary) !important;}
[class*="st-key-pgn_"] button p{color:inherit !important;}
.ell{text-align:center;color:var(--text-3);font:600 14px var(--font-body);letter-spacing:.1em;}
.st-key-dl_csv button, .st-key-dl_xlsx button{background:transparent !important;border:none !important;box-shadow:none !important;color:var(--text-2) !important;min-height:36px;padding:0 6px;}
.st-key-dl_csv button:hover, .st-key-dl_xlsx button:hover{background:var(--muted) !important;color:var(--primary) !important;}

/* ---------- Slider ---------- */
[data-testid="stSlider"] div[role="slider"]{background:var(--primary) !important;box-shadow:0 0 0 4px var(--primary-ring) !important;}
[data-testid="stSlider"] div[style*="linear-gradient"]{height:4px !important;border-radius:9999px;}
[data-testid="stSliderThumbValue"], [data-testid="stSliderTickBar"]{display:none !important;}

/* ---------- Table card ---------- */
.st-key-table_card{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-card);box-shadow:var(--shadow-1);padding:0;gap:0 !important;overflow:hidden;}
.st-key-table_card [data-testid="stHorizontalBlock"]{padding:20px 28px;}
.tc-title{display:flex;align-items:center;gap:12px;font:600 18px var(--font-head);letter-spacing:-.02em;color:var(--text);}
.count-pill{font:500 12px var(--font-body);letter-spacing:0;background:var(--muted);border-radius:9999px;padding:3px 10px;color:var(--text-2);}
.rows-note {
    display: flex !important;
    align-items: center !important;
    justify-content: flex-end !important;
    min-height: 34px !important;
    line-height: 34px !important;
    margin: 0 !important;
    padding: 0 !important;
    text-align: right;
    font: 400 13px var(--font-body);
    color: var(--text-2);
}
.foot-note{font:400 13px var(--font-body);color:var(--text-2);}
.tbl-wrap{overflow-x:auto;}
table.tbl{width:100%;border-collapse:collapse;}
.tbl th{background:var(--canvas);border-top:1px solid var(--border);border-bottom:1px solid var(--border);font:600 11px/1.3 var(--font-body);letter-spacing:.04em;text-transform:uppercase;color:var(--text-2);padding:14px 20px;text-align:left;}
.tbl th:first-child, .tbl td:first-child{padding-left:28px;}
.tbl th:last-child, .tbl td:last-child{padding-right:28px;}
.tbl th.r{text-align:right;}
.tbl td{padding:20px 20px;border-bottom:1px solid var(--muted);font:400 14px/20px var(--font-body);color:var(--text);vertical-align:middle;}
.tbl tr:hover td{background:var(--canvas);transition:background 120ms ease;}
.tbl tr.is-top td{background:var(--primary-row);}
.tbl td.idx{color:var(--text-3);font-variant-numeric:tabular-nums;font-size:13px;}
.tbl td.co{font-weight:600;white-space:nowrap;}
.tbl td.sc{text-align:right;font-weight:700;font-variant-numeric:tabular-nums;}
.tbl td.sc-ok{color:var(--success-strong);}
.tbl td.sc-bad{color:var(--danger);}
.dom{font:500 12px var(--font-mono);background:var(--muted);border:1px solid var(--border);border-radius:4px;padding:3px 8px;color:var(--text-2);white-space:nowrap;}
.is-top .dom{background:var(--primary-soft);border-color:var(--primary-soft-2);color:var(--primary);}
.top-badge{font:700 10px var(--font-body);background:var(--primary);color:#fff;border-radius:4px;padding:2px 6px;margin-left:8px;letter-spacing:.04em;vertical-align:middle;}
.pill{display:inline-block;padding:6px 14px;border-radius:9999px;font:600 11px/1.3 var(--font-body);letter-spacing:.02em;text-align:center;white-space:nowrap;}
.pill.ok{background:var(--success-bg);color:var(--success-text);}
.pill.neu{background:var(--border);color:var(--text-2);}
.pill.bad{background:var(--danger-bg);color:var(--danger);}
.empty{padding:40px 24px;text-align:center;color:var(--text-2);font:400 14px var(--font-body);}

/* ---------- Prospect Selector Redesign ---------- */

.st-key-selector {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 16px 20px !important;
    box-shadow: var(--shadow-1);
    gap: 8px !important;
}

.selector-heading {
    display: flex;
    flex-direction: column;
    gap: 4px;
    margin-bottom: 5px;
}

.selector-title {
    font: 600 14px var(--font-head);
    color: var(--text);
}

.selector-subtitle {
    font: 400 12px/1.5 var(--font-body);
    color: var(--text-2);
}

.st-key-selector [data-testid="stSelectbox"] {
    width: 100%;
    margin: 0 !important;
}

.st-key-selector [data-baseweb="select"] > div {
    min-height: 44px !important;
    border: 1px solid var(--border) !important;
    background: var(--canvas) !important;
    border-radius: 8px !important;
    box-shadow: none !important;
}

.st-key-selector [data-baseweb="select"] > div:focus-within {
    border-color: var(--primary) !important;
    box-shadow: 0 0 0 3px var(--primary-ring) !important;
}

/* ---------- Export Description ---------- */

.exp {
    display: flex;
    align-items: center;
    gap: 14px;
}

.exp-t {
    font: 600 14px/1.4 var(--font-body);
    color: var(--text);
}

.exp-s {
    font: 400 12px/1.6 var(--font-body);
    color: var(--text-2);
    margin-top: 4px;
    max-width: 440px;
}

.st-key-export_csv,
.st-key-export_xlsx {
    min-height: 105px;
    display: flex;
    justify-content: center;
}

/* ---------- Modern Pagination ---------- */

.page-indicator {
    display: flex;
    align-items: center;
    justify-content: center;
    min-height: 34px;
    line-height: 1.4;
    margin: 0 !important;
    padding: 0 !important;
    position: static !important;
    top: auto !important;
}


.st-key-bottom_prev button,
.st-key-bottom_next button {
    min-height: 34px !important;
    font-size: 12px !important;
    padding: 0 10px !important;
    border-radius: 7px !important;
}

.st-key-table_card [data-testid="stHorizontalBlock"] {
    align-items: center;
}

.st-key-bottom_prev button,
.st-key-bottom_next button {
    min-height: 34px !important;
    margin: 0 !important;
    align-self: center;
}

/* ---------- Detail section ---------- */
.sec-head{display:flex;align-items:center;gap:12px;}
.sec-ico{width:36px;height:36px;border-radius:8px;background:var(--primary-soft);color:var(--primary);display:flex;align-items:center;justify-content:center;}
.sec-title{font:600 22px var(--font-head);letter-spacing:-.02em;color:var(--text);}
.st-key-selector {
    background: var(--surface);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 18px 20px !important;
    box-shadow: var(--shadow-1);
    gap: 12px !important;
}

.st-key-selector [data-testid="stVerticalBlock"] {
    gap: 12px !important;
}

.st-key-selector .selector-heading {
    margin-bottom: 8px !important;
}

.st-key-selector [data-testid="stSelectbox"] {
    margin-top: 6px !important;
}
.st-key-selector [data-testid="stHorizontalBlock"]{gap:1rem;align-items:center;}
.st-key-selector [data-testid="stSelectbox"] [data-baseweb="select"] > div{background:var(--canvas) !important;min-height:42px;}
.sel-label{font:400 13px/1.3 var(--font-body);color:var(--text-2);white-space:nowrap;}
.cap-label{font:600 11px var(--font-body);letter-spacing:.06em;text-transform:uppercase;color:var(--text-2);}
.entity-row{display:flex;justify-content:space-between;align-items:flex-start;gap:12px;flex-wrap:wrap;}
.entity-name{font:700 24px/1.2 var(--font-head);letter-spacing:-.02em;color:var(--text);margin-top:4px;}
.loc-pill{display:inline-flex;gap:6px;align-items:center;background:var(--canvas);border:1px solid var(--border);border-radius:9999px;padding:6px 12px;font:500 12px var(--font-body);color:var(--text-2);}
.rationale{background:var(--canvas);border:1px solid var(--muted);border-radius:8px;padding:18px 20px;font:400 14.5px/1.7 var(--font-body);color:var(--text);margin:12px 0 28px;}
.hyp{color:var(--primary);font-weight:600;}
.evidence{display:flex;gap:12px;align-items:flex-start;background:var(--muted);border-radius:8px;padding:16px 18px;font:400 12.5px/1.65 var(--font-mono);color:var(--text-2);margin:12px 0 0;}
.evidence .str{color:var(--success-text);font-weight:600;}
.detail-foot{display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap;font:400 12.5px var(--font-body);color:var(--text-2);margin-top:32px;}
.score-row{display:flex;justify-content:space-between;align-items:baseline;}
.score-big{font:700 26px var(--font-head);letter-spacing:-.02em;color:var(--success-strong);font-variant-numeric:tabular-nums;}
.score-big small{font:500 22px var(--font-head);}
.bar{display:flex;height:8px;border-radius:9999px;background:var(--muted);overflow:hidden;margin:18px 0 24px;}
.mini-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;}
.mini{background:var(--muted);border-radius:8px;padding:16px 18px;}
.mini-l{font:400 13px var(--font-body);color:var(--text-2);}
.mini-v{font:700 22px var(--font-head);letter-spacing:-.02em;color:var(--text);font-variant-numeric:tabular-nums;}
.mini-v small{font:400 13px var(--font-body);color:var(--text-2);}
.route{display:flex;gap:18px;align-items:flex-start;justify-content:space-between;margin-top:26px;font:400 13px/1.5 var(--font-body);color:var(--text-2);}
.route a{color:var(--primary);text-decoration:none;font-weight:500;word-break:break-all;}
.route a:hover{text-decoration:underline;}
.route .k{min-width:64px;}
.route .v{flex:1;}
.gov{display:flex;gap:14px;background:var(--danger-bg);border:1px solid var(--danger-border);border-radius:8px;padding:18px 20px;margin-top:32px;}
.gov .ic{color:var(--danger);margin-top:2px;}
.gov-t{font:700 12px/1.4 var(--font-body);letter-spacing:.02em;text-transform:uppercase;color:var(--text);margin-bottom:2px;}
.gov-d{font:400 13px/1.5 var(--font-body);color:var(--text-2);}

/* ---------- Export ---------- */
.exp-title{font:600 20px var(--font-head);letter-spacing:-.02em;color:var(--text);}
.st-key-export_csv, .st-key-export_xlsx{background:var(--surface);border:1px solid var(--border);border-radius:var(--r-card);box-shadow:var(--shadow-1);padding:18px 22px;}
.exp{display:flex;align-items:center;gap:14px;}
.exp-ico{width:44px;height:44px;border-radius:8px;background:var(--muted);color:var(--text-2);display:flex;align-items:center;justify-content:center;flex:none;}
.exp-ico.green{background:var(--success-bg);color:var(--success-strong);}
.exp-t{font:600 14px var(--font-body);color:var(--text);}
.exp-s{font:400 13px var(--font-body);color:var(--text-2);}

/* ---------- Footer ---------- */
.app-foot{border-top:1px solid var(--border);margin-top:16px;padding:36px 0 8px;text-align:center;}
.app-foot .n{display:inline-flex;align-items:center;gap:8px;font:600 16px var(--font-head);letter-spacing:-.01em;color:var(--text);}
.app-foot .n .ic{color:var(--primary);}
.app-foot .r{font:400 13px var(--font-body);color:var(--text-2);margin-top:4px;}

.st-key-table_card [data-testid="stHorizontalBlock"] [data-testid="stHorizontalBlock"]{padding:0;gap:.4rem;}
.status-row{display:flex;align-items:center;gap:16px;flex-wrap:wrap;}
.sync-inline{font:400 12.5px var(--font-body);color:var(--text-3);}
.sync-inline b{font-weight:500;color:var(--text-2);}
[data-testid="stAlert"]{border-radius:10px;}
@media (max-width:768px){.block-container{padding:1rem;}.block-container > [data-testid="stVerticalBlock"]{gap:1.25rem;}.page-title{font-size:26px;}.kpi-num{font-size:32px;}}
"""


def inject_css(slider_pct, active_page):
    root = ":root{" + ";".join(f"--{k}:{v}" for k, v in THEME.items()) + ";}"
    dynamic = (
        # slider fill follows the live value
        '[data-testid="stSlider"] div[style*="linear-gradient"]{'
        f"background:linear-gradient(to right,var(--primary) 0%,var(--primary) {slider_pct}%,"
        f"var(--border-strong) {slider_pct}%,var(--border-strong) 100%) !important;}}"
        # active page number
        f".st-key-pgn_{active_page} button{{background:var(--primary) !important;"
        "border-color:var(--primary) !important;color:#fff !important;"
        "box-shadow:0 1px 2px rgba(15,23,42,.12) !important;}"
    )
    st.markdown(f"<style>{FONT_IMPORT}{root}{STATIC_CSS}{dynamic}</style>", unsafe_allow_html=True)


def tone_color(key, value, idx):
    """Pick a color for a selected filter chip based on its value (semantic) or position (cycle)."""
    v = str(value).lower()
    if key == "f_band":
        if "high" in v:
            return BASE["success"]
        if "low" in v or "<" in v:
            return BASE["danger"]
        if "potential" in v or "medium" in v:
            return BASE["warning"]
        return BASE["info"]
    if key == "f_review":
        if any(w in v for w in ("approv", "verif", "clear", "signed")):
            return BASE["success"]
        if any(w in v for w in ("reject", "block", "denied", "fail")):
            return BASE["danger"]
        if "pending" in v or "review" in v:
            return BASE["warning"]
        return BASE["info"]
    if key == "f_country":
        if "kingdom" in v or v == "uk":
            return BASE["primary"]
        if "states" in v or v == "us":
            return BASE["secondary"]
    cycle = ["primary", "secondary", "success", "info", "warning"]
    return BASE[cycle[idx % len(cycle)]]


def css_str(v):
    return str(v).replace("\\", "\\\\").replace('"', '\\"')


def chip_css(keys):
    colors = {
        "f_country": BASE["primary"],
        "f_band": BASE["success"],
        "f_service": BASE["secondary"],
        "f_review": BASE["warning"],
    }

    out = []

    for key in keys:
        color = colors.get(key, BASE["primary"])

        out.append(f"""
            .st-key-{key} [data-baseweb="tag"] {{
                background: {color} !important;
                border: 1px solid {color} !important;
                border-radius: 6px !important;
                color: white !important;
            }}

            .st-key-{key} [data-baseweb="tag"] * {{
                color: white !important;
                fill: white !important;
            }}
        """)

    return "".join(out)


# =====================================================================
#  4. STATE + DATA
# =====================================================================
TEXT_COLS = [
    "company_name", "official_domain", "country", "industry", "relevant_service",
    "priority_band", "review_status", "official_contact_route", "city_region",
    "fit_rationale", "evidence_notes",
]
NUM_COLS = ["total_score", "industry_fit_score", "service_relevance_score"]
FILTER_COLS = {"f_country": "country", "f_band": "priority_band", "f_service": "relevant_service", "f_review": "review_status"}

st.session_state.setdefault("page", 1)
st.session_state.setdefault("batch_no", 1)



def load_df():
    df = pd.read_csv(CSV_FILE) if os.path.exists(CSV_FILE) else pd.DataFrame()
    for c in TEXT_COLS:
        if c not in df.columns:
            df[c] = ""
        df[c] = df[c].fillna("").astype(str)
    for c in NUM_COLS:
        if c not in df.columns:
            df[c] = float("nan")
        df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in FILTER_COLS.values():
        df[c] = df[c].replace("", "Unspecified")
    return df


def sync_multi(key, options):
    """Keep multiselect state valid and auto-include newly discovered options."""
    options = list(options)
    prev = st.session_state.get(f"{key}_opts")
    if key not in st.session_state:
        st.session_state[key] = options
    else:
        keep = [v for v in st.session_state[key] if v in options]
        if prev is not None:
            keep += [o for o in options if o not in prev and o not in keep]
        st.session_state[key] = keep
    st.session_state[f"{key}_opts"] = options


def reset_filters():
    for k in FILTER_COLS:
        st.session_state[k] = list(st.session_state.get(f"{k}_opts", []))
    st.session_state["page"] = 1


def set_page(p):
    st.session_state["page"] = p


def page_items(cur, total_pages):
    """1 … 4 5 6 … 20 style page list."""
    if total_pages <= 7:
        return list(range(1, total_pages + 1))
    lo, hi = max(2, cur - 1), min(total_pages - 1, cur + 1)
    if cur <= 3:
        lo, hi = 2, 4
    if cur >= total_pages - 2:
        lo, hi = total_pages - 3, total_pages - 1
    items = [1]
    if lo > 2:
        items.append("…")
    items += list(range(lo, hi + 1))
    if hi < total_pages - 1:
        items.append("…")
    items.append(total_pages)
    return items


# =====================================================================
#  5. LAYOUT
# =====================================================================
slider_val = st.session_state.get("batch_size", 3)
inject_css(round((slider_val - 1) / 9 * 100, 1), st.session_state["page"])

# ----------------- SIDEBAR -----------------
with st.sidebar:
    html_block(f"""
    <div class="brand"><div class="logo">{icon('network', 20)}</div>
    <div class="brand-txt"><div class="b1">{esc(BRAND['name'])}</div><div class="b2">{esc(BRAND['sub'])}</div></div>
    <span class="pro">{esc(BRAND['tier'])}</span></div>
    """)
    html_block(f"""
    <div><div class="side-label">Intelligence Workspace</div>
    <div class="nav-item active">{icon('grid', 18)}<span>Live Pipeline</span></div></div>
    """)

    with st.container(key="discovery_card"):
        html_block(f"""
        <div class="disc-row"><span>Leads per Batch</span><b>{slider_val}</b></div>
        """)
        batch_size = st.slider("Leads per Batch", min_value=1, max_value=10, value=3,
                               key="batch_size", label_visibility="collapsed")
        run_discovery = st.button("Generate Leads", type="primary", key="discover",
                                  icon=":material/radar:")

    if THEME_SWITCHER:
        with st.container(key="theme_box"):
            st.selectbox("Theme", options=list(PALETTES), index=list(PALETTES).index(THEME_NAME),
                         key="theme", format_func=lambda x: x.title())

# ----------------- TOP BAR -----------------
st.session_state.setdefault("last_sync", datetime.now().strftime("%H:%M:%S"))


def pill_html():
    return ('<div class="status-row"><span class="live-pill"><i class="dot"></i>Live Pipeline • Online</span>'
            f'<span class="sync-inline">Last synced <b>{st.session_state["last_sync"]}</b></span></div>')


pill_slot = st.empty()
pill_slot.markdown(pill_html(), unsafe_allow_html=True)

# ----------------- TITLE + REFRESH -----------------
t_l, t_r = st.columns([5, 1.2], vertical_alignment="bottom")
with t_l:
    html_block("""
    <div class="page-title">Lead Intelligence Dashboard</div>
    <div class="page-sub">B2B Prospect Discovery &amp; Explainable Scoring Pipeline (UK &amp; US Markets)</div>
    """)
with t_r:
    refresh_clicked = st.button("Refresh", key="force_refresh", icon=":material/refresh:")

# ----------------- KPI CARDS -----------------
def ring(p):
    c = 50.27
    return (f'<svg width="22" height="22" viewBox="0 0 22 22"><circle cx="11" cy="11" r="8" fill="none" '
            f'stroke="var(--border)" stroke-width="2.5"/><circle cx="11" cy="11" r="8" fill="none" '
            f'stroke="var(--primary)" stroke-width="2.5" stroke-linecap="round" '
            f'stroke-dasharray="{c * p / 100:.1f} {c}" transform="rotate(-90 11 11)"/></svg>')


def kpi(label, num, unit="", badge="", top_right="", foot_l="", foot_r="", r_cls="ok", loading=False):
    unit_html = f'<span class="kpi-unit">{unit}</span>' if unit else ""
    top_right = f'<span class="spin-wrap">{icon("refresh", 18)}</span>'.replace('class="ic"', 'class="ic spin"') if loading else top_right
    return f"""
    <div class="card kpi{' loading' if loading else ''}">
    <div class="kpi-top"><span class="lbl">{label}</span>{top_right}</div>
    <div class="kpi-val"><span class="kpi-num">{num}</span>{unit_html}{badge}</div>
    <div class="kpi-foot"><span>{foot_l}</span><span class="r {r_cls}">{foot_r}</span></div>
    </div>
    """


def render_kpis(slots, data, loading=False):
    tot = len(data)
    ev = int(data["total_score"].notna().sum())
    hi = int(data["priority_band"].str.contains("High", na=False).sum())
    uk = int((data["country"] == "United Kingdom").sum())
    us = int((data["country"] == "United States").sum())
    cards = [
        kpi("Total Qualified Leads", tot,
            badge=f'<span class="badge ok">↑ {round(pct(ev, tot))}% indexed</span>',
            top_right=icon("check-circle", 18),
            foot_l=f"Target Universe: {ev}/{tot}",
            foot_r="Fully evaluated" if ev == tot else f"{tot - ev} pending", loading=loading),
        kpi("High Priority Fit (80-100)", hi, unit="accounts", top_right=ring(pct(hi, tot)),
            foot_l=f"{pct(hi, tot)}% of total", foot_r="Direct engagement ready", loading=loading),
        kpi("UK Market Prospects", uk, unit="targets", top_right='<span class="tag">UK</span>',
            foot_l=f"{pct(uk, tot)}% share", foot_r="London &amp; SE hub", r_cls="pri", loading=loading),
        kpi("US Market Prospects", us, unit="targets", top_right='<span class="tag">US</span>',
            foot_l=f"{pct(us, tot)}% share", foot_r="East/West Coast", r_cls="pri", loading=loading),
    ]
    for slot, card in zip(slots, cards):
        slot.markdown(compact(card), unsafe_allow_html=True)


kpi_slots = [col.empty() for col in st.columns(4)]

# ----------------- DATA (+ refresh / discovery actions) -----------------
df = load_df()
render_kpis(kpi_slots, df, loading=bool(run_discovery or refresh_clicked))

if run_discovery:
    with st.sidebar, st.spinner("Connecting to live websites and qualifying prospects..."):
        existing_domains = get_already_processed_domains(CSV_FILE)
        candidates = generate_infinite_target_candidates(existing_domains, count=batch_size)
        new_records = []
        for item in candidates:
            domain, url, market = item["domain"], item["url"], item["market"]
            live_content = fetch_live_website(url)
            rec = analyze_prospect(domain, live_content, url, market)
            new_records.append(rec)
            existing_domains.add(domain)

        if new_records:
            file_exists = os.path.exists(CSV_FILE)
            headers = list(new_records[0].keys())
            with open(CSV_FILE, mode="a", newline="", encoding="utf-8") as f:
                writer = csv.DictWriter(f, fieldnames=headers)
                if not file_exists:
                    writer.writeheader()
                writer.writerows(new_records)
            st.session_state["batch_no"] += 1
            st.session_state["new_domains"] = {r.get("official_domain", r.get("domain", "")) for r in new_records}
            st.session_state["last_sync"] = datetime.now().strftime("%H:%M:%S")
            st.session_state["flash"] = f"Added {len(new_records)} fresh leads"
            st.session_state["page"] = 1
            st.rerun()
        else:
            st.session_state["flash"] = "No new targets found"
elif refresh_clicked:
    time.sleep(0.6)  # brief pause so the refresh state is visible
    st.session_state["last_sync"] = datetime.now().strftime("%H:%M:%S")
    st.session_state["flash"] = "Data refreshed from source"

if run_discovery or refresh_clicked:
    df = load_df()

if "flash" in st.session_state:
    st.toast(f"{st.session_state.pop('flash')} • {len(df)} leads indexed", icon="✅")

pill_slot.markdown(pill_html(), unsafe_allow_html=True)
render_kpis(kpi_slots, df)
total = len(df)
df["total_score"] = df["total_score"].fillna(0)
for c in ("industry_fit_score", "service_relevance_score"):
    df[c] = df[c].fillna(0)

# ----------------- FILTERS -----------------
for k, col in FILTER_COLS.items():
    sync_multi(k, sorted(df[col].unique().tolist()))

with st.container(key="filters_card"):
    f_left, f_right = st.columns([6, 1.5], vertical_alignment="center")
    with f_left:
        for label, key in (("Country:", "f_country"), ("Priority:", "f_band"),
                           ("Service:", "f_service"), ("Status:", "f_review")):
            a, b = st.columns([1, 9], vertical_alignment="center")
            with a:
                html_block(f'<div class="f-label">{label}</div>')
            with b:
                st.multiselect(label, options=st.session_state[f"{key}_opts"], key=key,
                               label_visibility="collapsed", on_change=set_page, args=(1,))
    with f_right:
        st.button("Clear All", key="clear_all", on_click=reset_filters)

query = ""
mask = (
    df["country"].isin(st.session_state["f_country"])
    & df["priority_band"].isin(st.session_state["f_band"])
    & df["relevant_service"].isin(st.session_state["f_service"])
    & df["review_status"].isin(st.session_state["f_review"])
)
if query:
    hay = (df["company_name"] + " " + df["official_domain"] + " " + df["country"] + " " + df["industry"]
           + " " + df["relevant_service"] + " " + df["fit_rationale"]).str.lower()
    mask &= hay.str.contains(re.escape(query), na=False)
filtered = df[mask]
n = len(filtered)

# ----------------- TABLE -----------------
pages = max(1, -(-n // PAGE_SIZE))
page = min(max(1, st.session_state["page"]), pages)
st.session_state["page"] = page
start = (page - 1) * PAGE_SIZE
chunk = filtered.iloc[start:start + PAGE_SIZE]
end = start + len(chunk)
top_idx = filtered["total_score"].idxmax() if n else None

with st.container(key="table_card"):
    h1, h2, h3, h4 = st.columns(
    [6, 3, 0.5, 0.5],
    vertical_alignment="center"
)
    with h1:
        q_note = f' · “{esc(query)}”' if query else ""
        html_block(f'<div class="tc-title">Prospects View<span class="count-pill">{n} Matching Records{q_note}</span></div>')
    with h2:
        shown = f"Rows {start + 1}–{end} shown" if n else "No rows"
        html_block(f'<div class="rows-note">{shown}</div>')
    with h3:
        st.button("", key="pg_prev", icon=":material/chevron_left:", disabled=page <= 1,
                  on_click=set_page, args=(page - 1,))
    with h4:
        st.button("", key="pg_next", icon=":material/chevron_right:", disabled=page >= pages,
                  on_click=set_page, args=(page + 1,))

    if n:
        rows = []
        for i, (idx, r) in enumerate(chunk.iterrows(), start=start + 1):
            is_top = idx == top_idx
            badge = '<span class="top-badge">TOP</span>' if is_top else ""
            if r["official_domain"] in st.session_state.get("new_domains", set()):
                badge += '<span class="new-badge">NEW</span>' 
            sc = fmt_num(r["total_score"])
            rows.append(
                f'<tr class="{"is-top" if is_top else ""}">'
                f'<td class="idx">{i}</td>'
                f'<td class="co">{esc(r["company_name"])}{badge}</td>'
                f'<td><span class="dom">{esc(r["official_domain"])}</span></td>'
                f'<td>{esc(r["country"])}</td>'
                f'<td>{esc(pretty(r["industry"]))}</td>'
                f'<td>{esc(sentence(r["relevant_service"]))}</td>'
                f'<td class="sc {score_class(r["total_score"])}">{sc}</td>'
                f'<td><span class="pill {band_class(r["priority_band"])}">{esc(r["priority_band"])}</span></td>'
                f'</tr>'
            )
        html_block(f"""
        <div class="tbl-wrap"><table class="tbl"><thead><tr>
        <th>#</th><th>Company Name</th><th>Official Domain</th><th>Country</th><th>Industry</th>
        <th>Relevant Service</th><th class="r">Total Score</th><th>Priority Band</th>
        </tr></thead><tbody>{''.join(rows)}</tbody></table></div>
        """)
    else:
        msg = ("No leads in database yet. Click “Discover Fresh Leads” in the sidebar to start prospecting."
               if total == 0 else "No prospects match the current filters. Use Clear All to reset them.")
        html_block(f'<div class="empty">{msg}</div>')

    fl, fr = st.columns([6, 5], vertical_alignment="center")
    with fl:
        txt = (f"Showing batch offset #{start + 1} through #{end} of {n} indexable records"
               if n else "Showing 0 indexable records")
        html_block(f'<div class="foot-note">{txt}</div>')
    with fr:
       pg_left, pg_info, pg_right = st.columns(
        [1, 2, 1],
        vertical_alignment="center"
    )

    with pg_left:
        st.button(
            "Previous",
            key="bottom_prev",
            disabled=page <= 1,
            on_click=set_page,
            args=(page - 1,)
        )

    with pg_info:
        html_block(
            f'<div class="page-indicator">'
            f'Page <b>{page}</b> of <b>{pages}</b>'
            f'</div>'
        )

    with pg_right:
        st.button(
            "Next",
            key="bottom_next",
            disabled=page >= pages,
            on_click=set_page,
            args=(page + 1,)
        )

# ----------------- DETAIL -----------------
d_l, d_r = st.columns([4, 5], vertical_alignment="center")
with d_l:
    html_block(f'<div class="sec-head"><div class="sec-ico">{icon("scan", 20)}</div>'
               f'<div class="sec-title">Prospect Intelligence Details &amp; Governance</div></div>')
selected_domain = None
with d_r:
    with st.container(key="selector"):

        html_block("""
            <div class="selector-heading">
                <div class="selector-title">
                    Select Prospect
                </div>
                <div class="selector-subtitle">
                    Search a company to explore its intelligence and evidence.
                </div>
            </div>
        """)

        domains = filtered["official_domain"].tolist()

        selected_domain = (
            st.selectbox(
                "Search company",
                options=domains,
                key="sel_domain",
                placeholder="Search company or domain...",
                label_visibility="collapsed"
            )
            if domains else None
        )


def route_href(route, domain):
    m = re.search(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)+", route or "")
    if m:
        return "mailto:" + m.group(0)
    m = re.search(r"https?://\S+", route or "")
    return m.group(0) if m else "https://" + domain


def evidence_html(text):
    parts = re.split(r'("[^"]*")', text)
    return "".join(f'<span class="str">{esc(p)}</span>' if p.startswith('"') and p.endswith('"') and len(p) > 1
                   else esc(p) for p in parts)


def rationale_html(text):
    if text.lower().startswith("hypothesis:"):
        return f'<span class="hyp">{esc(text[:11])}</span>{esc(text[11:])}'
    return esc(text)


if selected_domain:
    row = filtered[filtered["official_domain"] == selected_domain].iloc[0]
    total_s = float(row["total_score"])
    ind_s, svc_s = float(row["industry_fit_score"]), float(row["service_relevance_score"])
    other = max(total_s - ind_s - svc_s, 0)
    loc = ", ".join(x for x in (row["city_region"], row["country"]) if x)
    sig = hashlib.md5(row["official_domain"].encode()).hexdigest()[:7]
    href = route_href(row["official_contact_route"], row["official_domain"])
    status = (row["review_status"] or "Pending human review").replace("_", " ")

    c_left, c_right = st.columns([11, 9])
    with c_left:
        html_block(f"""
        <div class="card detail">
        <div class="entity-row"><div><div class="cap-label">Prospect Entity</div>
        <div class="entity-name">{esc(row['company_name'])}</div></div>
        <span class="loc-pill">{icon('map-pin', 14)}{esc(loc)}</span></div>
        <div class="cap-label" style="margin-top:22px">Operational Rationale</div>
        <div class="rationale">{rationale_html(row['fit_rationale'])}</div>
        <div class="cap-label">Observed Evidence Notes</div>
        <div class="evidence">{icon('code', 16)}<span>{evidence_html(row['evidence_notes'])}</span></div>
        <div class="detail-foot"><span>Signal Validation Hash: #{sig}</span><span>Pipeline Stage: Extraction Complete</span></div>
        </div>
        """)
    with c_right:
        html_block(f"""
        <div class="card detail">
        <div class="score-row"><span class="cap-label">Fit Score Breakdown</span>
        <span class="score-big">{fmt_num(total_s)} <small>/ 100</small></span></div>
        <div class="bar">
        <div style="width:{min(ind_s, 100)}%;background:var(--primary)"></div>
        <div style="width:{min(other, 100)}%;background:var(--primary-mid)"></div>
        <div style="width:{min(svc_s, 100)}%;background:var(--success)"></div>
        </div>
        <div class="mini-grid">
        <div class="mini"><div class="mini-l">Industry Fit</div><div class="mini-v">{fmt_num(ind_s)} <small>pts</small></div></div>
        <div class="mini"><div class="mini-l">Service Fit</div><div class="mini-v">{fmt_num(svc_s)} <small>pts</small></div></div>
        </div>
        <div class="route"><span class="k">Official Route:</span>
        <span class="v"><a href="{esc(href)}" target="_blank" rel="noopener">{esc(row['official_contact_route'] or row['official_domain'])}</a></span>
        <a href="{esc(href)}" target="_blank" rel="noopener">{icon('external', 15)}</a></div>
        <div class="gov">{icon('shield-alert', 26)}<div>
        <div class="gov-t">{esc(status)} (Outreach Disabled)</div>
        <div class="gov-d">Automated dispatch is locked until compliance verification is signed by an account lead. Strict GDPR policy requires valid opt-in trail.</div>
        </div></div>
        </div>
        """)
elif n == 0:
    st.info("Select filters that match at least one prospect to see rationale and evidence.")

# ----------------- EXPORT -----------------
html_block('<div class="exp-title">Export Deliverables</div>')
e1, e2 = st.columns(2)
with e1:
    with st.container(key="export_csv"):
        a, b = st.columns([9, 1], vertical_alignment="center")
        with a:
            html_block(f"""
            <div class="exp"><div class="exp-ico">{icon('file', 20)}</div><div>
            <div class="exp-t">Download Technical Raw Data (CSV)</div>
            <div class="exp-s">All qualified leads with scores, company details and evaluation data. {total} records.</div>
            """)
        with b:
            st.download_button("", data=df.to_csv(index=False).encode("utf-8"),
                               file_name="bright_tech_qualified_leads.csv", mime="text/csv",
                               key="dl_csv", icon=":material/download:", disabled=total == 0)
with e2:
    with st.container(key="export_xlsx"):
        a, b = st.columns([9, 1], vertical_alignment="center")
        xlsx_ready = os.path.exists(EXCEL_FILE)
        with a:
            sub = (
    "Formatted report with executive metrics, charts and priority rankings."
    if xlsx_ready
    else "The executive report is not available yet."
)
            html_block(f"""
            <div class="exp"><div class="exp-ico green">{icon('table', 20)}</div><div>
            <div class="exp-t">Download Formatted Executive Report (Excel)</div>
            <div class="exp-s">{sub}</div></div></div>
            """)
        with b:
            xlsx_bytes = open(EXCEL_FILE, "rb").read() if xlsx_ready else b""
            st.download_button("", data=xlsx_bytes, file_name=EXCEL_FILE,
                               mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                               key="dl_xlsx", icon=":material/download:", disabled=not xlsx_ready)

# ----------------- FOOTER -----------------
html_block(f"""
<div class="app-foot"><div class="n">{icon('shield', 18)}{esc(BRAND['footer_name'])}</div>
<div class="r">{esc(BRAND['footer_role'])}</div></div>
""")

# ----------------- LIVE SEARCH (types -> filters after a short pause) -----------------
LIVE_SEARCH_HTML = """
<script>
(function(){
  const doc = window.parent.document;
  function commit(input){
    const pos = input.selectionStart;
    ['keydown','keypress','keyup'].forEach(function(type){
      input.dispatchEvent(new KeyboardEvent(type,{key:'Enter',code:'Enter',keyCode:13,which:13,charCode:13,bubbles:true,cancelable:true}));
    });
    // blur/focus makes Streamlit commit the value even if the Enter event is ignored
    setTimeout(function(){
      input.blur(); input.focus();
      try{ input.setSelectionRange(pos,pos); }catch(e){}
    }, 40);
  }
  function attach(){
    const input = doc.querySelector('.st-key-q input');
    if(!input || input.dataset.live) return;
    input.dataset.live = '1';
    let t, last = input.value;
    input.addEventListener('input', function(){
      clearTimeout(t);
      t = setTimeout(function(){
        if(input.value === last) return;
        last = input.value;
        commit(input);
      }, 450);
    });
  }
  attach(); setInterval(attach, 700);
})();
</script>
"""
with st.container(key="live_js"):
    st.markdown(f"<style>{chip_css(list(FILTER_COLS))}</style>", unsafe_allow_html=True)
    if hasattr(st, "iframe"):
        st.iframe(LIVE_SEARCH_HTML, height=1)
    else:
        components.html(LIVE_SEARCH_HTML, height=0)