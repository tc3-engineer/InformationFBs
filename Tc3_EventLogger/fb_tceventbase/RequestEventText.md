# RequestEventText

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcEventBase` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5007725963.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_RequestEventText.xml`](../examples/P_Demo_RequestEventText.xml) |

---

## 1. 功能简述

`FB_TcEventBase.RequestEventText()` 异步请求当前事件的**事件文本**——即 HMI 上显示的"温度过高 (95°C)" 这种带参数的本地化文本。

返回 `FB_AsyncStrResult` 实例承载结果。文本里的占位符（`{0}` / `{1}`…）由 EventLogger 用 `FB_TcArguments` 里的参数填充。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nLangId : DINT;
    sResult : REFERENCE TO STRING;
    nResultSize : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nLangId` | `DINT` | 目标语言 ID（Windows LCID） |
| `sResult` | `REFERENCE TO STRING` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `nResultSize` | `UDINT` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |


### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bError : BOOL;
    hrErrorCode : HRESULT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bError` | `BOOL` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `hrErrorCode` | `HRESULT` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |


### VAR_IN_OUT

无。

## 3. 行为说明

调用启动一次异步查询：把事件 GUID + EventID + Arguments 发到 EventLogger，EventLogger 按 LangId 查文本模板、用 Arguments 填占位符、把结果写回 `fbAsyncResult`。

**典型流程**：调本方法 → 拿到 fbAsync → 轮询 `IsCompleted()` → 完成后 `GetResult()` 取字符串。

这是 EventLogger 多语言能力的核心——同一事件在不同语言下显示不同文本，参数填充由 EventLogger 完成，PLC 端只管发事件 + 取文本，不需要管字符串拼接。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 异步请求已发起 | 轮询 fbAsync 状态 |
| `其他错误` | 事件未定义 / 文本资源缺失 ⚠️ PDF 未列详细码 | 查 ADS Return Codes / 检查 EventClass 配置 |

## 5. 使用注意 / 常见坑

- Arguments 必须先填好——否则文本占位符会显示原始 `{0}` 等。
- 不是同步：拿到 fbAsync 后必须 IsCompleted 才能读结果。
- 文本长度超过 STRING(80) 默认会被截断，建议 `STRING(255)`+。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_RequestEventText.xml`](../examples/P_Demo_RequestEventText.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

HMI 收到报警事件后异步取本地化文本显示


多语言 + 参数填充全部由 EventLogger 完成，PLC 不参与字符串拼接


PLC 端手写 CONCAT 拼字符串 → 多语言切换要重编译；走 EventLogger 多语言资源外部修改即可


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.9.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5007725963.html
- **相关**：`FB_TcEventBase.RequestEventClassName`, `FB_AsyncStrResult`, `FB_RequestEventText`
