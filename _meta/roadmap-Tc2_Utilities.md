# Roadmap · Tc2_Utilities

- **Library Version**: `2.18.2`
- **Source PDF**: https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf
- **InfoSys**: https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/
- **Discover 日期**: 2026-05-10
- **总条目数**: 343（FB 97 + FC 245 + GVL 1）
- **状态**: 🚧 in_progress（144/344 verified · Round 1-6 done）

> **注**：parse_toc 升级后识别 OO parent FB（`TC_CoreBoostMonitor`），总条目 343→344。

## 分批策略

| Round | Categories | 条目 | 状态 |
|---|---|---|---|
| 1 | LCOMPLEX / FLOAT / [Obsolete] / 16-bit fixed-point / Byte order / Library version | 28 | ✅ done |
| 2 | Time functions | 23 | ✅ done |
| 3 | TC_CoreBoostMonitor (parent + 5 methods) + [obsolete] FB (4) | 10 | ✅ done |
| 4 | T_Arg help functions | 27 | ✅ done |
| 5 | P[TYPE]_TO_[TYPE] converting functions | 26 | ✅ done |
| 6 | Extended STRING functions | 30 | ✅ done |
| 7 (pending) | 64-bit functions (signed) | 15 | ⏳ |
| 7 (pending) | 64-bit functions (signed) | 15 | ⏳ |
| 8 (pending) | 64-bit integer functions (unsigned) | 31 | ⏳ |
| 9 (pending) | Functions（散） | 66 | ⏳ |
| 10 (pending) | Function blocks | 88 | ⏳ |

## Round 1 已完成（28 条）

| # | Section | Name | Type | Category | Status |
|---|---|---|---|---|---|
| 1 | 4.5.1 | LcomplexIsNaN | FC | LCOMPLEX functions | ✅ |
| 2 | 4.5.2 | LcomplexAbs | FC | LCOMPLEX functions | ✅ |
| 3 | 4.4.2 | LrealIsFinite | FC | FLOAT functions | ✅ |
| 4 | 4.4.3 | LrealIsNaN | FC | FLOAT functions | ✅ |
| 5 | 4.4.4 | RealIsFinite | FC | FLOAT functions | ✅ |
| 6 | 4.4.5 | RealIsNaN | FC | FLOAT functions | ✅ |
| 7 | 4.11.3 | FLOATIsFinite | FC | [Obsolete] | ✅ deprecated |
| 8 | 4.11.4 | FLOATIsNaN | FC | [Obsolete] | ✅ deprecated |
| 9 | 4.7.1 | FIX16_TO_LREAL | FC | 16-bit fixed-point | ✅ |
| 10 | 4.7.2 | FIX16_TO_WORD | FC | 16-bit fixed-point | ✅ |
| 11 | 4.7.3 | FIX16Add | FC | 16-bit fixed-point | ✅ |
| 12 | 4.7.4 | FIX16Align | FC | 16-bit fixed-point | ✅ |
| 13 | 4.7.5 | FIX16Div | FC | 16-bit fixed-point | ✅ |
| 14 | 4.7.6 | FIX16Mul | FC | 16-bit fixed-point | ✅ |
| 15 | 4.7.7 | FIX16Sub | FC | 16-bit fixed-point | ✅ |
| 16 | 4.7.8 | LREAL_TO_FIX16 | FC | 16-bit fixed-point | ✅ |
| 17 | 4.7.9 | WORD_TO_FIX16 | FC | 16-bit fixed-point | ✅ |
| 18 | 4.3.2 | HOST_TO_BE16 | FC | Byte order | ✅ |
| 19 | 4.3.3 | HOST_TO_BE32 | FC | Byte order | ✅ |
| 20 | 4.3.4 | HOST_TO_BE64 | FC | Byte order | ✅ |
| 21 | 4.3.5 | HOST_TO_BE64EX | FC | Byte order | ✅ |
| 22 | 4.3.6 | HOST_TO_BE128 | FC | Byte order | ✅ |
| 23 | 4.3.7 | BE16_TO_HOST | FC | Byte order | ✅ |
| 24 | 4.3.8 | BE32_TO_HOST | FC | Byte order | ✅ |
| 25 | 4.3.9 | BE64_TO_HOST | FC | Byte order | ✅ |
| 26 | 4.3.10 | BE64_TO_HOSTEX | FC | Byte order | ✅ |
| 27 | 4.3.11 | BE128_TO_HOST | FC | Byte order | ✅ |
| 28 | 6.1 | stLibVersion_Tc2_Utilities | GVL | Library version | ✅ |
