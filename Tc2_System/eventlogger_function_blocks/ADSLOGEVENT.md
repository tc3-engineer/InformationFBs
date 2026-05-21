# ADSLOGEVENT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `EventLogger function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/45035996304705291.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_ADSLOGEVENT.xml`](../examples/P_Demo_ADSLOGEVENT.xml) |

---

## 1. 功能简述

ADSLOGEVENT 把事件「来 / 去 / 确认」同步发送给（旧版）TwinCAT EventLogger。用上升沿 `Event` 触发『事件到来』、下降沿触发『事件离开』、`EventQuit` 上升沿触发『事件确认』。**TwinCAT EventLogger vs TwinCAT 3 EventLogger**：本 FB 属于旧 TwinCAT EventLogger，仅在 TwinCAT 3 版本 ≤ 3.1.4024 支持；TwinCAT >= 3.1.4026.0 已不再支持，请改用 `Tc3_EventLogger` 库（如 `FB_TcAlarm`、`FB_TcMessage`）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID             : T_AmsNetId;
    PORT              : T_AmsPort;
    Event             : BOOL;
    EventQuit         : BOOL;
    EventConfigData   : TcEvent;
    EventDataAddress  : PVOID;
    EventDataLength   : UDINT;
    FbCleanup         : BOOL;
    TMOUT             : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 目标设备 AMS Net ID。本机用空串。 |
| `PORT` | `T_AmsPort` | - | ADS 端口号。TwinCAT EventLogger 固定为 `110`。 |
| `Event` | `BOOL` | - | 电平变化触发事件：上升沿 = 事件『到来』，下降沿 = 事件『离开』。 |
| `EventQuit` | `BOOL` | - | 上升沿确认（acknowledge）该事件。 |
| `EventConfigData` | `TcEvent` | - | 事件配置结构体（事件 ID、源 ID、类别、严重度等），类型 `TcEvent`。 |
| `EventDataAddress` | `PVOID` | - | 随事件附带的载荷数据缓冲首地址（可选）。 |
| `EventDataLength` | `UDINT` | - | 载荷数据长度（字节）。 |
| `FbCleanup` | `BOOL` | - | TRUE 时把 FB 内部状态完全重置（清空挂起的事件状态）。 |
| `TMOUT` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时时长。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    EventState : UDINT;
    Err        : BOOL;
    ErrId      : UDINT;
    Quit       : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `EventState` | `UDINT` | 当前事件状态机的状态字（active / acked / reset 等内部编码）。 |
| `Err` | `BOOL` | 上次执行出错。超时 `ErrId = 1861`。 |
| `ErrId` | `UDINT` | ADS 错误码或命令特定错误码；下次新命令启动时清 0。 |
| `Quit` | `BOOL` | TRUE 表示事件已被确认（来自 PLC 端 `EventQuit` 或来自可视化界面的 ack）。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用约束**：必须每周期调用让 ADS 状态机推进。

**消息序列（不需确认）**：`Event` 上升沿 → 事件在 EventLogger 出现并处于 active；`Event` 下降沿 → 事件复位（EventLogger 删除该事件）。

**消息序列（需确认 acknowledgable）**：`Event` 上升沿 → 事件出现 active；事件失效有两种路径：(1) `Event` 下降沿但事件复位前 PLC 端已经 `EventQuit` 上升沿（或可视化界面 ack）—— 事件直接撤；(2) `EventQuit` 上升沿到来在 `Event` 下降沿之前 —— 事件在被确认后于下次 `Event` 下降沿真正撤。如果在 active 期间 `Event` 又出现一次（先复位再激活），称为 'signal'，是一次新告警请求。

**陷阱**：必须周期调用让 ADS 完成；`FbCleanup` 在系统刚启动时拉一下可清掉残留事件状态；旧版库已不在 >= 3.1.4026.0 工作，请优先用 `Tc3_EventLogger`。

## 4. 错误码 / 返回值

`ErrId` 是 ADS 错误码或命令特定错误码。0 = 成功；1861 = 调用超时；其他常见 ADS 错误码见『ADS Return Codes』⚠️ 待人工确认。

## 5. 使用注意 / 常见坑

- **TwinCAT EventLogger vs TwinCAT 3 EventLogger**：本 FB 属于旧 TwinCAT EventLogger，仅在 TwinCAT 3 版本 ≤ 3.1.4024 支持；TwinCAT >= 3.1.4026.0 已不再支持，请改用 `Tc3_EventLogger` 库（如 `FB_TcAlarm`、`FB_TcMessage`）。
- 周期调用必须保证，不可只在 `Event` 上升沿那一帧调一次。
- 系统启动时建议先把 `FbCleanup := TRUE` 拉一下清残留态再开始正常使用。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ADSLOGEVENT.xml`](../examples/P_Demo_ADSLOGEVENT.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：旧 TwinCAT 3.1.4024 项目维护——温度报警出现时通过 ADSLOGEVENT 推到 TwinCAT EventLogger，让 HMI 可视化和系统日志同时记录。
- **价值**：替代手写日志文件写入 + HMI 报警表更新；EventLogger 自带可视化集成。
- **替代方案对比**：新项目（TwinCAT >= 3.1.4026.0）必须用 `Tc3_EventLogger` 库的 `FB_TcAlarm`；本 FB 仅维护老项目。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.4.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/45035996304705291.html
- **相关 FB / FC**：`ADSCLEAREVENTS`（批量清事件）、`FB_SimpleAdsLogEvent`（简化版本）、Tc3_EventLogger 库
