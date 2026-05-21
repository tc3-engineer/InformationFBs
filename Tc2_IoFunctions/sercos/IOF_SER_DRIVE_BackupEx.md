# IOF_SER_DRIVE_BackupEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `SERCOS` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59126923.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_IOF_SER_DRIVE_BackupEx.xml`](../examples/P_Demo_IOF_SER_DRIVE_BackupEx.xml) |

---

## 1. 功能简述

加强版 SERCOS drive 备份 / 恢复 FB。比 `IOF_SER_DRIVE_Backup` 多两点：① 支持自定义参数清单 (`bUserBackupList`)，用 `arrList` 数组定义要备份的 IDN 列表；② 支持 `bIgnoreParamErr` 让备份遇到不可读参数时跳过而不是中止。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bCheck : BOOL;
    bBackup : BOOL;
    bRestore : BOOL;
    bCRCEnable : BOOL;
    bStdBackupList : BOOL := TRUE;
    bUserBackupList : BOOL;
    sNetId : T_AmsNetId;
    nPort : UINT;
    sComment : T_MaxString;
    ePath : E_OpenPath := PATH_BOOTPATH;
    sPathName : T_MaxString := 'DRIVEPAR.BIN';
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
    bIgnoreParamErr : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bCheck` | `BOOL` | - | CRC 校验。 |
| `bBackup` | `BOOL` | - | 备份。 |
| `bRestore` | `BOOL` | - | 恢复。 |
| `bCRCEnable` | `BOOL` | - | 启用 CRC。 |
| `bStdBackupList` | `BOOL` | `TRUE` | TRUE = IDN-192。 |
| `bUserBackupList` | `BOOL` | - | TRUE = 用用户自定义清单。 |
| `sNetId` | `T_AmsNetId` | - | 本机用空串。 |
| `nPort` | `UINT` | - | drive port。 |
| `sComment` | `T_MaxString` | - | 注释。 |
| `ePath` | `E_OpenPath` | `PATH_BOOTPATH` | 路径常量。 |
| `sPathName` | `T_MaxString` | `'DRIVEPAR.BIN'` | 文件名。 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |
| `bIgnoreParamErr` | `BOOL` | - | TRUE = 备份时跳过不可读参数。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    bCheckOK : BOOL;
    iSkippedParams : UINT;
    iHandledParams : UINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bError` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `nErrId` | `UDINT` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |
| `bCheckOK` | `BOOL` | 布尔标志 `bCheckOK`。 |
| `iSkippedParams` | `UINT` | 无符号整数 `iSkippedParams`。 |
| `iHandledParams` | `UINT` | 无符号整数 `iHandledParams`。 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    arrList : ST_SercosParamList;
    arrSkippedList : ST_SercosParamErrList;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `arrList` | `ST_SercosParamList` | 参数 `arrList`（类型 `ST_SercosParamList`）。 |
| `arrSkippedList` | `ST_SercosParamErrList` | 参数 `arrSkippedList`（类型 `ST_SercosParamErrList`）。 |

## 3. 行为说明

触发方式与 `IOF_SER_DRIVE_Backup` 相同：`bCheck` / `bBackup` / `bRestore` 三个上升沿触发位互斥。`bStdBackupList = TRUE` 用 IDN-192；`bUserBackupList = TRUE` 用用户自定义清单（必须提供 `arrList` 数组——⚠️ PDF VAR 区未列 arrList，但 PDF 正文说"用 arrList 数组"，⚠️ 待人工确认接口）。`bIgnoreParamErr = TRUE` 备份过程中遇到不可读参数跳过；FALSE 中止。其它字段与基础版相同。⚠️ 本 FB 的输入 `arrList` 等接口字段 **PDF VAR 区未完整列出**，使用前请对照 PDF 正文 / drive 手册。

## 4. 错误码 / 返回值

本 FB 通过 `bError` / `ERR` + `nErrId` / `ERRID` 输出报告错误：

- `bError = FALSE` 且 `nErrId = 0`：调用成功。
- `bError = TRUE`：调用失败，错误号在 `nErrId`。

常见错误号（按 ADS Return Codes 表）：

| 错误号（十六进制） | 含义 |
|---|---|
| `0x06` | 目标端口未找到（ADSERR_DEVICE_NOTFOUND）—— 设备未启用或 DeviceId 错 |
| `0x07` | 目标机不在线（ADSERR_DEVICE_NOTREADY） |
| `0x745` | ADS 通讯超时（ADSERR_CLIENT_SYNCTIMEOUT）—— `TMOUT` 太短或现场总线响应慢 |
| 其他 | 见 Beckhoff **ADS Return Codes** 在线表，及现场总线主站特有的错误码（PDF 未列入本节） |

⚠️ PDF / InfoSys 未在本 FB 处列具体的现场总线错误号，需配合主站手册查询。

## 5. 使用注意 / 常见坑

- SERCOS 是早期 motion 总线（SERCANS SCS-P ISA / PCI / Beckhoff FC750x PCI）；现代工程多用 EtherCAT + EL72xx。本系列 FB 用于维护老线。
- SERCOS 通讯有 5 个 phase（0..4），通讯参数访问要求处于特定 phase（通常 phase 2）。（工程经验补充）
- ADS 错误号见 Beckhoff ADS Return Codes 在线表；SERCOS 自定义错误号见对应 IDN 的应答字段。（工程经验补充）
- drive 参数（S / P 参数）通过 IDN（Identification Number）寻址：S = 0..32767，P = 32768..65535。（工程经验补充）
- ⚠️ PDF VAR 区**未完整列出** `arrList`（用户自定义清单数组）；使用前请对照 PDF 正文与 drive 手册。（工程经验补充）
- 与基础版相同：需要 phase 2；CRC 写 IDN-142。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IOF_SER_DRIVE_BackupEx.xml`](../examples/P_Demo_IOF_SER_DRIVE_BackupEx.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：SERCOS drive 备份只关心 motion 关键参数（不含统计 / 诊断字段），用自定义清单减少备份文件大小。
- **价值**：更精细的备份控制；可针对工程特定参数清单。
- **替代方案对比**：
  - 基础版 `IOF_SER_DRIVE_Backup`：只能用 IDN-192 / IDN-17
  - **本 FB**：可自定义清单 + 忽略错误

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.12.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59126923.html
- **相关 FB / FC**：`IOF_SER_DRIVE_Backup`, `IOF_SER_IDN_Read`
