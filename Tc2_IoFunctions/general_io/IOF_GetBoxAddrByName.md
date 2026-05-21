# IOF_GetBoxAddrByName

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `General IO FBs` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59087371.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_IOF_GetBoxAddrByName.xml`](../examples/P_Demo_IOF_GetBoxAddrByName.xml) |

---

## 1. 功能简述

已知 box（slave / 模块 / 站）名字 + 所属设备的 DeviceId，查询该 box 的现场总线地址。对 Profibus 返回站地址，对 Beckhoff Lightbus 返回光纤环里的物理模块号；若现场总线本身无地址概念，返回 TwinCAT 内部的逻辑地址。box 名字是工程师在 System Manager 配置时给的，调用者把这个名字传入即可，FB 经 ADS 异步查询。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID : T_AmsNetId;
    DEVICEID : UDINT;
    BOXNAME : T_MaxString;
    START : BOOL;
    TMOUT : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 目标 TwinCAT 计算机的 AMS Net ID；本机用空串 `''`，远端填对端 AMS Net ID（例如 `'5.84.32.27.1.1'`）。 |
| `DEVICEID` | `UDINT` | - | TwinCAT 配置时由系统自动分配的 I/O 设备 ID（不可由用户配置）。可在 System Manager 中查看，或通过 `IOF_GetDeviceIDByName` 由设备名查得。 |
| `BOXNAME` | `T_MaxString` | - | 工程师在 TwinCAT System Manager 配置 box 时给的名字（字符串）。 |
| `START` | `BOOL` | - | 上升沿触发一次执行；调用期间保持高电平，完成后由用户决定何时回 FALSE 准备下次触发。 |
| `TMOUT` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY : BOOL;
    ERR : BOOL;
    ERRID : UDINT;
    BOXADDR : UINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `ERR` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `ERRID` | `UDINT` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |
| `BOXADDR` | `UINT` | 现场总线地址（如 Profibus 站号 / Lightbus 光纤环模块号）。 |

### VAR_IN_OUT

无。

## 3. 行为说明

`START` 上升沿触发一次查询：`BUSY := TRUE`，FB 把 (DEVICEID, BOXNAME) 通过 ADS 发到 I/O 子系统。TwinCAT I/O 驱动维护一张 box 名 ↔ 地址的查找表，返回结果填到 `BOXADDR`。成功时 `ERR := FALSE`、`ERRID := 0`、`BOXADDR` 有效；失败时 `ERR := TRUE`、`ERRID` 含 ADS 错误号，`BOXADDR` 不可用。**触发语义**：必须上升沿，持续 TRUE 不会重复触发。**典型用法**：工程图纸里 box 取了名字（例如 "Drive_X1"），但同事在 Profibus 配置时把站号改过，PLC 程序里用名字而非站号去定位 box 就能避免与 hardcode 站号绑死。

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
- **`BOXNAME` 大小写敏感**：System Manager 配置时用的具体大小写要原样传入，不然 ADS 返回 box not found。（工程经验补充）
- **返回的 `BOXADDR` 是 `UINT`**：Profibus 站号最大 125；Lightbus 光纤环最大约 254，都在 UINT 范围内；若现场总线允许更大编址要确认是否够用。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IOF_GetBoxAddrByName.xml`](../examples/P_Demo_IOF_GetBoxAddrByName.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：灌装线工程：6 台 Profibus 设备名字定义为 Fill1..Fill6，工程师在调试时偶尔会改 Profibus 站号。PLC 启动诊断脚本用名字查站号、写到诊断日志，避免硬编码站号被改后断链。
- **价值**：把 "名字 → 站号" 的查找做成 PLC 可调用接口，省去手抄 System Manager 配置表的工作，也保证 PLC 程序与现场配置同步。
- **替代方案对比**：
  - 硬编码站号：简单但与现场配置不同步
  - 用 `IOF_GetBoxNameByAddr` 反向查再缓存：可行，但需要先有有效站号
  - **本 FB**：直接用名字查站号，最常用

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59087371.html
- **相关 FB / FC**：`IOF_GetBoxAddrByNameEx`, `IOF_GetBoxNameByAddr`, `IOF_GetBoxCount`
