# FB_GetRtPerformanceData

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/9682569227.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_GetRtPerformanceData.xml`](../examples/P_Demo_FB_GetRtPerformanceData.xml) |

---

## 1. 功能简述

FB_GetRtPerformanceData 读取目标 TwinCAT 系统的实时性能数据：任务周期占比、超时次数、CPU 占用等。比 TC_CpuUsage 更细。

用于：深度性能分析、容量规划。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute : BOOL;
    bReset : BOOL;
    tTimeout : TIME;
    sNetId : T_AmsNetId;
    bBusy : BOOL;
    bError : BOOL;
    nErrorId : UDINT;
    nUsedCpuCount : UDINT;
    stRtPerformanceData : ARRAY [1..nMaxCpuCount] OF ST_RtPerformanceData;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bExecute` | `BOOL` | 上升沿触发一次执行；调用期间保持高电平，完成后自动复位无需手动清零。 |
| `bReset` | `BOOL` | 输入布尔标志：`bReset`。具体语义见 §3 行为说明。 |
| `tTimeout` | `TIME` | ADS 调用超时时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。 |
| `sNetId` | `T_AmsNetId` | 目标系统 AMS Net ID。本机用空串 `''`；远端填对端 AMS Net ID。 |
| `bBusy` | `BOOL` | TRUE 表示请求正在处理；同时 `bExecute` 仍为高电平时不响应新请求。 |
| `bError` | `BOOL` | TRUE 表示本次请求失败，错误号由 `nErrId` / `nErrorId` 给出。 |
| `nErrorId` | `UDINT` | ADS 错误码或本 FB 自定义错误号。0 = 无错。具体码表见 InfoSys / ADS Return Codes。 |
| `nUsedCpuCount` | `UDINT` | 无符号整数输入：`nUsedCpuCount`。 |
| `stRtPerformanceData` | `ARRAY [1..nMaxCpuCount] OF ST_RtPerformanceData` | 参数 `stRtPerformanceData`（类型 `ARRAY [1..nMaxCpuCount] OF ST_RtPerformanceData`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用**：`bExecute` 上升沿读一次。返回 `ST_RtPerformanceData` 结构。


**调用一般约束**：本 FB 的所有输入 / 输出引脚语义已在 §2 接口定义表的中文说明列详细列出；调用方应按上述时序与状态机分支组织程序，并参照 §5 使用注意 / 常见坑回避典型陷阱。若 PDF 与 InfoSys 中未对某种异常工况作出明确说明，本仓库会以 ⚠️ 标记，提示读者用实测或在 Beckhoff Forum 上确认，而非凭推测下结论。

## 4. 错误码 / 返回值

本 FB 无显式错误输出。状态可以通过 `bBusy` / `bValid` / `bDone` 等过程信号间接判断。

## 5. 使用注意 / 常见坑

- `bExecute` 必须是上升沿触发；持续高电平不会重发请求，要释放再拉起。
- `tTimeout` 默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。跨网段调用建议放大；过长会卡周期任务。（工程经验补充）
- PDF 没有枚举具体错误号——`nErrId / nErrorId` 引用通用 **ADS Return Codes** 表（参考 InfoSys 在线表）。
- `bBusy` 高电平期间业务侧不要再次拉起 `bExecute`，否则被忽略。（工程经验补充）
- 跨网段调用应放在非实时任务里执行，避免 PLC 周期任务被 ADS 抖动撑爆。（工程经验补充）
- **字段含义需查 PDF / InfoSys 文档**，细节多。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_GetRtPerformanceData.xml`](../examples/P_Demo_FB_GetRtPerformanceData.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：深度性能分析。
- **价值**：比 TC_CpuUsage 字段丰富。
- **替代方案对比**：
  - TC_CpuUsage / TC_SysLatency：简单字段。
  - **本 FB**：综合结构。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.63
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/9682569227.html
