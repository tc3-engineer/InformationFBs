# Tc2_SUPS

> 1-second UPS 控制库（断电时自动保存持久数据 + quick shutdown）。版本 `1.5.2`。

- [官方 InfoSys](https://infosys.beckhoff.com/content/1033/tcplclib_tc2_sups/)
- [官方 PDF](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_SUPS_EN.pdf)
- [Roadmap](../_meta/roadmap-Tc2_SUPS.md)

## 索引（7 条 · 全部 ✅ verified）

| Category | Name | 文档 | 例程 |
|---|---|---|---|
| CB3011 | FB_S_UPS_CB3011 | [✅ verified](cb3011/FB_S_UPS_CB3011.md) | [P_Demo_FB_S_UPS_CB3011.xml](examples/P_Demo_FB_S_UPS_CB3011.xml) |
| CX50x0 | FB_S_UPS | [✅ verified](cx50x0/FB_S_UPS.md) | [P_Demo_FB_S_UPS.xml](examples/P_Demo_FB_S_UPS.xml) |
| CX51x0 | FB_S_UPS_CX51x0 | [✅ verified](cx51x0/FB_S_UPS_CX51x0.md) | [P_Demo_FB_S_UPS_CX51x0.xml](examples/P_Demo_FB_S_UPS_CX51x0.xml) |
| CX9020-U900 | FB_S_UPS_CX9020_U900 | [✅ verified](cx9020_u900/FB_S_UPS_CX9020_U900.md) | [P_Demo_FB_S_UPS_CX9020_U900.xml](examples/P_Demo_FB_S_UPS_CX9020_U900.xml) |
| BAPI | FB_S_UPS_BAPI | [✅ verified](bapi/FB_S_UPS_BAPI.md) | [P_Demo_FB_S_UPS_BAPI.xml](examples/P_Demo_FB_S_UPS_BAPI.xml) |
| Function blocks | FB_NT_QuickShutdown | [✅ verified](function_blocks/FB_NT_QuickShutdown.md) | [P_Demo_FB_NT_QuickShutdown.xml](examples/P_Demo_FB_NT_QuickShutdown.xml) |
| Library version | stLibVersion_Tc2_SUPS | [✅ verified](global_constants/stLibVersion_Tc2_SUPS.md) | [P_Demo_stLibVersion_Tc2_SUPS.xml](examples/P_Demo_stLibVersion_Tc2_SUPS.xml) |

## 选用指南（按硬件）

- **CB3011 主板** → `FB_S_UPS_CB3011`
- **CX50x0 嵌入式 PC** → `FB_S_UPS`
- **CX51x0 嵌入式 PC** → `FB_S_UPS_CX51x0`
- **CX9020-U900** → `FB_S_UPS_CX9020_U900`
- **带 BIOS-API ≥ v1.15 的设备** → `FB_S_UPS_BAPI`（推荐，未来兼容性最好）
- 其他硬件 → 看 InfoSys 设备页确认型号

`FB_NT_QuickShutdown` 是内部 helper，**生产代码不要直接调用**。
