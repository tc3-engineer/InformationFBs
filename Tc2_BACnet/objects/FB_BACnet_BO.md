# FB_BACnet_BO

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Object · Binary Output` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_BO.TcPOU`](../examples/P_Demo_FB_BACnet_BO.TcPOU) |

---

## 1. 功能简述

代表 BACnet 标准里的「Binary Output」对象类型(BACnet Object_Type = 4 / Binary Output)。语义上是可写、支持命令优先级的二进制输出,典型用于继电器线圈、电磁阀线圈、灯具控制信号等。Present_Value 为 `BACnetBinaryPV`(`inactive` / `active`),16 个优先级槽位机制与 AO 完全相同。本对象类型在 BACnet 标准中独占 priority 6(Minimum_On_Time / Minimum_Off_Time 强制保护),PLC 不能直接写槽 6(PDF §6.2.1)。本库提供基础类 + `_IO` + `_ECAT` + `_5P` + `_IO5P` + `_RAW5P` 共 6 个变体。

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
| 基本信息 | `iParent` / `sObjectName` / `sDescription` / `sDeviceType` | `I_BACnet_View` / `STRING(*)` | DPAD 父节点 + 名称 |
| 文本 | `sInactiveText` / `sActiveText` | `STRING(*)` | Inactive_Text / Active_Text |
| Polarity | `ePolarity` | `E_BACnet_Polarity` | 物理电平到 BACnet 状态的映射方向 |
| Present_Value 命令(基础类 + `_5P`) | `bEnPgm` / `bValPgm` | `BOOL` / `BOOL` | PLC 在 Program 优先级写值;FALSE 释放该槽位 |
| `_5P` 增 | `bEnSfty/bValSfty` / `bEnCrit/bValCrit` / `bEnManLoc/bValManLoc` / `bEnManualOperator/bValManualOperator` | `BOOL` | 5 优先级槽位(LifeSafety / Critical / ManLoc / ManOperator / Pgm) |
| 回退 | `bRelinquishDefault` | `BOOL` | 16 槽位全 NULL 时回退值 |
| 最短保持 | `nMinimumOnTime` / `nMinimumOffTime` | `UDINT` | Minimum_On/Off_Time(秒),BACnet 标准的「避免输出抖动」机制 |
| 报警 | `bAlarmValue` / `bEventDetectionEnable` / `nNotificationClass` / `aEventEnable` / `aEventMessageTextsConfig` / `nTimeDelay` / `nTimeDelayNormal` | 同 BI | Intrinsic Reporting |
| 统计 | `nChangeOfStateCount` / `dtChangeOfStateTime` / `tElapsedActiveTime` | `UDINT` / `DT` / `TIME` | BACnet 标准统计属性 |

### 后缀变体(PDF §6.1.2)

| 变体 | 增/删的成员 | 用途 |
|---|---|---|
| `FB_BACnet_BO` | — | 基础类 |
| `FB_BACnet_BO_IO` | 增 `bRawVal AT %Q* : BOOL` | 写出到 K-bus 端子通道 |
| `FB_BACnet_BO_ECAT` | 增 `bRawVal AT %Q* : BOOL`、`nRawECatState : UINT` | 写出到 EtherCAT 端子通道 |
| `FB_BACnet_BO_5P` | 5 优先级槽位 | 楼控多优先级场景(PDF §9.5) |
| `FB_BACnet_BO_IO5P` | `_5P` + 写 K-bus 端子 | 5 优先级 + 端子直连 |
| `FB_BACnet_BO_RAW5P` | `_5P` + `bRawVal : BOOL` | 5 优先级 + PLC 自算 raw 值 |

## 3. 行为说明

运行机制与 FB_BACnet_AO 相同 — 取 16 优先级槽位中最高的非 NULL 值作为 Present_Value,基础类下 PLC 通过 `bEnPgm := TRUE` + `bValPgm := <0|1>` 占 Program 优先级(默认槽 16);BMS 用 `WriteProperty(Present_Value, ..., priority := 8)` 占 Manual Operator。`bEnPgm := FALSE` 等价写 NULL 释放槽位(PDF §6.2.1 + §6.6.5)。BO 独有的 `nMinimumOnTime` / `nMinimumOffTime` 由 BACnet stack 自动强制:Present_Value 切到 active 后,stack 在槽 6 写入 active 并锁定至少 `nMinimumOnTime` 秒,任何更高优先级写 inactive 都会被忽略;反之亦然。这能避免快速 ON/OFF 抖动损坏继电器或加热器(BACnet 标准 priority 6 是Minimum_On/Off,PLC 不能占用)。`_IO` / `_ECAT` 变体下 Present_Value 自动写到端子通道 `bRawVal`,受 `ePolarity` 控制反向。`_5P` 把 5 个常用优先级搬到 PLC 内 boolean 引脚,适合 BO 既要被 PLC 自动控制又要响应紧急 / 现场手动按钮的场景。

## 4. 错误码 / 返回值

无返回值;运行状态通过 `stStatusFlags.bInAlarm/bFault/bOverridden/bOutOfService` 暴露。⚠️ PDF + InfoSys 未列具体 BACnet error/reject 码。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **命令优先级(commandable 对象)**:`_5P` 系列在 BACnet 16 个优先级中取 5 个槽位(LifeSafety=1 / Critical=5 / ManLocal=7 / ManOperator=8 / Program=15,默认值见 `BACnet_Param`),用 `bEnSfty` / `bEnCrit` / `bEnManLoc` / `bEnPgm` / `bEnManualOperator` 配对的 `f|b|nVal*` 写槽位。`bEn*` 由 TRUE 转 FALSE 等价于写 NULL(释放该槽位)。全部 16 槽位都为 NULL 时取 `fRelinquishDefault` / `bRelinquishDefault` / `nRelinquishDefault`(PDF §6.2.1 / §9.5 / §9.6)。
- **不写槽位也要每周期调用 FB**:库内部用周期调用驱动写值锁存到 BACnet stack;只置 `bEnPgm := TRUE` 而不调用 FB,值不会被发布。
- **不要写 priority 6**:BACnet 标准把槽 6 永久保留给 Minimum_On/Off_Time 算法,BMS 客户端写槽 6 会被 reject。
- **`nMinimumOnTime / nMinimumOffTime` 设错会卡输出**:若设成 3600 秒,继电器一旦动作就锁定 1 小时不能再切,可能让保护逻辑失效。安全期间用 0(关闭)或小值(5..10 秒)。
- **`_RAW5P` 下 PLC 必须每周期写 `bRawVal`**:不写时 stack 把端子保持上次值,可能与 Present_Value 不同步;典型用法是 PLC 把「软件输出」按业务逻辑拼装后送给 `bRawVal`。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_BO.TcPOU`](../examples/P_Demo_FB_BACnet_BO.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_BO
VAR
    // 走廊灯继电器:PLC 自动控制 + BMS 手动覆盖
    fbHallLight : FB_BACnet_BO := (
        sObjectName := 'HallLight_3F_East',
        sInactiveText := 'Off',
        sActiveText := 'On',
        nMinimumOnTime := 10,             // 灯亮至少 10 秒(避免误触发抖动)
        nMinimumOffTime := 10);
    bAutoLightOn : BOOL := FALSE;
    bAutoMode : BOOL := TRUE;             // 在线写 FALSE 释放 Program 优先级
END_VAR

fbHallLight.bEnPgm  := bAutoMode;
fbHallLight.bValPgm := bAutoLightOn;
fbHallLight();
```

## 7. 业务场景与实际价值

- **场景**:走廊灯控,PLC 根据光照传感器 + 人体感应器自动开关,运维人员可在 BMS 上手动覆盖(强制开 / 强制关)。灯具有最短保持 10 秒保护避免继电器抖坏。
- **价值**:Min_On / Min_Off 保护是 BACnet 标准的成熟机制,本 FB 一行配置;手写要管时间戳 + 状态机至少 100 行。
- **替代方案对比**:用 `_5P` 适合「应急按钮 + 自动 + 手动 + 节能调度」四源覆盖;基础类适合 PLC 单源 + BMS 偶尔覆盖。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.1、§6.1.2、§3.2.46/47(Minimum_On/Off_Time)、§6.2.1(优先级 6 保留)、§9.5(_5P)、§9.6(WritePropertyNull)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_BI`(只读二进制输入)、`FB_BACnet_BV` / `FB_BACnet_BV_5P` / `FB_BACnet_BV_Event`(虚拟二进制值)、`FB_BACnet_BO_IO` / `_ECAT` / `_5P` / `_IO5P` / `_RAW5P`(本 FB 后缀变体)
