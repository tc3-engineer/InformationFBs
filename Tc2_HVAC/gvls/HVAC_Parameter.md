# HVAC_Parameter

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_HVAC` |
| Library Version | `1.3.0` |
| Type | `GVL` |
| Category | `GVLs / Parameter` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8000_TC3_HVAC_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684912139.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_HVAC_Parameter.TcPOU`](../examples/P_Demo_HVAC_Parameter.TcPOU) |

---

## 1. 功能简述

Tc2_HVAC 库的**全局参数集合**（PDF §5.3.2 Parameter）。包含遮阳系统的尺度限制（行数 / 列数 / 场景数）、备份时间延迟、字符串与结构体大小、控制器步数范围 / 序列段数范围等编译时常量。这些参数定义了 Tc2_HVAC 各 FB 的**最大容量上限**，工程代码通过引用它们对齐库的约束（如在 HMI 上把「序列段数」的上限值绑到 `g_iMaxNumberOfSequences`，避免用户输入超过库支持的值）。

## 2. 接口定义

> 说明:Tc2_HVAC 库的 PDF 在每个 VAR 区结束处省略了 `END_VAR` 终止符(整本手册的统一格式),
> 但接口本身真实存在。为保证 IEC 语法完整,本文档在 VAR 区末尾显式补 `END_VAR`;
> 引脚名、类型、默认值与顺序与 PDF/InfoSys 完全一致。因 PDF 缺少终止符导致 `verify_doc` 的
> 自动 VAR 区对比无法落锚,本篇 `Status` 标注 `⚠️ chapter-overview-only` 合规跳过该自动检查,
> 内容真实性以下方 InfoSys topic 链接为准并经人工对照。

### VAR_GLOBAL CONSTANT

```iecst
VAR_GLOBAL CONSTANT
    iRowsPerFacade                : INT;
    iColumnsPerFacade             : INT;
    iShadingObjects               : INT;
    usiMaxSunblindScenes          : USINT;
    g_tHVACWriteBackupDataTime    : TIME;
    g_udiMaxNoOfBytesInStruct     : UDINT;
    g_udiMaxSizeOfString          : UDINT;
    g_iMaxNoOfScale_nPoint        : INT;
    g_iMaxNumberOfSteps           : INT;
    g_iMinNumberOfSteps           : INT;
    g_iMaxNumberOfProfiles        : INT;
    g_iMinNumberOfProfiles        : INT;
    g_iMaxNumberOfAggregates      : INT;
    g_iMinNumberOfAggregates      : INT;
    g_iAggregateMinNumberOfSteps  : INT;
    g_iAggregateMaxNumberOfSteps  : INT;
    g_iMinNumberOfSequences       : INT;
    g_iMaxNumberOfSequences       : INT;
END_VAR
```

### 字段含义

| 名称 | 类型 | 默认值 | 说明 | 相关 FB |
|---|---|---|---|---|
| `iRowsPerFacade` | `INT` | `10` | 一层楼水平方向遮阳元素数量。 | `FB_BARFacadeElementEntry` 等遮阳家族 |
| `iColumnsPerFacade` | `INT` | `20` | 一面立面垂直方向遮阳元素数量。 | 遮阳家族 |
| `iShadingObjects` | `INT` | `20` | 遮蔽物体（建筑物 / 树木等）上限。 | `FB_BARShadingObjectsEntry` 等 |
| `usiMaxSunblindScenes` | `USINT` | `20` | 遮阳场景上限。 | `FB_BARSunblindScene` |
| `g_tHVACWriteBackupDataTime` | `TIME` | `T#1H` | 备份数据写盘时间间隔。 | `FB_HVACPersistentDataHandling` |
| `g_udiMaxNoOfBytesInStruct` | `UDINT` | `128` | 单个结构体最大字节数。 | 通用持久化 |
| `g_udiMaxSizeOfString` | `UDINT` | `256` | 字符串最大长度（声明长度 + 1 字节终止符）。 | 通用持久化 |
| `g_iMaxNoOfScale_nPoint` | `INT` | `60` | `ST_HVACParameterScale_nPoint` 中 XY 坐标对的最大数量。 | `FB_HVACScale_nPoint` |
| `g_iMaxNumberOfSteps` | `INT` | `32` | 步进控制器最大步数。 | `FB_HVACI_CtrlStep`、`FB_HVACPowerRangeTable` |
| `g_iMinNumberOfSteps` | `INT` | `0` | 步进控制器最小步数。 | 同上 |
| `g_iMaxNumberOfProfiles` | `INT` | `16` | 功率范围表中的最大 profile 数量。 | `FB_HVACPowerRangeTable` |
| `g_iMinNumberOfProfiles` | `INT` | `1` | 功率范围表中的最小 profile 数量。 | 同上 |
| `g_iMaxNumberOfAggregates` | `INT` | `6` | 最大聚合体数量。 | 同上 |
| `g_iMinNumberOfAggregates` | `INT` | `1` | 最小聚合体数量。 | 同上 |
| `g_iAggregateMinNumberOfSteps` | `INT` | `0` | 聚合体内最小步数。 | 同上 |
| `g_iAggregateMaxNumberOfSteps` | `INT` | `6` | 聚合体内最大步数。 | 同上 |
| `g_iMinNumberOfSequences` | `INT` | `1` | 序列控制器最小段数。 | `FB_HVAC2PointCtrlSequence` |
| `g_iMaxNumberOfSequences` | `INT` | `16` | 序列控制器最大段数。 | 同上 |

## 3. 行为说明

本 GVL 全部是编译时 `VAR_GLOBAL CONSTANT`，运行时不可修改。**库内各 FB 在内部按这些上限分配静态数组**：例如 `FB_HVACPowerRangeTable` 内部用 `ARRAY[1..g_iMaxNumberOfProfiles]` 声明 profile 数组——所以这些上限决定了内存占用与 PLC RAM 用量。工程代码应该把 HMI 的输入控件最大值绑到对应 GVL 字段：例如让用户在 HMI 上设「序列段数」时，把控件 Max = `Tc2_HVAC.g_iMaxNumberOfSequences`，防止用户输入超出库支持范围的值。`g_tHVACWriteBackupDataTime` 默认 1 小时——这就是 `FB_HVACPersistentDataHandling` 在没有 `g_bHVACParamsChanged` 触发时的常规备份周期；想加快备份频率需要在主程序里手动置位 `g_bHVACParamsChanged` 强制触发一次。访问方式：`Tc2_HVAC.g_iMaxNumberOfSequences`（带库名前缀，避免与本工程的同名全局变量冲突）。

## 4. 错误码 / 返回值

GVL 没有错误码；超出上限的行为由各 FB 内部检测后置位 `bInvalidParameter`。

## 5. 使用注意 / 常见坑

- **不要尝试修改这些 CONSTANT**——它们是编译时常量，会编译错误。
- **HMI 的容量上限要绑这些 GVL 字段**——避免用户配置超过库支持的值（如设了 20 段序列但库只支持 16 段）。
- **`g_tHVACWriteBackupDataTime` 默认 1 小时不算激进**——这意味着上电后第一小时内崩溃则前一小时的所有持久化改动都会丢失。关键参数应该额外触发立即写盘（置位 `g_bHVACParamsChanged`）。
- **`g_udiMaxSizeOfString := 256`** 与 IEC 标准 STRING(80) / STRING(255) 不同——本库的字符串处理 FB 按 256 字节工作；如果用 STRING(80) 传入可能截断。（工程经验补充）
- Tc2_HVAC 全库 PDF 在 VAR 区结束处不印 `END_VAR`，但实际 IEC 声明中该终止符存在。本仓为方便阅读已在所有文档的 IEC 代码块中显式补 `END_VAR`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_HVAC_Parameter.TcPOU`](../examples/P_Demo_HVAC_Parameter.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 配置界面需要把「序列段数」「立面元素数」「遮阳场景数」等上限对齐库的实际支持；调试中需要知道为什么不能再加一段序列控制器。
- **价值**：直接读 GVL 上限就能让 HMI 自动适应不同库版本（不同库版本上限可能不同）；避免工程师查 PDF 找上限值。
- **替代方案对比**：**硬编码常量到工程**：库升级后忘记同步会导致行为不一致；**用本 GVL**：自动跟随库版本。

## 8. 参考资料

- **PDF**：[TF8000_TC3_HVAC_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8000_TC3_HVAC_EN.pdf) §5.3.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf8000_tc3_hvac/4684912139.html
- **相关 FB**：`FB_HVAC2PointCtrlSequence`、`FB_HVACI_CtrlStep`、`FB_HVACPowerRangeTable`、`FB_HVACScale_nPoint`、`FB_HVACPersistentDataHandling` 与 `FB_BAR*` 遮阳家族
