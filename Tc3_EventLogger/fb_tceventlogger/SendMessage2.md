# SendMessage2

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcEventLogger` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/10361943563.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_SendMessage2.TcPOU`](../examples/P_Demo_SendMessage2.TcPOU) |

---

## 1. 功能简述

`FB_TcEventLogger.SendMessage2()` 是 `SendMessage()` 的扩展版——多一个 `sJsonAttribute` 参数用于附加 JSON 自定义属性，免去事后调 `SetJsonAttribute`。

适合需要附带工艺上下文（batch id / operator name 等）的一次性通知。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    eventClass : GUID;
    nEventId : UDINT;
    eSeverity : TcEventSeverity;
    ipSourceInfo : I_TcSourceInfo := 0;
    nTimeStamp : ULINT := 0;
    ipArguments : I_TcArguments := 0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `eventClass` | `GUID` | - | 事件类 GUID |
| `nEventId` | `UDINT` | - | 事件 ID |
| `eSeverity` | `TcEventSeverity` | - | 严重级别 |
| `ipSourceInfo` | `I_TcSourceInfo` | `0` | 源信息接口；传 0 用默认 |
| `nTimeStamp` | `ULINT` | `0` | 时间戳：0 = 当前系统时间 |
| `ipArguments` | `I_TcArguments` | `0` | 参数接口；传 0 = 无参数 |


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
| `sJsonAttribute` | `STRING` | 合法 JSON 字符串（STRING(255) 起步） |


## 3. 行为说明

参数 `eventClass` / `nEventId` / `eSeverity` / `ipSourceInfo` / `nTimeStamp` / `ipArguments` 与 `SendMessage()` 一致；多了 VAR_IN_OUT CONSTANT `sJsonAttribute : STRING`——EventLogger 把这段 JSON 一并写入事件，随事件分发到 HMI / 数据库 / 远程客户端。

**典型用法**：MES 集成审计——每次操作员动作发一条 message 同时附带 batch id + recipe + operator，免去事后再调 `SetJsonAttribute` 拼接。免实例发送场景下本方法是"一次到位"的首选——如果走 SendMessage 再 SetJsonAttribute 是不可能的（因为没有 message 实例可供后续修改）。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 消息已发送（含 JSON 属性） | 继续业务 |
| `其他错误` | 事件类未定义 / JSON 非法 ⚠️ PDF 未列详细码 | 校验 JSON 格式 / 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- JSON 必须是合法对象/数组——`'{"k":1}'`；裸 `'hello'` 会被丢弃。
- STRING 默认 80 字节往往不够——声明 STRING(255)+。（工程经验补充）
- 一次性免实例发送 = 无法事后修改——JSON 必须在调用时拼好。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SendMessage2.TcPOU`](../examples/P_Demo_SendMessage2.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

MES 集成审计：每次操作员动作发 message 同时附带 batch id + recipe + operator


一次调用同时完成事件发送 + JSON 上下文附加，省去两步调用


`SendMessage` + 手写 SetJsonAttribute → 不适用免实例场景；本方法专为此场景设计


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.10.12
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/10361943563.html
- **相关**：`FB_TcEventLogger.SendMessage`, `FB_TcEventLogger.SendMessageEx2`
