# Tc2_Utilities

> 通用工具库（数学/字符串/字节序/系统/许可/CSV...）。版本 `2.18.2`，**总条目 343** （97 FB + 245 FC + 1 GVL）。

- [官方 InfoSys](https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/)
- [官方 PDF](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf)
- [Roadmap](../_meta/roadmap-Tc2_Utilities.md)

## 当前进度

> 因库规模庞大（343 条），按 category 分多批 doc-shard。

| Round | Categories | 条目 | 状态 |
|---|---|---|---|
| 1 | LCOMPLEX / FLOAT / [Obsolete] / 16-bit fixed-point / Byte order / Library version | 28 | ✅ done |
| - | TC_CoreBoostMonitor | 5 | ⏳ pending（OO 结构，需父子模板） |
| - | [obsolete] FB | 4 | ⏳ pending |
| - | Time functions | 23 | ⏳ pending |
| - | T_Arg help functions | 27 | ⏳ pending |
| - | P[TYPE]_TO_[TYPE] | 26 | ⏳ pending |
| - | Extended STRING | 30 | ⏳ pending |
| - | 64-bit functions (signed) | 15 | ⏳ pending |
| - | 64-bit integer (unsigned) | 31 | ⏳ pending |
| - | Functions（散） | 66 | ⏳ pending |
| - | Function blocks | 88 | ⏳ pending |

## Round 1 索引（28 条 · 全部 ✅ verified）

### LCOMPLEX functions（2）

| Name | 文档 | 例程 |
|---|---|---|
| LcomplexIsNaN | [✅](lcomplex/LcomplexIsNaN.md) | [P_Demo_LcomplexIsNaN.xml](examples/P_Demo_LcomplexIsNaN.xml) |
| LcomplexAbs | [✅](lcomplex/LcomplexAbs.md) | [P_Demo_LcomplexAbs.xml](examples/P_Demo_LcomplexAbs.xml) |

### FLOAT functions（4）

| Name | 文档 | 例程 |
|---|---|---|
| LrealIsFinite | [✅](float/LrealIsFinite.md) | [P_Demo_LrealIsFinite.xml](examples/P_Demo_LrealIsFinite.xml) |
| LrealIsNaN | [✅](float/LrealIsNaN.md) | [P_Demo_LrealIsNaN.xml](examples/P_Demo_LrealIsNaN.xml) |
| RealIsFinite | [✅](float/RealIsFinite.md) | [P_Demo_RealIsFinite.xml](examples/P_Demo_RealIsFinite.xml) |
| RealIsNaN | [✅](float/RealIsNaN.md) | [P_Demo_RealIsNaN.xml](examples/P_Demo_RealIsNaN.xml) |

### [Obsolete]（2）

| Name | 文档 | 例程 |
|---|---|---|
| FLOATIsFinite | [✅ deprecated](obsolete/FLOATIsFinite.md) | [P_Demo_FLOATIsFinite.xml](examples/P_Demo_FLOATIsFinite.xml) |
| FLOATIsNaN | [✅ deprecated](obsolete/FLOATIsNaN.md) | [P_Demo_FLOATIsNaN.xml](examples/P_Demo_FLOATIsNaN.xml) |

### 16 bit fixed-point number functions (signed)（9）

| Name | 文档 | 例程 |
|---|---|---|
| FIX16_TO_LREAL | [✅](fix16/FIX16_TO_LREAL.md) | [P_Demo_FIX16_TO_LREAL.xml](examples/P_Demo_FIX16_TO_LREAL.xml) |
| FIX16_TO_WORD | [✅](fix16/FIX16_TO_WORD.md) | [P_Demo_FIX16_TO_WORD.xml](examples/P_Demo_FIX16_TO_WORD.xml) |
| FIX16Add | [✅](fix16/FIX16Add.md) | [P_Demo_FIX16Add.xml](examples/P_Demo_FIX16Add.xml) |
| FIX16Align | [✅](fix16/FIX16Align.md) | [P_Demo_FIX16Align.xml](examples/P_Demo_FIX16Align.xml) |
| FIX16Div | [✅](fix16/FIX16Div.md) | [P_Demo_FIX16Div.xml](examples/P_Demo_FIX16Div.xml) |
| FIX16Mul | [✅](fix16/FIX16Mul.md) | [P_Demo_FIX16Mul.xml](examples/P_Demo_FIX16Mul.xml) |
| FIX16Sub | [✅](fix16/FIX16Sub.md) | [P_Demo_FIX16Sub.xml](examples/P_Demo_FIX16Sub.xml) |
| LREAL_TO_FIX16 | [✅](fix16/LREAL_TO_FIX16.md) | [P_Demo_LREAL_TO_FIX16.xml](examples/P_Demo_LREAL_TO_FIX16.xml) |
| WORD_TO_FIX16 | [✅](fix16/WORD_TO_FIX16.md) | [P_Demo_WORD_TO_FIX16.xml](examples/P_Demo_WORD_TO_FIX16.xml) |

### Byte order converting functions（10）

| Name | 文档 | 例程 |
|---|---|---|
| HOST_TO_BE16 | [✅](byte_order/HOST_TO_BE16.md) | [P_Demo_HOST_TO_BE16.xml](examples/P_Demo_HOST_TO_BE16.xml) |
| HOST_TO_BE32 | [✅](byte_order/HOST_TO_BE32.md) | [P_Demo_HOST_TO_BE32.xml](examples/P_Demo_HOST_TO_BE32.xml) |
| HOST_TO_BE64 | [✅](byte_order/HOST_TO_BE64.md) | [P_Demo_HOST_TO_BE64.xml](examples/P_Demo_HOST_TO_BE64.xml) |
| HOST_TO_BE64EX | [✅](byte_order/HOST_TO_BE64EX.md) | [P_Demo_HOST_TO_BE64EX.xml](examples/P_Demo_HOST_TO_BE64EX.xml) |
| HOST_TO_BE128 | [✅](byte_order/HOST_TO_BE128.md) | [P_Demo_HOST_TO_BE128.xml](examples/P_Demo_HOST_TO_BE128.xml) |
| BE16_TO_HOST | [✅](byte_order/BE16_TO_HOST.md) | [P_Demo_BE16_TO_HOST.xml](examples/P_Demo_BE16_TO_HOST.xml) |
| BE32_TO_HOST | [✅](byte_order/BE32_TO_HOST.md) | [P_Demo_BE32_TO_HOST.xml](examples/P_Demo_BE32_TO_HOST.xml) |
| BE64_TO_HOST | [✅](byte_order/BE64_TO_HOST.md) | [P_Demo_BE64_TO_HOST.xml](examples/P_Demo_BE64_TO_HOST.xml) |
| BE64_TO_HOSTEX | [✅](byte_order/BE64_TO_HOSTEX.md) | [P_Demo_BE64_TO_HOSTEX.xml](examples/P_Demo_BE64_TO_HOSTEX.xml) |
| BE128_TO_HOST | [✅](byte_order/BE128_TO_HOST.md) | [P_Demo_BE128_TO_HOST.xml](examples/P_Demo_BE128_TO_HOST.xml) |

### Library version（1）

| Name | 文档 | 例程 |
|---|---|---|
| stLibVersion_Tc2_Utilities | [✅](global_constants/stLibVersion_Tc2_Utilities.md) | [P_Demo_stLibVersion_Tc2_Utilities.xml](examples/P_Demo_stLibVersion_Tc2_Utilities.xml) |
