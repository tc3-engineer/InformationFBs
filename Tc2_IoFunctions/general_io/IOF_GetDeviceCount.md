# IOF_GetDeviceCount

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `General IO FBs` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59095051.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_IOF_GetDeviceCount.xml`](../examples/P_Demo_IOF_GetDeviceCount.xml) |

---

## 1. 功能简述

读取本机 TwinCAT 系统中**配置且当前激活**的 I/O 设备总数（一个 I/O 设备 = 一块现场总线主站卡或一个虚拟 IO 接口）。`START` 上升沿触发一次，结果以 `DEVICECOUNT` 输出。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID : T_AmsNetId;
    START : BOOL;
    TMOUT : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 目标 TwinCAT 计算机的 AMS Net ID；本机用空串 `''`，远端填对端 AMS Net ID（例如 `'5.84.32.27.1.1'`）。 |
| `START` | `BOOL` | - | 上升沿触发一次执行；调用期间保持高电平，完成后由用户决定何时回 FALSE 准备下次触发。 |
| `TMOUT` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY : BOOL;
    ERR : BOOL;
    ERRID : UDINT;
    DEVICECOUNT : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `ERR` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `ERRID` | `UDINT` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |
| `DEVICECOUNT` | `UDINT` | 无符号整数 `DEVICECOUNT`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

`START` 上升沿触发一次查询：`BUSY := TRUE`，FB 经 ADS 调用 I/O 子系统返回当前激活的 I/O 设备数（典型值 1-10）。此处"激活"的含义是 System Manager 配置中未被 Disable、且底层驱动加载成功的 I/O 设备。完成后 `BUSY := FALSE`、`DEVICECOUNT` 含数量。可与 `IOF_GetDeviceIDs` 配合：先用本 FB 取设备数 N，再申请 N+1 个 WORD 的数组传给 `IOF_GetDeviceIDs` 拿到所有 ID 列表。触发语义为上升沿一次性，重复触发要先把 `START` 拉低再拉高。

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
- 结果只算"激活"设备：System Manager 中被 Disabled 的不计入。（工程经验补充）
- 上电后 IO 设备启动有先后，启动尚未完成时调本 FB 可能拿到比预期少的数字；建议放在上电延时 5 秒后调用。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IOF_GetDeviceCount.xml`](../examples/P_Demo_IOF_GetDeviceCount.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：上电诊断脚本：要枚举所有 I/O 设备做巡检 → 先调本 FB 拿到总数 N → 再调 `IOF_GetDeviceIDs` 拿到 N 个 ID → 逐个 ID 调 `IOF_GetDeviceType` / `IOF_GetDeviceName` 做日志。
- **价值**：把"系统里有几块现场总线卡"做成可程序化查询，避免硬编码"我知道有 3 块"。
- **替代方案对比**：
  - 硬编码已知设备数：工程改动不同步
  - 看 System Manager：人工不可程序化
  - **本 FB**：标准入口

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.1.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59095051.html
- **相关 FB / FC**：`IOF_GetDeviceIDs`, `IOF_GetDeviceIDByName`, `IOF_GetDeviceName`
