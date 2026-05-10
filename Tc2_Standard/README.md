# Tc2_Standard

> IEC 61131-3 标准 POU 集合（TwinCAT 3 自带库），版本 `1.3.4`（2026-04-08）。

- [官方 InfoSys](https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/index.html)
- [官方 PDF](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf)
- [Roadmap](../_meta/roadmap-Tc2_Standard.md)

## 索引（31 条 · 全部 ✅ verified）

> 每条 verify 完成的条目都配套一个 PLCopenXML 例程文件（`examples/` 目录）。
> 导入方式：右键 PLC 项目 → Import PLCopenXML → 选 `.xml` 文件。详见 [`examples/README.md`](examples/README.md)。

### Function Blocks（13）

| Category | Name | 文档 | 例程 |
|---|---|---|---|
| Bistable | RS | [✅ verified](bistable/RS.md) | [P_Demo_RS.xml](examples/P_Demo_RS.xml) |
| Bistable | SR | [✅ verified](bistable/SR.md) | [P_Demo_SR.xml](examples/P_Demo_SR.xml) |
| Counter | CTD | [✅ verified](counter/CTD.md) | [P_Demo_CTD.xml](examples/P_Demo_CTD.xml) |
| Counter | CTU | [✅ verified](counter/CTU.md) | [P_Demo_CTU.xml](examples/P_Demo_CTU.xml) |
| Counter | CTUD | [✅ verified](counter/CTUD.md) | [P_Demo_CTUD.xml](examples/P_Demo_CTUD.xml) |
| Timer | TOF | [✅ verified](timer/TOF.md) | [P_Demo_TOF.xml](examples/P_Demo_TOF.xml) |
| Timer | TON | [✅ verified](timer/TON.md) | [P_Demo_TON.xml](examples/P_Demo_TON.xml) |
| Timer | TP | [✅ verified](timer/TP.md) | [P_Demo_TP.xml](examples/P_Demo_TP.xml) |
| Timer (LTIME) | LTOF | [✅ verified](timer_ltime/LTOF.md) | [P_Demo_LTOF.xml](examples/P_Demo_LTOF.xml) |
| Timer (LTIME) | LTON | [✅ verified](timer_ltime/LTON.md) | [P_Demo_LTON.xml](examples/P_Demo_LTON.xml) |
| Timer (LTIME) | LTP | [✅ verified](timer_ltime/LTP.md) | [P_Demo_LTP.xml](examples/P_Demo_LTP.xml) |
| Trigger | F_TRIG | [✅ verified](trigger/F_TRIG.md) | [P_Demo_F_TRIG.xml](examples/P_Demo_F_TRIG.xml) |
| Trigger | R_TRIG | [✅ verified](trigger/R_TRIG.md) | [P_Demo_R_TRIG.xml](examples/P_Demo_R_TRIG.xml) |

### Functions（18）

| Category | Name | 文档 | 例程 |
|---|---|---|---|
| String | CONCAT | [✅ verified](string/CONCAT.md) | [P_Demo_CONCAT.xml](examples/P_Demo_CONCAT.xml) |
| String | DELETE | [✅ verified](string/DELETE.md) | [P_Demo_DELETE.xml](examples/P_Demo_DELETE.xml) |
| String | FIND | [✅ verified](string/FIND.md) | [P_Demo_FIND.xml](examples/P_Demo_FIND.xml) |
| String | INSERT | [✅ verified](string/INSERT.md) | [P_Demo_INSERT.xml](examples/P_Demo_INSERT.xml) |
| String | LEFT | [✅ verified](string/LEFT.md) | [P_Demo_LEFT.xml](examples/P_Demo_LEFT.xml) |
| String | LEN | [✅ verified](string/LEN.md) | [P_Demo_LEN.xml](examples/P_Demo_LEN.xml) |
| String | MID | [✅ verified](string/MID.md) | [P_Demo_MID.xml](examples/P_Demo_MID.xml) |
| String | REPLACE | [✅ verified](string/REPLACE.md) | [P_Demo_REPLACE.xml](examples/P_Demo_REPLACE.xml) |
| String | RIGHT | [✅ verified](string/RIGHT.md) | [P_Demo_RIGHT.xml](examples/P_Demo_RIGHT.xml) |
| WString | WCONCAT | [✅ verified](wstring/WCONCAT.md) | [P_Demo_WCONCAT.xml](examples/P_Demo_WCONCAT.xml) |
| WString | WDELETE | [✅ verified](wstring/WDELETE.md) | [P_Demo_WDELETE.xml](examples/P_Demo_WDELETE.xml) |
| WString | WFIND | [✅ verified](wstring/WFIND.md) | [P_Demo_WFIND.xml](examples/P_Demo_WFIND.xml) |
| WString | WINSERT | [✅ verified](wstring/WINSERT.md) | [P_Demo_WINSERT.xml](examples/P_Demo_WINSERT.xml) |
| WString | WLEFT | [✅ verified](wstring/WLEFT.md) | [P_Demo_WLEFT.xml](examples/P_Demo_WLEFT.xml) |
| WString | WLEN | [✅ verified](wstring/WLEN.md) | [P_Demo_WLEN.xml](examples/P_Demo_WLEN.xml) |
| WString | WMID | [✅ verified](wstring/WMID.md) | [P_Demo_WMID.xml](examples/P_Demo_WMID.xml) |
| WString | WREPLACE | [✅ verified](wstring/WREPLACE.md) | [P_Demo_WREPLACE.xml](examples/P_Demo_WREPLACE.xml) |
| WString | WRIGHT | [✅ verified](wstring/WRIGHT.md) | [P_Demo_WRIGHT.xml](examples/P_Demo_WRIGHT.xml) |

### Global Constants

- `stLibVersion_Tc2_Standard : ST_LibVersion`
