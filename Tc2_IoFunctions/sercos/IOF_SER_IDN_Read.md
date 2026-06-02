# IOF_SER_IDN_Read

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `SERCOS` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59122315.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_IOF_SER_IDN_Read.TcPOU`](../examples/P_Demo_IOF_SER_IDN_Read.TcPOU) |

---

## 1. 功能简述

读取 SERCOS drive 的 S 或 P 参数值（按 IDN 寻址）。数据类型 / 大小自动从参数的 attribute 字段判定。可读取 value / name / attribute / unit / minimum / maximum 等不同字段。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId : T_AmsNetId;
    nIDN : UINT;
    bExecute : BOOL;
    nPort : UINT;
    nMode : DINT;
    nAttrib : DWORD;
    cbLen : UDINT;
    dwDestAddr : PVOID;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | - | 本机用空串。 |
| `nIDN` | `UINT` | - | IDN 编号；S 参数 0..32767，P 参数 32768..65535。 |
| `bExecute` | `BOOL` | - | 上升沿触发一次 IDN 读。 |
| `nPort` | `UINT` | - | drive 端口号（System Manager 自动分配，区分多个 drive）。 |
| `nMode` | `DINT` | - | 读取模式：0=Value 2=Name 3=Attribute 4=Unit 5=Min 6=Max。 |
| `nAttrib` | `DWORD` | - | 已知属性（缓存值）；为 0 时 FB 自动先读属性。 |
| `cbLen` | `UDINT` | - | dwDestAddr 缓冲最大字节数。 |
| `dwDestAddr` | `PVOID` | - | 目标数据缓冲地址（用 `ADR()`）。 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    cbRead : UDINT;
    nAttribRd : DWORD;
    sAttrib : ST_SercosParamAttrib;
    bBusy : BOOL;
    bError : BOOL;
    nErrId : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `cbRead` | `UDINT` | 实际读到字节数。 |
| `nAttribRd` | `DWORD` | 本次读到的属性（DWORD，可缓存）。 |
| `sAttrib` | `ST_SercosParamAttrib` | 属性按字段分解结构 (`ST_SercosParamAttrib`)。 |
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bError` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `nErrId` | `UDINT` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |

### VAR_IN_OUT

无。

## 3. 行为说明

`bExecute` 上升沿触发一次 IDN 读：`bBusy := TRUE`，FB 经 ADS 让 SERCOS 主站对指定 drive 的指定 IDN 发读命令。`nIDN` 是 IDN 编号：0..32767 = S 参数，32768..65535 = P 参数。`nMode` 决定读取的字段：0 = Value（值），2 = Name（名字），3 = Attribute（属性），4 = Unit（单位，部分参数无），5 = Min，6 = Max。`nAttrib` 若非 0 是已知属性（避免每次自动读属性，加速）；为 0 时 FB 自动先读属性再读 value。`cbLen` 是 `dwDestAddr` 缓冲的最大长度；`cbRead` 输出实际读到的字节数；`nAttribRd` 输出本次读到的属性，可缓存供下次调用复用；`sAttrib` 是属性结构体（按字段分解 nAttribRd）。触发语义为上升沿一次性。

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
- **参数访问需要在 phase 2**（通讯参数模式）；在 phase 4 运行中部分参数读不到。（工程经验补充）
- 多次读同一 drive 的参数时**复用 `nAttribRd` 值传给下次 `nAttrib`**，可避免 FB 每次先读属性，提速明显。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IOF_SER_IDN_Read.TcPOU`](../examples/P_Demo_IOF_SER_IDN_Read.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：SERCOS drive 调试：读 IDN-100（位置环增益）+ IDN-101（速度环增益），与工程图纸比对。
- **价值**：封装 IDN 访问；业务侧只关心 IDN 号与缓冲。
- **替代方案对比**：
  - 用 SERCANS 工具：要带工具
  - **本 FB**：纯 PLC

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.12.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59122315.html
- **相关 FB / FC**：`IOF_SER_IDN_Write`, `IOF_SER_GetPhase`, `IOF_SER_SetPhase`
