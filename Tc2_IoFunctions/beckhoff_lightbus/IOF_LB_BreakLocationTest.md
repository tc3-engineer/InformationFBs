# IOF_LB_BreakLocationTest

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Beckhoff Lightbus` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59107211.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_IOF_LB_BreakLocationTest.TcPOU`](../examples/P_Demo_IOF_LB_BreakLocationTest.TcPOU) |

---

## 1. 功能简述

Beckhoff Lightbus（光纤总线）断纤定位测试。在光纤环里 walking 测试，若没有断纤则 `BOXNO` 返回当前环内模块总数；若有断纤则 `BREAK := TRUE` 且 `BOXNO` 返回断点前最后一个能通讯到的模块号。若 `BOXNO = 0xFF` 表示断点紧靠接收端，无法定位具体模块。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID : T_AmsNetId;
    DEVICEID : UDINT;
    START : BOOL;
    TMOUT : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 目标 TwinCAT 计算机的 AMS Net ID；本机用空串 `''`，远端填对端 AMS Net ID（例如 `'5.84.32.27.1.1'`）。 |
| `DEVICEID` | `UDINT` | - | TwinCAT 配置时由系统自动分配的 I/O 设备 ID（不可由用户配置）。可在 System Manager 中查看，或通过 `IOF_GetDeviceIDByName` 由设备名查得。 |
| `START` | `BOOL` | - | 上升沿触发一次执行；调用期间保持高电平，完成后由用户决定何时回 FALSE 准备下次触发。 |
| `TMOUT` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY : BOOL;
    ERR : BOOL;
    ERRID : UDINT;
    BREAK : BOOL;
    BOXNO : WORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `ERR` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `ERRID` | `UDINT` | 错误号；ADS 类错误参考 Beckhoff **ADS Return Codes** 在线表；FB 自定义错误号在 §4 列出（若 PDF 列出）。0 = 无错。 |
| `BREAK` | `BOOL` | TRUE = 检测到断纤；FALSE = 光纤环正常。 |
| `BOXNO` | `WORD` | BREAK=FALSE 时是模块总数；BREAK=TRUE 时是断点前最后能通讯的模块号；0xFF 表示接收端直接断纤。 |

### VAR_IN_OUT

无。

## 3. 行为说明

`START` 上升沿触发一次测试：`BUSY := TRUE`，FB 经 ADS 把 walking 测试命令发到 Lightbus 主站。主站在光纤环里按顺序探测每个模块的应答，直到无应答为止。完成后 `BUSY := FALSE`，结果：`BREAK = FALSE` 时 `BOXNO` = 环内模块总数（用于核对配置）；`BREAK = TRUE` 时 `BOXNO` = 断点前最后一个能通讯的模块号；若 `BOXNO = 0xFF` 表示接收端正面就断了。Lightbus 模块号是从发射器开始数 1, 2, ..., N。

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

- Beckhoff Lightbus 是早期光纤总线，**TwinCAT 3 已不再支持** Lightbus 主站硬件（C1220 ISA / FC200x PCI）。PDF 明确说 "not supported by TwinCAT 3 at present"。
- 本系列 FB 仅供老工程升级到 TwinCAT 3 后做"代码兼容性参考"，**实际运行需要 TwinCAT 2 或更早**。
- ADS 错误号见 Beckhoff **ADS Return Codes** 在线表；具体光纤错误码 PDF 未列入本节。（工程经验补充）
- 断纤定位是诊断功能，不要循环周期调用——会占用 Lightbus 主站带宽。（工程经验补充）
- 找到断点后 walking 测试会终止，需要修复光纤后再次调用本 FB 确认恢复。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IOF_LB_BreakLocationTest.TcPOU`](../examples/P_Demo_IOF_LB_BreakLocationTest.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：Lightbus 老线突然报通讯故障：调本 FB 定位断点 → 现场顺着光纤数到第 N 个模块（BOXNO 值）附近检查。
- **价值**：避免逐段拔光纤排查；一次测试定位到具体模块附近。
- **替代方案对比**：
  - 人工逐段排查：耗时
  - 用专门光纤测试仪：要带工具到现场
  - **本 FB**：PLC 程序触发即可

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.4.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59107211.html
- **相关 FB / FC**：`IOF_LB_ParityCheck`, `IOF_LB_ParityCheckWithReset`, `IOF_DeviceReset`
