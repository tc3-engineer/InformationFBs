# FB_FileRead

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `File function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30980619.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_FileRead.xml`](../examples/P_Demo_FB_FileRead.xml) |

---

## 1. 功能简述

FB_FileRead 通过 ADS 从一个已经用 `FB_FileOpen` 打开的文件读取指定字节数到本地缓冲区。读取的起点是当前文件指针位置；调用结束后文件指针自动向前推进读取的字节数，下次再调可继续读后续内容。对于按记录顺序消费的二进制 / 文本文件，本 FB 是流式读取的主力。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId : T_AmsNetId;
    hFile : UINT;
    pReadBuff : PVOID;
    cbReadLen : UDINT;
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | - | 目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。**注意**：路径只能指向本地文件系统，网络路径不支持。 |
| `hFile` | `UINT` | - | 文件句柄，由 `FB_FileOpen` 调用成功后返回的 `hFile`。所有后续读 / 写 / 关闭都要传同一个句柄。 |
| `pReadBuff` | `PVOID` | - | 读入缓冲区起始地址，调用方用 `ADR(myVar)` 取地址。本 FB 不做边界检查，调用方负责保证 `cbReadLen` 字节可写。 |
| `cbReadLen` | `UDINT` | - | 本次最多读取的字节数，应等于缓冲区大小 `SIZEOF(buf)`。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次 ADS 请求；调用期间保持高电平，完成后自动复位无需手动清零。 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。跨网段建议加到 10 秒以上。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    cbRead : UDINT;
    bEOF : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | TRUE 表示请求正在 ADS 通道上处理；同周期内 `bExecute` 仍为高电平也不会重新触发。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号在 `nErrId`。`bBusy` 复位为 FALSE 后才可信。 |
| `nErrId` | `UDINT` | ADS 错误码（见 ADS Return Codes）；常见值 `0x70C` 文件不存在、`0x70D` 文件已存在、`0x745` ADS 超时、`0x1804` 路径未知。 |
| `cbRead` | `UDINT` | **输出**：实际读到的字节数。`< cbReadLen` 可能因到达 EOF / 文本模式换行；`= 0` 通常代表 EOF。 |
| `bEOF` | `BOOL` | **输出**：TRUE = 本次读到达文件末尾。可与 `cbRead = 0` 联合作循环退出条件。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：周期调用，`bExecute` 上升沿触发一次读取，`bBusy` 期间不响应新触发。读完后 `bBusy = FALSE`，`cbRead` 给出实际读到的字节数（**可能小于 `cbReadLen`**：到文件末尾或文本模式下提前遇到换行）。

**缓冲区责任**：`pReadBuff` 由调用方提供，必须保证 `cbReadLen` 字节可写。常见写法 `pReadBuff := ADR(myBuffer)` + `cbReadLen := SIZEOF(myBuffer)`。本 FB 不做越界检查，越界会写坏邻近变量。

**EOF 检测**：`bEOF` 输出为 TRUE 表示本次读到达文件末尾；与 `cbRead = 0` 共同用于循环退出条件。

**文本 vs 二进制模式**：文本模式下 OS 会做 CR/LF → LF 转换，`cbRead` 是转换后的字节数，可能小于物理文件偏移推进量；要按字节精确读用 `FOPEN_MODEBINARY`。

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

- **`pReadBuff` 缓冲区越界**：`cbReadLen > SIZEOF(buffer)` 会让 FB 越界写本地变量，导致幽灵 bug 而无任何错误提示。**永远** `cbReadLen := SIZEOF(buf)`，不要手填常量。
- **忘检 EOF 死循环**：在 while 中调用 `FB_FileRead` 必须用 `cbRead = 0 OR bEOF` 退出条件，否则文件末尾后会无限触发返回 0 字节。
- **短读不是错误**：文本模式下可能 `cbRead < cbReadLen` 但 `bError = FALSE`，业务侧不能把『短读』当成错误。
- **句柄非法**：传 0 或已 Close 的 `hFile` → `bError = TRUE`，`nErrId` 通常是 `0x70C`。
- **大文件分段**：单次最大字节数受 ADS 报文上限限制（约 1 MB），更大文件要循环读多次。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_FileRead.xml`](../examples/P_Demo_FB_FileRead.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：启动时把存盘的配方 CSV 一次或分块读入内存数组，恢复上次班次的工艺参数。
- **价值**：封装好 ADS 0x10003 读命令的状态机 + EOF 检测；不用本 FB 要自己跟 ADS 流并解析二进制响应。
- **替代方案对比**：
  - `FB_FileLoad`：整文件一次性读取，自动 Open/Close，对配置文件更省事。
  - `FB_FileGets`：按行读文本，自带换行截断。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.3.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30980619.html
- **相关 FB / FC**：`FB_FileOpen`, `FB_FileClose`, `FB_FileLoad`, `FB_FileGets`, `FB_FileSeek`
