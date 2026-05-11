# CreateEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcAlarm` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050478347.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TcAlarm_CreateEx.xml`](../examples/P_Demo_FB_TcAlarm_CreateEx.xml) |

---

## 1. 功能简述

`FB_TcAlarm.CreateEx()` 与 `Create()` 功能相同——把 alarm 实例注册到 EventLogger——区别在于事件参数以 **`TcEventEntry` 结构体一次性传入**，而不是分散的 `eventClass`/`nEventId`/`eSeverity`。

适合"事件定义本身已经是结构化数据"的场景：从远程 EventLogger 接收事件、从配置文件加载事件清单、或在多个 FB 之间传递事件定义而不想拆解字段。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stEventEntry : TcEventEntry;
    bWithConfirmation : BOOL;
    ipSourceInfo : I_TcSourceInfo;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stEventEntry` | `TcEventEntry` | 事件入口结构体（含 GUID + EventID + Severity） |
| `bWithConfirmation` | `BOOL` | TRUE = 需要操作员 Confirm 才完整结束生命周期 |
| `ipSourceInfo` | `I_TcSourceInfo` | 源信息接口指针；传 0 用默认（PLC 符号路径） |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

调用同 `Create()`：成功返回 `S_OK` 并把 alarm 加入活动表，重复返回 `ERROR_ALREADY_EXISTS`。唯一区别是事件定义来源——`stEventEntry` 包含 GUID + EventID + Severity 三件套，EventLogger 内部把它们拆开后走和 `Create()` 一样的流程。

**典型用法**：维护一张全局 `aEvents : ARRAY[1..N] OF TcEventEntry`，初始化阶段循环遍历调用 `CreateEx()`批量注册；业务代码只通过下标引用，便于事件清单的版本控制。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | alarm 已成功注册 | 继续后续 Raise/Clear/Confirm |
| `ERROR_ALREADY_EXISTS` | 同事件已注册 | 用 bCreated latch 跳过 |
| `其他错误` | 事件类未定义或 ADS 异常 ⚠️ PDF 未列具体码 | 查 ADS Return Codes |

## 5. 使用注意 / 常见坑

- `stEventEntry` 必须是有效的事件定义——内部 GUID 全 0 / EventID = 0 会导致 HMI 显示空白。
- 批量 CreateEx 时把成功标志放在数组每个元素旁，便于失败重试。（工程经验补充）
- 和 `Create()` 一样要 latch 防止重复注册。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcAlarm_CreateEx.xml`](../examples/P_Demo_FB_TcAlarm_CreateEx.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

从配方文件加载 50 个工艺报警定义后批量注册到 EventLogger


事件清单与代码解耦——改报警定义不用改业务代码，只改配方文件或外部数据库


直接 `Create()` 分字段调用 → 当事件已是结构体时多此一举；`AdsErr_TO_TcEventEntry` → 把 ADS 错误码转 TcEventEntry 再 CreateEx 是常见 ADS 错误集中报警模式


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.6.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050478347.html
- **相关**：`FB_TcAlarm.Create`, `AdsErr_TO_TcEventEntry`, `HRESULTAdsErr_TO_TcEventEntry`
