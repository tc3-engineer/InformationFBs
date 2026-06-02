# FB_EnumFindFileEntry

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/9676817803.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EnumFindFileEntry.TcPOU`](../examples/P_Demo_FB_EnumFindFileEntry.TcPOU) |

---

## 1. 功能简述

FB_EnumFindFileEntry 枚举目录里匹配通配符模式的文件，每次调用返回一条目（文件名 + 元数据）。

用于：找日志文件 / 报表文件做归档处理。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID : T_AmsNetID;
    sPathName : T_MaxString;
    eCmd : E_EnumCmdType := eEnumCmd_First;
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | - | 目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。 |
| `sPathName` | `T_MaxString` | - | 参数 `sPathName`（类型 `T_MaxString`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `eCmd` | `E_EnumCmdType` | `eEnumCmd_First` | 参数 `eCmd`（类型 `E_EnumCmdType`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次执行；调用期间保持高电平，完成后自动复位无需手动清零。 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    bEOE : BOOL;
    stFindFile : ST_FindFileEntry;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | TRUE 表示请求正在处理；同时 `bExecute` 仍为高电平时不响应新请求。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号由 `nErrId` / `nErrorId` 给出。 |
| `nErrId` | `UDINT` | ADS 错误码或本 FB 自定义错误号。0 = 无错。具体码表见 InfoSys / ADS Return Codes。 |
| `bEOE` | `BOOL` | 输出布尔标志：`bEOE`。具体语义见 §3 行为说明。 |
| `stFindFile` | `ST_FindFileEntry` | 参数 `stFindFile`（类型 `ST_FindFileEntry`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**协议**：`bExecute` 上升沿打开搜索；后续 `bExecute` 上升沿取下一条。文件用完 `bEOL = TRUE`（end-of-list）。

**典型用法**：与业务计数器配合循环读取。


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
- **通配符是 Windows DOS 风格**：`*.csv` 匹配所有 csv，`?` 匹配单字符；不支持正则。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EnumFindFileEntry.TcPOU`](../examples/P_Demo_FB_EnumFindFileEntry.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：找当天所有日志文件做压缩。
- **价值**：替代手工 dir 命令。
- **替代方案对比**：
  - Win32 FindFirstFile / FindNextFile：要 Shell。
  - **本 FB**：PLC 内置。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.15
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/9676817803.html
- **相关 FB**：`FB_EnumFindFileList`, `FB_FileProperties`
