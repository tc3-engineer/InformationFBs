# Tc2_Standard

> IEC 61131-3 标准 POU 集合（TwinCAT 3 自带库），版本 `1.3.4`（2026-04-08）。

- [官方 InfoSys](https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/index.html)
- [官方 PDF](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf)
- [Roadmap](../_meta/roadmap-Tc2_Standard.md)

## 索引（32 条 · 全部 ✅ verified）

> 每条 verify 完成的条目都配套一个 TcPOU 例程文件（`examples/` 目录）。
> 导入方式：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选 .TcPOU 文件。详见 [`examples/README.md`](examples/README.md)。

### Function Blocks（13）

| Category | Name | 文档 | 例程 |
|---|---|---|---|
| Bistable | RS | [✅ verified](bistable/RS.md) | [P_Demo_RS.TcPOU](examples/P_Demo_RS.TcPOU) |
| Bistable | SR | [✅ verified](bistable/SR.md) | [P_Demo_SR.TcPOU](examples/P_Demo_SR.TcPOU) |
| Counter | CTD | [✅ verified](counter/CTD.md) | [P_Demo_CTD.TcPOU](examples/P_Demo_CTD.TcPOU) |
| Counter | CTU | [✅ verified](counter/CTU.md) | [P_Demo_CTU.TcPOU](examples/P_Demo_CTU.TcPOU) |
| Counter | CTUD | [✅ verified](counter/CTUD.md) | [P_Demo_CTUD.TcPOU](examples/P_Demo_CTUD.TcPOU) |
| Timer | TOF | [✅ verified](timer/TOF.md) | [P_Demo_TOF.TcPOU](examples/P_Demo_TOF.TcPOU) |
| Timer | TON | [✅ verified](timer/TON.md) | [P_Demo_TON.TcPOU](examples/P_Demo_TON.TcPOU) |
| Timer | TP | [✅ verified](timer/TP.md) | [P_Demo_TP.TcPOU](examples/P_Demo_TP.TcPOU) |
| Timer (LTIME) | LTOF | [✅ verified](timer_ltime/LTOF.md) | [P_Demo_LTOF.TcPOU](examples/P_Demo_LTOF.TcPOU) |
| Timer (LTIME) | LTON | [✅ verified](timer_ltime/LTON.md) | [P_Demo_LTON.TcPOU](examples/P_Demo_LTON.TcPOU) |
| Timer (LTIME) | LTP | [✅ verified](timer_ltime/LTP.md) | [P_Demo_LTP.TcPOU](examples/P_Demo_LTP.TcPOU) |
| Trigger | F_TRIG | [✅ verified](trigger/F_TRIG.md) | [P_Demo_F_TRIG.TcPOU](examples/P_Demo_F_TRIG.TcPOU) |
| Trigger | R_TRIG | [✅ verified](trigger/R_TRIG.md) | [P_Demo_R_TRIG.TcPOU](examples/P_Demo_R_TRIG.TcPOU) |

### Functions（18）

| Category | Name | 文档 | 例程 |
|---|---|---|---|
| String | CONCAT | [✅ verified](string/CONCAT.md) | [P_Demo_CONCAT.TcPOU](examples/P_Demo_CONCAT.TcPOU) |
| String | DELETE | [✅ verified](string/DELETE.md) | [P_Demo_DELETE.TcPOU](examples/P_Demo_DELETE.TcPOU) |
| String | FIND | [✅ verified](string/FIND.md) | [P_Demo_FIND.TcPOU](examples/P_Demo_FIND.TcPOU) |
| String | INSERT | [✅ verified](string/INSERT.md) | [P_Demo_INSERT.TcPOU](examples/P_Demo_INSERT.TcPOU) |
| String | LEFT | [✅ verified](string/LEFT.md) | [P_Demo_LEFT.TcPOU](examples/P_Demo_LEFT.TcPOU) |
| String | LEN | [✅ verified](string/LEN.md) | [P_Demo_LEN.TcPOU](examples/P_Demo_LEN.TcPOU) |
| String | MID | [✅ verified](string/MID.md) | [P_Demo_MID.TcPOU](examples/P_Demo_MID.TcPOU) |
| String | REPLACE | [✅ verified](string/REPLACE.md) | [P_Demo_REPLACE.TcPOU](examples/P_Demo_REPLACE.TcPOU) |
| String | RIGHT | [✅ verified](string/RIGHT.md) | [P_Demo_RIGHT.TcPOU](examples/P_Demo_RIGHT.TcPOU) |
| WString | WCONCAT | [✅ verified](wstring/WCONCAT.md) | [P_Demo_WCONCAT.TcPOU](examples/P_Demo_WCONCAT.TcPOU) |
| WString | WDELETE | [✅ verified](wstring/WDELETE.md) | [P_Demo_WDELETE.TcPOU](examples/P_Demo_WDELETE.TcPOU) |
| WString | WFIND | [✅ verified](wstring/WFIND.md) | [P_Demo_WFIND.TcPOU](examples/P_Demo_WFIND.TcPOU) |
| WString | WINSERT | [✅ verified](wstring/WINSERT.md) | [P_Demo_WINSERT.TcPOU](examples/P_Demo_WINSERT.TcPOU) |
| WString | WLEFT | [✅ verified](wstring/WLEFT.md) | [P_Demo_WLEFT.TcPOU](examples/P_Demo_WLEFT.TcPOU) |
| WString | WLEN | [✅ verified](wstring/WLEN.md) | [P_Demo_WLEN.TcPOU](examples/P_Demo_WLEN.TcPOU) |
| WString | WMID | [✅ verified](wstring/WMID.md) | [P_Demo_WMID.TcPOU](examples/P_Demo_WMID.TcPOU) |
| WString | WREPLACE | [✅ verified](wstring/WREPLACE.md) | [P_Demo_WREPLACE.TcPOU](examples/P_Demo_WREPLACE.TcPOU) |
| WString | WRIGHT | [✅ verified](wstring/WRIGHT.md) | [P_Demo_WRIGHT.TcPOU](examples/P_Demo_WRIGHT.TcPOU) |

### Global Constants（1）

| Category | Name | 文档 | 例程 |
|---|---|---|---|
| Library version | stLibVersion_Tc2_Standard | [✅ verified](global_constants/stLibVersion_Tc2_Standard.md) | [P_Demo_stLibVersion_Tc2_Standard.TcPOU](examples/P_Demo_stLibVersion_Tc2_Standard.TcPOU) |
