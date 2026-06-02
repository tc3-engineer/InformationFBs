# FB_FileDelete

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `File function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30974475.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_FileDelete.TcPOU`](../examples/P_Demo_FB_FileDelete.TcPOU) |

---

## 1. 功能简述

FB_FileDelete 通过 ADS 异步删除目标 PC 本地文件系统中的一个文件。删除前不需要 Open；直接给路径 + `ePath` 基准即可。删除操作不可撤销——文件被立刻移到回收站之外的彻底删除。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId : T_AmsNetId;
    sPathName : T_MaxString;
    ePath : E_OpenPath := PATH_GENERIC;
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | - | 目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。**注意**：路径只能指向本地文件系统，网络路径不支持。 |
| `sPathName` | `T_MaxString` | - | 要删除的文件路径（绝对或相对于 `ePath`）。 |
| `ePath` | `E_OpenPath` | `PATH_GENERIC` | 路径基准枚举。默认 `PATH_GENERIC`。 |
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

**调用方式**：周期调用，`bExecute` 上升沿触发一次删除。完成后 `bBusy = FALSE`，成功时 `bError = FALSE`。

**路径基准 `ePath`**：与 `FB_FileOpen` 一致，默认 `PATH_GENERIC`；要删 Boot 目录文件用 `PATH_BOOTPATH`。

**不可恢复**：本 FB 调用 OS 删除 API，不进回收站，删完即丢。

**正在被打开的文件**：如果文件还有 `hFile` 没 Close，Windows 通常拒绝删除（错误 32：文件被占用）。

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

- **误删风险**：路径错一个字符可能删掉重要文件且不可恢复。建议先用 `F_FileExists` 风格的检查再删（Tc2_System 没有直接的存在性查询，需通过 `FB_FileOpen` 尝试只读打开判断）。
- **被占用文件删除失败**：打开未关闭的文件删不掉，`nErrId` 通常返回 OS 错误码（32 SHARING_VIOLATION）。
- **通配符不支持**：`sPathName` 只能是单个文件名，不能 `*.log` 批删；批删要自己枚举目录。（工程经验补充）
- **`PATH_GENERIC` 默认**：写相对路径时实际在 TwinCAT Boot 目录下，常意外删错文件。建议显式写绝对路径或选 `PATH_GENERIC_USERDATA`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_FileDelete.TcPOU`](../examples/P_Demo_FB_FileDelete.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：每月清理一次过期的工艺日志文件，把上个月的 'D:/log/2026-04.csv' 删除腾空间。
- **价值**：封装 ADS 0x10008 命令；不用本 FB 要自己拼 ADS Write 命令。
- **替代方案对比**：
  - 直接 `ADSWRITE`：能用但要自己跟状态。
  - Windows 任务计划脚本：操作系统级，不依赖 PLC。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.3.11
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30974475.html
- **相关 FB / FC**：`FB_FileOpen`, `FB_FileRename`, `FB_CreateDir`, `FB_RemoveDir`
