# IsAlarmRaised

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_TcEventLogger` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050814859.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_IsAlarmRaised.TcPOU`](../examples/P_Demo_IsAlarmRaised.TcPOU) |

---

## 1. 功能简述

`FB_TcEventLogger.IsAlarmRaised()` 不取 alarm 引用，直接查询某事件（GUID + EventID + SourceInfo）是否处于 Raised 状态。

**返回 BOOL**——TRUE 表示当前 Raised。适合"只关心状态不操作"的轻量查询。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    eventClass : GUID;
    nEventId : UDINT;
    ipSourceInfo : I_TcSourceInfo := 0;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `eventClass` | `GUID` | - | 事件类 GUID |
| `nEventId` | `UDINT` | - | 事件 ID |
| `ipSourceInfo` | `I_TcSourceInfo` | `0` | 源信息接口；传 0 匹配默认源 |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

本方法直接查询 EventLogger 全局活动 alarm 表，按 GUID + EventID + SourceInfo 三键匹配 alarm 后读取其 Raised 状态并以 BOOL 返回。找不到 alarm 返回 FALSE（不区分"未注册过"与"已 Cleared"两种情况）。

**典型用法**：在工艺联锁逻辑里判断某安全报警是否还在 Raised，决定是否允许设备启动。比 `GetAlarm` 简化——不需要 REFERENCE 输出变量、不需要 SUCCEEDED 判断 HRESULT。调用次数频繁时注意性能开销——每次都走全局表查询，建议在高频循环里把结果缓存到局部 BOOL 变量。

## 4. 错误码 / 返回值

本方法/函数返回 `BOOL`。

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | alarm 处于 Raised 状态 | 联锁逻辑拦截操作 |
| `FALSE` | alarm 不在 Raised 状态或未找到 | 继续业务 |

## 5. 使用注意 / 常见坑

- "找不到"和"已 Cleared"都返回 FALSE——无法区分两者。
- `ipSourceInfo` 必须与 Create 时一致才能匹配。
- 调用次数多会有性能开销（内部查全局表）——别在高频循环里反复调。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_IsAlarmRaised.TcPOU`](../examples/P_Demo_IsAlarmRaised.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

设备启动联锁：检查所有安全报警是否都不在 Raised，是才允许启动按钮生效


一次 BOOL 查询替代手写 alarm 引用持有 + 状态访问


`GetAlarm` + 检查状态 → 多一步；本方法直接拿 BOOL 简洁


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.10.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5050814859.html
- **相关**：`FB_TcEventLogger.IsAlarmRaisedEx`, `FB_TcEventLogger.GetAlarm`
