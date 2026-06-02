# FB_RAIDFindCntlr

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `RAID Controller` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59208459.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_RAIDFindCntlr.TcPOU`](../examples/P_Demo_FB_RAIDFindCntlr.TcPOU) |

---

## 1. 功能简述

查询本机有几块 RAID 控制器，并返回它们的 ID。`bWrtRd` 上升沿触发一次查询，结果填到 `stRAIDCntlrFound`（含 RAID 控制器数量 + ID 列表）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNETID : T_AmsNetId;
    bWrtRd : BOOL;
    tTimeOut : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNETID` | `T_AmsNetId` | - | 目标 TwinCAT 计算机 AMS Net ID。本机用空串。 |
| `bWrtRd` | `BOOL` | - | 上升沿触发一次查询。**只能上电时调一次，不能循环调用**。 |
| `tTimeOut` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    stRAIDCntlrFound : ST_RAIDCntlrFound;
    nBytesRead : UDINT;
    bBusy : BOOL;
    bError : BOOL;
    nErrorID : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stRAIDCntlrFound` | `ST_RAIDCntlrFound` | RAID 控制器数量 + ID 列表结构（`ST_RAIDCntlrFound`）。 |
| `nBytesRead` | `UDINT` | 实际返回字节数。 |
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bError` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `nErrorID` | `UDINT` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |

### VAR_IN_OUT

无。

## 3. 行为说明

`bWrtRd` 上升沿触发一次 ADS 调用：`bBusy := TRUE`，FB 经 ADS 查内核 RAID 驱动。完成后 `stRAIDCntlrFound` 含控制器数量和各 ID。`nBytesRead` 显示实际返回的字节数；可用作返回数据完整性的校验。出错时 `bError := TRUE`、`nErrorID` 给 ADS 错误号；超时给 `0x745` (= 1861 dec)。**警告**：PDF NOTICE 明确说"本 FB 只调用一次"；循环调用会严重拖慢系统性能（RAID 驱动每次 IO 都要同步硬件状态）。上电诊断序列里调一次拿到 ID 列表后，把结果存起来后续用。

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

> 配套可导入文件：[`examples/P_Demo_FB_RAIDFindCntlr.TcPOU`](../examples/P_Demo_FB_RAIDFindCntlr.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：工业服务器 / NAS 一体机：上电时枚举 RAID 控制器，把每个控制器的状态做到 SCADA 显示。
- **价值**：让 PLC 程序能监控工控机的 RAID 状态，避免硬盘故障不报警。
- **替代方案对比**：
  - 用 Windows RAID 监控工具：通常要单独服务
  - 不监控：硬盘 fail 时 PLC 不知道
  - **本 FB**：纯 PLC 程序

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.11.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59208459.html
- **相关 FB / FC**：`FB_RAIDGetInfo`, `FB_RAIDGetStatus`
