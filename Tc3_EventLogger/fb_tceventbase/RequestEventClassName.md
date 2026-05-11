# RequestEventClassName

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcEventBase` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5007675915.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_RequestEventClassName.xml`](../examples/P_Demo_RequestEventClassName.xml) |

---

## 1. 功能简述

`FB_TcEventBase.RequestEventClassName()` 异步请求当前事件类的**名称字符串**（如 "包装机错误"）。

返回 `FB_AsyncStrResult` 实例（一次性句柄），调用方轮询 `IsCompleted()` 后用 `GetResult()` 取字符串。

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
| `nLangId` | `DINT` | 目标语言 ID（Windows LCID，如 1033=英文、2052=简体中文） |
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

EventLogger 事件类名是多语言资源。本方法启动一次异步查询，返回一个 `FB_AsyncStrResult` 实例承载结果。

**典型流程**：调本方法 → 拿到 fbAsync → 每个周期 `fbAsync.IsCompleted()` 判断 → 完成后 `fbAsync.GetResult(sName)` 取字符串 → 用于 HMI 显示或日志。

异步是因为多语言文本资源可能存放在远端（TwinCAT HMI Server / TF6420 数据库），不能阻塞 PLC 周期。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 异步请求已发起 | 轮询 fbAsync 状态 |
| `其他错误` | 事件类未定义 / 内部错误 ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- 不是同步——拿到 fbAsync 后必须轮询 IsCompleted 才能读结果。
- LangId 未在事件类配置过会得到"无翻译"或回退到默认语言。（工程经验补充）
- 同时发起多个请求要每个 fbAsync 独立——共享一个会被相互覆盖。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_RequestEventClassName.xml`](../examples/P_Demo_RequestEventClassName.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

HMI 显示报警时按当前 UI 语言取本地化事件类名


多语言文本异步获取，避免阻塞 PLC 周期


把所有翻译预先嵌入 PLC 代码 → 升级翻译要重编译；本方法走 EventLogger 资源，外部修改不需要 PLC 重编


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.9.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5007675915.html
- **相关**：`FB_TcEventBase.RequestEventText`, `FB_AsyncStrResult`, `FB_RequestEventClassName`
