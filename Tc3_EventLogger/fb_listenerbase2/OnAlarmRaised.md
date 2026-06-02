# OnAlarmRaised

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `METHOD` |
| Category | `FB_ListenerBase2` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5051489419.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_OnAlarmRaised.TcPOU`](../examples/P_Demo_OnAlarmRaised.TcPOU) |

---

## 1. 功能简述

`FB_ListenerBase2.OnAlarmRaised()` 是 alarm 从 Cleared 转 Raised 时被 EventLogger 调用的回调方法。

子类 OVERRIDE 本方法即可在 alarm 触发瞬间执行业务逻辑——如转发到 MES、记录故障开始时间、触发应急联动等。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    fbEvent : REFERENCE TO FB_TcEvent;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `fbEvent` | `REFERENCE TO FB_TcEvent` | 事件引用（只在回调期间有效，禁止拷贝） |


### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

本方法是事件驱动回调（callback），由 EventLogger 在 alarm 状态从 Cleared 转 Raised 时 调用。调用上下文是 PLC 任务（调用 listener.Execute() 的任务），因此回调里的代码占用 PLC 周期时间。

**实现约定**：用户继承 `FB_ListenerBase2` 后用 METHOD OVERRIDE 重写本方法，在方法体内执行业务逻辑——如更新内部状态、推送到第三方系统、转发到 OPC UA 等。返回 `S_OK` 让 EventLogger 继续后续回调；返回 `<> S_OK` 让 EventLogger **暂停**回调直到下次 Execute，可用作业务侧节流。

**重要**：参数 `fbEvent : REFERENCE TO FB_TcEvent` 只在本回调期间有效，回调返回后引用失效——绝对不要拷贝引用到全局变量或长期持有的结构里。需要保存事件信息请把 GUID / EventID / Severity / 时间戳等字段拷贝出来。

## 4. 错误码 / 返回值

本方法返回 `HRESULT`（32 位有符号整数）。`SUCCEEDED(hr)` 为 TRUE 表示调用成功。

| HRESULT | 含义 | 处理建议 |
|---|---|---|
| `S_OK` | 处理成功 | EventLogger 继续后续回调 |
| `<> S_OK` | 本回调失败 / 业务侧要求节流 | EventLogger 暂停回调到下次 Execute |

## 5. 使用注意 / 常见坑

- `fbEvent` 不能拷贝——回调返回后引用失效。
- 回调里耗时操作拖慢 PLC 周期——重操作必须异步化。（工程经验补充）
- 返回非 S_OK 让事件保留在队列等下次重试——可作节流但不要一直返回非 S_OK。
- 回调里禁止做阻塞 IO（文件 / 网络）——必须发到后台 FB 处理。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_OnAlarmRaised.TcPOU`](../examples/P_Demo_OnAlarmRaised.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

生产监控：alarm Raise 瞬间发邮件通知维护班长 + 推送到 MES 工单系统


事件驱动模型 = 零延迟接收，无需轮询


轮询 EventLogger 日志 → 延迟 + CPU 浪费；本回调是 Beckhoff 推荐方案


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.5.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5051489419.html
- **相关**：`FB_ListenerBase2`, `FB_ListenerBase2.Execute`, `FB_TcEvent`
