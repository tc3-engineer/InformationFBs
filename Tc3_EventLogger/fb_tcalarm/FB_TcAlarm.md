# FB_TcAlarm

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5001926923.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TcAlarm.xml`](../examples/P_Demo_FB_TcAlarm.xml) |

---

## 1. 功能简述

`FB_TcAlarm` 是 TwinCAT 3 EventLogger 体系里代表**有状态报警**（alarm）的功能块（FB），继承自 `FB_TcEventBase` 并实现 `I_TcAlarm` 接口。一条报警在生命周期里有Raised（已触发）/ Cleared（已清除）/ Confirmed（已确认）三种状态，本 FB 把这三态封装为 `Raise()` / `Clear()` / `Confirm()` 三个方法。

实际用法：声明一个 `FB_TcAlarm` 实例，先调 `Create()` 把它注册进 EventLogger（指定事件类 GUID、事件 ID、严重级别、是否需要确认），之后在业务里上升沿调 `Raise()`、下降沿调 `Clear()`、操作员点确认时调 `Confirm()`。EventLogger 负责把状态变化广播给所有 `FB_ListenerBase2` 订阅者，并写入事件日志，可被 TwinCAT HMI / ADS 客户端 / TF6420 数据库导出工具读取。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

本 FB 自身没有顶层 VAR_INPUT；交互全部通过方法调用。**典型生命周期**：上电后第一次扫描调一次 `Create()`（向 EventLogger 申请 alarm 槽位）；业务故障逻辑里上升沿调 `Raise()` 触发报警，故障恢复后调 `Clear()` 解除报警；如果 `bWithConfirmation = TRUE`，再等操作员在 HMI 上点确认按钮后调 `Confirm()` 把确认状态置位，整条报警才走完。

状态切换在调用方法时**同步**生效，但 EventLogger 把变化分发给监听器与持久化日志的过程是**异步**的（跨 RT/非 RT 域），HMI 刷新延迟通常在毫秒级。报警实例不在 RETAIN 区，CX 控制器重启后所有状态归零，长期审计必须依赖 EventLogger 自身的持久化日志（事件库文件）。

## 4. 错误码 / 返回值

本方法/属性不返回数值（`VOID` 或 getter 直接返回引用）。状态通过 EventLogger 的事件日志间接反映。

## 5. 使用注意 / 常见坑

- `Create()` 必须只调一次：用 `IF NOT bCreated THEN bCreated := SUCCEEDED(fb.Create(...)); END_IF` 包裹，否则每周期重复 `Create()` 会拿到 `ERROR_ALREADY_EXISTS` 并刷屏日志。
- `bWithConfirmation = TRUE` 时只 Raise + Clear 不够：HMI 仍显示"等待确认"。必须等操作员动作后调 `Confirm()` 才完成生命周期。
- 掉电不保持：实例不是 RETAIN，CX 重启所有 alarm 状态归零。（工程经验补充）
- 同一 FB 实例不要交错触发多个故障——每个故障开独立 `FB_TcAlarm` 实例。（工程经验补充）
- `Release()` 在动态 NEW/__DELETE 用法里必须显式调用；静态实例可以不释放。
- `ipSourceInfo := 0` 即用默认源信息（PLC 实例符号路径），多 PLC 共用一个 EventLogger 时才需要自定义 `FB_TcSourceInfo`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcAlarm.xml`](../examples/P_Demo_FB_TcAlarm.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

**场景**：包装机故障管理。每台机器配 30-50 个潜在故障点（封口温度异常、纸张卡住、气压不足、急停按下…），每个故障对应一个独立的 `FB_TcAlarm` 实例；故障发生时 HMI 红灯闪烁、生产计数暂停、要求操作员处理后按确认键，EventLogger 把全过程持久化以便事后审计。


**价值**：报警的「边沿触发-持续状态-确认归档」是工业最常见的三态模式，手写至少需要 3 个 BOOL + 1 个时间戳 + 1 套 HMI 联动。用本 FB 一句 `Raise()` 完成，且自动集成进 EventLogger 的统一审计/查询/导出，省掉自建报警表。


**替代方案对比**：纯 BOOL + HMI 自建报警表 → 没有审计追溯；`Tc2_System.ADSLOGSTR` → 只写文本日志、没结构化字段；第三方 SCADA 报警包 → 锁品牌、与 PLC 不同步。本 FB 走 Beckhoff 原生 EventLogger，免费、跨 HMI 厂商。


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5001926923.html
- **相关**：`FB_TcMessage`, `FB_TcEventBase`, `FB_TcEventLogger`, `FB_ListenerBase2`
