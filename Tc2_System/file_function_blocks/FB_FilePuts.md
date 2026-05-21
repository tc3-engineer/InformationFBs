# FB_FilePuts

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `File function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30979083.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_FilePuts.xml`](../examples/P_Demo_FB_FilePuts.xml) |

---

## 1. 功能简述

FB_FilePuts 把一个 `T_MaxString` 字符串写入已用文本模式打开的文件，写入长度为该字符串的有效字符数（直到 null 终止符，不含 null）。**不自动加换行符**：调用方需要换行的话自己在字符串末尾拼 `'$N'`。适用于按行追加文本日志 / CSV 行写入。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId : T_AmsNetId;
    hFile : UINT;
    sLine : T_MaxString;
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | - | 目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。**注意**：路径只能指向本地文件系统，网络路径不支持。 |
| `hFile` | `UINT` | - | 文件句柄，由 `FB_FileOpen` 调用成功后返回的 `hFile`。所有后续读 / 写 / 关闭都要传同一个句柄。 |
| `sLine` | `T_MaxString` | - | 要写入的字符串（最长 `T_MaxString`，255 字节）。**不自动加换行**，要换行自己拼 `$N`。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次 ADS 请求；调用期间保持高电平，完成后自动复位无需手动清零。 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。跨网段建议加到 10 秒以上。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | TRUE 表示请求正在 ADS 通道上处理；同周期内 `bExecute` 仍为高电平也不会重新触发。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号在 `nErrId`。`bBusy` 复位为 FALSE 后才可信。 |
| `nErrId` | `UDINT` | ADS 错误码（见 ADS Return Codes）；常见值 `0x70C` 文件不存在、`0x70D` 文件已存在、`0x745` ADS 超时、`0x1804` 路径未知。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：周期调用，`bExecute` 上升沿触发一次写入。`sLine` 中的可见字符（直到 null）被写到当前文件指针位置或追加模式下的末尾。

**字符串长度**：本 FB 写的字节数 = `LEN(sLine)`，不含尾部 null。

**换行符**：PDF 没说本 FB 自动加 LF；要换行必须自己拼 `CONCAT(sData, '$N')`。文本模式下写 `$N`，OS 在 Windows 上会自动转成 CR+LF。

**文件必须文本模式打开**：与 `FB_FileGets` 对应。

## 4. 错误码 / 返回值

本 FB 通过 `bError` + `nErrId` 输出报告错误：

- `bError = FALSE` 且 `nErrId = 0`：调用成功。
- `bError = TRUE`：调用失败，错误号在 `nErrId`（**ADS Return Codes**）。

常见错误号（部分）：

| 错误号（十六进制） | 含义 |
|---|---|
| `0x06` | 目标端口未找到（ADSERR_DEVICE_NOTFOUND） |
| `0x70C` | 文件不存在 / 路径无效（ADSERR_DEVICE_NOTFOUND_FILE） |
| `0x70D` | 文件已存在（创建模式时） |
| `0x745` | ADS 通讯超时（ADSERR_CLIENT_SYNCTIMEOUT） |
| `0x1804` | 路径错误（FOPEN_MODEAPPEND 时常见，需路径已知） |
| 其他 | 见 Beckhoff ADS Return Codes 在线表 |

## 5. 使用注意 / 常见坑

- **不自动加换行**：很多人误以为像 C 的 `fputs` 加换行，结果整个文件挤成一行。要换行自己 `sLine := CONCAT(sData, '$N')`。
- **必须文本模式**：二进制模式打开的文件喂给本 FB 行为未定义。
- **句柄非法**：传 0 或已 Close 的 `hFile` → `bError = TRUE`，错误号 `0x70C`。
- **字符串截断**：`T_MaxString` 限 255 字节，超长行用 `FB_FileWrite` 写。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_FilePuts.xml`](../examples/P_Demo_FB_FilePuts.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：把每条工艺事件（时间戳 + 事件文本，约 80 字符）以 CSV 行格式追加写入 D:/log/events.csv。
- **价值**：比 `FB_FileWrite` + ADR + SIZEOF 更直观；纯字符串行写入主力。
- **替代方案对比**：
  - `FB_FileWrite`：能写任何字节，灵活但 verbose。
  - TF3500 Logger：付费、高吞吐。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.3.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30979083.html
- **相关 FB / FC**：`FB_FileOpen`, `FB_FileGets`, `FB_FileWrite`
