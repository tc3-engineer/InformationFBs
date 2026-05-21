# FB_FileLoad

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `File function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/7083988875.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_FileLoad.xml`](../examples/P_Demo_FB_FileLoad.xml) |

---

## 1. 功能简述

FB_FileLoad 是 `FB_FileOpen` + `FB_FileRead` + `FB_FileClose` 的一次性封装。给定路径和缓冲区，本 FB 自动以二进制模式打开文件、读取最多 `cbReadLen` 字节到缓冲区、然后自动关闭。适用于一次性把整份小配置 / 配方文件读进内存的场景，无需自己维护句柄。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId : T_AmsNetId;
    sPathName : T_MaxString;
    pReadBuff : PVOID;
    cbReadLen : UDINT;
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | - | 目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。**注意**：路径只能指向本地文件系统，网络路径不支持。 |
| `sPathName` | `T_MaxString` | - | 要读取的文件本地路径。**只能本地路径**。 |
| `pReadBuff` | `PVOID` | - | 本地缓冲区起始地址，`ADR(myVar)`。 |
| `cbReadLen` | `UDINT` | - | 缓冲区容量字节数，应等于 `SIZEOF(buf)`。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次 ADS 请求；调用期间保持高电平，完成后自动复位无需手动清零。 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。跨网段建议加到 10 秒以上。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    cbRead : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | TRUE 表示请求正在 ADS 通道上处理；同周期内 `bExecute` 仍为高电平也不会重新触发。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号在 `nErrId`。`bBusy` 复位为 FALSE 后才可信。 |
| `nErrId` | `UDINT` | ADS 错误码（见 ADS Return Codes）；常见值 `0x70C` 文件不存在、`0x70D` 文件已存在、`0x745` ADS 超时、`0x1804` 路径未知。 |
| `cbRead` | `UDINT` | **输出**：实际读到的字节数；可能小于 `cbReadLen`（文件不够大）或 = `cbReadLen`（文件至少这么大但被截断）。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：周期调用，`bExecute` 上升沿触发整个 Open/Read/Close 序列。完成后 `bBusy = FALSE`，`cbRead` 给出实际读到的字节数。

**文件以二进制模式打开**（PDF 明确指出 implicit binary mode），所以读 CSV / 日志会保留 CR+LF 不做转换。

**缓冲区责任**：`pReadBuff` + `cbReadLen` 由调用方负责保证有效；`cbReadLen` 通常 = 缓冲区 `SIZEOF`。

**比手动三步省**：不用关心 `hFile` 生命周期；适合配方 / 配置 / 状态快照恢复。

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

- **只能读到 `cbReadLen` 字节**：文件超过该值的部分被丢弃，不会报错；要全文读，缓冲区必须 ≥ 文件大小。
- **二进制模式**：Windows 文本文件的 CR+LF 不会被转换为 LF，对比文本时注意。
- **`cbReadLen` > 缓冲区**：FB 不查越界，会越界写。永远 `cbReadLen := SIZEOF(buf)`。
- **ADS 报文上限**：单次 ≈ 1 MB；超过应用 `FB_FileOpen` + 分段 `FB_FileRead`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_FileLoad.xml`](../examples/P_Demo_FB_FileLoad.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：设备启动后一次性把 D:/config/recipe.bin 配方文件（约 4 KB）读入 stRecipeBuffer 结构体，作为运行参数。
- **价值**：替代 Open + Read + Close 三步状态机，省约 25 行代码。
- **替代方案对比**：
  - 手动 Open/Read/Close 三段：灵活但啰嗦。
  - 配合 `FB_FileGets` 按行读：文本场景更适合。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.3.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/7083988875.html
- **相关 FB / FC**：`FB_FileOpen`, `FB_FileRead`, `FB_FileClose`
