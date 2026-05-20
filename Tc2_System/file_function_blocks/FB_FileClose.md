# FB_FileClose

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `File function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30972939.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_FileClose.xml`](../examples/P_Demo_FB_FileClose.xml) |

---

## 1. 功能简述

FB_FileClose 通过 ADS 异步关闭一个由 `FB_FileOpen` 打开的文件，把缓冲区落盘并释放句柄。每个成功的 `FB_FileOpen` 调用必须配对一次 `FB_FileClose`，否则目标 PC 上文件句柄持续被占用，长时间运行会耗尽系统句柄表。

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
| `hFile` | `UINT` | - | 要关闭的文件句柄，必须是 `FB_FileOpen` 成功返回的 `hFile`。 |
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

**调用方式**：周期调用直到 `bBusy` 复位。`bExecute` 上升沿触发，ADS 异步关闭文件并刷盘。关闭后 `hFile` 在外部仍存有数值，但调用方必须主动清零以防误用：典型代码 `IF NOT bBusyMon AND NOT bErrMon THEN hFile := 0; END_IF;`。

**关闭语义**：关闭操作会强制刷写 OS 文件缓冲，对于以 `FOPEN_MODEWRITE` 或 `FOPEN_MODEAPPEND` 打开的文件，未 Close 时落盘不保证，断电易导致写入丢失。

**错误情况**：`hFile` 已经被关过、或不属于本 PC、或 ADS 通讯失败会导致 `bError = TRUE` 并在 `nErrId` 返回错误号。重复 Close 同一句柄通常返回错误而不会崩溃。

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

- **未关闭句柄泄漏**：长时间运行 / 频繁 Open 不 Close 的程序最终会耗尽 OS 句柄表，表现为后续 `FB_FileOpen` 永远 `bError = TRUE`。
- **必须主动清零 `hFile` 本地变量**：FB 不会把外部 `hFile` 自动清零，重复传递已关闭的句柄给读 / 写会得到错误号。
- **程序异常退出未 Close**：在线下载、PLC Reset、调试中断都不会自动 Close；建议把 Close 放在 `FB_Exit` / `FB_Reinit` 钩子中。（工程经验补充）
- **断电不刷盘**：未 Close 时缓冲区可能仍在 OS 缓存，CX 突然断电会丢数据。建议关键日志写完一行就主动 Close，或配合 `FB_S_UPS_*` 在掉电时强制 Close。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_FileClose.xml`](../examples/P_Demo_FB_FileClose.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：班次结束时关闭整天累计的工艺日志文件，确保所有缓冲数据落盘以防夜间断电丢失。
- **价值**：封装好 ADS 关闭命令的 busy / done 状态机；不用本 FB 要自己组装 IndexGroup 0x10004 ADS Write 命令并跟踪状态。
- **替代方案对比**：
  - `FB_FileLoad`：读模式下可以一次性读完并自动关闭，无须手动 Close。
  - 直接 `ADSWRITE`：能用但要自己跟状态。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.3.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30972939.html
- **相关 FB / FC**：`FB_FileOpen`, `FB_FileRead`, `FB_FileWrite`
