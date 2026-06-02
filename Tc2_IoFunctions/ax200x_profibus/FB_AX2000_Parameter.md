# FB_AX2000_Parameter

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `AX200x Profibus` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59142027.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_AX2000_Parameter.TcPOU`](../examples/P_Demo_FB_AX2000_Parameter.TcPOU) |

---

## 1. 功能简述

AX2000 Profibus 伺服驱动器的参数读 / 写功能块，使用 Profibus DP-V1 PKW 机制访问驱动器内部参数（如位置环增益、加减速时间、电流限）。注意：写参数改变运行模式时，必须把 `FB_AX2000_AXACT` 的 "STOP" 输入保持 TRUE。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    iSlaveAddress : BYTE := 0;
    iPnu : WORD := 16#03A2;
    nAxis : BYTE := 1;
    iLength : BYTE := 4;
    iSubIndex : BYTE;
    iParameterValue : DWORD := 2;
    iFC310xDeviceId : WORD := 1;
    bStartRead : BOOL;
    bStartWrite : BOOL;
    tTimeOut : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `iSlaveAddress` | `BYTE` | `0` | AX2000 在 Profibus 上的站地址。 |
| `iPnu` | `WORD` | `16#03A2` | PROFIDRIVE PKW 参数号（PNU）；可用值参见 AX2000 手册的 PKW 参数列表。 |
| `nAxis` | `BYTE` | `1` | 轴号（多轴扩展用）。 |
| `iLength` | `BYTE` | `4` | 参数长度（2 或 4 字节）。 |
| `iSubIndex` | `BYTE` | - | PKW 子索引（数组型参数访问元素用）。 |
| `iParameterValue` | `DWORD` | `2` | 要写入或读出的参数值。 |
| `iFC310xDeviceId` | `WORD` | `1` | Profibus 主站卡（FC310x）的 Device Id。 |
| `bStartRead` | `BOOL` | - | 上升沿启动读 PKW。 |
| `bStartWrite` | `BOOL` | - | 上升沿启动写 PKW；改运行模式时需 `FB_AX2000_AXACT.STOP = TRUE`。 |
| `tTimeOut` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    iErrorId : DWORD;
    iReadValue : DINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `iErrorId` | `DWORD` | AX2000 驱动器 PKW 错误码（不是 ADS 错误号；具体见 AX2000 手册）。 |
| `iReadValue` | `DINT` | 读 PKW 返回的参数值。 |

### VAR_IN_OUT

无。

## 3. 行为说明

`bStartRead` 上升沿触发一次读 PKW；`bStartWrite` 上升沿触发一次写 PKW。不要同时拉高两者，会冲突。`iPnu` 选择参数号（如 PNU 0x03A2 = velocity loop integral time）；`nAxis` 是双轴 / 三轴扩展时的轴号；`iLength` 区分 2 字节或 4 字节参数（按 PNU 列表决定）。`bBusy = TRUE` 直到驱动器应答；完成后 `iReadValue` 含读得的参数值（仅 `bStartRead` 路径）。出错时 `iErrorId` 给出 AX2000 驱动器错误号——这是 PROFIDRIVE 的 PKW 错误码体系，不是 ADS 错误号。`tTimeOut` 是 ADS 调用超时；PKW 本身在 Profibus 上需要多个 DP cycle 完成，超时建议 ≥ 2 秒。

## 4. 错误码 / 返回值

本 FB 无具体错误码表；状态由输出参数自行反映。具体错误语义需配合主站 / 现场总线设备手册查询。

## 5. 使用注意 / 常见坑

- AX2000 是 1990s-2000s 的 Kollmorgen 老型号伺服；现代工程基本用 AX5000 (EtherCAT) + Tc2/Tc3 NCI 替代。本系列 FB 仅用于维护老线。
- **`stPZDIN` / `stPZDOUT` 必须链到 System Manager 中 AX2000 在 Profibus 上的 PZD（过程数据）映射区**，否则数据交换不通。（工程经验补充）
- AX2000 通讯通过 Profibus FC310x / EL6731 主站；调用任何 AX2000 FB 前先确保 Profibus 主站本身已正常。（工程经验补充）
- 错误号 `iErrorId` 是 AX2000 驱动器返回的"驱动器错误号"，与 ADS 错误号无关。具体含义见 AX2000 / S300 手册的 Fault Code 表。（工程经验补充）
- 改运行模式（如位置 → 速度）时必须先让 `FB_AX2000_AXACT.bStop = TRUE` 把驱动器停下，否则写参数被驱动器拒绝。
- PKW 是慢速通道（DP 每个周期只能传一个参数读/写），不要循环周期读参数；上电时一次性配置即可。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_AX2000_Parameter.TcPOU`](../examples/P_Demo_FB_AX2000_Parameter.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：AX2000 维护：上电时把当前位置环增益从默认值改为工程定制值（例如 PNU 0x03A2 = 30）。
- **价值**：让 PLC 程序在上电时把驱动器参数写到一致状态，替换工人手拨 Kollmorgen 调试软件。
- **替代方案对比**：
  - Kollmorgen 调试软件 Drive.exe：能写但要插串口 / 工程模式
  - 改用现代 EL72xx + Tc2/Tc3 NCI：投资大但更可靠
  - **本 FB**：维护老线最现实做法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.3.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59142027.html
- **相关 FB / FC**：`FB_AX2000_AXACT`, `FB_AX2000_Reference`, `FB_AX200X_Profibus`
