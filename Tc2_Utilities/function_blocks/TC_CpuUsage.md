# TC_CpuUsage

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35033867.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_TC_CpuUsage.TcPOU`](../examples/P_Demo_TC_CpuUsage.TcPOU) |

---

## 1. 功能简述

TC_CpuUsage 读取目标 TwinCAT 系统当前的 CPU 占用率（百分比，单核或聚合，视配置）。

用于：HMI 系统状态面板、性能瓶颈诊断、容量规划。

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
    USAGE : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | 输出布尔标志：`BUSY`。具体语义见 §3 行为说明。 |
| `ERR` | `BOOL` | 输出布尔标志：`ERR`。具体语义见 §3 行为说明。 |
| `ERRID` | `UDINT` | 无符号整数输出：`ERRID`。 |
| `USAGE` | `UDINT` | 无符号整数输出：`USAGE`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用**：`bExecute` 上升沿读一次。返回 `nCpuUsage`（0..100 百分比）。

**采样窗口**：TwinCAT 内部典型 100 ms-1 s 滑动窗口，业务侧调用频率超过这个没意义。

**典型用法**：HMI 状态面板里每秒读一次。


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

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_TC_CpuUsage.TcPOU`](../examples/P_Demo_TC_CpuUsage.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 状态面板显示 CPU 占用率。
- **价值**：替代 Win32 perfmon。
- **替代方案对比**：
  - Win32 perfmon：复杂且需 Shell 通道。
  - **本 FB**：标准 ADS 调用。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.84
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35033867.html
- **相关 FB**：`TC_CpuUsageEx`, `TC_SysLatency`
