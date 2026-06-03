# BAComn_EnumDE

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `GVL` |
| Category | `GVLs / Enumerations` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/14592854027.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_BAComn_EnumDE.TcPOU`](../examples/P_Demo_BAComn_EnumDE.TcPOU) |

---

## 1. 功能简述

BA2_Common 库内全部枚举类型的"英文名 / 德文描述 / 短码"对照表 GVL。包含每个 `E_BA_*` 枚举对应的 `ARRAY[First..Last] OF ST_BA_EnumInfo` 字段（如 `aUnits` 给 `E_BA_Unit` 所有 119 项的单位字符串、`aDataType` 给 `E_BA_DataType` 的类型字符串、`aLanguage` 给语言名等）。所有内容随库 GVL 静态初始化为定值（PDF 用 PERSISTENT 注释列出每条目）。HMI / 趋势 / 报警等下游显示模块按枚举值查表即可拿到可读字符串，无需自行维护字符串表。本 GVL 标 `qualified_only`，必须用 `BAComn_EnumDE.<array>[<enum>]` 形式访问。

## 2. 接口定义

本 GVL 是一个 `VAR_GLOBAL` 集合，由 11 个数组字段组成。完整声明在 PDF §4.2.3.1 中给出（含每个数组每个槽位的初始化字面量，共约 645 行 60 KB；逐条引用见配套 .TcPOU 例程的访问示例）。每个数组元素的结构 `ST_BA_EnumInfo` 包含 3 个字符串字段：

| ST\_BA\_EnumInfo 字段 | 类型 | 内容含义 |
|---|---|---|
| `sName` | `STRING` | 英文名，如 `'Degrees Celsius'`、`'Square Meters'`、`'PT100'` 等 |
| `sDescription` | `STRING` | 德文描述，如 `'Temperatur'`、`'Fläche'` 等 |
| `sShortcut` | `STRING` | 短码符号，如 `'℃'`、`'m²'`、`'mA'`、`'°C'` |

本 GVL 提供的 11 个数组字段一览（每个数组以对应枚举的下标范围定义）：

| 数组字段 | 索引枚举 | 用途 |
|---|---|---|
| `aUnits` | `E_BA_Unit` | 测量单位（119 项：温度 / 长度 / 重量 / 电气 / 能量 / 频率 / 压力 / 流量 等） |
| `aDataType` | `E_BA_DataType` | 数据类型（eBool / eInt / eReal / ...） |
| `aDataClass` | `E_BA_DataClass` | 数据分类（BinaryInput / AnalogInput / ...） |
| `aLoggingType` | `E_BA_LoggingType` | 日志类型（Polled / COV / Triggered） |
| `aTrendEntryType` | `E_BA_TrendEntryType` | 趋势条目类型 |
| `aMeasuringElement` | `E_BA_MeasuringElement` | 传感器型号（Pt100 / Ni1000 / NTC 系列 / 等） |
| `aPolarity` | `E_BA_Polarity` | 极性（Normal / Inverted） |
| `aReliability` | `E_BA_Reliability` | 可靠性等级（NoFaultDetected / NoSensor / 等） |
| `aToggleMode` | `E_BA_ToggleMode` | 切换模式（Schalter / Taster — 自锁开关 / 点动按钮） |
| `aPIDMode` | `E_BA_PIDMode` | PID 模式（eP1ID / ePID） |
| `aLanguage` | `E_BA_Language` | 语言（Englisch / Deutsch） |
| `aAction` | `E_BA_Action` | 控制方向（Direkt / Indirekt） |
| `aByteMappingMode` | `E_BA_ByteMappingMode` | 字节映射方式（Binary 1-N / Index Up-Down / 等） |
| `aEventState` | `E_BA_EventState` | 事件状态 |

> 上表为 GVL 内主要数组的索引概览。逐条目（约 200 项字面量）见 PDF §4.2.3.1 完整列表；运行期访问示例见配套 P\_Demo\_BAComn\_EnumDE.TcPOU。

## 3. 行为说明

本 GVL 是静态初始化的全局常量数组集合：每个 `E_BA_*` 枚举（如 `E_BA_Unit`、`E_BA_DataType`、`E_BA_DataClass`、`E_BA_LoggingType`、`E_BA_TrendEntryType`、`E_BA_MeasuringElement`、`E_BA_Polarity`、`E_BA_Reliability`、`E_BA_ToggleMode`、`E_BA_PIDMode`、`E_BA_Language`）对应一个 `a<Enum> : ARRAY[..First..Last..] OF ST_BA_EnumInfo` 数组，下标为枚举值，元素结构包含 `sName`（英文名，如 `'Degrees Celsius'`）、`sDescription`（德文描述，如 `'Temperatur'`）、`sShortcut`（短码符号，如 `'℃'`）。HMI 端读 `BAComn_EnumDE.aUnits[eUnit].sShortcut` 拿到符号显示在测量值后面；趋势记录端读 `sName` 写入数据库的类型字段；多语言切换时 SCADA 端读 `sDescription`（PDF 内容是德文，可在自家工程里拷贝并翻译为中文）。所有字符串都已经在库加载时初始化，运行期只读、不可修改（编译器静态强制）。该 GVL 是 `F_BA_IsUnitValid` 等校验 FC 的查表基础——校验 FC 检查传入枚举值能否在对应数组里找到非空 `sName`。本 GVL 标 `qualified_only`，任何访问都必须写完整 `BAComn_EnumDE.aUnits[E_BA_Unit.eTemperature_DegreesCelsius]` 形式（不能 `aUnits[...]` 简写）。新工程需要新增枚举值（如自定义传感器单位）时，本 GVL 不能扩展——只能通过新建自己的 GVL + 自己的查表 FC 实现，BA 库的 EnumDE 表是封闭的。

## 4. 错误码 / 返回值

本 GVL 是只读全局常量，无运行时错误。仅在以下情况会"间接出错"：

| 现象 | 含义 | 处理建议 |
|---|---|---|
| 访问 `BAComn_EnumDE.aUnits[eVal]` 时 PLC Exception | `eVal` 超出 `E_BA_Unit.First..Last` 范围 | 先用 `F_BA_IsUnitValid(eVal)` 校验 |
| HMI 显示空字符串 | 对应枚举值的 `sShortcut` / `sName` 在 PDF 中本身为 `''` | 检查 PDF 原文该条目是否有内容；空内容时 HMI 应自己用 `sName` 兜底 |

## 5. 使用注意 / 常见坑

- ⚠️ **PDF 文本经过 pypdf 抽取后含轻微行折断**——是 PDF 转 txt 时把长字段折行造成的伪换行；实际库内的字符串完整无换行。要查权威字符串值请打开原始 PDF 而非 txt cache。
- **`qualified_only` 强制限定**：访问必须 `BAComn_EnumDE.aUnits[...]` 完整写，不能 `aUnits[...]` 短写。这是 BA 库的代码规范，避免与其它库的同名 GVL 撞符号。（PDF 明确）
- **`sDescription` 是德文**：BA2_Common 原是德语区楼宇控制库（Beckhoff 德国总部）。中文工程做 SCADA 时应自己拷贝 + 翻译，不要直接把 `BAComn_EnumDE.aUnits[...].sDescription` 显示给中国用户。（工程经验补充）
- **`sShortcut` 是单位符号**：可直接用于 HMI 显示（"℃"、"%"、"mA" 等已可读）。（工程经验补充）
- **新增枚举需扩展时**，建议另起 GVL（如 `MyApp_UnitsExt`），不要试图修改 BA 库的常量——库升级时会被覆盖。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_BAComn_EnumDE.TcPOU`](../examples/P_Demo_BAComn_EnumDE.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：楼宇 SCADA 界面要把 PLC 上传的"测点 = 22.5、单位 = E_BA_Unit.eTemperature_DegreesCelsius"显示成 "22.5 ℃"。如果在 SCADA 端硬编码 119 个单位的字符串映射，维护起来烦；用 PLC 端的 BAComn_EnumDE 查 `sShortcut` 直接得到 "℃"，把字符串和数值一起上传给 SCADA 显示。
- **价值**：① 消除 SCADA 端硬编码 119 项单位字符串的维护负担；② 中文化时只需翻译一次 PDF 内容；③ 校验 FC（`F_BA_IsUnitValid` 等）共享同一份枚举元数据。
- **替代方案对比**：在 HMI 端硬编码各单位字符串（约 119 行 + 多语言时再翻一遍 + 升级库时手动同步更新），与本 GVL 集中管理相比工作量大且易漏。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.2.3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/14592854027.html
- **相关枚举**：`E_BA_Unit`、`E_BA_DataType`、`E_BA_DataClass`、`E_BA_LoggingType`、`E_BA_TrendEntryType`、`E_BA_MeasuringElement`、`E_BA_Polarity`、`E_BA_Reliability`、`E_BA_ToggleMode`、`E_BA_PIDMode`、`E_BA_Language`、`E_BA_Action`、`E_BA_ByteMappingMode`、`E_BA_EventState`
- **相关 FC**：`F_BA_IsUnitValid`、`F_BA_IsDataTypeValid` 等（基于本 GVL 的查表校验函数）
