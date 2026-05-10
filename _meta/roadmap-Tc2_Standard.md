# Roadmap · Tc2_Standard

- **Library Version**: `1.3.4`
- **PDF 发布日期**: `2026-04-08`
- **Source PDF**: https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf
- **InfoSys**: https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/
- **Discover 日期**: 2026-05-09
- **总条目数**: 31（FB 13 + FC 18）

| # | Name | Type | Category | Output Path | Status |
|---|---|---|---|---|---|
| 1 | RS | FB | Bistable | `Tc2_Standard/bistable/RS.md` | verified ✅ |
| 2 | SR | FB | Bistable | `Tc2_Standard/bistable/SR.md` | verified ✅ |
| 3 | CTD | FB | Counter | `Tc2_Standard/counter/CTD.md` | pending |
| 4 | CTU | FB | Counter | `Tc2_Standard/counter/CTU.md` | pending |
| 5 | CTUD | FB | Counter | `Tc2_Standard/counter/CTUD.md` | pending |
| 6 | TOF | FB | Timer | `Tc2_Standard/timer/TOF.md` | pending |
| 7 | TON | FB | Timer | `Tc2_Standard/timer/TON.md` | verified ✅ |
| 8 | TP | FB | Timer | `Tc2_Standard/timer/TP.md` | pending |
| 9 | LTOF | FB | Timer (LTIME) | `Tc2_Standard/timer_ltime/LTOF.md` | pending |
| 10 | LTON | FB | Timer (LTIME) | `Tc2_Standard/timer_ltime/LTON.md` | pending |
| 11 | LTP | FB | Timer (LTIME) | `Tc2_Standard/timer_ltime/LTP.md` | pending |
| 12 | F_TRIG | FB | Trigger | `Tc2_Standard/trigger/F_TRIG.md` | pending |
| 13 | R_TRIG | FB | Trigger | `Tc2_Standard/trigger/R_TRIG.md` | pending |
| 14 | CONCAT | FC | String functions | `Tc2_Standard/string/CONCAT.md` | pending |
| 15 | DELETE | FC | String functions | `Tc2_Standard/string/DELETE.md` | pending |
| 16 | FIND | FC | String functions | `Tc2_Standard/string/FIND.md` | pending |
| 17 | INSERT | FC | String functions | `Tc2_Standard/string/INSERT.md` | pending |
| 18 | LEFT | FC | String functions | `Tc2_Standard/string/LEFT.md` | pending |
| 19 | LEN | FC | String functions | `Tc2_Standard/string/LEN.md` | pending |
| 20 | MID | FC | String functions | `Tc2_Standard/string/MID.md` | pending |
| 21 | REPLACE | FC | String functions | `Tc2_Standard/string/REPLACE.md` | pending |
| 22 | RIGHT | FC | String functions | `Tc2_Standard/string/RIGHT.md` | pending |
| 23 | WCONCAT | FC | String functions (WSTRING) | `Tc2_Standard/wstring/WCONCAT.md` | pending |
| 24 | WDELETE | FC | String functions (WSTRING) | `Tc2_Standard/wstring/WDELETE.md` | pending |
| 25 | WFIND | FC | String functions (WSTRING) | `Tc2_Standard/wstring/WFIND.md` | pending |
| 26 | WINSERT | FC | String functions (WSTRING) | `Tc2_Standard/wstring/WINSERT.md` | pending |
| 27 | WLEFT | FC | String functions (WSTRING) | `Tc2_Standard/wstring/WLEFT.md` | pending |
| 28 | WLEN | FC | String functions (WSTRING) | `Tc2_Standard/wstring/WLEN.md` | pending |
| 29 | WMID | FC | String functions (WSTRING) | `Tc2_Standard/wstring/WMID.md` | pending |
| 30 | WREPLACE | FC | String functions (WSTRING) | `Tc2_Standard/wstring/WREPLACE.md` | pending |
| 31 | WRIGHT | FC | String functions (WSTRING) | `Tc2_Standard/wstring/WRIGHT.md` | pending |

## 推荐执行顺序

```
/doc-shard Tc2_Standard Bistable           # 2 条（RS、SR 已 verified，跳过）
/doc-shard Tc2_Standard Counter            # 3 条
/doc-shard Tc2_Standard Timer              # 3 条（TON 已 verified，跳过）
/doc-shard Tc2_Standard Timer (LTIME)      # 3 条
/doc-shard Tc2_Standard Trigger            # 2 条
/doc-shard Tc2_Standard String functions   # 9 条 → 拆 1 批（≤12）
/doc-shard Tc2_Standard String functions (WSTRING)  # 9 条
```
