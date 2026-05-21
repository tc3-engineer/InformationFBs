# IOF_SER_ResetErr

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `SERCOS` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59119243.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_IOF_SER_ResetErr.xml`](../examples/P_Demo_IOF_SER_ResetErr.xml) |

---

## 1. 功能简述

复位 SERCOS 主站的所有错误：清掉各 drive 的错误、诊断通道的诊断状态、主站系统错误。常用于报警后的"全清"操作。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID : T_AmsNetId;
    DEVICEID : UDINT;
    RESET : BOOL;
    TMOUT : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 本机用空串。 |
| `DEVICEID` | `UDINT` | - | SERCOS 主站 Device Id。 |
| `RESET` | `BOOL` | - | 上升沿触发一次"清所有错"。 |
| `TMOUT` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY : BOOL;
    ERR : BOOL;
    ERRID : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `ERR` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `ERRID` | `UDINT` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |

### VAR_IN_OUT

无。

## 3. 行为说明

`RESET` 上升沿触发一次复位：`BUSY := TRUE`，FB 经 ADS 让 SERCOS 主站对所有 drive 发清错命令、清主站系统错。完成后 `BUSY := FALSE`，若复位本身遇错 `ERR := TRUE`。复位执行时间约 100-500 ms（取决于 drive 数量）。复位**不会复位 drive 自身的硬件故障**（例如过载 / 编码器丢失）——只是清掉错误状态字让 SERCOS 可以重新通讯。若 drive 的硬件故障仍存在，复位后下一周期错误会再次出现。

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
- **只清错误状态字，不修复硬件故障**——若硬件还有问题，复位后立刻又会报错。（工程经验补充）
- 循环周期复位会**掩盖硬件故障**，应人工触发 + 计数 / 报警。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IOF_SER_ResetErr.xml`](../examples/P_Demo_IOF_SER_ResetErr.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：SERCOS 老线报警后操作员按 HMI"清错"按钮：触发本 FB 让总线重新可用。
- **价值**：把 SERCOS 全清做成 HMI 一键操作。
- **替代方案对比**：
  - 重启 PLC：代价大
  - 用 SERCANS 工具：要带工具
  - **本 FB**：HMI 按钮

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.12.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59119243.html
- **相关 FB / FC**：`IOF_SER_DRIVE_Reset`, `IOF_SER_GetPhase`
