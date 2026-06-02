# IOF_GetBoxNameByAddr

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `General IO FBs` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59091979.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_IOF_GetBoxNameByAddr.TcPOU`](../examples/P_Demo_IOF_GetBoxNameByAddr.TcPOU) |

---

## 1. 功能简述

与 `IOF_GetBoxAddrByName` 反向：已知现场总线站地址 + 所属 DeviceId，查询该 box 在 System Manager 配置时被命名的字符串。常用于把"出错的 box 站号"翻译成人类可读的"出错设备名字"做到 HMI / 报警日志里。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID : T_AmsNetId;
    DEVICEID : UDINT;
    BOXADDR : UINT;
    START : BOOL;
    TMOUT : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 目标 TwinCAT 计算机的 AMS Net ID；本机用空串 `''`，远端填对端 AMS Net ID（例如 `'5.84.32.27.1.1'`）。 |
| `DEVICEID` | `UDINT` | - | TwinCAT 配置时由系统自动分配的 I/O 设备 ID（不可由用户配置）。可在 System Manager 中查看，或通过 `IOF_GetDeviceIDByName` 由设备名查得。 |
| `BOXADDR` | `UINT` | - | 现场总线地址（如 Profibus 站号 / Lightbus 光纤环模块号）。 |
| `START` | `BOOL` | - | 上升沿触发一次执行；调用期间保持高电平，完成后由用户决定何时回 FALSE 准备下次触发。 |
| `TMOUT` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY : BOOL;
    ERR : BOOL;
    ERRID : UDINT;
    BOXNAME : T_MaxString;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `ERR` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `ERRID` | `UDINT` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |
| `BOXNAME` | `T_MaxString` | 工程师在 TwinCAT System Manager 配置 box 时给的名字（字符串）。 |

### VAR_IN_OUT

无。

## 3. 行为说明

`START` 上升沿触发一次反向查询：`BUSY := TRUE`，FB 经 ADS 把 (DEVICEID, BOXADDR) 发到 I/O 子系统。主站查内部 box 注册表，返回 box 名字到 `BOXNAME`（`T_MaxString`，最大 255 字节）。执行成功 `ERR := FALSE`、`BOXNAME` 含工程命名；若 BOXADDR 是无效站号 / 该地址下没配 box，`ERR := TRUE`、`ERRID` 含错误码、`BOXNAME` 空串。名字字符串编码取决于 System Manager 配置时输入的编码（一般 ASCII；含中文需要 UTF-8 兼容字符串处理）。触发语义为上升沿一次性，重复触发要先把 `START` 拉低再拉高；不会循环触发。

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
- **`BOXNAME : T_MaxString`** 是 255 字节缓冲；接收侧 STRING 长度要够，否则会被截断。（工程经验补充）
- 若同一现场总线上存在重名 box（System Manager 允许重名以方便复制配置），返回的是第一个匹配项，不一定是预期项。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IOF_GetBoxNameByAddr.TcPOU`](../examples/P_Demo_IOF_GetBoxNameByAddr.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：Profibus 报警："Slave at station 17 failed"。直接把"17"显示给操作员意义不大；调本 FB 把 17 翻译成 "Drive_PaintPump_Left" 显示在 HMI 上，操作员立刻知道哪台设备。
- **价值**：把数字 ID 翻译成人类可读名字，HMI 报警 / 工单日志可读性大幅提升。
- **替代方案对比**：
  - 维护一份 PLC 静态查表：station 号 → 名字。手维护、易出错
  - 操作员翻图纸：低效
  - **本 FB**：自动从 TwinCAT 配置取名字，永远与工程同步

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.1.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59091979.html
- **相关 FB / FC**：`IOF_GetBoxAddrByName`, `IOF_GetBoxNetId`, `IOF_GetBoxCount`
