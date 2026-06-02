# FB_FileSeek

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `File function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30983691.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_FileSeek.TcPOU`](../examples/P_Demo_FB_FileSeek.TcPOU) |

---

## 1. 功能简述

FB_FileSeek 把已打开文件的读 / 写指针移动到指定位置。`nSeekPos` + `eOrigin` 共同决定新位置：`SEEK_SET`（从文件头）、`SEEK_CUR`（从当前位置）、`SEEK_END`（从文件末尾，`nSeekPos` 通常为负）。适用于在大文件里跳到特定偏移读 / 写，或在循环日志里 wrap-around 写入。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId : T_AmsNetId;
    hFile : UINT;
    nSeekPos : DINT;
    eOrigin : E_SeekOrigin := SEEK_SET;
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | - | 目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。**注意**：路径只能指向本地文件系统，网络路径不支持。 |
| `hFile` | `UINT` | - | 文件句柄，由 `FB_FileOpen` 调用成功后返回的 `hFile`。所有后续读 / 写 / 关闭都要传同一个句柄。 |
| `nSeekPos` | `DINT` | - | 新指针位置（相对 `eOrigin` 基准）。`SEEK_SET` 必须 ≥ 0；`SEEK_CUR` / `SEEK_END` 可为负。 |
| `eOrigin` | `E_SeekOrigin` | `SEEK_SET` | 基准点：`SEEK_SET`（文件头） / `SEEK_CUR`（当前位置） / `SEEK_END`（文件末尾）。默认 `SEEK_SET`。 |
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

**调用方式**：周期调用，`bExecute` 上升沿触发一次移动。

**三种基准 `eOrigin`**：

- `SEEK_SET`：`nSeekPos` 直接作为新指针位置（必须 ≥ 0）。
- `SEEK_CUR`：新位置 = 当前指针 + `nSeekPos`（可正可负）。
- `SEEK_END`：新位置 = 文件大小 + `nSeekPos`（通常 ≤ 0，正值会越过末尾）。

**追加模式限制**：以 `FOPEN_MODEAPPEND` / `a+` 打开的文件，**写位置始终是末尾**，Seek 只能改读位置；写永远从末尾追加。

**越界行为**：`nSeekPos` 超过文件末尾 PDF 未明确规定；通常成功但下次读会返回 0 字节 (`bEOF = TRUE`)。

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

- **追加模式下 Seek 对写无效**：典型坑：用户在 `a+` 模式下 Seek 到中间想覆盖一段数据，结果数据仍追加到末尾。要随机写必须用 `r+` / `w+`。
- **`nSeekPos` 是 `DINT` 有符号**：`SEEK_CUR` / `SEEK_END` 可用负值；`SEEK_SET` 用负值是错误。
- **句柄非法**：传 0 或已 Close 的 `hFile` → `bError = TRUE`。
- **>2 GB 文件**：`nSeekPos` 是 32 位有符号，上限 ≈ 2 GB；超大文件本 FB 不能定位到 2 GB 以后。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_FileSeek.TcPOU`](../examples/P_Demo_FB_FileSeek.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：对二进制循环日志文件 wrap-around 写入：写到文件尾后 Seek 回头部继续写，实现固定大小的环形日志。
- **价值**：封装 ADS 0x10006 命令；不用本 FB 要自己拼 ADS Write 命令。
- **替代方案对比**：
  - `FB_FileTell`：搭配使用，先读位置再 seek 回。
  - `FB_FileClose` + 重 `FB_FileOpen`：粗暴但能用。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.3.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30983691.html
- **相关 FB / FC**：`FB_FileOpen`, `FB_FileTell`, `FB_FileRead`, `FB_FileWrite`
