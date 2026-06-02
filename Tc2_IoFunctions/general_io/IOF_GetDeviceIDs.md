# IOF_GetDeviceIDs

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `General IO FBs` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59098123.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_IOF_GetDeviceIDs.TcPOU`](../examples/P_Demo_IOF_GetDeviceIDs.TcPOU) |

---

## 1. 功能简述

一次性读取所有激活 I/O 设备的 DeviceId 列表，写入用户提供的 WORD 数组。第 0 个 WORD 是 ID 总数，后续依次为每个设备的 ID。`START` 上升沿触发。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID : T_AmsNetId;
    LEN : UDINT;
    DESTADDR : PVOID;
    START : BOOL;
    TMOUT : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 目标 TwinCAT 计算机的 AMS Net ID；本机用空串 `''`，远端填对端 AMS Net ID（例如 `'5.84.32.27.1.1'`）。 |
| `LEN` | `UDINT` | - | 数据缓冲区字节长度。 |
| `DESTADDR` | `PVOID` | - | 数据缓冲区地址，用 `ADR()` 运算符取得。 |
| `START` | `BOOL` | - | 上升沿触发一次执行；调用期间保持高电平，完成后由用户决定何时回 FALSE 准备下次触发。 |
| `TMOUT` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY : BOOL;
    ERR : BOOL;
    ERRID : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `ERR` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `ERRID` | `UDINT` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |

### VAR_IN_OUT

无。

## 3. 行为说明

调用前用户准备一个 `ARRAY[1..N] OF WORD` 缓冲区（N ≥ 设备总数 + 1）并把 `LEN` 设为字节长度。`START` 上升沿触发一次查询：`BUSY := TRUE`，FB 经 ADS 把 ID 表读到 `DESTADDR` 指向的缓冲区。完成后 `BUSY := FALSE`，缓冲区里：第 1 个 WORD = 数量，第 2..N+1 WORD = 各设备 ID。常见调用顺序：先 `IOF_GetDeviceCount` 取总数 → 申请相应大小数组 → 调本 FB → 遍历 ID 列表做枚举诊断。触发语义为上升沿一次性；调用者需要在 `BUSY` 落回后再读缓冲区，否则可能读到旧数据。

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
- **缓冲区大小要够**：若工程实际有 5 个设备，至少给 6 个 WORD（第一个存计数）；不够会 ADS 报错或返回截断数据。（工程经验补充）
- **`DESTADDR : PVOID`** 必须用 `ADR(arrBuffer)` 取得；`LEN` 是字节数（`SIZEOF(arrBuffer)`）不是 WORD 个数。（工程经验补充）
- PDF 中 `LEN` VAR 表写 `UDINT`，描述表写 "UINT"——以 VAR 区为准（UDINT）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IOF_GetDeviceIDs.TcPOU`](../examples/P_Demo_IOF_GetDeviceIDs.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：上电诊断脚本：枚举所有 IO 设备做巡检 → 用本 FB 一次拿到所有 ID → for 循环逐个调 `IOF_GetDeviceType` 写日志。
- **价值**：避免多次 ADS 调用逐个取 ID；一次拿全部。
- **替代方案对比**：
  - 多次调 `IOF_GetDeviceIDByName`：需先知道所有名字
  - **本 FB**：一次拿全部 ID

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.1.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59098123.html
- **相关 FB / FC**：`IOF_GetDeviceCount`, `IOF_GetDeviceType`, `IOF_GetDeviceName`
