# FB_FileWrite

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `File function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30986763.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_FileWrite.TcPOU`](../examples/P_Demo_FB_FileWrite.TcPOU) |

---

## 1. 功能简述

FB_FileWrite 通过 ADS 把本地缓冲区指定字节数写入一个已经用 `FB_FileOpen` 打开的文件。起点是当前文件指针（追加模式下强制为末尾），写完后指针向前推进 `cbWrite` 字节。适用于二进制日志 / 数据流的写入；按行写文本用 `FB_FilePuts` 更方便。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId : T_AmsNetId;
    hFile : UINT;
    pWriteBuff : PVOID;
    cbWriteLen : UDINT;
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | - | 目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。**注意**：路径只能指向本地文件系统，网络路径不支持。 |
| `hFile` | `UINT` | - | 文件句柄，由 `FB_FileOpen` 调用成功后返回的 `hFile`。所有后续读 / 写 / 关闭都要传同一个句柄。 |
| `pWriteBuff` | `PVOID` | - | 要写入的数据缓冲区起始地址，用 `ADR(myVar)`。 |
| `cbWriteLen` | `UDINT` | - | 本次要写入的字节数。必须 ≤ 缓冲区实际大小。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次 ADS 请求；调用期间保持高电平，完成后自动复位无需手动清零。 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。跨网段建议加到 10 秒以上。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    cbWrite : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | TRUE 表示请求正在 ADS 通道上处理；同周期内 `bExecute` 仍为高电平也不会重新触发。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号在 `nErrId`。`bBusy` 复位为 FALSE 后才可信。 |
| `nErrId` | `UDINT` | ADS 错误码（见 ADS Return Codes）；常见值 `0x70C` 文件不存在、`0x70D` 文件已存在、`0x745` ADS 超时、`0x1804` 路径未知。 |
| `cbWrite` | `UDINT` | **输出**：实际写入的字节数。正常情况 `= cbWriteLen`；< 该值可能因磁盘满或异常。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：周期调用，`bExecute` 上升沿触发一次写入。`bBusy` 期间不响应新触发；完成后 `bBusy = FALSE`，`cbWrite` 给出实际写入的字节数。

**缓冲区责任**：`pWriteBuff` 由调用方提供有效内存地址，`cbWriteLen` 表示要写的字节数，本 FB 不会越界读但会读 `cbWriteLen` 字节，必须保证缓冲区至少有这么多字节。

**追加模式 vs 写模式**：`FOPEN_MODEAPPEND` 模式下不论指针在哪都从末尾追加；`FOPEN_MODEWRITE` 模式从当前指针位置覆盖式写入。

**不自动 flush**：本 FB 写入完成只是写到 OS 缓冲，断电仍可能丢；落盘要靠 `FB_FileClose` 触发的 flush。

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

- **断电丢数据**：写完不 Close，OS 缓冲区里的数据断电就丢。关键日志写完立刻 Close 或挂 `FB_S_UPS_*` 在掉电时强制 Close。
- **句柄非法**：传 0 或已 Close 的 `hFile` → `bError = TRUE`，错误号 `0x70C`。
- **单次写入上限**：ADS 报文上限约 1 MB，超过要循环多次。（工程经验补充）
- **追加模式下 Seek 无效**：`FB_FileSeek` 改写指针在 `a` / `a+` 模式下对写无效，写仍从末尾。要随机写必须用 `r+` / `w+`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_FileWrite.TcPOU`](../examples/P_Demo_FB_FileWrite.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：把每 100 ms 采集到的工艺数据结构（约 64 字节）追加写入二进制流日志，供日终批处理分析。
- **价值**：封装好 ADS 0x10004 写命令的状态机；不用本 FB 要自己跟 ADS 应答与重发。
- **替代方案对比**：
  - `FB_FilePuts`：按行写文本，自动加 / 不加换行视实现而定，文本日志更方便。
  - TF3500 Analytics Logger：付费、性能强，适合高吞吐二进制日志。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.3.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30986763.html
- **相关 FB / FC**：`FB_FileOpen`, `FB_FileClose`, `FB_FilePuts`, `FB_FileRead`
