# FB_ASI_Processdata_digital

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `ASI master terminal` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59155723.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_ASI_Processdata_digital.xml`](../examples/P_Demo_FB_ASI_Processdata_digital.xml) |

---

## 1. 功能简述

读 / 写 AS-Interface slave 的数字过程数据（4 bit 数据槽）。支持单次 / 连续模式、读 / 写选择、屏蔽访问 (`bmaskAccess`)。可作通用 ASI 数字 IO 访问入口，比把 slave 数据直接链到 PLC 任务输入 / 输出更灵活（按需访问）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    iSlaveaddress : BYTE;
    iSlavevalue : WORD;
    bParametermode : BOOL;
    bCycleMode : BOOL;
    bCommMode : BOOL;
    bRegComm : BOOL;
    bmaskAccess : BOOL;
    bStart : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `iSlaveaddress` | `BYTE` | slave 地址。 |
| `iSlavevalue` | `WORD` | 写入 slave 的数字数据（4 bit）。 |
| `bParametermode` | `BOOL` | 0 = 读，1 = 写。 |
| `bCycleMode` | `BOOL` | 0 = 单次，1 = 连续（`bBusy` 仅在 `bStart` 撤销后落回）。 |
| `bCommMode` | `BOOL` | PDF: currently always 0（保留为未来扩展，当前固件不可改）。 |
| `bRegComm` | `BOOL` | PDF: currently always 0（同上，保留）。 |
| `bmaskAccess` | `BOOL` | 0 = 普通访问，1 = 屏蔽访问（部分扩展 slave 用）。 |
| `bStart` | `BOOL` | 上升沿触发一次访问。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bErr : BOOL;
    iErrornumber : DWORD;
    iReadValue : WORD;
    iParametergroup : WORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bErr` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `iErrornumber` | `DWORD` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |
| `iReadValue` | `WORD` | 读出的 slave 数据。 |
| `iParametergroup` | `WORD` | 当前 slave 的参数分组信息（WORD）。 |

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

`bStart` 上升沿触发一次过程数据访问命令，FB 把命令排入 `stParameterBuffer` 让后台调度器送到 ASI 主端子。`bParametermode = 0` 表示读，`= 1` 表示写；`bCycleMode = 0` 表示单次操作，`= 1` 表示连续操作。`bCommMode` 与 `bRegComm` 在当前固件中 **必须保持 0**（PDF 备注：currently always 0），用于保留未来扩展。`bmaskAccess = 1` 走屏蔽访问模式，仅在某些扩展 slave 上有意义；普通 slave 保持 0。`iSlavevalue` 是写入数据（4 bit），`iReadValue` 是读出数据，`iParametergroup` 输出当前 slave 的参数分组信息。完成后 `bBusy := FALSE`；出错 `bErr := TRUE`、`iErrornumber` 给出 ASI 命令错误码。

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
- `bCommMode` / `bRegComm` **当前固件版本必须保持 0**，写其它值未定义。（工程经验补充）
- 循环模式 `bCycleMode = 1` 会占用大量 ASI 主端子调度时间，不建议同时对多个 slave 启用循环模式。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_ASI_Processdata_digital.xml`](../examples/P_Demo_FB_ASI_Processdata_digital.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：ASI 数字 IO slave 7 上挂 4 个数字按钮，需要在 PLC 程序里按需读取；用本 FB 比把数据链到 %I* 更灵活。
- **价值**：按需读写 ASI 数字数据，节省过程映像。
- **替代方案对比**：
  - 链到 %I* / %Q*：永远刷新但占过程映像
  - **本 FB**：按需读写

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.2.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59155723.html
- **相关 FB / FC**：`FB_ASI_ReadParameter`, `FB_ASI_ParameterControl`, `FB_ReadInput_analog`
