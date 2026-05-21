# FB_RemoveDir

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `File function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30989835.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_RemoveDir.xml`](../examples/P_Demo_FB_RemoveDir.xml) |

---

## 1. 功能简述

FB_RemoveDir 从目标 PC 本地文件系统中删除一个目录。**只能删空目录**——目录里如果还有文件 / 子目录，删除会失败。适用于归档完成后清理临时目录，或定期清理空目录。

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
| `sPathName` | `T_MaxString` | - | 要删除的目录路径。**目录必须为空**。 |
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

**调用方式**：周期调用，`bExecute` 上升沿触发一次删除。

**只删空目录**：PDF 明确指出『A directory containing files cannot be deleted』。要递归删除整个目录树，需要先枚举所有内容用 `FB_FileDelete` 删完再删目录。Tc2_System 本身不带目录枚举 API（Walk / FindFirstFile 之类），递归清理需通过 ADS 文件枚举接口或调 OS shell 完成。

**目录不存在**：报错（OS 错误号 2 / FILE_NOT_FOUND）。

**目录被占用**：进程当前工作目录在该目录、或目录里某文件被打开未关闭，删除会返回 SHARING_VIOLATION（错误号 32）；调用前应当确保所有 `FB_FileOpen` 已 Close。

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

- **非空目录无法删**：要清空目录树需自己写递归（Tc2_System 不带 Walk API），或调 OS shell。
- **`PATH_GENERIC` 默认**：相对路径在 Boot 目录下，建议显式绝对路径。（工程经验补充）
- **目录被占用**：进程 cwd 在该目录或某文件被打开未关 → 删除失败（错误 32 / SHARING_VIOLATION）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_RemoveDir.xml`](../examples/P_Demo_FB_RemoveDir.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：月底归档完成后删掉空的临时目录 'D:/log/tmp_archive'，整理磁盘结构。
- **价值**：封装 ADS rmdir 命令；非空目录的递归清空需要自己处理。
- **替代方案对比**：
  - 直接 OS shell `rmdir /s`：能递归但绕弯。
  - 自写递归：枚举 + 删文件 + 删目录三步。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.3.14
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30989835.html
- **相关 FB / FC**：`FB_CreateDir`, `FB_FileDelete`
