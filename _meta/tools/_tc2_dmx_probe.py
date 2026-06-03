#!/usr/bin/env python3
"""Deterministic InfoSys topic prober for Tc2_DMX (culture 1033 only).
Probes a set of candidate numeric ids, records each page's <title>.
Confirmed anchors show a ~1920 stride in the 2670xxxxxx block (Low Level),
so we scan that block on the stride plus a few off-stride offsets, and also
probe explicit known ids for High Level / EL6851 / status.
Writes _meta/tools/_tc2_dmx_topics.json: {map: {Name:url}, all: {id:title}}.
"""
import json, re, subprocess, os, sys

BASE="https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx"
os.makedirs("/tmp/dmxprobe",exist_ok=True)

def get(tid):
    p=f"/tmp/dmxprobe/{tid}.html"
    if not os.path.exists(p):
        code=subprocess.run(["curl","-s","-o",p,"-w","%{http_code}","--max-time","25",f"{BASE}/{tid}.html"],
                            capture_output=True,text=True).stdout.strip()
        if code!="200":
            open(p,"w").write(f"__HTTP_{code}__")
            return None
    txt=open(p,encoding="utf-8",errors="replace").read()
    if txt.startswith("__HTTP_"): return None
    m=re.search(r"<title>(.*?)</title>",txt,re.S)
    return m.group(1).strip() if m else "(no title)"

# anchors confirmed for the 2670 block (TOC order)
# stride observed = 1920 between adjacent TOC leaves
anchors_2670 = 2670450443  # FB_DMXGetDeviceLabel area start-ish
# scan the whole 2670 low-level block generously on stride 1920 with +/- offsets
candidates=set()
start=2670440000
end=2670500000
for base in range(start, end, 1920):
    for off in (3, 43, 123, 203, 283, 363, 443, 523, 603, 683, 763, 1163, 1483, 1803, 2043):
        candidates.add(base+off)
# also explicit known/likely ids
for x in ["55166859","2669681803","2670458123","2670460043","2670461963",
          "2670450443","2670478603","2670486283","2670488203","2670492043",
          "2670456203","2670476683"]:
    candidates.add(int(x))

found={}
n=0
for tid in sorted(candidates):
    t=get(str(tid))
    n+=1
    if t and (t.startswith("FB_") or t.startswith("F_")):
        # keep bare names; ignore "X: Inputs/outputs" subpages by preferring shortest
        name=t.split()[0]
        if name not in found or len(t)<len(found[name][1]):
            found[name]=(str(tid),t)
print(f"probed {n} ids; matched {len(found)} FB titles",file=sys.stderr)
res={k:f"{BASE}/{v[0]}.html" for k,v in found.items()}
json.dump({"map":res,"all":{k:v[1] for k,v in found.items()}},
          open("_meta/tools/_tc2_dmx_topics.json","w"),indent=2,ensure_ascii=False)
for k in sorted(res): print(f"{k}\t{res[k]}")
