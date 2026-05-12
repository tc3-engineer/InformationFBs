# EqualsTo

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcEventBase` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5002755467.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_EqualsTo.xml`](../examples/P_Demo_EqualsTo.xml) |

---

## 1. 功能简述

`FB_TcEventBase.EqualsTo()` 把当前事件实例与另一个 `I_TcEvent` 实例做**完整等值比较**——包括 EventClass GUID、EventID、Severity，以及 `FB_TcArguments`（事件参数列表）的逐项比对。

适用于「两个事件是否同一次具体发生」的判断，例如去重相邻的两条同名报警。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    ipOther : I_TcEventBase;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ipOther` | `I_TcEventBase` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

本方法返回 `BOOL`：TRUE 表示所有字段（包括 Arguments 列表逐项内容）完全一致；FALSE 表示任一字段不同。比较粒度从粗到细共有四个方法可选，分别对应不同业务需求：EqualsToEventClass 仅看事件类 GUID、EqualsToEventEntry 加上 EventID + Severity、EqualsToEventEntryEx 再加上 bWithConfirmation、本方法 EqualsTo 再加上 Arguments 内容，是粒度最严格的等值比较。

**Arguments 比较细节**：按位逐项对比，类型与值都要相同。因此两个事件即便 EventClass、EventID、Severity 都一样，只要 Arguments 列表里有一个参数值不同（比如批次号变化）就会返回 FALSE。用本方法做"重复报警去抖"时要先确认业务上是否真的需要这么细的粒度。

## 4. 错误码 / 返回值

本方法/函数返回 `BOOL`。

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 完全相同（含 Arguments） | 可视为同一次事件 |
| `FALSE` | 至少一字段不同 | 视为不同事件 |

## 5. 使用注意 / 常见坑

- Arguments 内容对比敏感——同一报警在 batch=001 与 batch=002 之间被认为不相等。
- `ipEvent = 0` 时方法返回 FALSE 而不是错误。（工程经验补充）
- 用 `EqualsTo` 做"短时间重复报警去抖" 要小心：Arguments 不同时仍会被认作不同事件。改用 `EqualsToEventEntry` 才能忽略 Arguments。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_EqualsTo.xml`](../examples/P_Demo_EqualsTo.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

去重报警：同一秒内同一故障的 5 条重复报警里只保留第一条进数据库


一次方法调用替代手写 GUID + EventID + Args 逐字段对比


`EqualsToEventEntry` 忽略 Arguments → 适合按定义去重；手写比较 → 代码冗长易错


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.9.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5002755467.html
- **相关**：`FB_TcEventBase.EqualsToEventClass`, `FB_TcEventBase.EqualsToEventEntry`, `FB_TcEventBase.EqualsToEventEntryEx`
