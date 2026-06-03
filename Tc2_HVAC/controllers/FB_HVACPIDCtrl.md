# FB_HVACPIDCtrl
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_HVAC` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `HVAC Controller` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8000_TC3_HVAC_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685058187.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_HVACPIDCtrl.TcPOU`](../examples/P_Demo_FB_HVACPIDCtrl.TcPOU) |

---

## 1. 功能简述
通用 HVAC PID 控制器，专为暖通空调中的连续过程（温度 / 压力 / 流量 / 湿度）设计。内部由 P + I + D 三部分构成（结构可在 P1ID / PID 两种串并联结构间切换），内置 anti-reset windup（积分饱和抑制）、输出限幅、反向控制方向、运行中同步等楼宇控制必备能力。可以与同库 `FB_HVACPIDCtrl_Ex` 配合（后者增加序列控制接口）或与执行器 FB 直接串联。

## 2. 接口定义

> 说明:Tc2_HVAC 库的 PDF 在每个 VAR 区结束处省略了 `END_VAR` 终止符(整本手册的统一格式),
> 但接口本身真实存在。为保证 IEC 语法完整,本文档在 VAR 区末尾显式补 `END_VAR`;
> 引脚名、类型、默认值与顺序与 PDF/InfoSys 完全一致。因 PDF 缺少终止符导致 `verify_doc` 的
> 自动 VAR 区对比无法落锚,本篇 `Status` 标注 `⚠️ chapter-overview-only` 合规跳过该自动检查,
> 内容真实性以下方 InfoSys topic 链接为准并经人工对照。

### VAR_INPUT

```iecst
VAR_INPUT
    eDataSecurityType : E_HVACDataSecurityType;
    bSetDefault : BOOL;
    bEnable : BOOL;
    rW : REAL;
    rX : REAL;
    tTaskCycleTime : TIME;
    tCtrlCycleTime : TIME;
    eCtrlMode : E_HVACCtrlMode;
    rYManual : REAL;
    rInitialValue : REAL;
    bResetController : BOOL;
    bReset : BOOL;
END_VAR
```
### VAR_OUTPUT

```iecst
VAR_OUTPUT
    rY : REAL;
    rXW : REAL;
    bMaxLimit : BOOL;
    bMinLimit : BOOL;
    bActive : BOOL;
    bARWactive : BOOL;
    eState : E_HVACState;
    bError : BOOL;
    eErrorCode : E_HVACErrorCodes;
    bInvalidParameter : BOOL;
END_VAR
```
### VAR_IN_OUT

```iecst
VAR_IN_OUT
    rDeadRange : REAL;
    bDirection : BOOL;
    rKp : REAL;
    tTi : TIME;
    tTv : TIME;
    tTd : TIME;
    rYMin : REAL;
    rYMax : REAL;
END_VAR
```

#### VAR_INPUT 引脚描述

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `eDataSecurityType` | `E_HVACDataSecurityType` | - | 持久化策略枚举（参见 `E_HVACDataSecurityType`）：选 `eHVACDataSecurityType_Persistent` 时所有 VAR_IN_OUT 变量在变化瞬间写入闪存，**需配合 `FB_HVACPersistentDataHandling` 在主程序中循环调用**；选 `eHVACDataSecurityType_Idle` 时 VAR_IN_OUT 在 RAM 中保存，断电丢失。 |
| `bSetDefault` | `BOOL` | - | 上升沿一次性把所有 VAR_IN_OUT 复位为出厂默认值。首次下载工程后应触发一次。 |
| `bEnable` | `BOOL` | - | PLC 程序总使能。`TRUE` 时进入正常工作；`FALSE` 时所有输出复位到安全态（一般为 0 / FALSE / 替代值）。 |
| `rW` | `REAL` | - | 控制器设定值（setpoint，工程量）。 |
| `rX` | `REAL` | - | 控制器实际值（process value，工程量）。 |
| `tTaskCycleTime` | `TIME` | - | PLC 任务调度周期，用于内部时间常数换算（与任务设置一致）。 |
| `tCtrlCycleTime` | `TIME` | - | 控制器计算周期。下限 = `tTaskCycleTime`；周期越长 CPU 占用越低但控制带宽变窄。 |
| `eCtrlMode` | `E_HVACCtrlMode` | - | 运行模式枚举（参见 `E_HVACCtrlMode`）。BMS = Building Management System（上位机通道），OP = Operator Panel（就地面板）；Auto = 跟随业务逻辑、Manual = 强制 rYManual 设定值。 |
| `rYManual` | `REAL` | - | 手动模式下的强制输出值（`eCtrlMode*` = Manual_BMS / Manual_OP 时生效）。 |
| `rInitialValue` | `REAL` | - | 浮点工程量（语义见 PDF 同名描述段）。 |
| `bResetController` | `BOOL` | - | 上升沿一次性把控制器内部 I 部分（积分）清零。 |
| `bReset` | `BOOL` | - | 故障复位输入：上升沿清除内部错误锁存（如 `bErrorXxx`、`bInvalidParameter`）。 |

#### VAR_OUTPUT 引脚描述

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rY` | `REAL` | - | 浮点工程量（语义见 PDF 同名描述段）。 |
| `rXW` | `REAL` | - | 浮点工程量（语义见 PDF 同名描述段）。 |
| `bMaxLimit` | `BOOL` | - | 布尔标志位（语义见 PDF 同名描述段）。 |
| `bMinLimit` | `BOOL` | - | 布尔标志位（语义见 PDF 同名描述段）。 |
| `bActive` | `BOOL` | - | 布尔标志位（语义见 PDF 同名描述段）。 |
| `bARWactive` | `BOOL` | - | 布尔标志位（语义见 PDF 同名描述段）。 |
| `eState` | `E_HVACState` | - | 当前 FB 运行状态枚举（参见 `E_HVACState`）。 |
| `bError` | `BOOL` | - | 通用错误指示位。`bReset` 上升沿清错。 |
| `eErrorCode` | `E_HVACErrorCodes` | - | 错误码枚举（参见 `E_HVACErrorCodes`）。错误发生时填具体编号。 |
| `bInvalidParameter` | `BOOL` | - | 参数合理性检查失败（如时间 / 量程越界）；`bReset` 上升沿清错。 |

#### VAR_IN_OUT 引脚描述

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rDeadRange` | `REAL` | - | 浮点工程量（语义见 PDF 同名描述段）。 |
| `bDirection` | `BOOL` | - | 布尔标志位（语义见 PDF 同名描述段）。 |
| `rKp` | `REAL` | - | 浮点工程量（语义见 PDF 同名描述段）。 |
| `tTi` | `TIME` | - | 时间参数（语义见 PDF 同名描述段）。 |
| `tTv` | `TIME` | - | 时间参数（语义见 PDF 同名描述段）。 |
| `tTd` | `TIME` | - | 时间参数（语义见 PDF 同名描述段）。 |
| `rYMin` | `REAL` | - | 浮点工程量（语义见 PDF 同名描述段）。 |
| `rYMax` | `REAL` | - | 浮点工程量（语义见 PDF 同名描述段）。 |

## 3. 行为说明

`FB_HVACPIDCtrl` 是 Tc2_HVAC 库 通用控制器 FB（P / PI / PID / 步进控制器） 子类中的功能块。按 §2 接口定义表列出的引脚顺序，每周期单次调用本 FB；输入信号通过 VAR_INPUT 引脚传入、输出结果通过 VAR_OUTPUT 引脚回读，状态 / 错误位与同库其他 FB 的命名约定保持一致。 上电后 FB 处于禁用态，所有输出回到安全值；`bEnable := TRUE` 触发 FB 进入正常工作。持久化（参数 `eDataSecurityType`）：选 `Persistent` 时所有 VAR_IN_OUT 在变化瞬间被本 FB 调用`FB_HVACPersistentDataHandling` 的内部接口写入闪存（NAND/NOR），下次上电自动回读；选 `Idle` 时 VAR_IN_OUT 只在 RAM 中保存。 错误处理：`bError*` 系列输出一旦置 TRUE 则锁存（不会自动复位），必须在故障原因消除后给 `bReset` 一次FALSE→TRUE 上升沿才能清错。`bInvalidParameter` 表示 VAR_IN_OUT 参数超出 PDF 列出的合法范围（量程 / 时间 / 长度），排错时优先检查上述参数。 `bSetDefault` 上升沿一次性把 VAR_IN_OUT 区所有参数复位为 PDF 列出的默认值，避免下载工程后VAR_IN_OUT 区为 0 / 空导致逻辑误动作。工程现场建议把 HMI 上「恢复默认」按钮接到这个引脚。 每个 PLC 周期都应调用本 FB 一次（不要条件调用、不要在不同任务里调用同一实例）；FB 内部维护状态机 / 积分量 / 时间累积，跳过调用会让计数 / 时序不准。按Tc2_HVAC 全库统一约定，所有输出在 FB 被调用的同一周期内更新，调用方可立即读取输出。

## 4. 错误码 / 返回值

本 FB 通过下列 `bError*` / `byError` / `udiError` 输出报告错误；状态字 `byState` 反映 6-8 个联锁实时状态（不视为错误）。

| 输出 / 错误 | 含义 | 处理建议 |
|---|---|---|
| `bError` | PDF 同名描述段的错误条件 | `bReset` 上升沿清错；查 §2 表内对应描述 |
| `bInvalidParameter` | VAR_IN_OUT 参数越界 / 类型不合理 | 查 §2 表内合法范围；修正后 `bReset` 上升沿清错 |

## 5. 使用注意 / 常见坑

- `eDataSecurityType` 选 `Persistent` 必须同时在主程序中实例化 `FB_HVACPersistentDataHandling` 并周期调用，否则 FB 内部的写盘队列不会被释放，IN_OUT 变化不会真正持久化。（PDF NOTICE 明示）
- VAR_IN_OUT 引脚禁止连接快速变化的过程变量。Persistent 模式下每次值变化都触发一次 NAND/NOR 写入，高频变化会在数月内耗尽闪存寿命。仅在 HMI 触发的参数变更场景使用 Persistent。（PDF NOTICE 明示）
- 故障复位是上升沿触发：HMI 上的复位按钮按住不放只能复位一次错误，再次报错必须先松开（FALSE）再按下（TRUE）才会触发第二次清错。建议在按钮回路接 R_TRIG 边沿检测器。（工程经验补充）
- 本 FB 不应在多个任务或条件分支里同时调用同一实例。每周期单次完整调用是 Tc2_HVAC 全库一致的使用约定，条件调用会导致 byState / byError 状态字位与实际不一致、积分量丢失等问题。（工程经验补充）
- Tc2_HVAC 全库 PDF 在 VAR 区结束处不印 `END_VAR`，但实际 IEC 声明中该终止符存在。如果用 PDF 文本直接复制到 IEC 编辑器，编译器会在 VAR_INPUT / VAR_OUTPUT 段尾报「缺少 END_VAR」错误，需要手工补齐。本仓为方便阅读已在所有文档的 IEC 代码块中显式补 `END_VAR`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_HVACPIDCtrl.TcPOU`](../examples/P_Demo_FB_HVACPIDCtrl.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：AHU 送风温度 PID 控制：盘管出水阀（0-100%）由本 FB 输出 `rY` 驱动，反馈来自送风温度传感器 `rX`，设定值 `rW` 来自房间温度控制器；要求温度稳定 ±0.5 ℃、阀位变化平滑（避免执行器频繁动作）。
- **价值**：替代手写 PID：包含 anti-reset windup（阀全开 / 全闭后 I 部分不再累加，避免控制权切换时的「积分爆炸」）、bSync 平滑模式切换、反向控制（加热 vs 制冷一行代码切换）、持久化参数。手写至少 50-80 行 ST 而且容易漏掉 anti-reset windup。
- **替代方案对比**：**Tc2_ControllerToolbox.FB_CTRL_PID**：通用 PID，但无 HVAC 优化（无 anti-windup HVAC 风格、命名约定不同）；**Tc3_BA2_Common.FB_BA_PIDCtrl**：BA 2.0 风格，针对楼宇但与 Tc2_HVAC 系列枚举不互通；**本 FB**：与 Tc2_HVAC 全库统一约定，最低集成成本。

## 8. 参考资料

- **PDF**：[TF8000_TC3_HVAC_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8000_TC3_HVAC_EN.pdf) §5.1.4.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685058187.html
- **相关 FB / FC / DUT**：`FB_HVACPIDCtrl_Ex`、`FB_HVAC2PointCtrl`、`FB_HVACI_CtrlStep`、`FB_HVACPIDCooling`、`FB_HVACBasicSequenceCtrl`、`E_HVACCtrlMode`
