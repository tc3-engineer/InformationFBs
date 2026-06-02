# FB_RequestEventClassDetails

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/13723757579.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_RequestEventClassDetails.TcPOU`](../examples/P_Demo_FB_RequestEventClassDetails.TcPOU) |

---

## 1. 功能简述

`FB_RequestEventClassDetails` 异步请求一个 EventClass 的「详情」列表（DescriptionText / DescriptionUrl / Comment）。

返回的每条详情通过 `FB_TcDetail` 子 FB 携带 name + text + comment 三字段，用于 HMI 显示帮助/链接/备注。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nIndex : UDINT;
    fbDetail : REFERENCE TO FB_TcDetail;
    eventClass : GUID;
    nLangId : DINT;
    ipRemoteLogger : I_TcRemoteEventLogger;
    eventClass : GUID;
    nLangId : DINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nIndex` | `UDINT` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `fbDetail` | `REFERENCE TO FB_TcDetail` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `eventClass` | `GUID` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `nLangId` | `DINT` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `ipRemoteLogger` | `I_TcRemoteEventLogger` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `eventClass` | `GUID` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `nLangId` | `DINT` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

本 FB 暴露 `Request()` 发起异步请求、`bBusy` / `bError` / `hrErrorCode` 监视状态、`Get()` / `Clear()` 取结果与清理。**典型流程**：调 `Request` 发起 → 每周期查 `bBusy` 直到 FALSE → 若 `bError = FALSE` 调取结果方法 → 用完调 `Clear` 准备下次请求。

**异步执行**：底层走 ADS 通讯（本地或远程），不阻塞 PLC 周期。远程查询请用 `RequestRemote()` 指定目标 AMS Net ID。并发查询需要多个 FB 实例（每个实例同时只能进行一个查询）。

## 4. 错误码 / 返回值

本方法/属性不返回数值（`VOID` 或 getter 直接返回引用）。状态通过 EventLogger 的事件日志间接反映。

## 5. 使用注意 / 常见坑

- **异步**：发起 Request 后必须周期检查 `bBusy` 直到 FALSE，再读结果——不能立即用。
- 失败要检查 `bError` 与 `hrErrorCode`——`bBusy = FALSE` 不等于成功。
- 发起多次 Request 之间要 `Clear()` 清理上次结果，否则可能读到旧数据。（工程经验补充）
- LangId 必须是 Windows LCID（如 1033=英文、2052=简体中文、1031=德文）；事件类未配置对应语言会回退默认。
- STRING 输出缓冲必须足够长（建议 STRING(255)+），否则文本被截断。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_RequestEventClassDetails.TcPOU`](../examples/P_Demo_FB_RequestEventClassDetails.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

HMI 右键报警 → 显示该 EventClass 的描述/链接/备注供操作员参考


非阻塞多语言资源访问；外部修改无需 PLC 重编译


把翻译嵌入 PLC 代码 → 升级翻译要重编译；本异步模式更灵活


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.1.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/13723757579.html
- **相关**：`FB_AsyncStrResult`, `FB_TcEventBase.RequestEventText`
