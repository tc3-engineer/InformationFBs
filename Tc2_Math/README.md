# Tc2_Math

> 数学辅助函数库（取整、模运算、小数提取等）。版本 `1.3.3`。

- [官方 InfoSys](https://infosys.beckhoff.com/content/1033/tcplclib_tc2_math/)
- [官方 PDF](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Math_EN.pdf)
- [Roadmap](../_meta/roadmap-Tc2_Math.md)

## 索引（9 条 · 全部 ✅ verified）

### Functions（7）

| Category | Name | 文档 | 例程 |
|---|---|---|---|
| Functions | CEIL | [✅ verified](functions/CEIL.md) | [P_Demo_CEIL.TcPOU](examples/P_Demo_CEIL.TcPOU) |
| Functions | FLOOR | [✅ verified](functions/FLOOR.md) | [P_Demo_FLOOR.TcPOU](examples/P_Demo_FLOOR.TcPOU) |
| Functions | FRAC | [✅ verified](functions/FRAC.md) | [P_Demo_FRAC.TcPOU](examples/P_Demo_FRAC.TcPOU) |
| Functions | LMOD | [✅ verified](functions/LMOD.md) | [P_Demo_LMOD.TcPOU](examples/P_Demo_LMOD.TcPOU) |
| Functions | LTRUNC | [✅ verified](functions/LTRUNC.md) | [P_Demo_LTRUNC.TcPOU](examples/P_Demo_LTRUNC.TcPOU) |
| Functions | MODABS | [✅ verified](functions/MODABS.md) | [P_Demo_MODABS.TcPOU](examples/P_Demo_MODABS.TcPOU) |
| Functions | MODTURNS | [✅ verified](functions/MODTURNS.md) | [P_Demo_MODTURNS.TcPOU](examples/P_Demo_MODTURNS.TcPOU) |

### [obsolete functions]（1）

| Category | Name | 文档 | 例程 |
|---|---|---|---|
| [obsolete functions] | F_GetVersionTcMath | [✅ verified](obsolete/F_GetVersionTcMath.md) | [P_Demo_F_GetVersionTcMath.TcPOU](examples/P_Demo_F_GetVersionTcMath.TcPOU) |

### Global Constants（1）

| Category | Name | 文档 | 例程 |
|---|---|---|---|
| Library version | stLibVersion_Tc2_Math | [✅ verified](global_constants/stLibVersion_Tc2_Math.md) | [P_Demo_stLibVersion_Tc2_Math.TcPOU](examples/P_Demo_stLibVersion_Tc2_Math.TcPOU) |

## 快速对照（取整与模运算族）

| 函数 | 类型 | 处理对象 | 符号行为 |
|---|---|---|---|
| `CEIL` | LREAL→LREAL | 浮点 | 朝 +∞（负数变小） |
| `FLOOR` | LREAL→LREAL | 浮点 | 朝 -∞（负数变大） |
| `LTRUNC` | LREAL→LREAL | 浮点 | 朝零（截断） |
| `FRAC` | LREAL→LREAL | 浮点小数部分 | 保留输入符号 |
| `LMOD` | (LREAL,LREAL)→LREAL | 浮点取模 | 保留输入符号 |
| `MODABS` | (LREAL,LREAL)→LREAL | 浮点取模 | 总返回非负（NC 常用） |
| `MODTURNS` | (LREAL,LREAL)→DINT | 圈数 | 带符号 |

`F_GetVersionTcMath` 已废弃——新代码请用 `stLibVersion_Tc2_Math`。
