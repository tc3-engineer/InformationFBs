# FB_ReadInput_analog

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `ASI master terminal` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59158795.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_ReadInput_analog.TcPOU`](../examples/P_Demo_FB_ReadInput_analog.TcPOU) |

---

## 1. 功能简述

读取 AS-Interface 模拟量 slave 的某通道值。常用于 ASI 模拟传感器（如温度 / 压力变送器）的现场总线接入。通过 `bValid` 表示读到的值是否有效（slave 是否在线、是否已采样），`bOverflow` 表示是否超量程。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    iSlaveaddress : BYTE;
    iChannel : BYTE;
    bCycleMode : BOOL;
    bStart : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `iSlaveaddress` | `BYTE` | 目标 ASI 模拟量 slave 地址。 |
| `iChannel` | `BYTE` | 通道号（多通道 slave 用 0..3 等）。 |
| `bCycleMode` | `BOOL` | 0 = 单次，1 = 连续读。 |
| `bStart` | `BOOL` | 上升沿触发。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bErr : BOOL;
    iErrornumber : DWORD;
    bValid : BOOL;
    bOverflow : BOOL;
    iReadValue : WORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bErr` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `iErrornumber` | `DWORD` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |
| `bValid` | `BOOL` | TRUE = 读到的 `iReadValue` 有效（slave 在线 + 已采样）；FALSE = 数据未就绪 / slave 离线。 |
| `bOverflow` | `BOOL` | TRUE = slave 报告 over-range（超量程）。 |
| `iReadValue` | `WORD` | 模拟值（16 bit；具体单位 / 量程由 slave 手册决定）。 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stParameterBuffer : ST_ParameterBuffer;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stParameterBuffer` | `ST_ParameterBuffer` | 参数 `stParameterBuffer`（类型 `ST_ParameterBuffer`）。 |

## 3. 行为说明

`bStart` 上升沿触发一次读取命令：FB 把"读模拟通道"命令排入 `stParameterBuffer`，`FB_ASI_ParameterControl` 在后台调度到 ASI 主端子，按 ASI 模拟 profile 经过几个 ASI 周期完成采样并回报。完成后 `iReadValue` 含 16 bit 模拟值（具体单位 / 量程由 slave 手册决定）。`bValid = TRUE` 表示该 slave 在线且通道有有效采样，业务侧应先判 `bValid` 再用 `iReadValue`，否则可能读到旧值或未初始化值。`bOverflow = TRUE` 表示 slave 报告的 over-range 超量程标志。`bCycleMode = 1` 模式下循环读，常用于把传感器数据周期性更新到 HMI。出错时 `bErr := TRUE`、`iErrornumber` 给出 ASI 命令错误码。

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

- **必须循环调用 `FB_ASI_ParameterControl`**，它是所有 ASI FB 的后台通讯调度器。不调它，其它所有 ASI FB 都不会动。
- `stParameterBuffer : ST_ParameterBuffer` 是全局共享缓冲：所有 ASI FB 实例 + `FB_ASI_ParameterControl` 必须传同一个实例，否则后台调度无法工作。（工程经验补充）
- `stParameter_IN` / `stParameter_OUT` 必须 **链到 System Manager 中 ASI 主端子（如 KL6201 / EL6201）的过程数据**——通过 AT %I* / AT %Q* 映射；不链则 ASI 通讯通道根本没建立。（工程经验补充）
- `bBusy = TRUE` 只表示 *命令被接受*，**不是命令被执行**。具体执行是否完成需要看 `bErr` + `iErrornumber` 在 `bBusy` 落回后的状态。（工程经验补充）
- ASI 命令专用错误码（`bErrornumber` / `iErrornumber`）见 ASI 主端子文档（KL6201/EL6201 手册）——PDF 未列入本节，调用方需要查 ASI master 错误码表。（工程经验补充）
- **`bValid` 是真伪标志**，业务侧必须先判 `bValid` 再用 `iReadValue`，否则读到旧值。（工程经验补充）
- ASI 模拟传输使用专门的 ASI Analog Profile，slave 必须支持；普通数字 slave 不能用本 FB 读。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_ReadInput_analog.TcPOU`](../examples/P_Demo_FB_ReadInput_analog.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：ASI 总线下挂温度变送器 slave 14（通道 0 是温度），周期读取送到 HMI 显示。
- **价值**：ASI 模拟量访问标准方式；自带 `bValid` / `bOverflow` 让数据可信度可判。
- **替代方案对比**：
  - 直接读 ASI 主端子原始字：底层繁琐
  - **本 FB**：标准入口

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.2.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59158795.html
- **相关 FB / FC**：`FB_WriteOutput_analog`, `FB_ASI_ParameterControl`, `FB_ASI_Processdata_digital`
