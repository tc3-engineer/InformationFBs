# SetJsonAttribute

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcAlarm` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5006660363.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TcAlarm_SetJsonAttribute.xml`](../examples/P_Demo_FB_TcAlarm_SetJsonAttribute.xml) |

---

## 1. 功能简述

`FB_TcAlarm.SetJsonAttribute()` 给 alarm 实例追加一个 JSON 形式的自定义属性，在事件分发到 HMI / 数据库 / 远程客户端时一起传递。

用途：在标准 alarm 字段（EventClass/EventID/Severity/SourceInfo/Arguments）之外携带工程语义信息，例如 `{"batch":"B-2026-0511-001","operator":"WangWu","recipe":"R03"}`，便于 MES/ERP 系统结构化分析。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sJsonAttribute : STRING;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sJsonAttribute` | `STRING` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |


### VAR_OUTPUT

无。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    sJsonAttribute : STRING;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sJsonAttribute` | `STRING` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |


## 3. 行为说明

方法接收 `sName`（属性名）和 `sValue`（属性值，JSON 字符串）。EventLogger 把它存到 alarm 的扩展属性表里，再下一次状态变化（Raise/Clear/Confirm）时随事件一起广播。

**调用时机**：通常在 Raise 之前调用，确保事件分发时属性已附上。多次调同名属性会覆盖。属性值必须是合法 JSON——字符串要双引号、数字直接写、bool 用 true/false。手写时常见错误是漏掉外层引号或者把 Tab/换行不转义。

本方法是 TwinCAT 3 EventLogger 4026+ 版本才支持，老版本调用会被静默忽略或返回错误。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 属性已添加/更新 | 继续业务 |
| `E_INVALIDARG` | 属性名或值无效（如空字符串、非法 JSON） | 检查 JSON 格式 |
| `其他错误` | ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- `sValue` 必须是 JSON 合法值：`'"hello"'`（字符串带引号）/ `'42'`（数字）/ `'true'`。漏外层引号是最常见错误。
- TwinCAT 老版本（4022 及以下）此方法可能无效，迁移工程时确认目标版本。（工程经验补充）
- 属性名同名会覆盖；删除属性需要传空 JSON `null`。（工程经验补充）
- HMI 端要主动消费 JSON 属性——TwinCAT HMI 默认只显示标准字段，需要绑定 JSON 属性到自定义控件。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcAlarm_SetJsonAttribute.xml`](../examples/P_Demo_FB_TcAlarm_SetJsonAttribute.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

批次追溯。每个 alarm 附带 batch id + operator name + recipe version，事故事后能精确定位"某批某操作员在某配方下出的问题"


把工艺上下文直接附在 alarm 上，省掉手写"alarm + 上下文表"的 JOIN 查询；MES 拉数据时一个 EventEntry 就够


把上下文塞进 `FB_TcArguments` → 适合数值型参数（int/real/bool）不适合复杂 JSON；走外部数据库 INSERT → 阻塞 PLC 周期、且与 alarm 时间戳不严格同步


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.6.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5006660363.html
- **相关**：`FB_TcAlarm.Create`, `FB_TcMessage.SetJsonAttribute`, `FB_TcEventBase.GetJsonAttribute`
