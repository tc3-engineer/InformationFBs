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

## 库级别（no-plc-api：库存在但无独立 PLC FB 文档）

```
2026-06-02T00:00:00Z | Tc2_NC | * | 库为 stub：仅 AXIS_REF / PTP 数据结构。TF50x0_TC3_NC_PTP_EN.pdf 是 NC PTP 引擎配置手册（NC 配置 / 参数 / 控制环），无 PLC API 章节；InfoSys 无 tcplclib_tc2_nc 主页。所有 NC 控制 FB 实际由以下库提供：MC_*（Tc2_MC2 ✅）/ FB_SoE*（Tc2_NcDrive ✅）/ Tc2_NCI ⏳。无独立 doc 可写。
2026-06-02T00:00:00Z | Tc2_EthernetIP | * | 库为 stub：TF6280_EtherNet_IP_Adapter_EN.pdf 是配置型产品手册，正文 0 个 FB_ token、无 "PLC API"/"Function blocks" 章节（章节仅 Configuration / Properties / Diagnostic history）。EtherNet/IP 适配器在 XAE 中配置映射，PLC 侧直接读写过程映像，无独立 PLC 库 FB。同 Tc2_NC 处理。
```

