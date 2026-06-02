# IsAlarmRaisedEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcEventLogger` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050828939.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_IsAlarmRaisedEx.TcPOU`](../examples/P_Demo_IsAlarmRaisedEx.TcPOU) |

---

## 1. 功能简述

`FB_TcEventLogger.IsAlarmRaisedEx()` 与 `IsAlarmRaised()` 行为相同——查询 alarm 是否 Raised——区别在事件参数以 **`TcEventEntry` 结构体一次性传入**。

返回 BOOL。

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
| `stEventEntry` | `TcEventEntry` | - | 事件入口（GUID + EventID + Severity） |
| `ipSourceInfo` | `I_TcSourceInfo` | `0` | 源信息接口；传 0 匹配默认源 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

查询过程与 `IsAlarmRaised()` 完全一致：内部按 stEventEntry 三件套（GUID + EventID + Severity）+ ipSourceInfo 匹配活动 alarm 表，返回其 Raised 状态。区别仅在事件参数来源——本方法用结构体一次性传入。

**Severity 参与匹配**：与 `IsAlarmRaised` 相同，Severity 是 stEventEntry 的一部分；同 GUID+EventID 不同 Severity 算不同 alarm 实例。工程实践里要确保查询用的 stEventEntry 与 Create 时的 alarm 完全一致，否则查不到。找不到与已 Cleared 都返回 FALSE，无法区分两者。

## 4. 错误码 / 返回值

本方法/函数返回 `BOOL`。

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | alarm 处于 Raised 状态 | 联锁逻辑拦截 |
| `FALSE` | alarm 不在 Raised 状态或未找到 | 继续业务 |

## 5. 使用注意 / 常见坑

- Severity 参与匹配——别误把 Severity 配错。
- "找不到"与"已 Cleared"都返回 FALSE。
- 高频循环里调用有开销。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IsAlarmRaisedEx.TcPOU`](../examples/P_Demo_IsAlarmRaisedEx.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

结构体形式的联锁判断——事件定义来自远程或配方


结构体接口适合事件清单已经打包的场景


`IsAlarmRaised` 分字段 → 已知 GUID/ID 时更直观；本方法适合结构体已在手的场景


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.10.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050828939.html
- **相关**：`FB_TcEventLogger.IsAlarmRaised`, `FB_TcEventLogger.GetAlarmEx`
