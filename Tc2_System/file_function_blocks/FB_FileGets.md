# FB_FileGets

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `File function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30976011.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_FileGets.xml`](../examples/P_Demo_FB_FileGets.xml) |

---

## 1. 功能简述

FB_FileGets 从已用文本模式打开的文件中读取一行文本到字符串 `sLine`，遇到换行符或字符串容量上限（`T_MaxString` = 255 字节）即停止。末尾的换行符**包含在内**返回，调用方需自行用 `MID` / `LEFT` 或 `FIND` 截掉。适用于按行处理 CSV / INI / 文本日志的场景。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId : T_AmsNetId;
    hFile : UINT;
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | - | 目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。**注意**：路径只能指向本地文件系统，网络路径不支持。 |
| `hFile` | `UINT` | - | 文件句柄，由 `FB_FileOpen` 调用成功后返回的 `hFile`。所有后续读 / 写 / 关闭都要传同一个句柄。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次 ADS 请求；调用期间保持高电平，完成后自动复位无需手动清零。 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。跨网段建议加到 10 秒以上。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    sLine : T_MaxString;
    bEOF : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | TRUE 表示请求正在 ADS 通道上处理；同周期内 `bExecute` 仍为高电平也不会重新触发。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号在 `nErrId`。`bBusy` 复位为 FALSE 后才可信。 |
| `nErrId` | `UDINT` | ADS 错误码（见 ADS Return Codes）；常见值 `0x70C` 文件不存在、`0x70D` 文件已存在、`0x745` ADS 超时、`0x1804` 路径未知。 |
| `sLine` | `T_MaxString` | **输出**：读到的一行文本（含末尾 LF），最长 `T_MaxString`（255）字节。 |
| `bEOF` | `BOOL` | 布尔标志：`bEOF`。具体语义见 §3 行为说明。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：周期调用，`bExecute` 上升沿触发一次读取。读取过程：从当前文件指针开始向前扫描，遇到 LF（`16#0A`）即停止并把含换行的字符串返回；若先到 `T_MaxString` 长度上限则截断返回；若先到 EOF 则返回已读到的部分并把 `bEOF = TRUE`。

**文件必须文本模式打开**：PDF 明确要求 `FOPEN_MODETEXT`，二进制模式下行为未定义。

**`sLine` 自动空终止**：返回字符串带 null 终止符（C 风格），可直接当 IEC `STRING` 用。

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

- **换行符没去掉**：`sLine` 末尾带 `$N`（LF），后续比对 / 拼接前应当 `LEN := LEN(sLine); IF MID(sLine, 1, LEN) = '$N' THEN ...; END_IF`。
- **必须文本模式**：二进制模式打开的文件喂给本 FB 行为未定义；常见症状是 `sLine` 中含 CR 字符。
- **超长行被截断**：超过 255 字节的行只会返回前 255 字节，剩余在下次调用时返回；CSV 列数过多时要注意。
- **句柄非法**：传 0 或已 Close 的 `hFile` → `bError = TRUE`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_FileGets.xml`](../examples/P_Demo_FB_FileGets.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：启动时逐行读取 D:/config/recipe.csv 文件，把每一行解析成一条配方记录恢复到内存中。
- **价值**：比 `FB_FileRead` + 自己扫换行省心；用 `FB_FileLoad` 全文件读再分割也行但占内存。
- **替代方案对比**：
  - `FB_FileRead`：手动按字节读，自己找换行。
  - `FB_FileLoad`：一次性读全文，适合 < 几 KB 的小配置。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.3.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30976011.html
- **相关 FB / FC**：`FB_FileOpen`, `FB_FilePuts`, `FB_FileRead`
