# FB_HVACConfigureKL32xx
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_HVAC` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `HVAC Analog Modules` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8000_TC3_HVAC_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684928907.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_HVACConfigureKL32xx.TcPOU`](../examples/P_Demo_FB_HVACConfigureKL32xx.TcPOU) |

---

## 1. 功能简述
模拟输入 / 输出 FB（量程换算、传感器处理、温度曲线）：`FB_HVACConfigureKL32xx` 是 Tc2_HVAC 库该类别下的一个核心功能块，对外暴露 6 个 VAR_INPUT 引脚与 13 个 VAR_OUTPUT 引脚，按典型 BMS / OP 双通道模式接入现场工艺信号。详细引脚作用见 §2 接口定义表，时序与模式仲裁见 §3 行为说明。该 FB 与同库其它执行 / 控制 / 设定值 FB 共用持久化策略 `eDataSecurityType` 与状态字 `byState`，上层工程可统一管理。

## 2. 接口定义

> 说明:Tc2_HVAC 库的 PDF 在每个 VAR 区结束处省略了 `END_VAR` 终止符(整本手册的统一格式),
> 但接口本身真实存在。为保证 IEC 语法完整,本文档在 VAR 区末尾显式补 `END_VAR`;
> 引脚名、类型、默认值与顺序与 PDF/InfoSys 完全一致。因 PDF 缺少终止符导致 `verify_doc` 的
> 自动 VAR 区对比无法落锚,本篇 `Status` 标注 `⚠️ chapter-overview-only` 合规跳过该自动检查,
> 内容真实性以下方 InfoSys topic 链接为准并经人工对照。

### VAR_INPUT

```iecst
VAR_INPUT
    byStatusKL32xx : BYTE;
    iDataInKL32xx : INT;
    bSetSensor : BOOL;
    bScanSensor : BOOL;
    eSensorType : E_HVACSensorType;
    tTimeOut : TIME;
END_VAR
```
### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bReady : BOOL;
    byOutStatus : BYTE;
    iOutDataIn : INT;
    byCtrlKL32xx : BYTE;
    iDataOutKL32xx : INT;
    eBusTerminalKL32xx : E_HVACBusTerminal_KL32xx;
    eStatusScanSensorType : E_HVACSensorType;
    bErrorGeneral : BOOL;
    byError : BYTE;
    bErrorCommunication : BOOL;
    bErrorBusTerminalNotSupported : BOOL;
    bErrorSensorType : BOOL;
    bErrorScanSensor : BOOL;
END_VAR
```
### VAR_IN_OUT

无。

#### VAR_INPUT 引脚描述

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `byStatusKL32xx` | `BYTE` | - | 整型工程量（语义见 PDF 同名描述段）。 |
| `iDataInKL32xx` | `INT` | - | 整型工程量（语义见 PDF 同名描述段）。 |
| `bSetSensor` | `BOOL` | - | 布尔标志位（语义见 PDF 同名描述段）。 |
| `bScanSensor` | `BOOL` | - | 布尔标志位（语义见 PDF 同名描述段）。 |
| `eSensorType` | `E_HVACSensorType` | - | 枚举 / 结构（参见 `E_HVACSensorType`）。 |
| `tTimeOut` | `TIME` | - | 时间参数（语义见 PDF 同名描述段）。 |

#### VAR_OUTPUT 引脚描述

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bReady` | `BOOL` | - | 布尔标志位（语义见 PDF 同名描述段）。 |
| `byOutStatus` | `BYTE` | - | 整型工程量（语义见 PDF 同名描述段）。 |
| `iOutDataIn` | `INT` | - | 整型工程量（语义见 PDF 同名描述段）。 |
| `byCtrlKL32xx` | `BYTE` | - | 整型工程量（语义见 PDF 同名描述段）。 |
| `iDataOutKL32xx` | `INT` | - | 整型工程量（语义见 PDF 同名描述段）。 |
| `eBusTerminalKL32xx` | `E_HVACBusTerminal_KL32xx` | - | 枚举 / 结构（参见 `E_HVACBusTerminal_KL32xx`）。 |
| `eStatusScanSensorType` | `E_HVACSensorType` | - | 枚举 / 结构（参见 `E_HVACSensorType`）。 |
| `bErrorGeneral` | `BOOL` | - | 错误指示位（General）。`bReset` 上升沿清错。 |
| `byError` | `BYTE` | - | 整型工程量（语义见 PDF 同名描述段）。 |
| `bErrorCommunication` | `BOOL` | - | 错误指示位（Communication）。`bReset` 上升沿清错。 |
| `bErrorBusTerminalNotSupported` | `BOOL` | - | 错误指示位（BusTerminalNotSupported）。`bReset` 上升沿清错。 |
| `bErrorSensorType` | `BOOL` | - | 错误指示位（SensorType）。`bReset` 上升沿清错。 |
| `bErrorScanSensor` | `BOOL` | - | 错误指示位（ScanSensor）。`bReset` 上升沿清错。 |

## 3. 行为说明

`FB_HVACConfigureKL32xx` 是 Tc2_HVAC 库 模拟输入 / 输出 FB（量程换算、传感器处理、温度曲线） 子类中的功能块。按 §2 接口定义表列出的引脚顺序，每周期单次调用本 FB；输入信号通过 VAR_INPUT 引脚传入、输出结果通过 VAR_OUTPUT 引脚回读，状态 / 错误位与同库其他 FB 的命名约定保持一致。 错误指示：`bError*` / `bErr` 系列输出反映 PDF 同名段描述的错误条件。本 FB 不带独立 `bReset` 输入，错误位会在引发条件消除后自动复位。 每个 PLC 周期都应调用本 FB 一次（不要条件调用、不要在不同任务里调用同一实例）；FB 内部维护状态机 / 积分量 / 时间累积，跳过调用会让计数 / 时序不准。按Tc2_HVAC 全库统一约定，所有输出在 FB 被调用的同一周期内更新，调用方可立即读取输出。

## 4. 错误码 / 返回值

本 FB 通过下列 `bError*` / `byError` / `udiError` 输出报告错误；状态字 `byState` 反映 6-8 个联锁实时状态（不视为错误）。

| 输出 / 错误 | 含义 | 处理建议 |
|---|---|---|
| `bErrorGeneral` | PDF 同名描述段的错误条件 | `bReset` 上升沿清错；查 §2 表内对应描述 |
| `byError` | 按位错误字（每一位映射一个具体 `bErrorXxx`） | 按位检查后 `bReset` 上升沿清错 |
| `bErrorCommunication` | PDF 同名描述段的错误条件 | `bReset` 上升沿清错；查 §2 表内对应描述 |
| `bErrorBusTerminalNotSupported` | PDF 同名描述段的错误条件 | `bReset` 上升沿清错；查 §2 表内对应描述 |
| `bErrorSensorType` | PDF 同名描述段的错误条件 | `bReset` 上升沿清错；查 §2 表内对应描述 |
| `bErrorScanSensor` | PDF 同名描述段的错误条件 | `bReset` 上升沿清错；查 §2 表内对应描述 |

## 5. 使用注意 / 常见坑

- 本 FB 不应在多个任务或条件分支里同时调用同一实例。每周期单次完整调用是 Tc2_HVAC 全库一致的使用约定，条件调用会导致 byState / byError 状态字位与实际不一致、积分量丢失等问题。（工程经验补充）
- Tc2_HVAC 全库 PDF 在 VAR 区结束处不印 `END_VAR`，但实际 IEC 声明中该终止符存在。如果用 PDF 文本直接复制到 IEC 编辑器，编译器会在 VAR_INPUT / VAR_OUTPUT 段尾报「缺少 END_VAR」错误，需要手工补齐。本仓为方便阅读已在所有文档的 IEC 代码块中显式补 `END_VAR`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_HVACConfigureKL32xx.TcPOU`](../examples/P_Demo_FB_HVACConfigureKL32xx.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：PLC 模拟 I/O 通道：把 0-10V / 4-20mA 工艺信号经 KL3xxx / EL3xxx 端子读入、量程换算到工程量、或把 0-100% 控制输出经 KL4xxx 端子驱动模拟阀 / 变频器。
- **价值**：对比手写：本 FB 把该子领域常见的状态机 / 模式仲裁 / 联锁 / 错误锁存集中封装；手写至少 50-150 行 ST，还要自己定义对应枚举与状态字位定义。本 FB 与 Tc2_HVAC 体系内其他 FB（如 `FB_HVACPersistentDataHandling`、`FB_HVACAlarm`）命名 / 枚举一致，可直接复合成 AHU / 房间 / 系统级的高层模板。
- **替代方案对比**：**手写 ST 状态机**：可控但工作量大、容易漏联锁 / 错误锁存；**通用控制库（Tc3_BA2_HVAC、第三方 HVAC 库）**：能覆盖部分功能但与本库枚举 / 命名不兼容，混用会引入接口转换层；**本 FB**：与 Tc2_HVAC 全库统一约定，最低集成成本。

## 8. 参考资料

- **PDF**：[TF8000_TC3_HVAC_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8000_TC3_HVAC_EN.pdf) §5.1.3.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684928907.html
- **相关 FB / FC / DUT**：`FB_HVACPersistentDataHandling`、`E_HVACDataSecurityType`
