# IOF_SER_IDN_Write

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `SERCOS` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59123851.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_IOF_SER_IDN_Write.TcPOU`](../examples/P_Demo_IOF_SER_IDN_Write.TcPOU) |

---

## 1. 功能简述

写 SERCOS drive 的 S 或 P 参数值（按 IDN 寻址）。与 `IOF_SER_IDN_Read` 对称：自动读属性 → 写入。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId : T_AmsNetId;
    nIDN : UINT;
    bExecute : BOOL;
    nPort : UINT;
    nAttrib : DWORD;
    cbLen : UDINT;
    dwSrcAddr : PVOID;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | - | 本机用空串。 |
| `nIDN` | `UINT` | - | IDN 编号。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次 IDN 写。 |
| `nPort` | `UINT` | - | drive 端口号。 |
| `nAttrib` | `DWORD` | - | 已知属性（缓存值）；0 = FB 自动读。 |
| `cbLen` | `UDINT` | - | 源数据缓冲长度。 |
| `dwSrcAddr` | `PVOID` | - | 源数据缓冲地址。 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    nAttribRd : DWORD;
    sAttrib : ST_SercosParamAttrib;
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nAttribRd` | `DWORD` | 本次读到的属性。 |
| `sAttrib` | `ST_SercosParamAttrib` | 属性字段分解。 |
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bError` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `nErrId` | `UDINT` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |

### VAR_IN_OUT

无。

## 3. 行为说明

`bExecute` 上升沿触发一次 IDN 写：`bBusy := TRUE`，FB 经 ADS 让主站对指定 drive 的指定 IDN 发写命令。`nIDN` 范围与读相同（S: 0..32767, P: 32768..65535）。`nAttrib = 0` 时 FB 自动先读属性以决定写入字节长度；非 0 时直接用已知属性写。`dwSrcAddr` 是源数据缓冲地址（用 `ADR()`），`cbLen` 是缓冲长度。`nAttribRd` / `sAttrib` 输出本次读到的属性（与 Read 同）。⚠️ PDF VAR 描述里 `dwDestAddr` 是排版错，实际接口名是 `dwSrcAddr`——写时用 `dwSrcAddr`。注意：参数写入需要在 phase 2 进行；phase 4 运行中部分参数被锁。

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
- **写参数需要 phase 2**；phase 4 运行中 drive 多数参数被锁；先用 `IOF_SER_SetPhase` 切到 phase 2。（工程经验补充）
- PDF VAR 描述列把 `dwDestAddr` 写在 VAR_INPUT 中（实际是 `dwSrcAddr`）；以接口实际命名为准。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IOF_SER_IDN_Write.TcPOU`](../examples/P_Demo_IOF_SER_IDN_Write.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：SERCOS drive 调试完成后，把工程定制的位置环增益写到 drive 内（IDN-100）。
- **价值**：参数写入纳入 PLC 程序，不用 SERCANS 工具。
- **替代方案对比**：
  - SERCANS 工具：要带
  - **本 FB**：纯 PLC

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.12.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59123851.html
- **相关 FB / FC**：`IOF_SER_IDN_Read`, `IOF_SER_SetPhase`, `IOF_SER_SaveFlash`
