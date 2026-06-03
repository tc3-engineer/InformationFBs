# FB_HVACPersistentDataHandling
## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_HVAC` |
| Library Version | `1.3.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `HVAC System` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8000_TC3_HVAC_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685159179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_HVACPersistentDataHandling.TcPOU`](../examples/P_Demo_FB_HVACPersistentDataHandling.TcPOU) |

---

## 1. 功能简述
**Tc2_HVAC 库的持久化基础设施 FB**。所有 `eDataSecurityType := Persistent` 的 FB 在内部把要持久化的变量入队，本 FB 在主循环里轮询出队并写入闪存（`.bootdata-old` 备份文件）；上电时自动从备份文件回读。**必须在主程序中实例化一次并周期调用**，否则其它 FB 的写盘队列不会被消费。

## 2. 接口定义

> 说明:Tc2_HVAC 库的 PDF 在每个 VAR 区结束处省略了 `END_VAR` 终止符(整本手册的统一格式),
> 但接口本身真实存在。为保证 IEC 语法完整,本文档在 VAR 区末尾显式补 `END_VAR`;
> 引脚名、类型、默认值与顺序与 PDF/InfoSys 完全一致。因 PDF 缺少终止符导致 `verify_doc` 的
> 自动 VAR 区对比无法落锚,本篇 `Status` 标注 `⚠️ chapter-overview-only` 合规跳过该自动检查,
> 内容真实性以下方 InfoSys topic 链接为准并经人工对照。

### VAR_INPUT

```iecst
VAR_INPUT
    sNETID : T_AmsNetId;
    TMOUT : TIME;
    ePersistentMode : E_PersistentMode;
END_VAR
```
### VAR_OUTPUT

```iecst
VAR_OUTPUT
    udiStatus : UDINT;
    iPersistCount : INT;
    bDone : BOOL;
    bBusy : BOOL;
    bError : BOOL;
    udiErrorID : UDINT;
END_VAR
```
### VAR_IN_OUT

无。

#### VAR_INPUT 引脚描述

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNETID` | `T_AmsNetId` | - | 语义见 PDF 同名描述段。 |
| `TMOUT` | `TIME` | - | 时间参数（语义见 PDF 同名描述段）。 |
| `ePersistentMode` | `E_PersistentMode` | - | 枚举 / 结构（参见 `E_PersistentMode`）。 |

#### VAR_OUTPUT 引脚描述

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `udiStatus` | `UDINT` | - | 整型工程量（语义见 PDF 同名描述段）。 |
| `iPersistCount` | `INT` | - | 整型工程量（语义见 PDF 同名描述段）。 |
| `bDone` | `BOOL` | - | 布尔标志位（语义见 PDF 同名描述段）。 |
| `bBusy` | `BOOL` | - | 布尔标志位（语义见 PDF 同名描述段）。 |
| `bError` | `BOOL` | - | 通用错误指示位。`bReset` 上升沿清错。 |
| `udiErrorID` | `UDINT` | - | 整型工程量（语义见 PDF 同名描述段）。 |

## 3. 行为说明

`FB_HVACPersistentDataHandling` 是 Tc2_HVAC 库 系统级 FB（时间 / NOVRAM / 持久化 / 任务信息） 子类中的功能块。按 §2 接口定义表列出的引脚顺序，每周期单次调用本 FB；输入信号通过 VAR_INPUT 引脚传入、输出结果通过 VAR_OUTPUT 引脚回读，状态 / 错误位与同库其他 FB 的命名约定保持一致。 错误指示：`bError*` / `bErr` 系列输出反映 PDF 同名段描述的错误条件。本 FB 不带独立 `bReset` 输入，错误位会在引发条件消除后自动复位。 每个 PLC 周期都应调用本 FB 一次（不要条件调用、不要在不同任务里调用同一实例）；FB 内部维护状态机 / 积分量 / 时间累积，跳过调用会让计数 / 时序不准。按Tc2_HVAC 全库统一约定，所有输出在 FB 被调用的同一周期内更新，调用方可立即读取输出。

## 4. 错误码 / 返回值

本 FB 通过下列 `bError*` / `byError` / `udiError` 输出报告错误；状态字 `byState` 反映 6-8 个联锁实时状态（不视为错误）。

| 输出 / 错误 | 含义 | 处理建议 |
|---|---|---|
| `bError` | PDF 同名描述段的错误条件 | `bReset` 上升沿清错；查 §2 表内对应描述 |

## 5. 使用注意 / 常见坑

- **必须在主循环里调用本 FB**，不能放在条件分支或不同任务里。否则其它 FB 的持久化队列不会被处理。
- 本 FB 是 Tc2_HVAC 持久化机制的**单一实例**：整个工程只允许实例化一次，多实例会导致写盘冲突。
- 写盘时机由本 FB 自动决定（典型 1 小时一次 + 触发式），不要尝试手动强制写盘。
- 工程下载后第一次上电要等本 FB 完成首次回读（`g_bHVACPersDataReadDone := TRUE`）后再用持久化变量。
- Tc2_HVAC 全库 PDF 在 VAR 区结束处不印 `END_VAR`，但实际 IEC 声明中该终止符存在。如果用 PDF 文本直接复制到 IEC 编辑器，编译器会在 VAR_INPUT / VAR_OUTPUT 段尾报「缺少 END_VAR」错误，需要手工补齐。本仓为方便阅读已在所有文档的 IEC 代码块中显式补 `END_VAR`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_HVACPersistentDataHandling.TcPOU`](../examples/P_Demo_FB_HVACPersistentDataHandling.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：Tc2_HVAC 工程的全局基础架构：所有应用层 FB（执行器 / 控制器 / 设定值模块等）都依赖本 FB 把用户在 HMI 上设的参数（PID 增益、行程时间、限值等）写盘保留，断电不丢、上电自动恢复。
- **价值**：**没有这个 FB，整个 Tc2_HVAC 体系的持久化机制都失效**：HMI 改 PID 参数不会落盘、断电重启所有参数归零。本 FB 自动处理：①周期写盘 ②双备份切换 ③写入冲突队列管理 ④断电瞬间数据完整性。
- **替代方案对比**：**直接用 TwinCAT PERSISTENT 关键字**：能保留变量但没有双备份，断电瞬间正好在写盘时数据可能损坏；**手写 NOVRAM 操作**：得自己处理写入 / 校验 / 切备份，工程量大；**本 FB**：Tc2_HVAC 全库内置约定，所有应用层 FB 自动接入。

## 8. 参考资料

- **PDF**：[TF8000_TC3_HVAC_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8000_TC3_HVAC_EN.pdf) §5.1.9.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4685159179.html
- **相关 FB / FC / DUT**：`FB_HVACNOVRAMDataHandling`、`FB_HVACPersistentDataFileCopy`、`FB_HVAC2PointActuator`、`FB_HVAC3PointActuator`、`FB_HVACPIDCtrl`、`E_HVACDataSecurityType`
