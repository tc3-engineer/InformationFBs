# FB_TcEventLogger

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_EventLogger` |
| Library Version | `1.6.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function block` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5002818315.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TcEventLogger.TcPOU`](../examples/P_Demo_FB_TcEventLogger.TcPOU) |

---

## 1. 功能简述

`FB_TcEventLogger` 是 TwinCAT 3 EventLogger 体系的**单例式中心组件**，代表整个 PLC 运行时里的 EventLogger 实例本身。所有报警与消息的注册、广播、查询、清除、确认、导出操作最终都通过本 FB 完成。

实际工程里**不需要自己声明实例**——TwinCAT 运行时已自动持有一个全局可用的 EventLogger，PLC 代码通过 `Tc3_EventLogger` 库提供的全局变量 `FB_TcEventLogger` 或工具函数访问。本 FB 的方法集分四类：批量管理报警（ClearAlarms / ConfirmAlarms / GetAlarm / IsAlarmRaised…）、免实例发送消息（SendMessage / SendMessageEx / SendMessage2 / SendMessageEx2）、清除历史事件（ClearLoggedEvents）、导出事件历史（ExportLoggedEvents 为 CSV）。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

FB_TcEventLogger 没有 VAR_INPUT 或 VAR_OUTPUT——它是"对象集合的容器"，所有交互通过方法。

**生命周期**：运行时启动时初始化，PLC 停止时清理。报警注册（来自 `FB_TcAlarm.Create()`）后留在内部活动表，事件按需写入持久化事件日志（默认在 `C:\ProgramData\Beckhoff\TwinCAT3\EventLogger\` 下）。

**批量管理方法**接收一个 `I_TcEventFilter` 过滤器（不传则操作全部）——这让运维代码能针对「某事件类下所有 alarm」、「某 Severity 以上的事件」做集中清除/确认。**免实例消息方法**（SendMessage*）适合一次性通知场景，省去注册 FB_TcMessage 实例的样板代码。

## 4. 错误码 / 返回值

本方法/属性不返回数值（`VOID` 或 getter 直接返回引用）。状态通过 EventLogger 的事件日志间接反映。

## 5. 使用注意 / 常见坑

- EventLogger 是 PLC 运行时的资源——清除日志、批量确认这类操作影响所有订阅者，权限管控应在 HMI 端实施。（工程经验补充）
- `ClearLoggedEvents` 不可逆——一旦执行历史事件被永久删除（除非配合 ExportLoggedEvents 先导出）。
- `GetAlarm` / `IsAlarmRaised` 走的是符号查询不是引用——大量循环里频繁调用会有性能开销。（工程经验补充）
- `ExportLoggedEvents` 是异步——发起后必须轮询 BOOL 返回值。
- `SendMessage*` 系列各版本差别细微：带 2/Ex/Ex2 后缀依次增加 JSON 支持 / TcEventEntry 入口 / 二者组合。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TcEventLogger.TcPOU`](../examples/P_Demo_FB_TcEventLogger.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .xml 文件
```

## 7. 业务场景与实际价值

MES 系统每天 23:00 触发一次「导出今日全部事件到 CSV → 清除已导出事件」的归档流程


一组 ClearLoggedEvents + ExportLoggedEvents + ConfirmAlarms 完成全自动归档，免去自建事件表 + 文件管理 + 状态同步的全部样板代码


自建数据库 + 自定义清理脚本 → 阻塞 PLC 周期、与 EventLogger 状态不同步；靠 HMI 手动导出 → 漏归档风险、人工成本高


## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_EventLogger_EN.pdf) §3.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_eventlogger/5002818315.html
- **相关**：`FB_TcAlarm`, `FB_TcMessage`, `FB_TcEventCsvExportSettings`, `FB_TcClearLoggedEventsSettings`
