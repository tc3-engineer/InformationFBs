# FB_PLCDBAutoLog

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_Database` |
| Library Version | `1.14.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Obsolete` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1031/tf6420_tc3_database_server/6184899467.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PLCDBAutoLog.TcPOU`](../examples/P_Demo_FB_PLCDBAutoLog.TcPOU) |

---

## 1. 功能简述

⚠️ **已废弃（obsolete）** —— 早期版本的 AutoLog 控制 FB（PDF §6.1.4.1.2 / §6.1.4.2.2）。提供 `RunOnce` / `Start` / `Status` / `Stop` 四个方法，行为与 `FB_PLCDBAutoLogEvt` 完全一致；差别仅在输出接口名 `ipTcResultEvent : I_TcResultEvent`（旧）vs `ipTcResult : I_TcMessage`（新）。新项目用 `FB_PLCDBAutoLogEvt`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID: T_AmsNetID := '';
    tTimeout: TIME := T#5S;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | `''` | Database Server AMS Net ID。 |
| `tTimeout` | `TIME` | `T#5S` | ADS 超时。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy: BOOL;
    bError: BOOL;
    ipTcResultEvent: Tc3_EventLogger.I_TcResultEvent;
    bBusy_Status: BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | RunOnce / Start / Stop 任一运行中。 |
| `bError` | `BOOL` | 错误置 TRUE。 |
| `ipTcResultEvent` | `Tc3_EventLogger.I_TcResultEvent` | 旧式事件接口。 |
| `bBusy_Status` | `BOOL` | Status 方法专属忙位（独立于 bBusy）。 |

### VAR_IN_OUT

无。

### Method: `RunOnce`

```iecst
METHOD RunOnce : BOOL
VAR_INPUT
    hAutoLogGrpID: UDINT;
    bAll: BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `hAutoLogGrpID` | `UDINT` | 要执行一次的 AutoLog 组 ID。 |
| `bAll` | `BOOL` | TRUE = 所有组各执行一次。 |

### Method: `Start`

`METHOD Start : BOOL` —— 无入参，启动所有 AutoLog 组。

### Method: `Status`

```iecst
METHOD Status : BOOL
VAR_INPUT
    tCheckCycle: TIME;
    pError: POINTER TO BOOL;
    pAutoLogGrpStatus: POINTER TO ARRAY [1..MAX_CONFIGURATIONS] OF ST_AutoLogGrpStatus;
    cbAutoLogGrpStatus: UDINT;
END_VAR
```

参数同 `FB_PLCDBAutoLogEvt.Status`。

### Method: `Stop`

`METHOD Stop : BOOL` —— 无入参，停所有 AutoLog 组。

## 3. 行为说明

与 `FB_PLCDBAutoLogEvt` 完全一致——Server 后台按周期采集 + 批量入库的控制台。`Start` / `Stop` 全局生效；`RunOnce` 单组或全组立即采一次；`Status` 通过 `bBusy_Status` 独立运行不阻塞 RunOnce / Start / Stop。

**与 `Evt` 版差别**：仅错误接口类型 `I_TcResultEvent` vs `I_TcMessage`。两者本质上都通过 `RequestEventText(nLangId, ...)` 取事件文本，能力近似。

**迁移路径**：替换 FB 类型为 `FB_PLCDBAutoLogEvt`，把 `ipTcResultEvent` 字段改为 `ipTcResult`，接口类型从 `I_TcResultEvent` 改为 `I_TcMessage`。其他方法签名 / 参数 / 状态机不变。

**为何保留**：向后二进制兼容老 PLC 工程。

## 4. 错误码 / 返回值

每方法返回 `BOOL`。`bError + ipTcResultEvent` 报实际成败。错误码集合与 Evt 版一致——`hAutoLogGrpID` 不存在、关联 hDBID 连接失败、超时等；典型 ADS 码 `0x6` / `0x745` / `0x712`，Database Server 内部码见 PDF §8.1.1。

## 5. 使用注意 / 常见坑

- **⚠️ 已废弃**：新项目用 `FB_PLCDBAutoLogEvt`。
- **`Start` 全局生效**：单组启用 / 禁用要在配置层做。
- **`Status` 的 `pAutoLogGrpStatus` 数组要 255 槽**：与 Evt 版同。
- **`RunOnce(bAll := TRUE)` 在大量组场景代价高**：每组同时采集 → DB 压力大。
- **行为细节与 Evt 版完全一致**：可直接套用 Evt 版的所有注意事项。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PLCDBAutoLog.TcPOU`](../examples/P_Demo_FB_PLCDBAutoLog.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：老 OEM 项目（2018 年 TF6420 v1.8）用本 FB 控 AutoLog 组。设备出货 5+ 年，更新 TwinCAT 版本但不重新编译 PLC 代码——本 FB 仍能正常工作。
- **价值**：老工程二进制兼容；新项目应迁移到 `FB_PLCDBAutoLogEvt`。
- **替代方案对比**：
  - **`FB_PLCDBAutoLogEvt`**（推荐）：完全等价 + 现代 EventLogger 接口。
  - **本 FB**：仅老工程兼容。

## 8. 参考资料

- **PDF**：[tf6420_tc3_database_server_en.pdf](https://download.beckhoff.com/download/document/automation/twincat3/tf6420_tc3_database_server_en.pdf) §6.1.4.1.2 / §6.1.4.2.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1031/tf6420_tc3_database_server/6184899467.html
- **相关 FB / FC / DUT**：`FB_PLCDBAutoLogEvt`（现代版）、`ST_AutoLogGrpStatus`、`MAX_CONFIGURATIONS`、`I_TcResultEvent` vs `I_TcMessage`
