# TC_SysLatency

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35036171.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_TC_SysLatency.xml`](../examples/P_Demo_TC_SysLatency.xml) |

---

## 1. 功能简述

TC_SysLatency 读取目标 TwinCAT 系统的 RT（实时）任务调度延迟（latency）——任务实际启动时刻与调度时刻的差，单位微秒。

用于：评估系统实时性，识别调度抖动是否在容许范围内。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID : T_AmsNetId;
    START : BOOL;
    TMOUT : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 参数 `NETID`（类型 `T_AmsNetId`）。⚠️ PDF 未详述含义，请按 §3 行为说明使用。 |
| `START` | `BOOL` | - | 输入布尔标志：`START`。具体语义见 §3 行为说明。 |
| `TMOUT` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 时间值：`TMOUT`。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY : BOOL;
    ERR : BOOL;
    ERRID : UDINT;
    ACTUAL : UDINT;
    MAXIMUM : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | 输出布尔标志：`BUSY`。具体语义见 §3 行为说明。 |
| `ERR` | `BOOL` | 输出布尔标志：`ERR`。具体语义见 §3 行为说明。 |
| `ERRID` | `UDINT` | 无符号整数输出：`ERRID`。 |
| `ACTUAL` | `UDINT` | 无符号整数输出：`ACTUAL`。 |
| `MAXIMUM` | `UDINT` | 无符号整数输出：`MAXIMUM`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用**：`bExecute` 上升沿。返回当前 latency（瞬时值）+ 最大值（统计值）。

**典型值**：CX 设备空载 < 20 µs，重负载或非实时驱动干扰 > 100 µs。

**用途**：HMI 实时性诊断；超过阈值告警。


**调用一般约束**：本 FB 的所有输入 / 输出引脚语义已在 §2 接口定义表的中文说明列详细列出；调用方应按上述时序与状态机分支组织程序，并参照 §5 使用注意 / 常见坑回避典型陷阱。若 PDF 与 InfoSys 中未对某种异常工况作出明确说明，本仓库会以 ⚠️ 标记，提示读者用实测或在 Beckhoff Forum 上确认，而非凭推测下结论。

## 4. 错误码 / 返回值

本 FB 无显式错误输出。状态可以通过 `bBusy` / `bValid` / `bDone` 等过程信号间接判断。

## 5. 使用注意 / 常见坑

- `bExecute` 必须是上升沿触发；持续高电平不会重发请求，要释放再拉起。
- `tTimeout` 默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。跨网段调用建议放大；过长会卡周期任务。（工程经验补充）
- PDF 没有枚举具体错误号——`nErrId / nErrorId` 引用通用 **ADS Return Codes** 表（参考 InfoSys 在线表）。
- `bBusy` 高电平期间业务侧不要再次拉起 `bExecute`，否则被忽略。（工程经验补充）
- 跨网段调用应放在非实时任务里执行，避免 PLC 周期任务被 ADS 抖动撑爆。（工程经验补充）
- CPU / latency 数据来自 TwinCAT 内部统计，更新周期由 SystemService 控制（典型 100 ms-1 s）。（工程经验补充）
- 数值是相对值（百分比 / 微秒），跨设备直接比较意义不大；应在同设备内做趋势分析。（工程经验补充）
- 最大值字段是 TwinCAT 启动以来的累计最大值——业务侧若关心『当前 1 分钟内』需要自己周期复位。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_TC_SysLatency.xml`](../examples/P_Demo_TC_SysLatency.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 实时性面板。
- **价值**：标准实时性观测。
- **替代方案对比**：
  - TwinCAT XAE Realtime 选项卡：单机方便。
  - **本 FB**：PLC 程序可读，能进 HMI 仪表盘。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.88
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35036171.html
- **相关 FB**：`TC_SysLatencyEx`, `TC_CpuUsage`
