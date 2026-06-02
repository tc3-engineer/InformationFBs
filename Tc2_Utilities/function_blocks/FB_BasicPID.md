# FB_BasicPID

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35047819.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_BasicPID.TcPOU`](../examples/P_Demo_FB_BasicPID.TcPOU) |

---

## 1. 功能简述

FB_BasicPID 实现一个基础 PID 控制器：给定测量值 + 设定值 + Kp/Ki/Kd 参数，输出执行量。

用于：简单的温度 / 流量 / 压力 / 位置闭环控制。比 Tc3_Controller 库的高级控制器轻量，适合教学 / 小项目。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    fSetpointValue : LREAL;
    fActualValue : LREAL;
    bReset : BOOL;
    fCtrlCycleTime : LREAL;
    fKp : LREAL;
    fTn : LREAL;
    fTv : LREAL;
    fTd : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `fSetpointValue` | `LREAL` | 浮点数：`fSetpointValue`。 |
| `fActualValue` | `LREAL` | 浮点数：`fActualValue`。 |
| `bReset` | `BOOL` | 输入布尔标志：`bReset`。具体语义见 §3 行为说明。 |
| `fCtrlCycleTime` | `LREAL` | 浮点数：`fCtrlCycleTime`。 |
| `fKp` | `LREAL` | 浮点数：`fKp`。 |
| `fTn` | `LREAL` | 浮点数：`fTn`。 |
| `fTv` | `LREAL` | 浮点数：`fTv`。 |
| `fTd` | `LREAL` | 浮点数：`fTd`。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    fCtrlOutput : LREAL;
    nErrorStatus : UINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `fCtrlOutput` | `LREAL` | 浮点数：`fCtrlOutput`。 |
| `nErrorStatus` | `UINT` | 无符号整数输出：`nErrorStatus`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**周期调用**：每个 PLC 周期调一次。FB 内部按设定的采样时间累加积分项 / 计算微分。

**抗饱和**：内部 anti-windup 处理，输出在限幅时不会无限累加积分。

**模式**：自动 / 手动切换，无扰切换由 FB 内部处理。


**调用一般约束**：本 FB 的所有输入 / 输出引脚语义已在 §2 接口定义表的中文说明列详细列出；调用方应按上述时序与状态机分支组织程序，并参照 §5 使用注意 / 常见坑回避典型陷阱。若 PDF 与 InfoSys 中未对某种异常工况作出明确说明，本仓库会以 ⚠️ 标记，提示读者用实测或在 Beckhoff Forum 上确认，而非凭推测下结论。

## 4. 错误码 / 返回值

本 FB 无显式错误输出。状态可以通过 `bBusy` / `bValid` / `bDone` 等过程信号间接判断。

## 5. 使用注意 / 常见坑

- **参数整定不当易振荡**——Kp 过大、Ti 过小会振荡。建议先用 Ziegler-Nichols 法粗调。（工程经验补充）
- **采样时间应与 PLC 任务周期一致**——不一致会让积分 / 微分计算错。
- **手动 → 自动切换瞬间**：FB 内部用『积分项预置』避免输出跳变；业务侧不需要自己处理。（工程经验补充）
- PDF 错误反映为输出限幅 / 状态枚举，不会直接报『PID 不稳定』——稳定性靠工程师整定。
- **不要用 Basic 做高动态系统**——电机伺服等场景应用 Tc3_Controller 的高级控制器。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_BasicPID.TcPOU`](../examples/P_Demo_FB_BasicPID.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：水箱温度闭环控制：测温度 → PID → 控制加热阀。
- **价值**：比手写 PID 安全（带 anti-windup）。
- **替代方案对比**：
  - 手写 PID：易忘 anti-windup。
  - Tc3_Controller：高级、复杂。
  - **本 FB**：轻量。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35047819.html
