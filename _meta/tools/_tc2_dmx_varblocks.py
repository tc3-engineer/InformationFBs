#!/usr/bin/env python3
"""Library-scoped helper: print the verbatim VAR_INPUT/OUTPUT/IN_OUT code blocks
for a given Tc2_DMX FB section, exactly as they appear in the cached PDF, plus
the raw Name/Type/Description rows so the doc author can translate descriptions.
Usage: python3 _meta/tools/_tc2_dmx_varblocks.py <section>   (e.g. 4.1.2.4.1)
"""
import re,sys,subprocess
sec=sys.argv[1]
txt=subprocess.run(["python3","_meta/tools/extract_section.py","Tc2_DMX",sec],capture_output=True,text=True).stdout
# print the exact VAR blocks (between VAR_xxx and END_VAR)
for m in re.finditer(r"(VAR_(?:INPUT|OUTPUT|IN_OUT))\s*\n([\s\S]*?)END_VAR", txt):
    print(f"=== {m.group(1)} ===")
    print(m.group(1))
    for line in m.group(2).rstrip().split("\n"):
        if line.strip(): print(line)
    print("END_VAR")
    print()
# also dump first 6 lines of section (the English summary) for translation reference
print("=== SUMMARY (first lines) ===")
lines=[l for l in txt.split("\n") if l.strip()][1:8]
for l in lines: print(l)
