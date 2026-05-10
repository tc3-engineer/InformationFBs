# Blocked / Unavailable

> 列出所有由于 PDF 不可达或自验证连续失败而无法处理的库/条目。
> 格式：`<UTC> | <library> | <name|*> | <reason>`

---

## 库级别（PDF 不可达）

来自 `_meta/preflight-2026-05-10.md` 第二轮（含 URL_ALIASES）：

```
2026-05-10T08:30:00Z | Tc2_KNXLib | * | 标准 URL 与 TF8030_TC3_KNX_*.pdf 全部 404；公开下载站无对应 PDF
```

之前一轮误判为不可达的 18 个库（Tc2_NC、Tc2_TcpIp、Tc2_SerialCom、Tc2_ModbusSrv、Tc2_ModbusRTU、Tc2_EthernetIP、Tc3_Database、Tc2_Database、Tc2_Filter、Tc2_MC2_Camming、Tc2_MC2_FlyingSaw、Tc2_NCI、Tc3_Vision、Tc2_Hydraulic、Tc2_BACnet、Tc3_BA2、Tc2_HVAC、Tc2_Lighting）已通过 `URL_ALIASES` 解锁——见 `_meta/tools/fetch_pdf.py` 的 `URL_ALIASES` 字典。

> ⚠️ TF 系列产品手册的 TOC 结构与 PLC Library 不同（章节如"PLC API"嵌套 FB），跑 /discover 之前需要抽样确认 `parse_toc.py` 能识别。

## 条目级别（verify-failed / example-build-failed）

（暂无）
