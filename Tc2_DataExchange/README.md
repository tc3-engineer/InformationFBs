# Tc2_DataExchange

> 跨 PLC/ADS 设备的 watchdog 数据交换。版本 `1.2.2`。

- [官方 InfoSys](https://infosys.beckhoff.com/content/1033/tcplclib_tc2_dataexchange/)
- [官方 PDF](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_DataExchange_EN.pdf)
- [Roadmap](../_meta/roadmap-Tc2_DataExchange.md)

## 索引（3 条 · 全部 ✅ verified）

| Category | Name | 文档 | 例程 |
|---|---|---|---|
| Watchdog function blocks | FB_CheckWatchdog | [✅ verified](watchdog/FB_CheckWatchdog.md) | [P_Demo_FB_CheckWatchdog.TcPOU](examples/P_Demo_FB_CheckWatchdog.TcPOU) |
| Watchdog function blocks | FB_WriteWatchdog | [✅ verified](watchdog/FB_WriteWatchdog.md) | [P_Demo_FB_WriteWatchdog.TcPOU](examples/P_Demo_FB_WriteWatchdog.TcPOU) |
| Library version | stLibVersion_Tc2_DataExchange | [✅ verified](global_constants/stLibVersion_Tc2_DataExchange.md) | [P_Demo_stLibVersion_Tc2_DataExchange.TcPOU](examples/P_Demo_stLibVersion_Tc2_DataExchange.TcPOU) |

## 用法套路

- **发送侧**：`FB_WriteWatchdog` 周期把递增计数写到目标设备
- **接收侧**：`FB_CheckWatchdog` 监视计数变化，超时未变 → 报警

`tWatchdogTime` 应为发送周期的 5-10 倍。
