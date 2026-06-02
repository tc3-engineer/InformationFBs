# EqualsToEventClass

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcEventBase` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5007175435.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_EqualsToEventClass.TcPOU`](../examples/P_Demo_EqualsToEventClass.TcPOU) |

---

## 1. 功能简述

`FB_TcEventBase.EqualsToEventClass()` 比较当前事件与给定 EventClass GUID 是否属于同一事件类。

粒度最粗——只看事件类，不看 EventID / Severity / Arguments。适合"是否属于报警类、消息类、调试类"这种分类判断。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    OtherEventClass : GUID;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `OtherEventClass` | `GUID` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

本方法接收 `eventClass : GUID`，返回 `BOOL`：当前实例的 EventClass GUID 与参数完全相同 → TRUE，否则 FALSE。不看 EventID、不看 Severity、不看 Arguments——是四个 EqualsTo 系列里粒度最粗的一个。

**典型用法**：在 listener 回调里快速分流事件类型——比如先用本方法判断「是否安全报警类」，若是再走急停处理流程；否则继续走普通报警流程。也常用在多 PLC 互连场景里「事件是不是来自本 PLC 定义的某个事件类」的快速过滤，避免误处理其他系统的事件。

## 4. 错误码 / 返回值

本方法/函数返回 `BOOL`。

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | EventClass GUID 匹配 | 属于该事件类 |
| `FALSE` | 不匹配 | 不属于该事件类 |

## 5. 使用注意 / 常见坑

- 仅按 GUID 比较，忽略 EventID/Severity——同事件类不同 ID 仍返回 TRUE。
- GUID 误传 16 字节零值会让所有判断都 FALSE。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_EqualsToEventClass.TcPOU`](../examples/P_Demo_EqualsToEventClass.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

listener 回调里按事件类分流（安全报警 / 工艺报警 / 调试事件分别走不同处理流程）


一次 GUID 比较替代结构体多字段 IF


`EqualsToEventEntry` → 同时看 EventID，粒度更细；手写 GUID 比较 → 一行 vs 一行没区别但本方法语义明确


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.9.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5007175435.html
- **相关**：`FB_TcEventBase.EqualsTo`, `FB_TcEventBase.EqualsToEventEntry`
