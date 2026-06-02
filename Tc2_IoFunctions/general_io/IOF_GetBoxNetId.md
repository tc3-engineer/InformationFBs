# IOF_GetBoxNetId

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `General IO FBs` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59093515.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_IOF_GetBoxNetId.TcPOU`](../examples/P_Demo_IOF_GetBoxNetId.TcPOU) |

---

## 1. 功能简述

一部分 box（例如带固件的智能模块）会在 TwinCAT 配置时被分配自己的 AMS Net ID，这样 PLC 程序可以经 ADS 直接调用该 box 内部的固件功能。本 FB 已知主站 DeviceId + box 在现场总线上的地址，反查该 box 的 AMS Net ID（如有）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID : T_AmsNetId;
    DEVICEID : UDINT;
    BOXADDR : WORD;
    START : BOOL;
    TMOUT : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 目标 TwinCAT 计算机的 AMS Net ID；本机用空串 `''`，远端填对端 AMS Net ID（例如 `'5.84.32.27.1.1'`）。 |
| `DEVICEID` | `UDINT` | - | TwinCAT 配置时由系统自动分配的 I/O 设备 ID（不可由用户配置）。可在 System Manager 中查看，或通过 `IOF_GetDeviceIDByName` 由设备名查得。 |
| `BOXADDR` | `WORD` | - | 现场总线地址（如 Profibus 站号 / Lightbus 光纤环模块号）。 |
| `START` | `BOOL` | - | 上升沿触发一次执行；调用期间保持高电平，完成后由用户决定何时回 FALSE 准备下次触发。 |
| `TMOUT` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY : BOOL;
    ERR : BOOL;
    ERRID : UDINT;
    BoxNetId : T_AmsNetId;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `ERR` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `ERRID` | `UDINT` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |
| `BoxNetId` | `T_AmsNetId` | 字符串参数 `BoxNetId`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

`START` 上升沿触发一次查询：`BUSY := TRUE`，FB 经 ADS 把 (DEVICEID, BOXADDR) 发到 I/O 子系统。若该 box 在工程配置时被分配过 AMS Net ID，结果通过 `BoxNetId` 输出（字符串形式如 "1.2.3.4.5.6"）。若 box 未配 AMS Net ID 或硬件不支持，`ERR := TRUE`、`ERRID` 给出错误号，`BoxNetId` 为空串。查询结果可直接作为后续 ADS 调用的目标 NetId 参数使用，无需手抄字符串到 PLC 程序。触发语义为上升沿一次性，调用者需要在 `BUSY` 落回后再决定下一次是否重新触发。

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
- **并非所有 box 都有 AMS Net ID**：只有带固件 / 智能型 box（如 FC310x、CP9030）才会分配。普通无源 IO 设备无此项。（工程经验补充）
- `BOXADDR : WORD` 与其他 box FB 的 `BOXADDR : UINT` 类型不同——VAR 区里 PDF 明确写 WORD，调用方注意类型转换。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IOF_GetBoxNetId.TcPOU`](../examples/P_Demo_IOF_GetBoxNetId.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：Profibus 主卡 FC3101 自带 AMS Net ID，要从 PLC 调用 FC3101 内部固件功能（例如读总线统计）需要先拿到它的 NetId。
- **价值**：避免在 System Manager 里手抄 NetId 写死在 PLC 程序里——以工程改动后两端不同步为代价。
- **替代方案对比**：
  - 手抄 NetId 写常量：简单但工程改动易断链
  - 用 box 名字查 NetId：需要更多步骤
  - **本 FB**：站号直接查 NetId，最直接

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.1.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59093515.html
- **相关 FB / FC**：`IOF_GetDeviceNetId`, `IOF_GetBoxAddrByName`, `IOF_GetBoxNameByAddr`
