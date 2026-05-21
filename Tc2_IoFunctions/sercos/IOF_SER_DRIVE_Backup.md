# IOF_SER_DRIVE_Backup

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `SERCOS` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59125387.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_IOF_SER_DRIVE_Backup.xml`](../examples/P_Demo_IOF_SER_DRIVE_Backup.xml) |

---

## 1. 功能简述

把 SERCOS drive 的全部 S / P 参数备份到 PLC 文件，或反向恢复。默认按 IDN-192（标准备份列表）；可关闭走 IDN-17（所有参数列表）但部分参数只读、restore 会失败。可生成 CRC16-CCITT 校验保存到 IDN-142。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bCheck : BOOL;
    bBackup : BOOL;
    bRestore : BOOL;
    bCRCEnable : BOOL := TRUE;
    bStdBackupList : BOOL := TRUE;
    sNetId : T_AmsNetId;
    nPort : UINT;
    sComment : T_MaxString;
    ePath : E_OpenPath := PATH_BOOTPATH;
    sPathName : T_MaxString := 'DRIVEPAR.BIN';
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bCheck` | `BOOL` | - | 上升沿启动 CRC 校验。 |
| `bBackup` | `BOOL` | - | 上升沿启动备份 drive → 文件。 |
| `bRestore` | `BOOL` | - | 上升沿启动恢复 文件 → drive。 |
| `bCRCEnable` | `BOOL` | `TRUE` | 启用 CRC16-CCITT 校验（保存到 IDN-142）。 |
| `bStdBackupList` | `BOOL` | `TRUE` | TRUE = 用 IDN-192 标准清单；FALSE = 用 IDN-17 全参数清单（restore 不可用）。 |
| `sNetId` | `T_AmsNetId` | - | 本机用空串。 |
| `nPort` | `UINT` | - | drive 端口号。 |
| `sComment` | `T_MaxString` | - | 备份文件头部注释字符串。 |
| `ePath` | `E_OpenPath` | `PATH_BOOTPATH` | 文件路径常量（默认 `PATH_BOOTPATH`）。 |
| `sPathName` | `T_MaxString` | `'DRIVEPAR.BIN'` | 文件名（默认 `DRIVEPAR.BIN`）。 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    bCheckOK : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bError` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `nErrId` | `UDINT` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |
| `bCheckOK` | `BOOL` | 布尔标志 `bCheckOK`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

本 FB 是 3 合 1：`bBackup` 上升沿触发备份（drive → 文件）；`bRestore` 上升沿触发恢复（文件 → drive）；`bCheck` 上升沿触发 CRC 校验。`bCRCEnable = TRUE` 启用 CRC16-CCITT + 16 bit 校验和，并保存到 IDN-142（若 drive 有此 IDN）。`bStdBackupList = TRUE` 用 IDN-192（标准备份清单，可 restore）；`FALSE` 用 IDN-17（全参数清单，restore 会失败）。文件路径由 `ePath` + `sPathName` 决定（默认 `PATH_BOOTPATH` + `DRIVEPAR.BIN`）。`sComment` 写到备份文件头部做注释。`bCheckOK` 输出 CRC 校验结果（仅 bCheck 路径）。需要 SERCOS phase 2（参数访问模式）。

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
- **需要 phase 2**：所有操作都要先把环切到 phase 2。（工程经验补充）
- `bStdBackupList = FALSE` (用 IDN-17) 时 restore **会失败**——IDN-17 含只读参数。仅用于审计，不用于恢复。（工程经验补充）
- 备份文件较大（典型几十到几百 KB），网络盘 / 硬盘空间要留够。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IOF_SER_DRIVE_Backup.xml`](../examples/P_Demo_IOF_SER_DRIVE_Backup.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：SERCOS drive 维护：每年备份所有 drive 的参数文件存档；故障更换 drive 后 restore 让备件直接可用。
- **价值**：让 drive 参数版本化，更换硬件不丢工艺参数。
- **替代方案对比**：
  - 用 SERCANS 工具备份：要带工具到现场
  - 不备份：故障换硬件后要重新调试
  - **本 FB**：PLC 程序触发，可定期 / HMI 一键

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.12.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59125387.html
- **相关 FB / FC**：`IOF_SER_DRIVE_BackupEx`, `IOF_SER_IDN_Read`, `IOF_SER_IDN_Write`
