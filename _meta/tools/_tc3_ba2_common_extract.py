#!/usr/bin/env python3
"""
Library-specific extraction helper for Tc3_BA2_Common.

Reads PDF cached text and extracts per-entry:
  - section number
  - syntax block (FUNCTION_BLOCK / FUNCTION ... END_VAR)
  - description tables (Inputs / Outputs / In/Outs)
  - body prose (1st few paragraphs as narrative)
  - requirements (development env + min lib version)

Writes JSON to /tmp/tc3_ba2_common_extracts.json keyed by entry name.

NOT a public tool — only Tc3_BA2_Common consumes this.
"""
from __future__ import annotations
import re, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PDF_TXT = ROOT / '_meta/.pdf-cache/Tc3_BA2_Common.txt'

# Headings format: e.g. "4.3.2.1.1 FB_BA_PIDCtrl" — section, name (where name is FB_*/F_BA_*/BAComn*)
HEADING_RE = re.compile(r'^(\d+(?:\.\d+){2,6})\s+([A-Za-z_][\w]*)\s*$', re.MULTILINE)
TARGET_NAME_RE = re.compile(r'^(FB_BA_|F_BA_|BAComn_|stLibVersion_)')


def load_text() -> str:
    return PDF_TXT.read_text()


def collect_headings(text: str) -> list[tuple[str, str, int]]:
    """Return [(section, name, start_pos), ...] for relevant entries."""
    out = []
    for m in HEADING_RE.finditer(text):
        sec = m.group(1)
        name = m.group(2)
        if TARGET_NAME_RE.match(name):
            out.append((sec, name, m.start()))
    return out


def extract_sections(text: str) -> dict[str, dict]:
    """Map name -> {section, raw_body_text} by computing slices between adjacent
    headings."""
    headings = collect_headings(text)
    # Also need to find any next heading (not just relevant) to stop at.
    all_heads = [(m.group(1), m.group(2), m.start()) for m in HEADING_RE.finditer(text)]
    name_to = {}
    for i, (sec, name, start) in enumerate(headings):
        # find next heading anywhere (relevant or not)
        end = len(text)
        for j, (sec2, _, start2) in enumerate(all_heads):
            if start2 > start:
                end = start2
                break
        # Also ensure stop at top-level section change e.g. "4.4 ..." (no relevant POU)
        body = text[start:end]
        name_to[name] = {'section': sec, 'body': body}
    return name_to


def _strip_page_chrome(text: str) -> str:
    text = re.sub(r'=== PAGE \d+ ===\s*\n', '', text)
    text = re.sub(r'^Programming\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^TE\d+\s*\d*\s*Version:\s*\d+\.\d+\.\d+\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'^TE\d+\d*\s+Version:\s*\d+\.\d+\.\d+\s*$', '', text, flags=re.MULTILINE)
    return text


def find_syntax_block(body: str) -> str:
    """Find the FUNCTION_BLOCK / FUNCTION header through the matching END_VAR block.

    Returns verbatim syntax text including FUNCTION_BLOCK/FUNCTION header line(s),
    all VAR_INPUT/OUTPUT/IN_OUT regions, terminated at last END_VAR (or before
    next "Inputs"/"Outputs"/"Requirements" marker).
    """
    body_c = _strip_page_chrome(body)
    # Look for "Syntax" marker if present
    m = re.search(r'(?:^|\n)(?:Syntax\s*\n)?((?:FUNCTION_BLOCK|FUNCTION|VAR_INPUT|VAR_GLOBAL)[\s\S]*?)(?=\n\s*(?:Inputs|Outputs|Inputs/outputs|Properties|Requirements|Return value|Sample|Description)\b|\Z)', body_c)
    if not m:
        # Try GVL pattern
        m = re.search(r'(?:^|\n)(VAR_GLOBAL[\s\S]*?END_VAR)', body_c)
    if not m:
        return ''
    syntax = m.group(1)
    # Trim trailing junk after last END_VAR
    last = syntax.rfind('END_VAR')
    if last >= 0:
        syntax = syntax[:last + len('END_VAR')]
    return syntax.strip()


def find_inputs_tables(body: str) -> dict[str, list[dict]]:
    """Find Inputs / Outputs / Inputs/outputs description tables.

    PDF format is:
      Inputs
      Name Type Description
      bEn BOOL Enable of the controller.
      ...
      Outputs
      Name Type Description
      fY REAL ...

    Returns dict with keys 'inputs', 'outputs', 'inouts', 'inputs_const', 'properties'.
    Values are list of {name, type, desc} dicts.
    """
    body_c = _strip_page_chrome(body)
    out = {'inputs': [], 'outputs': [], 'inouts': [], 'inputs_const': [], 'properties': []}

    # Find every "Name Type Description" header and parse rows until next heading
    # or section-change.
    section_pat = re.compile(
        r'(?:^|\n)\s*(?:Inputs(?:/outputs)?(?:\s+CONSTANT\s+PERSISTENT)?|Outputs|Properties|Return value|Returns)\s*\n\s*Name\s+Type\s+(?:Access\s+)?Description\s*\n',
        re.IGNORECASE,
    )
    matches = list(section_pat.finditer(body_c))
    for i, m in enumerate(matches):
        # Determine label from full match (case-preserved)
        hdr = m.group(0)
        label_match = re.search(r'\b(Inputs/outputs|Inputs(?:\s+CONSTANT\s+PERSISTENT)?|Outputs|Properties|Returns|Return value)\b', hdr, re.IGNORECASE)
        if not label_match:
            continue
        label_raw = label_match.group(0).lower().strip()
        if 'inputs/outputs' in label_raw:
            key = 'inouts'
        elif 'constant' in label_raw:
            key = 'inputs_const'
        elif label_raw == 'inputs':
            key = 'inputs'
        elif label_raw == 'outputs':
            key = 'outputs'
        elif 'properties' in label_raw:
            key = 'properties'
        elif 'return' in label_raw:
            key = 'returns'
        else:
            continue
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body_c)
        chunk = body_c[start:end]
        # Stop at "Requirements" or "Sample" or next heading
        stop = re.search(r'\n\s*(Requirements|Sample|See also|Description of|^\d+\.\d+(?:\.\d+)*\s+\w+)\s*\n', chunk)
        if stop:
            chunk = chunk[:stop.start()]
        # Parse rows: lines like "Name TYPE Description text..."
        # Names can be split across lines. We greedily concatenate lines that
        # start with a name pattern, treating wrap-lines as continuation.
        rows = _parse_table_rows(chunk, has_access='properties' in label_raw)
        out.setdefault(key if key != 'returns' else 'inputs', [])
        if key == 'returns':
            # Returns is treated separately
            out.setdefault('returns', [])
            out['returns'].extend(rows)
        else:
            out[key].extend(rows)
    return out


def _parse_table_rows(chunk: str, has_access: bool = False) -> list[dict]:
    """Parse "Name Type Description" rows out of plain text.

    Heuristic: a row starts with an identifier (alnum_), followed by a recognised
    type token, then desc to end of line, with subsequent indented lines being
    desc continuation until the next identifier line.
    """
    # First, sometimes the Name is wrapped onto its own line if very long (e.g.
    # "fProportionalConsta\nnt"). Join such cases.
    lines = chunk.split('\n')
    rejoined = []
    i = 0
    while i < len(lines):
        ln = lines[i]
        # Check if the line looks like an unfinished identifier
        # (alnum_ with no space after)
        stripped = ln.strip()
        if stripped and re.match(r'^[A-Za-z_][A-Za-z0-9_]*$', stripped):
            # check next line: identifier continuation or actual type token
            if i + 1 < len(lines):
                next_stripped = lines[i + 1].strip()
                if re.match(r'^[A-Za-z_][A-Za-z0-9_]*\s+[A-Za-z_]', next_stripped):
                    # Looks like continuation of name: "(prefix)(continuation_type) ..."
                    # Combine if next starts lowercase and prev ends without complete identifier
                    pass
        rejoined.append(ln)
        i += 1
    chunk2 = '\n'.join(rejoined)

    # Naive row parser: walk lines, group when a new "name TYPE ..." starts
    rows = []
    cur = None
    name_type_re = re.compile(
        r'^\s*([A-Za-z_][A-Za-z0-9_]*(?:,\s*[A-Za-z_][A-Za-z0-9_]*)?)\s+'
        r'([A-Z_][\w\(\)\.\s\,]*?(?:\[\s*\}\s*\d+\s*\])?)\s+'
        r'(.+)$'
    )
    name_type_access_re = re.compile(
        r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s+'
        r'([A-Z_][\w\(\)\.\s\,]*?)\s+'
        r'(Get|Set|Get,\s*Set|Get/Set)\s+'
        r'(.+)$'
    )
    pure_name_re = re.compile(r'^\s*([A-Za-z_][A-Za-z0-9_]*)\s*$')
    type_token_re = re.compile(r'^[A-Z_][\w\(\)\.\s\,]+$')

    raw_lines = chunk2.split('\n')

    for raw in raw_lines:
        stripped = raw.strip()
        if not stripped:
            if cur:
                rows.append(cur)
                cur = None
            continue
        # Skip cross-ref hint pages like "[ }   29 ]"
        if re.match(r'^\[\s*\}\s*\d+\s*\]', stripped):
            if cur:
                cur['desc'] += ' ' + stripped
            continue
        if has_access:
            m = name_type_access_re.match(stripped)
        else:
            m = name_type_re.match(stripped)
        if m:
            if cur:
                rows.append(cur)
            if has_access:
                cur = {'name': m.group(1).strip(), 'type': m.group(2).strip(),
                       'access': m.group(3).strip(), 'desc': m.group(4).strip()}
            else:
                cur = {'name': m.group(1).strip(), 'type': m.group(2).strip(),
                       'desc': m.group(3).strip()}
        else:
            # continuation
            if cur:
                cur['desc'] += ' ' + stripped
    if cur:
        rows.append(cur)
    return rows


def find_requirements(body: str) -> dict:
    """Find requirements: development environment + required PLC lib min version."""
    body_c = _strip_page_chrome(body)
    m = re.search(r'Requirements\s*\nDevelopment environment\s+Required PLC library\s*\n([^\n]+)\s*\n', body_c)
    if not m:
        # Alt: try single line
        m2 = re.search(r'(TwinCAT\s+(?:from\s+)?v?3\.1\.\d+\.\d+)\s+(Tc3_(?:BA2?_Common|XBA)\s+from\s+v?\d+\.\d+\.\d+\.\d+)', body_c)
        if m2:
            return {'env': m2.group(1).strip(), 'lib': m2.group(2).strip()}
        return {'env': '', 'lib': ''}
    line = m.group(1)
    # Split: first token = env, rest = lib
    parts = re.split(r'\s{2,}', line.strip())
    if len(parts) >= 2:
        return {'env': parts[0].strip(), 'lib': ' '.join(parts[1:]).strip()}
    # Try by recognized prefix
    m3 = re.search(r'^(TwinCAT[\s\w\.]+?)(Tc3?_\w+\s+from\s+v?\d+\.[\d.]+)\s*$', line)
    if m3:
        return {'env': m3.group(1).strip(), 'lib': m3.group(2).strip()}
    return {'env': '', 'lib': line.strip()}


def find_prose_summary(body: str, name: str) -> str:
    """Pull the first 2-4 lines of prose after the heading (before 'Syntax' or
    'FUNCTION' or first table). This is the English description we'll translate."""
    body_c = _strip_page_chrome(body)
    lines = body_c.split('\n')
    # Skip the heading line
    out = []
    started = False
    for ln in lines[1:]:  # skip heading
        s = ln.strip()
        if not s:
            if started and len(out) > 0:
                break
            continue
        # Stop conditions
        if re.match(r'^(Syntax|FUNCTION_BLOCK|FUNCTION|VAR_INPUT|VAR_GLOBAL|Inputs|Outputs|Properties|Requirements|Sample)\b', s):
            break
        if re.match(r'^\d+\.\d+(?:\.\d+)+\s+\w+$', s):
            break
        # Collect
        out.append(s)
        started = True
        if len(out) > 8:
            break
    return ' '.join(out)


def main():
    text = load_text()
    sections = extract_sections(text)
    result = {}
    for name, info in sections.items():
        body = info['body']
        result[name] = {
            'section': info['section'],
            'syntax': find_syntax_block(body),
            'tables': find_inputs_tables(body),
            'requirements': find_requirements(body),
            'prose': find_prose_summary(body, name),
            'body_full': body,
        }
    out_path = Path('/tmp/tc3_ba2_common_extracts.json')
    out_path.write_text(json.dumps(result, indent=2, ensure_ascii=False))
    print(f'Wrote {len(result)} entries to {out_path}')


if __name__ == '__main__':
    main()
