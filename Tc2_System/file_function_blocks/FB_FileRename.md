# FB_FileRename

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `File function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30982155.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_FileRename.TcPOU`](../examples/P_Demo_FB_FileRename.TcPOU) |

---

## 1. 功能简述

FB_FileRename 把目标 PC 本地文件系统中的一个文件改名（也可以同时变目录，本质上是 OS 的 rename / move 调用）。源路径 `sOldName` 和目的路径 `sNewName` 都相对于同一个 `ePath` 基准。适用于班次切换时把当日日志 'process.csv' 改名为 '20260520.csv' 归档。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId : T_AmsNetId;
    sOldName : T_MaxString;
    sNewName : T_MaxString;
    ePath : E_OpenPath := PATH_GENERIC;
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | - | 目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。**注意**：路径只能指向本地文件系统，网络路径不支持。 |
| `sOldName` | `T_MaxString` | - | 源文件路径（绝对或相对 `ePath`）。 |
| `sNewName` | `T_MaxString` | - | 目标文件路径（绝对或相对 `ePath`）。 |
| `ePath` | `E_OpenPath` | `PATH_GENERIC` | 路径基准枚举，同时作用于 `sOldName` 和 `sNewName`。默认 `PATH_GENERIC`。 |
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

**调用方式**：周期调用，`bExecute` 上升沿触发一次改名。完成后 `bBusy = FALSE`，成功 `bError = FALSE`。

**同盘改名是原子操作**：在同一磁盘卷内改名是 OS 原子 rename，瞬间完成。

**跨盘是复制 + 删除**：目标和源在不同盘符时，OS 会做复制然后删除，时间随文件大小线性增长。

**目标已存在**：PDF 未明确目标存在时的行为，实测通常拒绝（错误 80 / FILE_EXISTS），建议先确保目标不存在。

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

- **目标已存在会失败**：覆盖目标需要先 `FB_FileDelete` 删除目标。
- **跨盘改名很慢**：内部是复制 + 删除；大文件可能要数秒到数十秒，`tTimeout` 默认 5 秒可能不够。
- **正在被打开的文件**：源文件 `hFile` 未 Close 时通常无法 rename（错误 32）。
- **`PATH_GENERIC` 默认**：相对路径基准是 TwinCAT Boot 目录，建议显式用 `PATH_GENERIC_USERDATA` 或写绝对路径。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_FileRename.TcPOU`](../examples/P_Demo_FB_FileRename.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：班次切换：把当日累计日志 'D:/log/process.csv' 改名为 'D:/log/20260520.csv' 归档，准备新建空文件继续记录。
- **价值**：封装 ADS rename 命令；替代 OS 命令行调用。
- **替代方案对比**：
  - OS shell `rename` 命令 + `WinExecute`：能但绕弯。
  - 复制内容到新文件 + 删旧文件：低效且非原子。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.3.12
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30982155.html
- **相关 FB / FC**：`FB_FileDelete`, `FB_FileOpen`, `FB_CreateDir`
