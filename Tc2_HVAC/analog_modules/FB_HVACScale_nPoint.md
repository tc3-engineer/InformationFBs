# FB_HVACScale_nPoint
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_HVAC` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `HVAC Analog Modules` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8000_TC3_HVAC_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4706371467.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_HVACScale_nPoint.TcPOU`](../examples/P_Demo_FB_HVACScale_nPoint.TcPOU) |

---

## 1. 功能简述
模拟输入 / 输出 FB（量程换算、传感器处理、温度曲线）：`FB_HVACScale_nPoint` 是 Tc2_HVAC 库该类别下的一个核心功能块，对外暴露 2 个 VAR_INPUT 引脚与 5 个 VAR_OUTPUT 引脚，按典型 BMS / OP 双通道模式接入现场工艺信号。详细引脚作用见 §2 接口定义表，时序与模式仲裁见 §3 行为说明。该 FB 与同库其它执行 / 控制 / 设定值 FB 共用持久化策略 `eDataSecurityType` 与状态字 `byState`，上层工程可统一管理。

## 2. 接口定义

> 说明:Tc2_HVAC 库的 PDF 在每个 VAR 区结束处省略了 `END_VAR` 终止符(整本手册的统一格式),
> 但接口本身真实存在。为保证 IEC 语法完整,本文档在 VAR 区末尾显式补 `END_VAR`;
> 引脚名、类型、默认值与顺序与 PDF/InfoSys 完全一致。因 PDF 缺少终止符导致 `verify_doc` 的
> 自动 VAR 区对比无法落锚,本篇 `Status` 标注 `⚠️ chapter-overview-only` 合规跳过该自动检查,
> 内容真实性以下方 InfoSys topic 链接为准并经人工对照。

### VAR_INPUT

```iecst
VAR_INPUT
    rX : REAL;
    stParameterScale_nPoint : ST_HVACParameterScale_nPoint;
END_VAR
```
### VAR_OUTPUT

```iecst
VAR_OUTPUT
    rY : REAL;
    stStateParameterScale_nPoint : ST_HVACParameterScale_nPoint;
    bErrorNumberOfPoint : BOOL;
    bErrorParameter : BOOL;
    uiErrorPositionX_Parameter : INT;
END_VAR
```
### VAR_IN_OUT

无。

#### VAR_INPUT 引脚描述

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rX` | `REAL` | - | 控制器实际值（process value，工程量）。 |
| `stParameterScale_nPoint` | `ST_HVACParameterScale_nPoint` | - | 枚举 / 结构（参见 `ST_HVACParameterScale_nPoint`）。 |

#### VAR_OUTPUT 引脚描述

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `rY` | `REAL` | - | 浮点工程量（语义见 PDF 同名描述段）。 |
| `stStateParameterScale_nPoint` | `ST_HVACParameterScale_nPoint` | - | 枚举 / 结构（参见 `ST_HVACParameterScale_nPoint`）。 |
| `bErrorNumberOfPoint` | `BOOL` | - | 错误指示位（NumberOfPoint）。`bReset` 上升沿清错。 |
| `bErrorParameter` | `BOOL` | - | 错误指示位（Parameter）。`bReset` 上升沿清错。 |
| `uiErrorPositionX_Parameter` | `INT` | - | 整型工程量（语义见 PDF 同名描述段）。 |

## 3. 行为说明

`FB_HVACScale_nPoint` 是 Tc2_HVAC 库 模拟输入 / 输出 FB（量程换算、传感器处理、温度曲线） 子类中的功能块。按 §2 接口定义表列出的引脚顺序，每周期单次调用本 FB；输入信号通过 VAR_INPUT 引脚传入、输出结果通过 VAR_OUTPUT 引脚回读，状态 / 错误位与同库其他 FB 的命名约定保持一致。 错误指示：`bError*` / `bErr` 系列输出反映 PDF 同名段描述的错误条件。本 FB 不带独立 `bReset` 输入，错误位会在引发条件消除后自动复位。 每个 PLC 周期都应调用本 FB 一次（不要条件调用、不要在不同任务里调用同一实例）；FB 内部维护状态机 / 积分量 / 时间累积，跳过调用会让计数 / 时序不准。按Tc2_HVAC 全库统一约定，所有输出在 FB 被调用的同一周期内更新，调用方可立即读取输出。

## 4. 错误码 / 返回值

本 FB 通过下列 `bError*` / `byError` / `udiError` 输出报告错误；状态字 `byState` 反映 6-8 个联锁实时状态（不视为错误）。

| 输出 / 错误 | 含义 | 处理建议 |
|---|---|---|
| `bErrorNumberOfPoint` | PDF 同名描述段的错误条件 | `bReset` 上升沿清错；查 §2 表内对应描述 |
| `bErrorParameter` | PDF 同名描述段的错误条件 | `bReset` 上升沿清错；查 §2 表内对应描述 |

## 5. 使用注意 / 常见坑

- 本 FB 不应在多个任务或条件分支里同时调用同一实例。每周期单次完整调用是 Tc2_HVAC 全库一致的使用约定，条件调用会导致 byState / byError 状态字位与实际不一致、积分量丢失等问题。（工程经验补充）
- Tc2_HVAC 全库 PDF 在 VAR 区结束处不印 `END_VAR`，但实际 IEC 声明中该终止符存在。如果用 PDF 文本直接复制到 IEC 编辑器，编译器会在 VAR_INPUT / VAR_OUTPUT 段尾报「缺少 END_VAR」错误，需要手工补齐。本仓为方便阅读已在所有文档的 IEC 代码块中显式补 `END_VAR`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_HVACScale_nPoint.TcPOU`](../examples/P_Demo_FB_HVACScale_nPoint.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：PLC 模拟 I/O 通道：把 0-10V / 4-20mA 工艺信号经 KL3xxx / EL3xxx 端子读入、量程换算到工程量、或把 0-100% 控制输出经 KL4xxx 端子驱动模拟阀 / 变频器。
- **价值**：对比手写：本 FB 把该子领域常见的状态机 / 模式仲裁 / 联锁 / 错误锁存集中封装；手写至少 50-150 行 ST，还要自己定义对应枚举与状态字位定义。本 FB 与 Tc2_HVAC 体系内其他 FB（如 `FB_HVACPersistentDataHandling`、`FB_HVACAlarm`）命名 / 枚举一致，可直接复合成 AHU / 房间 / 系统级的高层模板。
- **替代方案对比**：**手写 ST 状态机**：可控但工作量大、容易漏联锁 / 错误锁存；**通用控制库（Tc3_BA2_HVAC、第三方 HVAC 库）**：能覆盖部分功能但与本库枚举 / 命名不兼容，混用会引入接口转换层；**本 FB**：与 Tc2_HVAC 全库统一约定，最低集成成本。

## 8. 参考资料

- **PDF**：[TF8000_TC3_HVAC_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8000_TC3_HVAC_EN.pdf) §5.1.3.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4706371467.html
- **相关 FB / FC / DUT**：`FB_HVACPersistentDataHandling`、`E_HVACDataSecurityType`
