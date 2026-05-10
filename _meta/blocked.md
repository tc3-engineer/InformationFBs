# Blocked / Unavailable

> 列出所有由于 PDF 不可达或自验证连续失败而无法处理的库/条目。
> 格式：`<UTC> | <library> | <name|*> | <reason>`

---

## 库级别（PDF 不可达）

来自 `_meta/preflight-2026-05-10.md`：

```
2026-05-10T07:50:04Z | Tc2_NC              | * | HTTP 404 on standard PDF URL
2026-05-10T07:50:04Z | Tc2_TcpIp           | * | HTTP 404 on standard PDF URL
2026-05-10T07:50:04Z | Tc2_SerialCom       | * | HTTP 404 on standard PDF URL
2026-05-10T07:50:04Z | Tc2_ModbusSrv       | * | HTTP 404 on standard PDF URL
2026-05-10T07:50:04Z | Tc2_ModbusRTU       | * | HTTP 404 on standard PDF URL
2026-05-10T07:50:04Z | Tc2_EthernetIP      | * | HTTP 404 on standard PDF URL
2026-05-10T07:50:04Z | Tc3_Database        | * | HTTP 404 on standard PDF URL
2026-05-10T07:50:04Z | Tc2_Database        | * | HTTP 404 on standard PDF URL
2026-05-10T07:50:04Z | Tc2_Filter          | * | HTTP 404 on standard PDF URL
2026-05-10T07:50:04Z | Tc2_MC2_Camming     | * | HTTP 404 on standard PDF URL
2026-05-10T07:50:04Z | Tc2_MC2_FlyingSaw   | * | HTTP 404 on standard PDF URL
2026-05-10T07:50:04Z | Tc2_NCI             | * | HTTP 404 on standard PDF URL
2026-05-10T07:50:04Z | Tc3_Vision          | * | HTTP 404 on standard PDF URL
2026-05-10T07:50:04Z | Tc2_Hydraulic       | * | HTTP 404 on standard PDF URL
2026-05-10T07:50:04Z | Tc2_BACnet          | * | HTTP 404 on standard PDF URL
2026-05-10T07:50:04Z | Tc2_KNXLib          | * | HTTP 404 on standard PDF URL
2026-05-10T07:50:04Z | Tc3_BA2             | * | HTTP 404 on standard PDF URL
2026-05-10T07:50:04Z | Tc2_HVAC            | * | HTTP 404 on standard PDF URL
2026-05-10T07:50:04Z | Tc2_Lighting        | * | HTTP 404 on standard PDF URL
```

人工提供 PDF 后可解锁。

## 条目级别（verify-failed / example-build-failed）

（暂无）
