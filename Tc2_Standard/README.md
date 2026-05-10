# Tc2_Standard

> IEC 61131-3 标准 POU 集合（TwinCAT 3 自带库），版本 `1.3.4`（2026-04-08）。

- [官方 InfoSys](https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/index.html)
- [官方 PDF](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf)
- [Roadmap](../_meta/roadmap-Tc2_Standard.md)

## 索引（31 条 · 已 verify 3）

> 每条 verify 完成的条目都配套一个 PLCopenXML 例程文件（`examples/` 目录）。
> 导入方式：右键 PLC 项目 → Import PLCopenXML → 选 `.xml` 文件。详见 [`examples/README.md`](examples/README.md)。

### Function Blocks（13）

| Category | Name | 文档 | 例程 |
|---|---|---|---|
| Bistable | RS | [✅ verified](bistable/RS.md) | [P_Demo_RS.xml](examples/P_Demo_RS.xml) |
| Bistable | SR | [✅ verified](bistable/SR.md) | [P_Demo_SR.xml](examples/P_Demo_SR.xml) |
| Counter | CTD | [⏳ pending](counter/CTD.md) | - |
| Counter | CTU | [⏳ pending](counter/CTU.md) | - |
| Counter | CTUD | [⏳ pending](counter/CTUD.md) | - |
| Timer | TOF | [⏳ pending](timer/TOF.md) | - |
| Timer | TON | [✅ verified](timer/TON.md) | [P_Demo_TON.xml](examples/P_Demo_TON.xml) |
| Timer | TP | [⏳ pending](timer/TP.md) | - |
| Timer (LTIME) | LTOF | [⏳ pending](timer_ltime/LTOF.md) | - |
| Timer (LTIME) | LTON | [⏳ pending](timer_ltime/LTON.md) | - |
| Timer (LTIME) | LTP | [⏳ pending](timer_ltime/LTP.md) | - |
| Trigger | F_TRIG | [⏳ pending](trigger/F_TRIG.md) | - |
| Trigger | R_TRIG | [⏳ pending](trigger/R_TRIG.md) | - |

### Functions（18）

| Category | Name | 文档 | 例程 |
|---|---|---|---|
| String | CONCAT | [⏳ pending](string/CONCAT.md) | - |
| String | DELETE | [⏳ pending](string/DELETE.md) | - |
| String | FIND | [⏳ pending](string/FIND.md) | - |
| String | INSERT | [⏳ pending](string/INSERT.md) | - |
| String | LEFT | [⏳ pending](string/LEFT.md) | - |
| String | LEN | [⏳ pending](string/LEN.md) | - |
| String | MID | [⏳ pending](string/MID.md) | - |
| String | REPLACE | [⏳ pending](string/REPLACE.md) | - |
| String | RIGHT | [⏳ pending](string/RIGHT.md) | - |
| WString | WCONCAT | [⏳ pending](wstring/WCONCAT.md) | - |
| WString | WDELETE | [⏳ pending](wstring/WDELETE.md) | - |
| WString | WFIND | [⏳ pending](wstring/WFIND.md) | - |
| WString | WINSERT | [⏳ pending](wstring/WINSERT.md) | - |
| WString | WLEFT | [⏳ pending](wstring/WLEFT.md) | - |
| WString | WLEN | [⏳ pending](wstring/WLEN.md) | - |
| WString | WMID | [⏳ pending](wstring/WMID.md) | - |
| WString | WREPLACE | [⏳ pending](wstring/WREPLACE.md) | - |
| WString | WRIGHT | [⏳ pending](wstring/WRIGHT.md) | - |

### Global Constants

- `stLibVersion_Tc2_Standard : ST_LibVersion`
