# FB_TcCauseRemedy

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/13723759883.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TcCauseRemedy.TcPOU`](../examples/P_Demo_FB_TcCauseRemedy.TcPOU) |

---

## 1. 功能简述

`FB_TcCauseRemedy` 用于显示一个事件的 cause/remedy 项。通常配合 `FB_RequestCauseRemedy.Get()` 使用——Get 把指定下标的 cause/remedy 写入本 FB 实例，调用方再通过 `GetCause` / `GetRemedy` / `GetId` 读字段。

工程上是"承载子项"的视图 FB，不直接发起请求。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sResult : REFERENCE TO STRING;
    nResult : UDINT;
    sResult : REFERENCE TO STRING;
    nResult : UDINT;
    sResult : REFERENCE TO STRING;
    nResult : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sResult` | `REFERENCE TO STRING` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `nResult` | `UDINT` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `sResult` | `REFERENCE TO STRING` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `nResult` | `UDINT` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `sResult` | `REFERENCE TO STRING` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |
| `nResult` | `UDINT` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

本 FB 由 `FB_RequestCauseRemedy.Get(nIndex := i, fbResult := myFbCauseRemedy)` 填充——调用 Get 后内部携带第 i 项的 cause + remedy + id 三个字段。之后业务代码分别调 `GetCause(sResult)`、`GetRemedy(sResult)`、`GetId(nResult)` 把字段值读到调用方变量。

**生命周期**：Get 填充 → 读字段 → 下次 Get 前可调 `Release` 清空内部缓存。实例可以反复复用，避免反复 NEW/DELETE。需要循环遍历多项 cause/remedy 时复用同一 FB_TcCauseRemedy 实例即可。字段读方法（GetCause/GetRemedy/GetId）通过 VAR_IN_OUT 输出，调用方负责声明足够长的 STRING 缓冲。

## 4. 错误码 / 返回值

本方法/属性不返回数值（`VOID` 或 getter 直接返回引用）。状态通过 EventLogger 的事件日志间接反映。

## 5. 使用注意 / 常见坑

- 本 FB 自己不发起请求——必须配合 FB_RequestCauseRemedy 使用。
- Get 之前的字段值不定义——不要直接读 GetCause/GetRemedy。（工程经验补充）
- 不要在多个 Request 实例之间共享同一 FB_TcCauseRemedy——可能被覆盖。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcCauseRemedy.TcPOU`](../examples/P_Demo_FB_TcCauseRemedy.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

HMI 显示报警 cause/remedy 时通过 Get 拿到承载 FB，再分别读字段


字段化访问替代字符串拼接


把 cause/remedy 拼成一段字符串返回 → 字段分不开；本 FB 提供结构化访问


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.1.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/13723759883.html
- **相关**：`FB_RequestCauseRemedy`
