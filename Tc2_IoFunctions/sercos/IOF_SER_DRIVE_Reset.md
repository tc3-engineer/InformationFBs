# IOF_SER_DRIVE_Reset

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `SERCOS` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59128459.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_IOF_SER_DRIVE_Reset.xml`](../examples/P_Demo_IOF_SER_DRIVE_Reset.xml) |

---

## 1. 功能简述

复位指定 SERCOS drive：清掉 drive 自身的错误状态。与 `IOF_SER_ResetErr` 的区别：本 FB 针对**单个 drive**（按端口号 `nPort`）；ResetErr 是清整个 SERCOS 主站 + 所有 drive。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId : T_AmsNetId;
    nPort : UINT;
    bReset : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | - | 本机用空串。 |
| `nPort` | `UINT` | - | drive 端口号。 |
| `bReset` | `BOOL` | - | 上升沿触发一次复位。 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

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
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bError` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `nErrId` | `UDINT` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |

### VAR_IN_OUT

无。

## 3. 行为说明

`bReset` 上升沿触发一次单 drive 复位：`bBusy := TRUE`，FB 经 ADS 让主站对 `nPort` 指定的 drive 发清错命令。复位**只清错误状态字，不修复硬件故障**——若 drive 硬件故障仍存在（如过载 / 编码器丢失），下次周期还会重新报错。触发语义为上升沿一次性，重复触发需要先把 `bReset` 拉低再拉高。`tTimeout` 控制 ADS 调用超时，单 drive 清错通常 50-200 ms 完成。与 `IOF_SER_ResetErr`（清整个 SERCOS 主站 + 所有 drive）相比，本 FB **只清单个 drive**，不影响其它 drive 的工作；常用于"只清出错那一个轴"的场景。

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
- 与 `IOF_SER_ResetErr` 不同的是本 FB 只影响单个 drive，**不影响其它 drive 的运行**。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IOF_SER_DRIVE_Reset.xml`](../examples/P_Demo_IOF_SER_DRIVE_Reset.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：生产线某轴报错：单独清这一个 drive 而不打断其它 drive 的运行。
- **价值**：更精细的清错粒度。
- **替代方案对比**：
  - `IOF_SER_ResetErr`：影响所有 drive
  - **本 FB**：单 drive

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.12.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59128459.html
- **相关 FB / FC**：`IOF_SER_ResetErr`, `IOF_SER_GetPhase`
