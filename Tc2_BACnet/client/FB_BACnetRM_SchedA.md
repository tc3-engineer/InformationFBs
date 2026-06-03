# FB_BACnetRM_SchedA

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Client · Remote Schedule Analog` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319405195.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnetRM_SchedA.TcPOU`](../examples/P_Demo_FB_BACnetRM_SchedA.TcPOU) |

---

## 1. 功能简述

代表远端 BACnet 设备中一个「Schedule Analog」对象的引用。BACnet 标准的 Schedule 不带具体数据类型,必须按对端实际类型选择对应的 RM 变体 (SchedA = REAL / SchedB = BOOL / SchedM = UDINT,PDF §7.8 明确)。用于让本机 PLC 引用对端时间表对象 — 读其当前 Present_Value 或当作 Loop 输入。

## 2. 接口定义

> PDF §6.1.1 / §6.1.2 把所有对象 FB 统一用对象类型表 + 后缀规则描述,**未**针对单个 FB 列 `VAR_INPUT` / `VAR_OUTPUT` 区;以下表把 PDF/InfoSys 在 §6.1.1 / §6.1.2 / §9.x 提及的成员按 BACnet 标准属性分类整理。

### VAR_INPUT

```iecst
VAR_INPUT
END_VAR
```

> ⚠️ PDF/InfoSys 均未给出独立 `VAR_INPUT` 区;成员见下表。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
END_VAR
```

> ⚠️ PDF/InfoSys 均未给出独立 `VAR_OUTPUT` 区;运行状态以 FB 成员形式暴露,见下表。

### VAR_IN_OUT

无。

### 关键属性 / 成员(分组)

| 类别 | FB 成员 | 类型 | 含义 |
|---|---|---|---|
| 绑定 | `Client` | `FB_BACnet_Client` | 所属 client |
| 远端对象 | `nObjectInstance` | `UDINT` | 远端 Schedule 实例号 |
| 当前值(只读) | `bPresVal` / `fPresVal` / `nPresVal`(按变体) | 同 SchedB/A/M | Present_Value(stack 周期读) |

## 3. 行为说明

本远端 Schedule 引用 FB 每周期调用一次,stack 按 client 的 tReadCycleTime 周期 ReadProperty 读对端 Schedule 的 Present_Value 并写入对应类型的 PresVal 成员。对端时间表的 aWeek / aException / aCalendar 由对端维护本身,本 FB 只读 Present_Value;如果要修改对端时间表的内容,用 WriteProperty / WritePropertyEx 写对应属性 ID(`PropWeeklySchedule` 等)。PDF §7.8 强调:Schedule 对象在 BACnet 标准里是无具体数据类型的容器,本 RM 变体必须按对端实际类型选对应一个 — 选错(对端是 Analog 类型你用 SchedB 拉)读不到值。

## 4. 错误码 / 返回值

无返回值;`stStatusFlags` 暴露远端状态。⚠️ 未列具体错误码。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **必须知道对端 Schedule 数据类型**:PDF §7.8 说 function block must be selected manually — 用 BACnet Explorer 先看对端 Schedule 的 Weekly_Schedule 数据类型。
- **本 RM 只能读 Present_Value**:改对端时间表需要 FB_BACnetRM_WriteProperty 写 WeeklySchedule / ExceptionSchedule;且对端通常对这些属性有写保护。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnetRM_SchedA.TcPOU`](../examples/P_Demo_FB_BACnetRM_SchedA.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnetRM_SchedA
VAR
    fbClient : FB_BACnet_Client := (nDeviceInstance := 42);
    fbDevice : FB_BACnetRM_Device := (Client := fbClient);
    fbRemoteSched : FB_BACnetRM_SchedA := (Client := fbClient, nObjectInstance := 1);
END_VAR
fbClient();
fbDevice();
fbRemoteSched();
```

## 7. 业务场景与实际价值

- **场景**:把对端设备的 Schedule Analog 引到本机 — 例如对端 BMS 已经配好了「楼宇运行时间表」,本机 PLC 跟随这个时间表做相关动作。
- **价值**:跨设备共享时间表,无需各 PLC 复制一份;改对端表自动跟随。
- **替代方案对比**:本机 PLC 自建 Schedule:多份时间表难同步;远端引用让「时间表唯一来源」。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §7.8(Remote schedule objects 选 SchedA/B/M 规则)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319405195.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_SchedA` / `SchedB` / `SchedM`(本机 Schedule)、`FB_BACnetRM_Device`(必须先建)
