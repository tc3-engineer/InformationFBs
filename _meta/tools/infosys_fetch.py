#!/usr/bin/env python3
"""
Fetch + parse a Beckhoff InfoSys topic page and emit structured FB/method info.

The HTML is fully server-rendered (the SPA assumption in CLAUDE.md is stale).
A topic page typically contains:
  <pre class="prettyprint lang-st"><code>...METHOD Foo : HRESULT<br/>...
        a : T;<br/>END_VAR</code></pre>
  <h2>Inputs</h2><table>...</table>
  <h2>Outputs</h2>... (optional)
  <h2>Return value</h2><table>... (optional, for methods)

Usage:
  python3 _meta/tools/infosys_fetch.py <url>

Output: JSON to stdout with:
  {
    "url": "...",
    "title": "...",
    "syntax": "<verbatim ST code block>",
    "inputs":  [{"name": "...", "type": "...", "desc": "..."}],
    "outputs": [...],
    "in_out":  [...],
    "return":  {"name": "...", "type": "HRESULT", "desc": "..."} | null,
    "html_sha1": "..."
  }

Cache: HTML stored under _meta/.infosys-cache/<sha1>.html (24h TTL).
"""
from __future__ import annotations

import argparse
import hashlib
import html as htmllib
import json
import re
import sys
import time
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / "_meta" / ".infosys-cache"
CACHE.mkdir(parents=True, exist_ok=True)
TTL_SEC = 24 * 3600


def fetch_html(url: str) -> str:
    key = hashlib.sha1(url.encode()).hexdigest()
    cache_p = CACHE / f"{key}.html"
    meta_p = CACHE / f"{key}.url"
    if cache_p.exists() and (time.time() - cache_p.stat().st_mtime) < TTL_SEC:
        return cache_p.read_text()
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "tc3-libraries-kb-audit/1.0"},
    )
    with urllib.request.urlopen(req, timeout=30) as resp:
        raw = resp.read().decode("utf-8", errors="replace")
    cache_p.write_text(raw)
    meta_p.write_text(url)
    return raw


def _strip_tags(s: str) -> str:
    s = re.sub(r"<br\s*/?>", "\n", s, flags=re.I)
    s = re.sub(r"<[^>]+>", "", s)
    return htmllib.unescape(s).strip()


SYNTAX_RE = re.compile(
    r'<pre[^>]*lang-st[^>]*>.*?<code[^>]*>(.*?)</code>\s*</pre>',
    re.IGNORECASE | re.DOTALL,
)
TITLE_RE = re.compile(r'<h1[^>]*>(.*?)</h1>', re.IGNORECASE | re.DOTALL)
SUBHEADING_RE = re.compile(
    r'<h2[^>]*subheading[^>]*>(?:\s*<img[^>]*>)?\s*([^<]+?)\s*</h2>(.*?)(?=<h2[^>]*subheading|</article>|</body>)',
    re.IGNORECASE | re.DOTALL,
)
ROW_RE = re.compile(r'<tr[^>]*>(.*?)</tr>', re.IGNORECASE | re.DOTALL)
CELL_RE = re.compile(r'<t[dh][^>]*>(.*?)</t[dh]>', re.IGNORECASE | re.DOTALL)


def _rows_from_table(section_html: str) -> list[list[str]]:
    table = re.search(r'<table[^>]*>(.*?)</table>', section_html, re.I | re.S)
    if not table:
        return []
    rows = []
    for rm in ROW_RE.finditer(table.group(1)):
        cells = [_strip_tags(c.group(1)) for c in CELL_RE.finditer(rm.group(1))]
        if cells:
            rows.append(cells)
    return rows


def _vars_from_section(section_html: str) -> list[dict]:
    rows = _rows_from_table(section_html)
    out = []
    for r in rows[1:]:
        if len(r) >= 2:
            out.append(
                {"name": r[0], "type": r[1], "desc": r[2] if len(r) >= 3 else ""}
            )
    return out


def parse(url: str) -> dict:
    html = fetch_html(url)
    title_m = TITLE_RE.search(html)
    title = _strip_tags(title_m.group(1)) if title_m else ""

    syntax = ""
    sm = SYNTAX_RE.search(html)
    if sm:
        syntax = _strip_tags(sm.group(1))

    inputs: list[dict] = []
    outputs: list[dict] = []
    in_out: list[dict] = []
    ret: dict | None = None

    for sm2 in SUBHEADING_RE.finditer(html):
        label = sm2.group(1).strip().lower()
        body = sm2.group(2)
        if label.startswith("input"):
            inputs = _vars_from_section(body)
        elif label.startswith("output"):
            outputs = _vars_from_section(body)
        elif "in/out" in label or "inout" in label or "in_out" in label:
            in_out = _vars_from_section(body)
        elif label.startswith("return"):
            rows = _vars_from_section(body)
            if rows:
                ret = rows[0]

    return {
        "url": url,
        "title": title,
        "syntax": syntax,
        "inputs": inputs,
        "outputs": outputs,
        "in_out": in_out,
        "return": ret,
        "html_sha1": hashlib.sha1(html.encode()).hexdigest(),
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("url", nargs="?")
    args = ap.parse_args()
    if not args.url:
        ap.print_help()
        return 1
    result = parse(args.url)
    json.dump(result, sys.stdout, ensure_ascii=False, indent=2)
    sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
