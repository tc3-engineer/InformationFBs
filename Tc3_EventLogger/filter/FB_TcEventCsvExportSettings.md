# FB_TcEventCsvExportSettings

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/9956771211.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TcEventCsvExportSettings.xml`](../examples/P_Demo_FB_TcEventCsvExportSettings.xml) |

---

## 1. 功能简述

`FB_TcEventCsvExportSettings` 配置 `FB_TcEventLogger.ExportLoggedEvents()` 的 CSV 导出格式与过滤规则。

继承 `FB_TcEventExportSettings`、实现 `I_TcEventCsvExportSettings`。支持设置：`bWithHeader`（是否含表头）、`nLangId`（导出语言 LCID）、`sDelimiter`（分隔符，默认分号）。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

FB 是配置容器，不直接发起导出。**用法**：实例化 → 通过属性 setter 配置 CSV 选项（`bWithHeader` 是否带表头、`nLangId` 导出语言、`sDelimiter` 字段分隔符）→ 把实例传给 `FB_TcEventLogger.ExportLoggedEvents(ipExportSettings := this)` 让它生效。

**默认值**：`bWithHeader = TRUE`、`nLangId = 1033`（英文）、`sDelimiter = ';'`（分号）。导出的 CSV 列通常包括事件 ID、EventClass GUID、Severity、SourceName、时间戳、本地化事件文本等。中国/欧洲场景常用分号分隔（避免与日期/小数里的逗号冲突）；美国习惯用逗号。继承 FB_TcEventExportSettings 因此也具备父类的过滤能力（按时间/严重级别等）。

## 4. 错误码 / 返回值

本方法/属性不返回数值（`VOID` 或 getter 直接返回引用）。状态通过 EventLogger 的事件日志间接反映。

## 5. 使用注意 / 常见坑

- `nLangId` 决定事件文本的导出语言——中文 LCID 是 2052 不是 0x804。
- `sDelimiter` 选错会让 Excel 打开 CSV 时无法分列——欧洲一般用 `;`，美国 `,`。（工程经验补充）
- CSV 没有数据类型保留——数字会被 Excel 自动判断类型，可能误判（例如长 EventID 变科学计数法）。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcEventCsvExportSettings.xml`](../examples/P_Demo_FB_TcEventCsvExportSettings.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

按当前 UI 语言导出本月事件 CSV 供运维分析


一处配置控制导出格式，灵活适配不同地区/不同分析工具


导出固定 CSV 格式 → 不灵活；本 FB 提供完整可配置


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.3.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/9956771211.html
- **相关**：`FB_TcEventLogger.ExportLoggedEvents`, `FB_TcClearLoggedEventsSettings`
