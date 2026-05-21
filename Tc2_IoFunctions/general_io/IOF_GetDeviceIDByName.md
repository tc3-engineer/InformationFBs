# IOF_GetDeviceIDByName

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `General IO FBs` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59096587.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_IOF_GetDeviceIDByName.xml`](../examples/P_Demo_IOF_GetDeviceIDByName.xml) |

---

## 1. 功能简述

已知 I/O 设备名字，查它的 DeviceId。设备名字是工程师在 System Manager 配置时输入的字符串，DeviceId 由 TwinCAT 系统自动分配（用户不可改）。该 FB 让 PLC 程序通过"稳定的名字"得到"可能变化的 ID"，便于后续把 ID 用于其它 `IOF_*` 调用。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID : T_AmsNetId;
    DEVICENAME : T_MaxString;
    START : BOOL;
    TMOUT : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 目标 TwinCAT 计算机的 AMS Net ID；本机用空串 `''`，远端填对端 AMS Net ID（例如 `'5.84.32.27.1.1'`）。 |
| `DEVICENAME` | `T_MaxString` | - | 工程师在 TwinCAT System Manager 配置 I/O 设备时给的名字（字符串）。 |
| `START` | `BOOL` | - | 上升沿触发一次执行；调用期间保持高电平，完成后由用户决定何时回 FALSE 准备下次触发。 |
| `TMOUT` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY : BOOL;
    ERR : BOOL;
    ERRID : UDINT;
    DEVICEID : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `ERR` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `ERRID` | `UDINT` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |
| `DEVICEID` | `UDINT` | TwinCAT 配置时由系统自动分配的 I/O 设备 ID（不可由用户配置）。可在 System Manager 中查看，或通过 `IOF_GetDeviceIDByName` 由设备名查得。 |

### VAR_IN_OUT

无。

## 3. 行为说明

`START` 上升沿：`BUSY := TRUE`，FB 经 ADS 在 TwinCAT I/O 子系统的设备注册表里查名字 → ID。成功 `DEVICEID` 输出有效；失败 `ERR := TRUE`、`ERRID` 给错误号（常见 `0x6` 名字找不到）。工程改动重新分配 ID 后，本 FB 仍按名字找得到正确 ID——前提是名字保持不变。建议把所有 `IOF_*` 调用入口都先经过本 FB 解析 ID 再用。

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
- **`DEVICENAME` 大小写敏感**。（工程经验补充）
- 多块同类型设备命名时若有空格 / 特殊字符要小心；建议命名只用 `A-Z 0-9 _`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IOF_GetDeviceIDByName.xml`](../examples/P_Demo_IOF_GetDeviceIDByName.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：工程多块现场总线卡，部分被禁用 / 重新分配后 DeviceId 改变。用名字查 ID 让 PLC 程序与硬件解耦。
- **价值**：避免硬编码 DeviceId 导致工程改动后断链；名字查询是工程上的标准做法。
- **替代方案对比**：
  - 硬编码 DeviceId：易断链
  - **本 FB**：标准做法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.1.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59096587.html
- **相关 FB / FC**：`IOF_GetDeviceCount`, `IOF_GetDeviceName`, `IOF_GetDeviceNetId`
