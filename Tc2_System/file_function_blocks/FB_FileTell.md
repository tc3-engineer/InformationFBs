# FB_FileTell

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `File function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30985227.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_FileTell.TcPOU`](../examples/P_Demo_FB_FileTell.TcPOU) |

---

## 1. 功能简述

FB_FileTell 返回已打开文件的当前指针位置（从文件头算起的字节偏移），输出到 `nSeekPos`。常与 `FB_FileSeek` 配合使用：先 Tell 保存位置 → 做完读 / 写 → Seek 回原位置。也用于估算文件大小（Seek 到末尾再 Tell）。

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
    nSeekPos : DINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | TRUE 表示请求正在 ADS 通道上处理；同周期内 `bExecute` 仍为高电平也不会重新触发。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号在 `nErrId`。`bBusy` 复位为 FALSE 后才可信。 |
| `nErrId` | `UDINT` | ADS 错误码（见 ADS Return Codes）；常见值 `0x70C` 文件不存在、`0x70D` 文件已存在、`0x745` ADS 超时、`0x1804` 路径未知。 |
| `nSeekPos` | `DINT` | **输出**：当前文件指针字节偏移（从文件头起算）。追加模式下反映最近 I/O 后位置而非下次写位置。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：周期调用，`bExecute` 上升沿触发一次查询。完成后 `nSeekPos` 给出当前指针字节偏移。

**追加模式细节**：PDF 明确指出在 `FOPEN_MODEAPPEND` 模式下，`nSeekPos` 反映的是『最近一次 I/O 操作』后的位置，**不是**下次写入位置——下次写入永远在末尾。读操作后 Tell 反映读完位置；写操作后位置变化未必如直觉。

**未做 I/O 时**：以 `a` / `a+` 打开且尚未读 / 写过，`nSeekPos = 0`（文件头），与 r/w/+ 模式一致。

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

- **追加模式下不是下次写位置**：在 `a` / `a+` 模式下 Tell 出来的位置只是最近一次 I/O 后的位置，**不是**下次写入位置（永远末尾）。要算文件大小用 Seek 到 SEEK_END 再 Tell。
- **句柄非法**：传 0 或已 Close 的 `hFile` → `bError = TRUE`。
- **>2 GB 限制**：`nSeekPos` 是 `UDINT`，理论 4 GB；但 Seek 是 `DINT` 限 2 GB，所以联合使用上限 2 GB。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_FileTell.TcPOU`](../examples/P_Demo_FB_FileTell.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：对一份大配方文件做断点续传读取：把 Tell 拿到的位置存到 retain，重启后 Seek 回原位置继续读。
- **价值**：封装 ADS 0x10007 命令；不用本 FB 要自己拼 ADS Read 命令。
- **替代方案对比**：
  - 手动维护一个本地 UDINT 跟踪每次读写后的偏移：能用但断电后会丢同步。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.3.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30985227.html
- **相关 FB / FC**：`FB_FileOpen`, `FB_FileSeek`
