# FB_CreateDir

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `File function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30988299.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_CreateDir.TcPOU`](../examples/P_Demo_FB_CreateDir.TcPOU) |

---

## 1. 功能简述

FB_CreateDir 在目标 PC 本地文件系统中创建一个新目录。只能创建**单级**目录——`sPathName` 中的父目录必须已存在；不能像 `mkdir -p` 一次性创建多级。适用于按日期 / 班次自动归档日志：每天上电时确保 'D:/log/<YYYYMMDD>' 目录存在。

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
| `sPathName` | `T_MaxString` | - | 要创建的目录路径。父目录必须已存在（**不递归补建**）。 |
| `ePath` | `E_OpenPath` | `PATH_GENERIC` | 路径基准。默认 `PATH_GENERIC`。 |
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

**调用方式**：周期调用，`bExecute` 上升沿触发一次创建。完成后 `bBusy = FALSE`，成功时 `bError = FALSE`。

**单级限制**：`D:/log/2026/05/20` 必须 `D:/log/2026` 与 `D:/log/2026/05` 已存在，本 FB 不会递归补建多级。要一次性建多级，调用方应当循环调用本 FB，从顶层目录开始逐层创建，遇到错误号 183（目录已存在）继续即可。

**目录已存在**：PDF 未明确，实测通常返回错误（错误号 183 / ALREADY_EXISTS），调用方可以选择忽略此错误号视为已就绪状态。

**`ePath` 路径基准**：与 `FB_FileOpen` 一致，建议用 `PATH_GENERIC` + 绝对路径或 `PATH_GENERIC_USERDATA` + 相对路径避免误建到 Boot 目录。

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

- **单级**：要建多级用循环或先 `FB_RemoveDir` 测试父目录。
- **目录已存在**：报错号 183（ALREADY_EXISTS）；业务侧可视为『已就绪』。
- **`PATH_GENERIC` 默认**：相对路径在 TwinCAT Boot 目录下，建议显式绝对路径。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CreateDir.TcPOU`](../examples/P_Demo_FB_CreateDir.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：每日 0 点 PLC 自动确保 'D:/log/20260520' 目录存在，准备当天日志写入。
- **价值**：封装 ADS mkdir 命令的状态机。
- **替代方案对比**：
  - 提前手工建好年 / 月目录：可行但繁琐。
  - OS shell `mkdir`：能但绕弯。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.3.13
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30988299.html
- **相关 FB / FC**：`FB_RemoveDir`, `FB_FileOpen`
