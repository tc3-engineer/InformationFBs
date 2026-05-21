# IOF_SER_SaveFlash

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `SERCOS` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59117707.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_IOF_SER_SaveFlash.xml`](../examples/P_Demo_IOF_SER_SaveFlash.xml) |

---

## 1. 功能简述

把 DPRAM 内的 SERCOS 系统参数检查无误后，激活并保存到主站 EEPROM。让工程化的 SERCOS 配置永久生效。PDF NOTICE：EEPROM 寿命 10 万次；不应由 PLC 程序自动调用，要由用户手动触发。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID : T_AmsNetId;
    DEVICEID : UDINT;
    SAVE : BOOL;
    TMOUT : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 本机用空串。 |
| `DEVICEID` | `UDINT` | - | SERCOS 主站 Device Id。 |
| `SAVE` | `BOOL` | - | 上升沿触发一次"检查 + 保存 + 激活"。**只在工程师手动触发时调用**。 |
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

`SAVE` 上升沿触发：`BUSY := TRUE`，FB 经 ADS 让 SERCOS 主站检查 DPRAM 中的系统参数 → 无错则激活 + 写 EEPROM。执行时长 100 ms 到几秒，取决于参数数量。完成后 `BUSY := FALSE`，`ERR := FALSE` 表示参数已激活并存入 EEPROM。若 DPRAM 中参数有冲突 / 越界，`ERR := TRUE`、`ERRID` 给错误号；EEPROM 不写。**该操作不应自动触发**——由工程师手动决定（例如 HMI 上"保存配置"按钮），避免循环 / 误调写坏 EEPROM。触发语义为上升沿一次性，重复触发要先把 `SAVE` 拉低再拉高。

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
- **EEPROM 最多 10 万次写入**：不要循环 / 周期调用，只在工程师"保存配置"时触发。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IOF_SER_SaveFlash.xml`](../examples/P_Demo_IOF_SER_SaveFlash.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：SERCOS 配置调试完成后，工程师在 HMI 点击"保存配置"按钮永久写入 EEPROM。
- **价值**：让 SERCOS 配置永久生效，断电不丢。
- **替代方案对比**：
  - SERCANS 配置工具：要带工具
  - **本 FB**：HMI 按钮触发

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.12.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59117707.html
- **相关 FB / FC**：`IOF_SER_GetPhase`, `IOF_SER_SetPhase`, `IOF_SER_IDN_Write`
