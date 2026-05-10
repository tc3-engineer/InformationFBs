#!/usr/bin/env python3
"""
Download Beckhoff library PDF and extract per-page text into the cache.

Usage:
    python3 _meta/tools/fetch_pdf.py <Library_Name>
    python3 _meta/tools/fetch_pdf.py --all     # iterate library-catalog.md

Outputs (under _meta/.pdf-cache/):
    <Library>.pdf       raw PDF
    <Library>.txt       full text, concatenated with form-feed separators per page
    <Library>.meta.json {url, http_status, sha256, page_count, version, fetched_utc}

Exit codes:
    0 = success (text cached and version found)
    2 = HTTP error (PDF not reachable -> caller writes blocked.md)
    3 = PDF parse error
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "_meta" / ".pdf-cache"
URL_TMPL = (
    "https://download.beckhoff.com/download/document/automation/twincat3/"
    "TwinCAT_3_PLC_Lib_{lib}_EN.pdf"
)

# Libraries that don't follow the standard `TwinCAT_3_PLC_Lib_<NAME>_EN.pdf`
# convention. Most are TwinCAT Functions (TF-numbered products) where the FBs
# we want are documented inside the product manual instead of a separate PLC
# library doc. Verified reachable on 2026-05-10.
URL_ALIASES: dict[str, str] = {
    "Tc2_NC": "https://download.beckhoff.com/download/document/automation/twincat3/TF50x0_TC3_NC_PTP_EN.pdf",
    "Tc2_TcpIp": "https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf",
    "Tc2_SerialCom": "https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf",
    "Tc2_ModbusSrv": "https://download.beckhoff.com/download/document/automation/twincat3/TF6250_TC3_Modbus_TCP_EN.pdf",
    "Tc2_ModbusRTU": "https://download.beckhoff.com/download/document/automation/twincat3/TF6255_TC3_Modbus_RTU_EN.pdf",
    "Tc2_EthernetIP": "https://download.beckhoff.com/download/document/automation/twincat3/TF6280_EtherNet_IP_Adapter_EN.pdf",
    "Tc3_Database": "https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf",
    "Tc2_Database": "https://download.beckhoff.com/download/document/automation/twincat2/TS6420_tcdbserver_en.pdf",
    "Tc2_Filter": "https://download.beckhoff.com/download/document/automation/twincat3/TF3680_TC3_Filter_EN.pdf",
    "Tc2_MC2_Camming": "https://download.beckhoff.com/download/document/automation/twincat3/TF5050_TC3_NC_Camming_EN.pdf",
    "Tc2_MC2_FlyingSaw": "https://download.beckhoff.com/download/document/automation/twincat3/TF5055_TC3_NC_Flying_Saw_EN.pdf",
    "Tc2_NCI": "https://download.beckhoff.com/download/document/automation/twincat3/TF5100_TC3_NC_I_EN.pdf",
    "Tc3_Vision": "https://download.beckhoff.com/download/document/automation/twincat3/TF7000-TF7810_TC3_Vision_EN.pdf",
    "Tc2_Hydraulic": "https://download.beckhoff.com/download/document/automation/twincat3/TF5810_TC3_Hydraulic_Positioning_EN.pdf",
    "Tc2_BACnet": "https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf",
    "Tc3_BA2": "https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf",
    "Tc2_HVAC": "https://download.beckhoff.com/download/document/automation/twincat3/TF8000_TC3_HVAC_EN.pdf",
    "Tc2_Lighting": "https://download.beckhoff.com/download/document/automation/twincat3/TF8050_LS_EN.pdf",
    # Tc2_KNXLib — no public PDF found (TF8030 returns 404). Leave unaliased.
}


def _resolve_url(lib: str) -> str:
    """Return the canonical PDF URL for `lib`, honoring aliases."""
    return URL_ALIASES.get(lib, URL_TMPL.format(lib=lib))


TTL_SECONDS = 24 * 3600
USER_AGENT = "tc3-libraries-kb/1.0 (+https://github.com/tc3-engineer/informationfbs)"


def _http_get(url: str, timeout: int = 60) -> tuple[int, bytes]:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, b""


def _http_head(url: str, timeout: int = 30) -> int:
    """Probe a URL without downloading the full body.

    Some Beckhoff endpoints return 0/connection-close on HEAD; fall back to a
    Range GET asking for the first 1 KB.
    """
    req = urllib.request.Request(url, method="HEAD", headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        pass
    # fallback: Range GET (servers typically honor and return 206 or 200)
    req = urllib.request.Request(
        url, headers={"User-Agent": USER_AGENT, "Range": "bytes=0-1023"}
    )
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            # treat 200 / 206 as OK
            return r.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return 0


def _extract_text(pdf_bytes: bytes) -> tuple[str, int]:
    import pypdf  # local import so failures surface clearly
    import io

    reader = pypdf.PdfReader(io.BytesIO(pdf_bytes))
    chunks = []
    for i, page in enumerate(reader.pages):
        chunks.append(f"\n=== PAGE {i + 1} ===\n")
        chunks.append(page.extract_text() or "")
    return "".join(chunks), len(reader.pages)


def _find_version(text: str) -> str | None:
    m = re.search(r"Version[:\s]+(\d+\.\d+(?:\.\d+)?)", text)
    return m.group(1) if m else None


def fetch(lib: str, force: bool = False) -> dict:
    CACHE.mkdir(parents=True, exist_ok=True)
    pdf_path = CACHE / f"{lib}.pdf"
    txt_path = CACHE / f"{lib}.txt"
    meta_path = CACHE / f"{lib}.meta.json"

    fresh = (
        not force
        and meta_path.exists()
        and pdf_path.exists()
        and txt_path.exists()
        and (time.time() - meta_path.stat().st_mtime) < TTL_SECONDS
    )
    if fresh:
        meta = json.loads(meta_path.read_text())
        meta["from_cache"] = True
        return meta

    url = _resolve_url(lib)
    status, body = _http_get(url)
    if status != 200 or not body.startswith(b"%PDF"):
        meta = {
            "library": lib,
            "url": url,
            "http_status": status,
            "ok": False,
            "fetched_utc": datetime.now(timezone.utc).isoformat(),
            "error": "HTTP non-200" if status != 200 else "Not a PDF",
        }
        meta_path.write_text(json.dumps(meta, indent=2))
        return meta

    pdf_path.write_bytes(body)
    text, pages = _extract_text(body)
    txt_path.write_text(text)
    meta = {
        "library": lib,
        "url": url,
        "http_status": 200,
        "ok": True,
        "sha256": hashlib.sha256(body).hexdigest(),
        "size_bytes": len(body),
        "page_count": pages,
        "version": _find_version(text),
        "fetched_utc": datetime.now(timezone.utc).isoformat(),
    }
    meta_path.write_text(json.dumps(meta, indent=2))
    return meta


def main() -> int:
    p = argparse.ArgumentParser()
    p.add_argument("library", nargs="?")
    p.add_argument("--all", action="store_true", help="preflight every lib in catalog")
    p.add_argument("--force", action="store_true", help="ignore cache TTL")
    p.add_argument("--head-only", action="store_true", help="HEAD request only (preflight)")
    args = p.parse_args()

    if args.all or args.head_only:
        return preflight(head_only=args.head_only)

    if not args.library:
        p.error("library name required")

    meta = fetch(args.library, force=args.force)
    print(json.dumps(meta, indent=2, ensure_ascii=False))
    if not meta.get("ok"):
        return 2
    return 0


# ---------------------------------------------------------------------------
# Pre-flight against catalog
# ---------------------------------------------------------------------------
CATALOG = ROOT / "_meta" / "library-catalog.md"


def _libs_from_catalog() -> list[str]:
    libs: list[str] = []
    if not CATALOG.exists():
        return libs
    pat = re.compile(r"\|\s*(Tc[23]_[A-Za-z0-9_]+)\s*\|")
    for line in CATALOG.read_text().splitlines():
        m = pat.search(line)
        if m and m.group(1) not in libs:
            libs.append(m.group(1))
    return libs


def preflight(head_only: bool = True) -> int:
    CACHE.mkdir(parents=True, exist_ok=True)
    libs = _libs_from_catalog()
    out = []
    for lib in libs:
        url = _resolve_url(lib)
        if head_only:
            status = _http_head(url)
            # 200 = full GET fallback, 206 = Range GET partial content; both reachable.
            out.append({"library": lib, "http_status": status, "ok": status in (200, 206)})
        else:
            meta = fetch(lib)
            out.append(meta)
        print(f"{lib:24s}  {out[-1].get('http_status')}  {'OK' if out[-1].get('ok') else 'FAIL'}")
    report = CACHE / "preflight.json"
    report.write_text(json.dumps(out, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
