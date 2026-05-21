# ADSCLEAREVENTS

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `EventLogger function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31001867.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_ADSCLEAREVENTS.xml`](../examples/P_Demo_ADSCLEAREVENTS.xml) |

---

## 1. 功能简述

ADSCLEAREVENTS 通过 ADS 命令批量清除旧 TwinCAT EventLogger 中的事件。清除模式由 `iMode` 选择，对应枚举 `E_TcEventClearModes`。**TwinCAT EventLogger vs TwinCAT 3 EventLogger**：本 FB 属于旧 TwinCAT EventLogger，仅在 TwinCAT 3 版本 ≤ 3.1.4024 支持；TwinCAT >= 3.1.4026.0 已不再支持，请改用 `Tc3_EventLogger` 库（如 `FB_TcAlarm`、`FB_TcMessage`）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID    : T_AmsNetId;
    bClear   : BOOL;
    iMode    : UDINT;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 目标设备 AMS Net ID。本机空串。 |
| `bClear` | `BOOL` | - | 上升沿触发一次清除。 |
| `iMode` | `UDINT` | - | 清除模式，取值见枚举 `E_TcEventClearModes`（同库定义）。 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时时长。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy  : BOOL;
    bErr   : BOOL;
    iErrId : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中。期间不接受新的 `bClear` 上升沿。 |
| `bErr` | `BOOL` | 上次执行出错。超时 `iErrId = 1861`。 |
| `iErrId` | `UDINT` | ADS 错误码或命令特定错误码；下次新命令启动时清 0。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用约束**：必须每周期调用让 ADS 状态机推进。`bClear` 上升沿启动一次清除：`bBusy := TRUE`，命令发到 EventLogger 服务（端口 110，本 FB 内部固定），收到应答后 `bBusy := FALSE` 并根据应答置 `bErr`/`iErrId`。

**`iMode` 语义**：来自枚举 `E_TcEventClearModes`，典型取值包括「清全部事件」「仅清已确认事件」「仅清非激活事件」等，具体值看 Tc2_System 中该枚举定义。

**典型用法**：维护期把历史日志清空准备新一轮采样；测试脚本每轮清一次让告警计数从零开始。

**陷阱**：清是不可逆的，生产期慎用；本 FB 仍仅适用于旧 EventLogger，TwinCAT >= 3.1.4026 上无效，请改用 Tc3_EventLogger 的等效清理。

## 4. 错误码 / 返回值

`iErrId` 是 ADS 错误码或命令特定错误码。0 = 成功；1861 = 调用超时；其他常见错误码见『ADS Return Codes』⚠️ 待人工确认。

## 5. 使用注意 / 常见坑

- **TwinCAT EventLogger vs TwinCAT 3 EventLogger**：本 FB 属于旧 TwinCAT EventLogger，仅在 TwinCAT 3 版本 ≤ 3.1.4024 支持；TwinCAT >= 3.1.4026.0 已不再支持，请改用 `Tc3_EventLogger` 库（如 `FB_TcAlarm`、`FB_TcMessage`）。
- 清是破坏性操作，建议只在维护接口（HMI 维护页面）触发，不要在常规业务里周期触发。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ADSCLEAREVENTS.xml`](../examples/P_Demo_ADSCLEAREVENTS.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：每天凌晨自动维护任务把昨天的事件归档后调用本 FB 清空 EventLogger，让运维人员只看到今天的新告警。
- **价值**：替代逐条调 ADSWRITE 删事件，一次调用按模式批清；维护流程更简洁。
- **替代方案对比**：旧项目唯一选择；TwinCAT >= 3.1.4026 用 Tc3_EventLogger 的 `Clear()` 方法。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.4.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31001867.html
- **相关 FB / FC**：`ADSLOGEVENT`（推事件）、`E_TcEventClearModes`（清除模式枚举）、`Tc3_EventLogger.FB_TcEventLogger.Clear`
