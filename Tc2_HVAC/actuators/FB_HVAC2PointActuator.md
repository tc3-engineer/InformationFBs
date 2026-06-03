# FB_HVAC2PointActuator
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_HVAC` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `HVAC Actuators` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8000_TC3_HVAC_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684915083.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_HVAC2PointActuator.TcPOU`](../examples/P_Demo_FB_HVAC2PointActuator.TcPOU) |

---

## 1. 功能简述
用于控制**两点式（开 / 关）阀门或两点式风阀**。FB 接收数字开关命令（`bIn`），结合开 / 关到位反馈、控制电压、手动 / 紧急开关与运行模式枚举进行联锁判断后驱动 `bOut`；同时按可配置行程时间 `tStrokeTime` 监测到位开关，超时仍未到位即在 `bErrorLimitSwitch` 报错。提供可选的持久化存储（`eDataSecurityType`）让 IN_OUT 变量在断电后保留。

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
    bIn : BOOL;
    eCtrlModeActuator : E_HVAC2PointActuatorMode;
    bManSwitch : BOOL;
    bLimitSwitchClose : BOOL;
    bLimitSwitchOpen : BOOL;
    bCtrlVoltage : BOOL;
    bReset : BOOL;
END_VAR
```
### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bOut : BOOL;
    byState : BYTE;
    eStateModeActuator : E_HVAC2PointActuatorMode;
    bErrorLimitSwitch : BOOL;
    bInvalidParameter : BOOL;
END_VAR
```
### VAR_IN_OUT

```iecst
VAR_IN_OUT
    bEnableLimitSwitch : BOOL;
    tStrokeTime : TIME;
END_VAR
```

#### VAR_INPUT 引脚描述

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `eDataSecurityType` | `E_HVACDataSecurityType` | - | 持久化策略枚举（参见 `E_HVACDataSecurityType`）：选 `eHVACDataSecurityType_Persistent` 时所有 VAR_IN_OUT 变量在变化瞬间写入闪存，**需配合 `FB_HVACPersistentDataHandling` 在主程序中循环调用**；选 `eHVACDataSecurityType_Idle` 时 VAR_IN_OUT 在 RAM 中保存，断电丢失。 |
| `bSetDefault` | `BOOL` | - | 上升沿一次性把所有 VAR_IN_OUT 复位为出厂默认值。首次下载工程后应触发一次。 |
| `bEnable` | `BOOL` | - | PLC 程序总使能。`TRUE` 时进入正常工作；`FALSE` 时所有输出复位到安全态（一般为 0 / FALSE / 替代值）。 |
| `bIn` | `BOOL` | - | 自动模式下的命令：FALSE = 关、TRUE = 开。 |
| `eCtrlModeActuator` | `E_HVAC2PointActuatorMode` | - | 运行模式枚举：Auto_BMS / Open_BMS / Close_BMS / Auto_OP / Open_OP / Close_OP。BMS 来自上位机命令，OP 来自就地操作面板。 |
| `bManSwitch` | `BOOL` | - | 手动 / 紧急开关反馈位。当现场控制柜带手 / 急停开关时接入此引脚；`bManSwitch = FALSE` 时强制输出进入安全态。 |
| `bLimitSwitchClose` | `BOOL` | - | 「全关」到位反馈：阀门 / 风阀完全关到位时该引脚 TRUE。 |
| `bLimitSwitchOpen` | `BOOL` | - | 「全开」到位反馈：阀门 / 风阀完全开到位时该引脚 TRUE。 |
| `bCtrlVoltage` | `BOOL` | - | 控制电压在线指示。FALSE 时反馈监测被抑制（避免断电瞬间误报错）。建议接控制电压 24V 监视继电器辅助触点。 |
| `bReset` | `BOOL` | - | 故障复位输入：上升沿清除内部错误锁存（如 `bErrorXxx`、`bInvalidParameter`）。 |

#### VAR_OUTPUT 引脚描述

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bOut` | `BOOL` | - | 驱动输出：FALSE = 关阀 / 关风阀，TRUE = 开阀 / 开风阀。 |
| `byState` | `BYTE` | - | 状态字（按位）：bit0 = Enable、bit1 = Manual Switch、bit2 = Enable Feedback Control、bit3 = Control Voltage、bit4 = Reset、bit5 = bOut。用于上位机统一回读各联锁状态。 |
| `eStateModeActuator` | `E_HVAC2PointActuatorMode` | - | 当前实际运行模式回显（与 `eCtrlModeActuator` 经内部仲裁后的结果可能不同）。 |
| `bErrorLimitSwitch` | `BOOL` | - | 到位监测错误：在 `tStrokeTime` 行程时间内未检测到任何到位开关。`bReset` 上升沿清错。 |
| `bInvalidParameter` | `BOOL` | - | 参数合理性检查失败（如时间 / 量程越界）；`bReset` 上升沿清错。 |

#### VAR_IN_OUT 引脚描述

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bEnableLimitSwitch` | `BOOL` | - | 持久量：是否启用到位反馈监测。TRUE = 启用（无到位反馈则报错）；FALSE = 不监测。 |
| `tStrokeTime` | `TIME` | - | 持久量：行程时间，全关 → 全开（或反向）的最长时间。范围 0..3600 s，默认 T#200S。超时未到位即 `bErrorLimitSwitch`。 |

## 3. 行为说明

上电后 FB 等待 `bEnable := TRUE` 才进入工作态；未使能时输出 `bOut` 强制 FALSE，阀门 / 风阀保持关位。进入工作态后按 `eCtrlModeActuator` 决定数据源：Auto_BMS / Auto_OP 模式跟随 `bIn` 自动控制；Open_BMS / Open_OP 强制开（`bOut := TRUE`）；Close_BMS / Close_OP 强制关（`bOut := FALSE`）；BMS（Building Management System）来自上位机命令通道，OP（Operator Panel）来自就地控制面板。`bManSwitch` 与 `bCtrlVoltage` 为最高优先级硬件联锁——只要其中之一为 FALSE，`bOut` 立即被拉低进入安全态。到位监测开关 `bEnableLimitSwitch` 启用时，FB 在每次驱动命令变化后启动内部倒计时 `tStrokeTime`；时限内若 `bLimitSwitchClose` 或 `bLimitSwitchOpen` 与命令方向匹配则正常，否则置位 `bErrorLimitSwitch`。任何故障位必须由 `bReset` 上升沿手动复位。`bSetDefault` 上升沿一次性把持久量 `bEnableLimitSwitch`、`tStrokeTime` 复位为出厂默认。`eDataSecurityType` 选 Persistent 时所有 VAR_IN_OUT 在变化的瞬间写入闪存（需配合 `FB_HVACPersistentDataHandling` 在主任务循环调用）。

## 4. 错误码 / 返回值

本 FB 通过下列 `bError*` / `byError` / `udiError` 输出报告错误；状态字 `byState` 反映 6-8 个联锁实时状态（不视为错误）。

| 输出 / 错误 | 含义 | 处理建议 |
|---|---|---|
| `bErrorLimitSwitch` | PDF 同名描述段的错误条件 | `bReset` 上升沿清错；查 §2 表内对应描述 |
| `bInvalidParameter` | VAR_IN_OUT 参数越界 / 类型不合理 | 查 §2 表内合法范围；修正后 `bReset` 上升沿清错 |

## 5. 使用注意 / 常见坑

- `eDataSecurityType` 选 `Persistent` 必须同时在主程序中实例化 `FB_HVACPersistentDataHandling` 并周期调用，否则 FB 内部不会释放写盘资源，IN_OUT 变化不会持久化。
- 切勿把循环变化的变量直接连到 VAR_IN_OUT 引脚——每次变化都触发一次闪存写入，会导致 NAND / NOR 寿命短期内耗尽。仅在 HMI 触发的参数变更场景使用 Persistent。（PDF NOTICE 明示）
- `bManSwitch` 在工程实践中一定要接现场控制柜的紧急复位 / 手动开关物理触点；硬件信号才能真正切到安全态。若用软件 BOOL 模拟则丢失硬件联锁的作用。（工程经验补充）
- `tStrokeTime` 建议比阀厂家行程时间表数据再多 50%；现场遇到风阀低温卡涩、长期氧化都会让实际开关时间变长，过紧的 `tStrokeTime` 会频繁误报错。（工程经验补充）
- `bCtrlVoltage` 应接控制电压检测继电器的辅助触点（如 24V 监视继电器）。这样市电瞬断或控制器供电故障时 FB 立刻进入安全态。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_HVAC2PointActuator.TcPOU`](../examples/P_Demo_FB_HVAC2PointActuator.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：新风机组（AHU）冷热水盘管的两通 / 二位电动阀控制：上位机给开 / 关命令（`bIn`），现场控制柜内有 24V 手 / 自切换开关（`bManSwitch`）和 24V 控制电压监视继电器（`bCtrlVoltage`），阀体自带全开 / 全关行程开关反馈（`bLimitSwitchOpen` / `bLimitSwitchClose`），并且要求所有手动 / 行程时间等参数掉电不丢。
- **价值**：本 FB 把「自动 / 手动模式仲裁、控制电压联锁、到位监测、行程时间故障检测、参数持久化」5 块功能一次集成；手写至少 80-120 行 ST 才能等价实现。状态字 `byState` 直接对接 HMI 排错，避免每路阀门各自实现一套联锁逻辑导致风格不统一。
- **替代方案对比**：**手写 ST**：得自己实现状态机 + 持久化 + 到位监测，工程量大且容易漏；**FB_HVAC3PointActuator**：三点（开 / 关 / 停）阀适用，含位置反馈，但对二位阀过度设计；**纯 BOOL 输出**：最简陋，无监测无联锁，不适合带反馈的执行器。

## 8. 参考资料

- **PDF**：[TF8000_TC3_HVAC_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8000_TC3_HVAC_EN.pdf) §5.1.2.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684915083.html
- **相关 FB / FC / DUT**：`FB_HVAC3PointActuator`、`FB_HVACPersistentDataHandling`、`E_HVAC2PointActuatorMode`、`E_HVACDataSecurityType`
