#!/usr/bin/env python3
"""BFS InfoSys nav crawler for Tc2_DMX (culture 1033). Follows every <id>.html
link found on each page (category pages list children; leaf pages link
siblings/parent/next). Records each page <title>. Reuses /tmp/dmxprobe cache.
Writes _meta/tools/_tc2_dmx_topics.json {map:{Name:url}, all:{id:title}}.
"""
import json, re, subprocess, os, sys, time
BASE="https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dmx"
CACHE="/tmp/dmxprobe"; os.makedirs(CACHE,exist_ok=True)

def get(tid):
    p=f"{CACHE}/{tid}.html"
    if not os.path.exists(p):
        code=subprocess.run(["curl","-s","-o",p,"-w","%{http_code}","--max-time","25",f"{BASE}/{tid}.html"],
                            capture_output=True,text=True).stdout.strip()
        if code!="200":
            open(p,"w").write(f"__HTTP_{code}__"); return None
        time.sleep(0.05)
    txt=open(p,encoding="utf-8",errors="replace").read()
    if txt.startswith("__HTTP_"): return None
    return txt

def title_of(html):
    m=re.search(r"<title>(.*?)</title>",html,re.S)
    return m.group(1).strip() if m else None

# seeds: index + every id we've seen from searches/crawls
SEEDS=["4329452299","4340797963",
 "2670492043","2670486283","2670488203","2670478603","2670450443",
 "2670458123","2670460043","2670461963","2670456203","2670476683",
 "55166859","2669681803","6200987659","55193739","55177227",
 "27021597819423755","576795787","577716619","2764043531",
 "18014401179938187","36028797549182603","36028797595759755","55192331",
 "2209688203","2670552715","55200779"]
seen=set(); titles={}; queue=list(dict.fromkeys(SEEDS))
while queue:
    tid=queue.pop(0)
    if tid in seen: continue
    seen.add(tid)
    html=get(tid)
    if html is None: continue
    titles[tid]=title_of(html)
    for m in re.findall(r"([0-9]{6,})\.html", html):
        if m not in seen and m not in queue: queue.append(m)

out={}
for tid,t in titles.items():
    if not t: continue
    name=t.split()[0]
    if name.startswith("FB_") or name.startswith("F_"):
        if name not in out or len(t)<len(out[name][1]):
            out[name]=(tid,t)
res={k:f"{BASE}/{v[0]}.html" for k,v in out.items()}
json.dump({"map":res,"all":titles},open("_meta/tools/_tc2_dmx_topics.json","w"),indent=2,ensure_ascii=False)
print(f"crawled {len(seen)} pages, FB topics found={len(res)}",file=sys.stderr)
for k in sorted(res): print(f"{k}\t{res[k].split('/')[-1]}")
