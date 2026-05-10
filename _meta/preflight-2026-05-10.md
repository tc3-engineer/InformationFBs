# Pre-flight 报告 · 2026-05-10

> 由 `python3 _meta/tools/fetch_pdf.py --head-only` 生成。
> 对 `library-catalog.md` 中所有 41 个库的标准 PDF URL 做 Range GET 探测。

- **总数**：41
- **可达（200）**：22
- **不可达（404）**：19

## ✅ 可达（22）— 标准 URL 模式有效

| 库 | 状态 |
|---|---|
| Tc2_Standard | 200 |
| Tc2_System | 200 |
| Tc2_Utilities | 200 |
| Tc2_Math | 200 |
| Tc3_EventLogger | 200 |
| Tc2_MC2 | 200 |
| Tc2_MC2_Drive | 200 |
| Tc2_NcDrive | 200 |
| Tc2_Drive | 200 |
| Tc2_EtherCAT | 200 |
| Tc2_IoFunctions | 200 |
| Tc2_ProfinetDiag | 200 |
| Tc3_JsonXml | 200 |
| Tc2_DataExchange | 200 |
| Tc2_SUPS | 200 |
| Tc3_DriveMotionControl | 200 |
| Tc3_MC2_AdvancedHoming | 200 |
| Tc2_DALI | 200 |
| Tc2_DMX | 200 |
| Tc2_EIB | 200 |
| Tc2_EnOcean | 200 |
| Tc2_Coupler | 200 |

## ❌ 不可达（19）— 标记 unavailable，跳过

URL 模式 `TwinCAT_3_PLC_Lib_<NAME>_EN.pdf` 返回 404。
按 CLAUDE.md 规则不尝试 InfoSys / 其他 URL 模式。如有人工提供的 PDF 可手工放入 `_meta/.pdf-cache/<lib>.pdf` 后跑 fetch_pdf 解析。

| 库 | HTTP | 备注 |
|---|---|---|
| Tc2_NC | 404 | NC PTP 底层 |
| Tc2_TcpIp | 404 | Socket TCP/UDP（可能在不同 URL，待人工确认） |
| Tc2_SerialCom | 404 | 串口通信 |
| Tc2_ModbusSrv | 404 | Modbus TCP/RTU 服务端 |
| Tc2_ModbusRTU | 404 | Modbus RTU 主站 |
| Tc2_EthernetIP | 404 | EtherNet/IP |
| Tc3_Database | 404 | 数据库访问 |
| Tc2_Database | 404 | 旧版数据库 |
| Tc2_Filter | 404 | 信号滤波 |
| Tc2_MC2_Camming | 404 | 凸轮 |
| Tc2_MC2_FlyingSaw | 404 | 飞剪 |
| Tc2_NCI | 404 | 插补 / CNC |
| Tc3_Vision | 404 | TF7xxx 机器视觉 |
| Tc2_Hydraulic | 404 | 液压闭环 |
| Tc2_BACnet | 404 | 楼宇自动化 |
| Tc2_KNXLib | 404 | KNX/EIB |
| Tc3_BA2 | 404 | Building Automation 2.0 |
| Tc2_HVAC | 404 | 暖通 |
| Tc2_Lighting | 404 | 照明（曾在 catalog 出现） |

## 后续

- catalog 中上述 19 个库的 Status 字段统一改为 ❌ unavailable
- `_meta/blocked.md` 记录每条 404
- 若用户能提供 PDF（手工下载、内部分发），放入 `_meta/.pdf-cache/<lib>.pdf` 后跑：
  ```bash
  python3 -c "import _meta.tools.fetch_pdf as f; f.fetch('<lib>')"
  # 或直接 cp 后用 pypdf 抽文本
  ```
- 标准 URL 模式以外可能存在别名（如 Tc2_TcpIp ↔ TwinCAT_PLC_TcpIp 等），未来 batch 时可考虑加 URL 候选列表。当前阶段不做。
