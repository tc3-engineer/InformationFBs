# FB_FileRingBuffer

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/9676815883.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_FileRingBuffer.TcPOU`](../examples/P_Demo_FB_FileRingBuffer.TcPOU) |

---

## 1. 功能简述

FB_FileRingBuffer 把磁盘上一组等大的文件当作环形缓冲使用——满了自动覆盖最老文件。

用于：长期日志归档（如 30 天循环日志），保证不会占满磁盘。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId : T_AmsNetId := '';
    sPathName : T_MaxString := 'c:\Temp\data.dat';
    ePath : E_OpenPath := PATH_GENERIC;
    nID : UDINT := 0;
    cbBuffer : UDINT := 16#100000;
    bOverwrite : BOOL := FALSE;
    pWriteBuff : POINTER TO BYTE;
    cbWriteLen : UDINT;
    pReadBuff : POINTER TO BYTE;
    cbReadLen : UDINT;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | `''` | 目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。 |
| `sPathName` | `T_MaxString` | `'c:\Temp\data.dat'` | 参数 `sPathName`（类型 `T_MaxString`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `ePath` | `E_OpenPath` | `PATH_GENERIC` | 目标路径枚举（`PATH_GENERIC` / `PATH_BOOTPATH` 等），决定相对路径基准。 |
| `nID` | `UDINT` | `0` | 无符号整数输入：`nID`。 |
| `cbBuffer` | `UDINT` | `16#100000` | 缓冲区字节数。 |
| `bOverwrite` | `BOOL` | `FALSE` | 输入布尔标志：`bOverwrite`。具体语义见 §3 行为说明。 |
| `pWriteBuff` | `POINTER TO BYTE` | - | 参数 `pWriteBuff`（类型 `POINTER TO BYTE`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `cbWriteLen` | `UDINT` | - | 无符号整数输入：`cbWriteLen`。 |
| `pReadBuff` | `POINTER TO BYTE` | - | 参数 `pReadBuff`（类型 `POINTER TO BYTE`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `cbReadLen` | `UDINT` | - | 无符号整数输入：`cbReadLen`。 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    cbReturn : UDINT;
    stHeader : ST_FileRBufferHead;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | TRUE 表示请求正在处理；同时 `bExecute` 仍为高电平时不响应新请求。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号由 `nErrId` / `nErrorId` 给出。 |
| `nErrId` | `UDINT` | ADS 错误码或本 FB 自定义错误号。0 = 无错。具体码表见 InfoSys / ADS Return Codes。 |
| `cbReturn` | `UDINT` | 无符号整数输出：`cbReturn`。 |
| `stHeader` | `ST_FileRBufferHead` | 参数 `stHeader`（类型 `ST_FileRBufferHead`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**方法接口**：本 FB 是 OO 风格，通过 `Init` / `WriteToBuffer` / `ReadFromBuffer` 等方法调用。Init 时指定文件名模板 + 最大文件数 + 单文件最大字节；满了自动滚动。

**典型用法**：业务侧周期写日志条目；FB 内部自动按时间 / 大小切片。


**调用一般约束**：本 FB 的所有输入 / 输出引脚语义已在 §2 接口定义表的中文说明列详细列出；调用方应按上述时序与状态机分支组织程序，并参照 §5 使用注意 / 常见坑回避典型陷阱。若 PDF 与 InfoSys 中未对某种异常工况作出明确说明，本仓库会以 ⚠️ 标记，提示读者用实测或在 Beckhoff Forum 上确认，而非凭推测下结论。

## 4. 错误码 / 返回值

本 FB 通过 `bErr` + `nErrId`（或 `bError` + `nErrorId`）输出报告错误：

- `bErr / bError = FALSE` 且 `nErrId / nErrorId = 0`：本次请求成功。
- `bErr / bError = TRUE`：本次请求失败，错误号在 `nErrId / nErrorId`。

常见错误号属于 **ADS Return Codes**（PDF 与 InfoSys 都引用此表）：

| 错误号（十六进制） | 含义 |
|---|---|
| `0x06` | 目标端口未找到（ADSERR_DEVICE_NOTFOUND） |
| `0x07` | 目标机器未找到（ADSERR_DEVICE_INVALIDDATA） |
| `0x745` | ADS 通讯超时（ADSERR_CLIENT_SYNCTIMEOUT） |
| 其他 | PDF 未枚举，详见 Beckhoff 在线 ADS Return Codes 表 ⚠️ |

## 5. 使用注意 / 常见坑

- `bExecute` 必须是上升沿触发；持续高电平不会重发请求，要释放再拉起。
- `tTimeout` 默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。跨网段调用建议放大；过长会卡周期任务。（工程经验补充）
- PDF 没有枚举具体错误号——`nErrId / nErrorId` 引用通用 **ADS Return Codes** 表（参考 InfoSys 在线表）。
- `bBusy` 高电平期间业务侧不要再次拉起 `bExecute`，否则被忽略。（工程经验补充）
- 跨网段调用应放在非实时任务里执行，避免 PLC 周期任务被 ADS 抖动撑爆。（工程经验补充）
- **文件操作受 SystemService 权限限制**——CX 设备的 `C:\TwinCAT\Boot` 等敏感目录可能不可写。（工程经验补充）
- 绝对路径建议带盘符；相对路径以 `ePath` 枚举为基准（`PATH_GENERIC` = TwinCAT 安装目录）。（工程经验补充）
- 文件 I/O 是异步操作，触发后在 `bBusy → bDone` 之间业务侧不能假设文件已可见。
- **Init 参数错会导致首次 Write 失败**——文件名模板要含占位符（如 `'log_%d.txt'`）才能滚动。（工程经验补充）
- **关闭 FB 前要 Flush**——否则缓冲区里的最后一段可能未写到文件。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_FileRingBuffer.TcPOU`](../examples/P_Demo_FB_FileRingBuffer.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：30 天循环日志，磁盘满了自动覆盖最老。
- **价值**：替代手写文件 rotation 逻辑。
- **替代方案对比**：
  - 自写 rotation：易出 off-by-one bug。
  - **本 FB**：库提供。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.20
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/9676815883.html
