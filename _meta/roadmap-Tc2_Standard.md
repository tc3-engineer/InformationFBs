# Roadmap · Tc2_Standard

- **Library Version**: `1.3.4`
- **PDF 发布日期**: `2026-04-08`
- **Source PDF**: https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf
- **InfoSys**: https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/
- **Discover 日期**: 2026-05-09（重新解析 2026-05-10）
- **总条目数**: 31（FB 13 + FC 18）
- **状态**: ✅ done（31/31 verified）

| # | Section | Name | Type | Category | Output Path | Status |
|---|---|---|---|---|---|---|
| 1 | 3.1.1 | RS | FB | Bistable | `Tc2_Standard/bistable/RS.md` | verified ✅ |
| 2 | 3.1.2 | SR | FB | Bistable | `Tc2_Standard/bistable/SR.md` | verified ✅ |
| 3 | 3.2.1 | CTD | FB | Counter | `Tc2_Standard/counter/CTD.md` | verified ✅ |
| 4 | 3.2.2 | CTU | FB | Counter | `Tc2_Standard/counter/CTU.md` | verified ✅ |
| 5 | 3.2.3 | CTUD | FB | Counter | `Tc2_Standard/counter/CTUD.md` | verified ✅ |
| 6 | 3.3.1 | TOF | FB | Timer | `Tc2_Standard/timer/TOF.md` | verified ✅ |
| 7 | 3.3.2 | TON | FB | Timer | `Tc2_Standard/timer/TON.md` | verified ✅ |
| 8 | 3.3.3 | TP | FB | Timer | `Tc2_Standard/timer/TP.md` | verified ✅ |
| 9 | 3.4.1 | LTOF | FB | Timer (LTIME) | `Tc2_Standard/timer_ltime/LTOF.md` | verified ✅ |
| 10 | 3.4.2 | LTON | FB | Timer (LTIME) | `Tc2_Standard/timer_ltime/LTON.md` | verified ✅ |
| 11 | 3.4.3 | LTP | FB | Timer (LTIME) | `Tc2_Standard/timer_ltime/LTP.md` | verified ✅ |
| 12 | 3.5.1 | F_TRIG | FB | Trigger | `Tc2_Standard/trigger/F_TRIG.md` | verified ✅ |
| 13 | 3.5.2 | R_TRIG | FB | Trigger | `Tc2_Standard/trigger/R_TRIG.md` | verified ✅ |
| 14 | 4.1 | CONCAT | FC | String functions | `Tc2_Standard/string/CONCAT.md` | verified ✅ |
| 15 | 4.2 | DELETE | FC | String functions | `Tc2_Standard/string/DELETE.md` | verified ✅ |
| 16 | 4.3 | FIND | FC | String functions | `Tc2_Standard/string/FIND.md` | verified ✅ |
| 17 | 4.4 | INSERT | FC | String functions | `Tc2_Standard/string/INSERT.md` | verified ✅ |
| 18 | 4.5 | LEFT | FC | String functions | `Tc2_Standard/string/LEFT.md` | verified ✅ |
| 19 | 4.6 | LEN | FC | String functions | `Tc2_Standard/string/LEN.md` | verified ✅ |
| 20 | 4.7 | MID | FC | String functions | `Tc2_Standard/string/MID.md` | verified ✅ |
| 21 | 4.8 | REPLACE | FC | String functions | `Tc2_Standard/string/REPLACE.md` | verified ✅ |
| 22 | 4.9 | RIGHT | FC | String functions | `Tc2_Standard/string/RIGHT.md` | verified ✅ |
| 23 | 5.1 | WCONCAT | FC | String functions (WSTRING) | `Tc2_Standard/wstring/WCONCAT.md` | verified ✅ |
| 24 | 5.2 | WDELETE | FC | String functions (WSTRING) | `Tc2_Standard/wstring/WDELETE.md` | verified ✅ |
| 25 | 5.3 | WFIND | FC | String functions (WSTRING) | `Tc2_Standard/wstring/WFIND.md` | verified ✅ |
| 26 | 5.4 | WINSERT | FC | String functions (WSTRING) | `Tc2_Standard/wstring/WINSERT.md` | verified ✅ |
| 27 | 5.5 | WLEFT | FC | String functions (WSTRING) | `Tc2_Standard/wstring/WLEFT.md` | verified ✅ |
| 28 | 5.6 | WLEN | FC | String functions (WSTRING) | `Tc2_Standard/wstring/WLEN.md` | verified ✅ |
| 29 | 5.7 | WMID | FC | String functions (WSTRING) | `Tc2_Standard/wstring/WMID.md` | verified ✅ |
| 30 | 5.8 | WREPLACE | FC | String functions (WSTRING) | `Tc2_Standard/wstring/WREPLACE.md` | verified ✅ |
| 31 | 5.9 | WRIGHT | FC | String functions (WSTRING) | `Tc2_Standard/wstring/WRIGHT.md` | verified ✅ |

## 完成证据

- 全部 31 条由 `python3 _meta/tools/verify_doc.py` 退出码 0
- 全部 31 个例程由 `python3 _meta/tools/lint_plcopen.py` 退出码 0
- verify 报告：`_meta/verify/Tc2_Standard/<name>.md`
