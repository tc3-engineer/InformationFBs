# FB_ASI_ReadParameter

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `ASI master terminal` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59152651.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_ASI_ReadParameter.TcPOU`](../examples/P_Demo_FB_ASI_ReadParameter.TcPOU) |

---

## 1. 功能简述

读取 AS-Interface slave 的参数值（4 bit 参数槽位）。常用于读 slave 配置参数（如传感器灵敏度档位）。支持单次读或周期读 (`bCycleMode = 1`)。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    iParameternumber : WORD;
    bCycleMode : BOOL;
    bStart : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `iParameternumber` | `WORD` | ASI 参数编号（slave 内部参数索引）。具体含义因 slave 而异，参见各 slave 手册。 |
| `bCycleMode` | `BOOL` | 0 = 单次读（Acyclic），1 = 连续读（Cyclic，`bBusy` 仅在 `bStart` 回 FALSE 后落回）。 |
| `bStart` | `BOOL` | 上升沿触发一次读命令。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bErr : BOOL;
    iErrornumber : DWORD;
    iParameterReadvalue : BYTE;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bErr` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `iErrornumber` | `DWORD` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |
| `iParameterReadvalue` | `BYTE` | 读得的 ASI slave 参数值（实际只用低 4 bit）。 |

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

`bStart` 上升沿触发：FB 把"读参数"命令放入 `stParameterBuffer`，`FB_ASI_ParameterControl` 在每个 PLC 周期把缓冲里的命令取走、经 ASI 主端子的过程数据发到目标 slave。`bCycleMode = 1` (Cyclic) 时持续读，`bBusy` 仅在 `bStart` 回 FALSE 后才落回；`bCycleMode = 0` (Acyclic) 时单次读完即停，`bBusy` 自动落回。ASI 标准 slave 的参数是 4 bit，所以 `iParameterReadvalue : BYTE` 实际只用低 4 bit。出错时 `bErr := TRUE`、`iErrornumber` 给出 ASI 主端子的命令错误号；具体错误码表见 KL6201 / EL6201 手册。

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
- ASI slave 参数槽是 4 bit；返回 BYTE 但只低 4 bit 有效。（工程经验补充）
- 参数编号含义因 slave 厂家不同，请查 slave 手册。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_ASI_ReadParameter.TcPOU`](../examples/P_Demo_FB_ASI_ReadParameter.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：读 ASI 光电传感器 slave 12 的灵敏度档位（参数 0），用于 HMI 显示当前传感器配置。
- **价值**：把 ASI 参数读做成程序接口，避免反复用 ASI 配置工具。
- **替代方案对比**：
  - ASI 配置工具：手动
  - 直接读 ASI 主端子寄存器：底层繁琐
  - **本 FB**：标准

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.2.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59152651.html
- **相关 FB / FC**：`FB_ASI_WriteParameter`, `FB_ASI_ParameterControl`, `FB_ASI_SlaveDiag`
