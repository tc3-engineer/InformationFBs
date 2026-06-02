# FB_ASI_SlaveDiag

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `ASI master terminal` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59151115.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_ASI_SlaveDiag.TcPOU`](../examples/P_Demo_FB_ASI_SlaveDiag.TcPOU) |

---

## 1. 功能简述

AS-Interface slave 周期诊断。读取指定 slave 的错误 / 超时计数器（物理错、超时、应答、退出数据交换、数据交换失败），或读取整个 ASI 总线的"已识别 slave 列表 (LES)" / "已激活 slave 列表 (LAS)"。通过 `bCycleMode` 控制单次读或连续读。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    iSlaveaddress : BYTE;
    iCounter : INT;
    bReadLES : BOOL;
    bReadLAS : BOOL;
    bCyleMode : BOOL;
    bStart : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `iSlaveaddress` | `BYTE` | 目标 slave 地址 (1..31 标准 / A/B 扩展 0..62)。 |
| `iCounter` | `INT` | 诊断计数器选择：1 = PhysicalFaultCounter（物理层错误），2 = TimeoutCounter（超时），3 = ResponseCounter（应答），4 = Leave-DataExchCounter（退出数据交换），5 = DataExch-FailedCounter（数据交换失败）。 |
| `bReadLES` | `BOOL` | TRUE = 读 LES (List of Existing Slaves)，返回总线上识别到的 slave 位图。 |
| `bReadLAS` | `BOOL` | TRUE = 读 LAS (List of Activated Slaves)，返回当前激活通讯的 slave 位图。 |
| `bCyleMode` | `BOOL` | `bCycleMode`（PDF 拼写错误为 `bCyleMode`）：0 = 单次读，1 = 连续读（`bBusy` 仅在 `bStart` 回 FALSE 后才落回）。 |
| `bStart` | `BOOL` | 上升沿触发一次执行；调用期间保持高电平，完成后由用户决定何时回 FALSE 准备下次触发。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bErr : BOOL;
    iErrornumber : DWORD;
    iCounterValue : WORD;
    iSlaveList : DWORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bErr` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `iErrornumber` | `DWORD` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |
| `iCounterValue` | `WORD` | 当前所选 slave 的计数器值（仅当 `iCounter` ≠ 0 时有效）。 |
| `iSlaveList` | `DWORD` | 所有 slave 的 LES / LAS 位图（DWORD，每个 bit 对应一个 slave 地址）。 |

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

`bStart` 上升沿触发一次诊断命令；命令类型由其它输入位决定：`iCounter` ∈ {1..5} 表示读哪一种计数器（1: PhysicalFault, 2: Timeout, 3: Response, 4: LeaveDataExch, 5: DataExchFailed）；`bReadLES` = TRUE 时读 LES（List of Existing Slaves，已识别 slave 位图）；`bReadLAS` = TRUE 时读 LAS（List of Activated Slaves，已激活 slave 位图）。`bCycleMode = TRUE` 时持续读，`bBusy` 仅在 `bStart` 撤销后才落回；常用于看板循环刷新计数器；`bCycleMode = FALSE` 时单次读，命令完成 `bBusy` 落回。计数器值通过 `iCounterValue` 输出；位图通过 `iSlaveList`（DWORD = 32 bit 位图）输出。**`bCounterReset` 在 PDF 描述列出现但不在 VAR_INPUT 中**——是 PDF 列名混淆，不要使用，请用 `FB_ASI_WriteParameter` 实现复位。

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
- **`bCyleMode` 是 PDF 拼写错误**（应为 `bCycleMode`）；调用时用 PDF 写的名字 `bCyleMode` 才能通过编译。（工程经验补充）
- PDF 描述里出现 `bCounterReset` 字段但 VAR_INPUT 中**没有**此字段，是 PDF 文档错误；本 FB 不支持复位计数器。（工程经验补充）
- `iSlaveList` 是 DWORD 位图，bit N 对应 slave N（注意 ASI 标准地址 1..31，bit 0 通常保留 / 不使用）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_ASI_SlaveDiag.TcPOU`](../examples/P_Demo_FB_ASI_SlaveDiag.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：ASI 总线长期运行：周期读 slave 12 的 PhysicalFaultCounter 监控物理层抖动，超过阈值报警；同时读 LAS 看是否所有期望 slave 还在数据交换。
- **价值**：把 ASI 主端子的诊断字段做成可程序化访问，便于 SCADA 趋势曲线与报警。
- **替代方案对比**：
  - 直接读 ASI 主端子寄存器：底层繁琐
  - 用专门的 ASI 诊断工具：在线但无法接 PLC
  - **本 FB**：标准方式

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.2.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59151115.html
- **相关 FB / FC**：`FB_ASI_ParameterControl`, `FB_ASI_Addressing`, `FB_ASI_ReadParameter`
