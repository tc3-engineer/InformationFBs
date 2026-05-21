# FB_RAIDGetInfo

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `RAID Controller` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59209995.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_RAIDGetInfo.xml`](../examples/P_Demo_FB_RAIDGetInfo.xml) |

---

## 1. 功能简述

已知 RAID 控制器 ID（来自 `FB_RAIDFindCntlr`），查询该控制器的 RAID 集数（多少组 RAID 阵列）+ 每组最大盘数。同样 PDF NOTICE 警告"只调一次"，循环调用拖慢系统。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNETID : T_AmsNetId;
    bWrtRd : BOOL;
    nRAIDCntlrID : UDINT;
    tTimeOut : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNETID` | `T_AmsNetId` | - | 本机用空串。 |
| `bWrtRd` | `BOOL` | - | 上升沿触发一次查询（仅一次）。 |
| `nRAIDCntlrID` | `UDINT` | - | 目标 RAID 控制器 ID（来自 `FB_RAIDFindCntlr`）。 |
| `tTimeOut` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    stRAIDInfo : ST_RAIDInfo;
    nBytesRead : UDINT;
    bBusy : BOOL;
    bError : BOOL;
    nErrorID : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stRAIDInfo` | `ST_RAIDInfo` | RAID 控制器元信息结构。 |
| `nBytesRead` | `UDINT` | 实际返回字节数。 |
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bError` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `nErrorID` | `UDINT` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |

### VAR_IN_OUT

无。

## 3. 行为说明

`bWrtRd` 上升沿触发一次查询：`bBusy := TRUE`，FB 经 ADS 查 RAID 驱动。完成后 `stRAIDInfo` 含 RAID 集数（多少组阵列）+ 每组最大盘数。`nRAIDCntlrID` 是要查的 RAID 控制器 ID（来自先前的 `FB_RAIDFindCntlr` 查询）。与 `FB_RAIDFindCntlr` 配套使用：先 Find 拿到所有控制器 ID，再用本 FB 查每个控制器的元信息，最后用 `FB_RAIDGetStatus` 查具体阵列健康状态。上电诊断序列里**调一次拿到结果即可**，不要循环；循环调用会显著降低系统性能（PDF NOTICE 警告）。

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

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_RAIDGetInfo.xml`](../examples/P_Demo_FB_RAIDGetInfo.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：上电后枚举 RAID 控制器 → 对每个控制器调本 FB 拿 RAID 集数与最大盘数 → SCADA 显示拓扑。
- **价值**：让 PLC 知道每块 RAID 控制器管几组 RAID。
- **替代方案对比**：
  - 不监控：SCADA 没有 RAID 拓扑信息
  - **本 FB**：拿到拓扑

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.11.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59209995.html
- **相关 FB / FC**：`FB_RAIDFindCntlr`, `FB_RAIDGetStatus`
