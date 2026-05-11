# EqualsToEventEntryEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcEventBase` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5007275531.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_EqualsToEventEntryEx.xml`](../examples/P_Demo_EqualsToEventEntryEx.xml) |

---

## 1. 功能简述

`FB_TcEventBase.EqualsToEventEntryEx()` 比较当前事件与给定 `TcEventEntry` 及其**确认要求标志**（bWithConfirmation）是否一致。

粒度介于 `EqualsToEventEntry` 与 `EqualsTo` 之间——比基本三件套多比一项 `bWithConfirmation`，但不比 Arguments。适合"事件定义 + 确认策略"完全一致的判断。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stOther : TcEventEntry;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stOther` | `TcEventEntry` | ⚠️ 待人工确认（PDF/InfoSys Description 列为空或仅英文） |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

接收 `stEventEntry`（含 GUID + EventID + Severity）和 `bWithConfirmation` 共四个字段。全部相同时返回 TRUE，任一字段不同返回 FALSE。Arguments 仍不在比较范围内——需要逐参数比较请用 EqualsTo。

**典型用法**：在批量注册 alarm 前检查是否已存在同「事件 + 确认要求」的 alarm 以避免重复 Create；或在工程升级时对比新旧事件清单中确认策略是否变化，自动迁移 alarm 实例。比 EqualsToEventEntry 多看一个 bWithConfirmation 字段，适合需要严格区分确认策略的场景。

## 4. 错误码 / 返回值

本方法/函数返回 `BOOL`。

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 事件定义 + 确认要求全匹配 | 属于同一条 alarm |
| `FALSE` | 任一字段不同 | 不同 alarm |

## 5. 使用注意 / 常见坑

- 仍不比较 Arguments——若需要逐参数比较用 `EqualsTo`。
- `bWithConfirmation` 误传错值会让本应相等的事件被判为不等。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_EqualsToEventEntryEx.xml`](../examples/P_Demo_EqualsToEventEntryEx.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

批量注册 alarm 前的去重检查


一次比较涵盖事件定义 + 确认策略


`EqualsToEventEntry` → 不看 bWithConfirmation；`EqualsTo` → 还看 Arguments


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.9.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5007275531.html
- **相关**：`FB_TcEventBase.EqualsToEventEntry`, `FB_TcEventBase.EqualsTo`
