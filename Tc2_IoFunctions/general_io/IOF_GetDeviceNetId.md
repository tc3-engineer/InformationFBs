# IOF_GetDeviceNetId

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `General IO FBs` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59101195.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_IOF_GetDeviceNetId.TcPOU`](../examples/P_Demo_IOF_GetDeviceNetId.TcPOU) |

---

## 1. 功能简述

部分 I/O 设备（如 FC310x Profibus 卡 / CP9030 通讯卡）在 System Manager 配置时会被分配自己的 AMS Net ID，用以让 PLC 经 ADS 直接调用该卡的固件功能。本 FB 已知 DeviceId，反查该 AMS Net ID。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID : T_AmsNetId;
    DEVICEID : UDINT;
    START : BOOL;
    TMOUT : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 目标 TwinCAT 计算机的 AMS Net ID；本机用空串 `''`，远端填对端 AMS Net ID（例如 `'5.84.32.27.1.1'`）。 |
| `DEVICEID` | `UDINT` | - | TwinCAT 配置时由系统自动分配的 I/O 设备 ID（不可由用户配置）。可在 System Manager 中查看，或通过 `IOF_GetDeviceIDByName` 由设备名查得。 |
| `START` | `BOOL` | - | 上升沿触发一次执行；调用期间保持高电平，完成后由用户决定何时回 FALSE 准备下次触发。 |
| `TMOUT` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY : BOOL;
    ERR : BOOL;
    ERRID : UDINT;
    DeviceNetId : T_AmsNetId;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `ERR` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `ERRID` | `UDINT` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |
| `DeviceNetId` | `T_AmsNetId` | 字符串参数 `DeviceNetId`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

`START` 上升沿触发一次反查：`BUSY := TRUE`，FB 经 ADS 查 I/O 子系统的 NetId 注册表。成功时 `DeviceNetId` 含字符串（如 "1.2.3.4.5.6"），该 NetId 可直接作为后续 ADS 调用的目标参数使用。若该设备未配 NetId 或硬件不支持（普通 KL 耦合器 / EtherCAT 主站常无），`ERR := TRUE`、`ERRID` 给出错误号。触发语义为上升沿一次性，调用者需要在 `BUSY` 落回后再使用 `DeviceNetId` 字符串。与 `IOF_GetDeviceInfoByName` 相比，本 FB 只返回 NetId 一个字段；若同时还需要 DeviceId，用 ByName 版本更省调用。

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

- ADS 错误号需要查 Beckhoff 在线 **ADS Return Codes** 表理解，本 FB 自身不附带具体码表。
- 触发输入（如 `bExecute` / `START` / `RESET` 等）必须给上升沿一次性触发，不能持续给 TRUE。持续高电平时只有第一次进入会启动一次新请求，之后不会重新触发。（工程经验补充）
- 不要在 `BUSY = TRUE` 期间修改其它输入参数，结果未定义。等 `BUSY` 落回 FALSE 后再准备下一次的入参。（工程经验补充）
- 现场总线设备未上电 / 未通讯时 `ERRID` 会带 `0x06` (port not found) 或硬件接口特有错误号，不一定是 ADS 通讯本身问题。（工程经验补充）
- 不是所有 IO 设备都有 AMS Net ID——纯 EtherCAT 主站 / 普通 KL 端子耦合器一般没有。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IOF_GetDeviceNetId.TcPOU`](../examples/P_Demo_IOF_GetDeviceNetId.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：程序需要对 FC310x Profibus 卡调用 ADS 读总线诊断字 → 先查得卡的 AMS Net ID 再调 ADSREAD。
- **价值**：避免硬编码 NetId；工程改动也同步。
- **替代方案对比**：
  - 硬编码 NetId：工程改动易断链
  - 用 `IOF_GetDeviceInfoByName` 一次取齐 ID + NetId：更通用
  - **本 FB**：已经有 DeviceId 时最直接

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.1.12
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59101195.html
- **相关 FB / FC**：`IOF_GetDeviceInfoByName`, `IOF_GetDeviceIDByName`, `IOF_GetBoxNetId`
