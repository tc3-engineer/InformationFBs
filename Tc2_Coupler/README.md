# Tc2_Coupler

> 老式 BK 耦合器（K-bus）的 PLC 操作库。版本 `1.1.1`。

- [官方 InfoSys](https://infosys.beckhoff.com/content/1033/tcplclib_tc2_coupler/)
- [官方 PDF](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf)
- [Roadmap](../_meta/roadmap-Tc2_Coupler.md)

## 索引（7 条 · 全部 ✅ verified）

| Category | Name | 文档 | 例程 |
|---|---|---|---|
| Function blocks | ReadWriteTerminalReg | [✅ verified](function_blocks/ReadWriteTerminalReg.md) | [P_Demo_ReadWriteTerminalReg.xml](examples/P_Demo_ReadWriteTerminalReg.xml) |
| Function blocks | CouplerReset | [✅ verified](function_blocks/CouplerReset.md) | [P_Demo_CouplerReset.xml](examples/P_Demo_CouplerReset.xml) |
| Function blocks | FB_ReadCouplerDiag | [✅ verified](function_blocks/FB_ReadCouplerDiag.md) | [P_Demo_FB_ReadCouplerDiag.xml](examples/P_Demo_FB_ReadCouplerDiag.xml) |
| Function blocks | FB_ReadCouplerRegs | [✅ verified](function_blocks/FB_ReadCouplerRegs.md) | [P_Demo_FB_ReadCouplerRegs.xml](examples/P_Demo_FB_ReadCouplerRegs.xml) |
| Function blocks | FB_WriteCouplerRegs | [✅ verified](function_blocks/FB_WriteCouplerRegs.md) | [P_Demo_FB_WriteCouplerRegs.xml](examples/P_Demo_FB_WriteCouplerRegs.xml) |
| [obsolete functions] | F_GetVersionTcPlcCoupler | [✅ verified](obsolete/F_GetVersionTcPlcCoupler.md) | [P_Demo_F_GetVersionTcPlcCoupler.xml](examples/P_Demo_F_GetVersionTcPlcCoupler.xml) |
| Library version | stLibVersion_Tc2_Coupler | [✅ verified](global_constants/stLibVersion_Tc2_Coupler.md) | [P_Demo_stLibVersion_Tc2_Coupler.xml](examples/P_Demo_stLibVersion_Tc2_Coupler.xml) |

## 使用须知

- 所有 FB 都依赖 **2-byte PLC interface**（端子的 Control/Status 字节），必须在 System Manager 链接对应 IO 变量。
- 寄存器修改后**断电重启耦合器**才会持久化。
- `F_GetVersionTcPlcCoupler` 已废弃，新代码请用 `stLibVersion_Tc2_Coupler`。
