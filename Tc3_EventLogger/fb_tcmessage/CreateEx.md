# CreateEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcMessage` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050947211.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TcMessage_CreateEx.xml`](../examples/P_Demo_FB_TcMessage_CreateEx.xml) |

---

## 1. 功能简述

`FB_TcMessage.CreateEx()` 与 `Create()` 功能相同，区别在于事件参数以**`TcEventEntry` 结构体一次性传入**而不是分散字段。

适用：从远程 EventLogger 接收事件清单后批量注册、从配方文件加载消息定义、或在多个 FB 之间传递事件定义而不想拆解字段。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stEventEntry : TcEventEntry;
    ipSourceInfo : I_TcSourceInfo := 0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stEventEntry` | `TcEventEntry` | - | 事件入口结构体（含 GUID + EventID + Severity） |
| `ipSourceInfo` | `I_TcSourceInfo` | `0` | 源信息接口指针；传 0 用默认 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

调用过程与 `Create()` 完全一致：成功返回 `S_OK`，重复注册返回 `ERROR_ALREADY_EXISTS`。区别只在事件来源——`stEventEntry` 已经把 GUID、EventID、Severity 三件套打包在一个结构体里，EventLogger 内部拆开后走和分散字段一样的注册流程。

**典型用法**：在 PLC 工程里维护一张 `aEvents : ARRAY[1..N] OF TcEventEntry` 的全局事件清单，初始化阶段用 FOR 循环遍历这张表调用 `CreateEx()` 批量注册，业务代码后续都通过下标引用事件，便于事件清单的版本控制（清单可以从配方文件或外部数据库加载，事件类型变更不动业务代码）。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | message 已成功注册 | 继续后续 Send() |
| `ERROR_ALREADY_EXISTS` | 同事件已注册 | 用 latch 跳过 |
| `其他错误` | ⚠️ PDF 未列详细码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- `stEventEntry` 必须是有效的事件定义——内部 GUID 全 0 / EventID = 0 会导致 HMI 显示空白。
- 批量 CreateEx 时把成功标志放在数组每个元素旁，便于失败重试。（工程经验补充）
- 和 `Create()` 一样要 latch 防止重复注册。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcMessage_CreateEx.xml`](../examples/P_Demo_FB_TcMessage_CreateEx.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

从配方文件加载 30 个消息定义后批量注册


事件清单与代码解耦——改消息定义不用改业务代码


`Create()` 分字段 → 当事件已是结构体时多此一举；`AdsErr_TO_TcEventEntry` → 把 ADS 错误码转 TcEventEntry 后 CreateEx，统一上报 ADS 错误


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.11.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050947211.html
- **相关**：`FB_TcMessage.Create`, `AdsErr_TO_TcEventEntry`
