# F_GetEventClassName

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `FUNCTION` |
| Category | `Function` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/4278877579.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetEventClassName.TcPOU`](../examples/P_Demo_F_GetEventClassName.TcPOU) |

---

## 1. 功能简述

`F_GetEventClassName` 是函数形式的便捷调用——把「为某事件触发 EventClass 名称异步查询」封装为一个 `FUNCTION`。内部把 fbResult 配置好后返回。

等价于直接调 `FB_TcEventBase.RequestEventClassName()`，区别是函数形式更适合一次性调用。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nLangId : DINT;
    fbEventBase : REFERENCE TO FB_TcEventBase;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nLangId` | `DINT` | 目标 LangId（Windows LCID） |
| `fbEventBase` | `REFERENCE TO FB_TcEventBase` | 事件实例引用（继承自 FB_TcEventBase 的具体 alarm/message） |


### VAR_OUTPUT

无。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    fbResult : FB_AsyncStrResult;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `fbResult` | `FB_AsyncStrResult` | 用于承载异步结果的实例 |


## 3. 行为说明

本函数发起异步请求并立即返回 HRESULT：S_OK 表示请求已提交（不代表已完成）。调用方持有 `fbResult : FB_AsyncStrResult` 实例，之后周期检查 `fbResult.bBusy`，完成后 `fbResult.GetString` 取本地化类名。

**与 FB 形式的区别**：FB 形式（FB_RequestEventClassName）适合复用同一查询模板；本函数形式适合临时一次性调用，代码简洁。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 请求已成功提交 | 周期检查 fbResult.bBusy |
| `其他错误` | 事件未注册 / 内部异常 ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- **异步**：发起 Request 后必须周期检查 `bBusy` 直到 FALSE，再读结果——不能立即用。
- 失败要检查 `bError` 与 `hrErrorCode`——`bBusy = FALSE` 不等于成功。
- 发起多次 Request 之间要 `Clear()` 清理上次结果，否则可能读到旧数据。（工程经验补充）
- LangId 必须是 Windows LCID（如 1033=英文、2052=简体中文、1031=德文）；事件类未配置对应语言会回退默认。
- STRING 输出缓冲必须足够长（建议 STRING(255)+），否则文本被截断。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetEventClassName.TcPOU`](../examples/P_Demo_F_GetEventClassName.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

HMI 一次性查某 alarm 的 EventClass 名（用完即丢，不复用模板）


函数式接口比 FB 形式更简洁


`FB_RequestEventClassName` FB 形式 → 适合复用；本函数适合一次性


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.1.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/4278877579.html
- **相关**：`FB_TcEventBase.RequestEventClassName`, `FB_RequestEventClassName`, `FB_AsyncStrResult`, `F_GetEventText`
