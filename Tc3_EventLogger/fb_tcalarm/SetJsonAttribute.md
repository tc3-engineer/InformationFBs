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

`FB_TcAlarm.SetJsonAttribute()` 给 alarm 实例追加一段 JSON 形式的自定义属性，在事件分发到 HMI / 数据库 / 远程客户端时与标准字段（EventClass/EventID/Severity/SourceInfo/Arguments）一并传递。

整段属性以 JSON 字符串形式传入，可携带任意键值结构，例如 `'{"batch":"B-2026-0511-001","operator":"WangWu","recipe":"R03"}'`。便于 MES/ERP 系统在事后审计时做结构化分析。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sJsonAttribute : STRING;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sJsonAttribute` | `STRING` | 合法 JSON 字符串（建议用 STRING(255) 或更长以容纳完整 JSON 对象） |


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
| `sJsonAttribute` | `STRING` | 合法 JSON 字符串（建议用 STRING(255) 或更长以容纳完整 JSON 对象） |


## 3. 行为说明

方法签名只有一个 `VAR_IN_OUT CONSTANT sJsonAttribute : STRING`。EventLogger 把整段 JSON 存入 alarm 的扩展属性，下一次状态变化（Raise/Clear/Confirm）时随事件一起广播。

**调用时机**：在 Raise 之前调用，确保事件分发时属性已附上。多次调用会**覆盖**上一次的 JSON 内容。字符串必须是合法 JSON，否则 EventLogger 端解析失败、HMI 看不到自定义字段。

本方法在 TwinCAT 3 EventLogger 4026+ 版本完整可用，老版本可能行为受限。VAR_IN_OUT CONSTANT 形式：调用方传入字符串时 PLC 不复制（节省栈），方法内部不能修改它。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | JSON 属性已成功写入 | 继续业务 |
| `其他错误` | ⚠️ PDF 未列详细码，可能因 JSON 非法、长度超限等 | 校验 JSON 格式 / 缩短内容 / 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- 传入字符串必须是**合法 JSON 整体**——`'{"a":1}'` 行；裸 `'hello'` 不是合法 JSON 对象/数组会被丢弃。
- STRING 默认长度 80 字节往往不够，注意声明 `STRING(255)` 或 `STRING(1024)`。（工程经验补充）
- 调用会覆盖上次内容——要追加键得自己在 PLC 端拼接完整 JSON 再传入。（工程经验补充）
- HMI 端要主动消费 JSON——TwinCAT HMI 默认只显示标准字段，需要绑定 JSON 到自定义控件。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcAlarm_SetJsonAttribute.xml`](../examples/P_Demo_FB_TcAlarm_SetJsonAttribute.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

批次追溯。每个 alarm 附带 batch id + operator name + recipe version，事故事后能精确定位"某批某操作员在某配方下出的问题"


把工艺上下文直接挂在 alarm 上，省掉手写"alarm + 上下文表"的 JOIN 查询；MES 拉数据时一个 EventEntry 就够


把上下文塞进 `FB_TcArguments` → 适合标准类型参数（int/real/bool/string），JSON 属性更适合**嵌套/动态**结构；走外部数据库 INSERT → 阻塞 PLC 周期、且与 alarm 时间戳不严格同步


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.6.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5006660363.html
- **相关**：`FB_TcAlarm.Create`, `FB_TcMessage.SetJsonAttribute`, `FB_TcEventBase.GetJsonAttribute`
