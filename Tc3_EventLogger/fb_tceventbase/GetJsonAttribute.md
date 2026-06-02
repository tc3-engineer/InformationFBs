# GetJsonAttribute

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcEventBase` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5007475723.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_GetJsonAttribute.TcPOU`](../examples/P_Demo_GetJsonAttribute.TcPOU) |

---

## 1. 功能简述

`FB_TcEventBase.GetJsonAttribute()` 读取当前事件实例上之前用 `SetJsonAttribute()` 写入的 JSON 属性。

返回的字符串是完整 JSON——调用方负责自己解析。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sJsonAttribute : REFERENCE TO STRING;
    nJsonAttribute : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sJsonAttribute` | `REFERENCE TO STRING` | 输出 JSON 字符串的缓冲（调用方声明足够长度） |
| `nJsonAttribute` | `UDINT` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

方法的 `sJsonAttribute` 是 VAR_IN_OUT 形式作为**输出缓冲**：方法把当前事件实例上的 JSON 内容写入这个 STRING 变量。调用方负责声明足够长度的 STRING——默认 80 字节往往不够装下完整 JSON，建议 `STRING(255)` 或 `STRING(1024)`。

**典型用法**：listener（FB_ListenerBase2）的 OnAlarmRaised / OnMessageSent 回调里用本方法读出事件附带的 JSON，解析后转交 MES / ERP 系统做结构化审计或工艺追溯。若事件没设过 JSON 属性，返回的字符串通常为空，建议读取后用 `LEN(sJson) > 0` 主动判空。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 成功取出 JSON | 解析使用 |
| `其他错误` | 无 JSON / 缓冲区太小 ⚠️ PDF 未列详细码 | 确认 SetJsonAttribute 是否已写过 / 加大 STRING 容量 |

## 5. 使用注意 / 常见坑

- 缓冲不够大会被截断——分析时可能 JSON 不完整。
- 没设过 JSON 属性时返回内容未定义——通常是空串，建议主动判断 `LEN(sJson) > 0`。（工程经验补充）
- VAR_IN_OUT CONSTANT：调用方传入的字符串变量会被方法写入，不要传字符串字面量。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_GetJsonAttribute.TcPOU`](../examples/P_Demo_GetJsonAttribute.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

listener 收到 alarm 后读取附带的 batch id 上报 MES


一次调用拿到完整 JSON，无需自己反序列化标准字段以外的部分


把上下文塞 `FB_TcArguments` → 适合数值参数不适合嵌套；走外部数据库 → 阻塞 PLC 周期


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.9.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5007475723.html
- **相关**：`FB_TcAlarm.SetJsonAttribute`, `FB_TcMessage.SetJsonAttribute`
