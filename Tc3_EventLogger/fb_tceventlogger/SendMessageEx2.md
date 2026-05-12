# SendMessageEx2

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcEventLogger` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/10361958283.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_SendMessageEx2.xml`](../examples/P_Demo_SendMessageEx2.xml) |

---

## 1. 功能简述

`FB_TcEventLogger.SendMessageEx2()` 是 `SendMessageEx()` 的扩展版——事件参数以结构体传入，同时支持附加 JSON 自定义属性。

适用：结构化事件清单 + 需要附带工艺上下文的免实例发送。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stEventEntry : TcEventEntry;
    ipSourceInfo : I_TcSourceInfo := 0;
    nTimeStamp : ULINT := 0;
    ipArguments : I_TcArguments := 0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stEventEntry` | `TcEventEntry` | - | 事件入口（GUID + EventID + Severity） |
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
| `sJsonAttribute` | `STRING` | 合法 JSON 字符串 |


## 3. 行为说明

本方法组合了 `SendMessageEx`（结构体入口）+ `SendMessage2`（JSON 属性）两个版本的语义，是 SendMessage 系列中参数最全的版本。`stEventEntry` 三件套 + 可选 `ipSourceInfo` / `nTimeStamp` / `ipArguments` + VAR_IN_OUT CONSTANT `sJsonAttribute : STRING` 一次调用完成完整事件发送（含元数据 + 参数 + JSON）。

**典型用法**：MES 集成场景里事件清单来自外部表（关系数据库或配方文件），每条事件同时携带 batch / operator / recipe 等 JSON 上下文——本方法一次到位，免去拆分调用。命名实参写法更易读。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 消息已发送（含结构体 + JSON） | 继续业务 |
| `其他错误` | ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- 结合了 SendMessage2 / SendMessageEx 两边的注意点——见各自条目。
- 一次调用 6+ 个参数，命名实参写法更易读。（工程经验补充）
- JSON 必须合法、STRING 容量要够。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SendMessageEx2.xml`](../examples/P_Demo_SendMessageEx2.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

MES 集成的结构化事件 + JSON 上下文一次性发送


单方法调用覆盖最完整的事件发送场景


`SendMessageEx` → 无 JSON；`SendMessage2` → 无结构体；本方法是完整组合版


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.10.14
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/10361958283.html
- **相关**：`FB_TcEventLogger.SendMessageEx`, `FB_TcEventLogger.SendMessage2`
