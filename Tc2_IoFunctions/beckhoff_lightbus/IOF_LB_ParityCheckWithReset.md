# IOF_LB_ParityCheckWithReset

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Beckhoff Lightbus` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59110283.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_IOF_LB_ParityCheckWithReset.xml`](../examples/P_Demo_IOF_LB_ParityCheckWithReset.xml) |

---

## 1. 功能简述

与 `IOF_LB_ParityCheck` 相同，**但读后立即把每个模块的奇偶错计数器清零**。用于做"过去 T 时间内的奇偶错增量"采样。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID : T_AmsNetId;
    DEVICEID : UDINT;
    LEN : UDINT;
    DESTADDR : PVOID;
    START : BOOL;
    TMOUT : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 目标 TwinCAT 计算机的 AMS Net ID；本机用空串 `''`，远端填对端 AMS Net ID（例如 `'5.84.32.27.1.1'`）。 |
| `DEVICEID` | `UDINT` | - | TwinCAT 配置时由系统自动分配的 I/O 设备 ID（不可由用户配置）。可在 System Manager 中查看，或通过 `IOF_GetDeviceIDByName` 由设备名查得。 |
| `LEN` | `UDINT` | - | 要读的模块计数（字节数）。 |
| `DESTADDR` | `PVOID` | - | 数据缓冲区地址，用 `ADR()` 运算符取得。 |
| `START` | `BOOL` | - | 上升沿触发一次执行；调用期间保持高电平，完成后由用户决定何时回 FALSE 准备下次触发。 |
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

调用前用户准备 `ARRAY[1..N] OF BYTE` 缓冲区。`START` 上升沿触发：`BUSY := TRUE`，FB 经 ADS 把 N 个计数器读到缓冲区**并复位主站侧的计数到 0**。完成后 `buffer[k]` = 模块 k 从上次复位到现在的奇偶错次数。常见用法：每分钟调本 FB 采样一次 → 用差量做 1 分钟内的错误率统计 → SCADA 显示。

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
- 调用之后主站侧计数器复位 0；想拿"自上次复位以来的累积"用本 FB；想看"长期累积"用不带 Reset 的版本。
- 两个版本不要混用 / 并发调用，会让两边的复位时机错乱。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IOF_LB_ParityCheckWithReset.xml`](../examples/P_Demo_IOF_LB_ParityCheckWithReset.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：Lightbus 实时错误率监控：每分钟调本 FB 一次 → 把结果直接当成"该分钟错误数"送 SCADA 画趋势图。
- **价值**：做实时错误率监控，比累积型计数更直观。
- **替代方案对比**：
  - 不带 Reset + 自己减上次值：可行但容易出软件 bug（计数到 255 饱和时差量算错）
  - **本 FB**：硬件帮忙做差量

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.4.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59110283.html
- **相关 FB / FC**：`IOF_LB_ParityCheck`, `IOF_LB_BreakLocationTest`
