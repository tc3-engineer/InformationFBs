# FB_RAIDGetStatus

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `RAID Controller` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59211531.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_RAIDGetStatus.xml`](../examples/P_Demo_FB_RAIDGetStatus.xml) |

---

## 1. 功能简述

查询指定 RAID 集（在指定控制器内）的运行状态：RAID 类型、整体状态、盘数、各盘状态。可在线监控 RAID 阵列是否降级 / 重建中 / 故障。PDF NOTICE 说**最多每秒调一次**——比 Find/Info 宽松，但仍不能高频调。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNETID : T_AmsNetId;
    bWrtRd : BOOL;
    stRAIDConfigReq : ST_RAIDConfigReq;
    tTimeOut : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNETID` | `T_AmsNetId` | - | 本机用空串。 |
| `bWrtRd` | `BOOL` | - | 上升沿触发一次（频率上限：每秒一次）。 |
| `stRAIDConfigReq` | `ST_RAIDConfigReq` | - | 请求结构：要查的控制器 ID + RAID 集索引。 |
| `tTimeOut` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    stRAIDStatusRes : ST_RAIDStatusRes;
    nBytesRead : UDINT;
    bBusy : BOOL;
    bError : BOOL;
    nErrorID : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stRAIDStatusRes` | `ST_RAIDStatusRes` | RAID 状态结果结构。 |
| `nBytesRead` | `UDINT` | 返回字节数。 |
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bError` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `nErrorID` | `UDINT` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |

### VAR_IN_OUT

无。

## 3. 行为说明

`bWrtRd` 上升沿触发：`bBusy := TRUE`，FB 经 ADS 查 RAID 驱动指定阵列的状态。完成后 `stRAIDStatusRes` 含 RAID 集索引 + 类型 + 整体状态 + 盘数 + 各盘状态。`stRAIDConfigReq` 是 IN 结构，业务侧填写要查的 (控制器 ID, RAID 集索引)。调用频率上限：**每秒一次**（PDF NOTICE）。比 Find/Info 宽松，但**仍不能高频调**。常见用法：每秒一次循环触发本 FB → 拿到 RAID 健康状态 → 任一盘 Failed 立即报警 + 自动写 SCADA。

## 4. 错误码 / 返回值

本 FB 通过 `bError` / `ERR` + `nErrId` / `ERRID` 输出报告错误：

- `bError = FALSE` 且 `nErrId = 0`：调用成功。
- `bError = TRUE`：调用失败，错误号在 `nErrId`。

常见错误号（按 ADS Return Codes 表）：

| 错误号（十六进制） | 含义 |
|---|---|
| `0x06` | 目标端口未找到（ADSERR_DEVICE_NOTFOUND）—— 设备未启用或 DeviceId 错 |
| `0x07` | 目标机不在线（ADSERR_DEVICE_NOTREADY） |
| `0x745` | ADS 通讯超时（ADSERR_CLIENT_SYNCTIMEOUT）—— `TMOUT` 太短或现场总线响应慢 |
| 其他 | 见 Beckhoff **ADS Return Codes** 在线表，及现场总线主站特有的错误码（PDF 未列入本节） |

⚠️ PDF / InfoSys 未在本 FB 处列具体的现场总线错误号，需配合主站手册查询。

## 5. 使用注意 / 常见坑

- **本 FB 不要循环调用**（PDF NOTICE 明确警告）：会显著降低系统性能。上电时调一次拿到结果即可。
- `bWrtRd` 是上升沿触发，与"读写"语义无关；只是上升沿触发一次 ADS 通讯。命名是 PDF 沿用早期的 ADS API 风格。（工程经验补充）
- 返回字段的具体结构（`ST_RAIDInfo` / `ST_RAIDStatusRes` 等）见 PDF §5；本 FB 只输出整体结构，调用方按字段名访问。（工程经验补充）
- ADS 错误号见 ADS Return Codes 在线表；超时错为 `0x745` (= 1861 dec)。（工程经验补充）
- **最多每秒触发一次**（PDF NOTICE：Call once per second at the most）；更高频会影响系统性能。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_RAIDGetStatus.xml`](../examples/P_Demo_FB_RAIDGetStatus.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：生产线工业服务器：每秒读 RAID 状态，任一硬盘掉线立即报警 + 发邮件给 IT；避免硬盘 fail 几小时后才发现。
- **价值**：RAID 健康状态进入实时监控；从被动等用户发现变成主动报警。
- **替代方案对比**：
  - Windows 报警邮件：依赖 RAID 厂商驱动
  - IT 定期人工巡检：滞后
  - **本 FB**：实时监控

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.11.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59211531.html
- **相关 FB / FC**：`FB_RAIDFindCntlr`, `FB_RAIDGetInfo`
