# FB_SimpleAdsLogEvent

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `EventLogger function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/54043196325365643.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SimpleAdsLogEvent.xml`](../examples/P_Demo_FB_SimpleAdsLogEvent.xml) |

---

## 1. 功能简述

FB_SimpleAdsLogEvent 是 `ADSLOGEVENT` 的简化版本——只暴露 `SourceId` / `EventId` / `bSetEvent` / `bQuit` 四个引脚就能完成事件出现/消失/确认。不支持运行时改事件参数，因此只适合预先在 EventLogger 配置好的简单事件场景。**TwinCAT EventLogger vs TwinCAT 3 EventLogger**：本 FB 属于旧 TwinCAT EventLogger，仅在 TwinCAT 3 版本 ≤ 3.1.4024 支持；TwinCAT >= 3.1.4026.0 已不再支持，请改用 `Tc3_EventLogger` 库（如 `FB_TcAlarm`、`FB_TcMessage`）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    SourceId   : INT;
    EventId    : INT;
    bSetEvent  : BOOL;
    bQuit      : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `SourceId` | `INT` | - | 事件源 ID。EventLogger 用它定位事件源。 |
| `EventId` | `INT` | - | 事件 ID。EventLogger 用它定位具体事件。 |
| `bSetEvent` | `BOOL` | - | 电平变化触发：上升沿 = 事件『到来』，下降沿 = 事件『离开』。 |
| `bQuit` | `BOOL` | - | 上升沿确认事件。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    ErrId     : UDINT;
    Error     : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ErrId` | `UDINT` | ADS 错误码或命令特定错误码；下次新命令启动时清 0。 |
| `Error` | `BOOL` | 上次执行出错。超时 `ErrId = 1861`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用约束**：必须每周期调用让 ADS 状态机推进。

**消息序列**：与 `ADSLOGEVENT` 相同——`bSetEvent` 上升沿事件 active，下降沿事件复位；`bQuit` 上升沿确认。在 active 期间 `bSetEvent` 再上升沿，称为 'signal'，是新一次告警请求。

**与 ADSLOGEVENT 的差异**：(1) 不能在 PLC 端动态指定事件类别 / 严重度 / 文本（需要预先在 EventLogger 配置好对应 SourceId+EventId）；(2) 不能附带载荷数据；(3) 没有显式 `EventState`、`Quit` 输出。换来的好处是接口干净，业务侧只关心『哪个事件发生了 / 是否确认』。

**典型用法**：固定的几条告警（例如『冷却液位低』『马达过载』），事件文本和颜色已在 EventLogger 编辑器里一次配好，PLC 代码里只需 `fbX(SourceId := 1, EventId := 4711, bSetEvent := bAlarm);`。

## 4. 错误码 / 返回值

`ErrId` 是 ADS 错误码或命令特定错误码。0 = 成功；1861 = 调用超时；其他常见错误码见『ADS Return Codes』⚠️ 待人工确认。

## 5. 使用注意 / 常见坑

- **TwinCAT EventLogger vs TwinCAT 3 EventLogger**：本 FB 属于旧 TwinCAT EventLogger，仅在 TwinCAT 3 版本 ≤ 3.1.4024 支持；TwinCAT >= 3.1.4026.0 已不再支持，请改用 `Tc3_EventLogger` 库（如 `FB_TcAlarm`、`FB_TcMessage`）。
- 需要在 EventLogger 编辑器里把 SourceId+EventId 与事件文本、严重度、是否需要确认提前配好；否则推送的事件没有可视化效果。
- 想动态控制事件属性请用 `ADSLOGEVENT` 而非本 FB。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SimpleAdsLogEvent.xml`](../examples/P_Demo_FB_SimpleAdsLogEvent.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：包装线上几条固定故障（缺料、过载、急停），事件文本一次性在 EventLogger 配好，PLC 程序里几行调用就能把状态推到 HMI 报警表。
- **价值**：替代 ADSLOGEVENT 需要业务侧组 TcEvent 结构体，本 FB 接口干净，业务侧只看『事件 ID + 状态』。
- **替代方案对比**：变动事件参数用 `ADSLOGEVENT`；纯固定事件用本 FB；新项目（TwinCAT >= 3.1.4026.0）改用 Tc3_EventLogger。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.4.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/54043196325365643.html
- **相关 FB / FC**：`ADSLOGEVENT`（功能完整版）、Tc3_EventLogger 库
