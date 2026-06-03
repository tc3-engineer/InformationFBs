# FB_BACnet_MV

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Object · Multistate Value` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_MV.TcPOU`](../examples/P_Demo_FB_BACnet_MV.TcPOU) |

---

## 1. 功能简述

代表 BACnet 标准里的「Multistate Value」对象类型(BACnet Object_Type = 19 / Multistate Value)。语义上是虚拟多态值,典型用于「程序参数选项」、「运行场景」(`Day`/`Night`/`Holiday`/`Eco`)等非物理输出但需要 BMS 配置 / 订阅的多态枚举。本库提供基础类 + `_5P`(5 优先级)两个变体。PDF §9.5 末尾的`fbMV5P.bEnCrit := TRUE; fbMV5P.nValCrit := 3;` 是典型片段。

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
| 基本信息 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |
| 状态枚举 | `aStateText` | `ARRAY[1..*] OF STRING(*)` | State_Text |
| Present_Value 命令(基础类 + `_5P`) | `bEnPgm` / `nValPgm` | `BOOL` / `UDINT` | PLC 在 Program 优先级写值 |
| `_5P` 增 | `bEnSfty/nValSfty` 等 5 优先级 | `BOOL` / `UDINT` | 5 优先级槽位 |
| 回退 | `nRelinquishDefault` | `UDINT` | 16 槽位全 NULL 时回退值 |
| 报警 | `aAlarmValues` / `aFaultValues` / `bEventDetectionEnable` / `nNotificationClass` / `aEventEnable` / `aEventMessageTextsConfig` | 同 MO | Intrinsic Reporting |

### 后缀变体(PDF §6.1.2)

| 变体 | 增/删的成员 | 用途 |
|---|---|---|
| `FB_BACnet_MV` | — | 基础类,16 优先级 |
| `FB_BACnet_MV_5P` | 5 优先级槽位 | 楼控多优先级场景(PDF §9.5) |

## 3. 行为说明

FB_BACnet_MV 与 MO 的差别仅在语义(虚拟值,不绑物理输出端子)。运行机制 / 优先级处理与 MO 完全相同。典型用途:全局运行场景切换 — `aStateText := ['Day','Night','Holiday','Eco']`,BMS 写 Present_Value 来切换全楼运行模式,PLC 读后驱动一组下游对象(灯光场景、空调温度设定点表、等等)。PDF §9.5 示例展示 `_5P` 变体下 PLC 用 `bEnCrit := TRUE; nValCrit := 3;` 临时占用 Critical 优先级 (如出现紧急工况时强制切到 Holiday 模式停掉空调)。

## 4. 错误码 / 返回值

无返回值。⚠️ PDF + InfoSys 未列具体 BACnet error/reject 码。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **命令优先级(commandable 对象)**:`_5P` 系列在 BACnet 16 个优先级中取 5 个槽位(LifeSafety=1 / Critical=5 / ManLocal=7 / ManOperator=8 / Program=15,默认值见 `BACnet_Param`),用 `bEnSfty` / `bEnCrit` / `bEnManLoc` / `bEnPgm` / `bEnManualOperator` 配对的 `f|b|nVal*` 写槽位。`bEn*` 由 TRUE 转 FALSE 等价于写 NULL(释放该槽位)。全部 16 槽位都为 NULL 时取 `fRelinquishDefault` / `bRelinquishDefault` / `nRelinquishDefault`(PDF §6.2.1 / §9.5 / §9.6)。
- **不写槽位也要每周期调用 FB**:库内部用周期调用驱动写值锁存到 BACnet stack;只置 `bEnPgm := TRUE` 而不调用 FB,值不会被发布。
- **MV 常用于「全局运行场景」**:一个 MV 控制全楼空调时间表 + 灯光场景,改一个值带动几十个下游对象切换,类似 BACnet 标准的 Command 对象但更简单。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_MV.TcPOU`](../examples/P_Demo_FB_BACnet_MV.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_MV
VAR
    // 全楼运行场景:Day/Night/Holiday/Eco
    fbBuildingMode : FB_BACnet_MV := (
        sObjectName := 'BuildingMode',
        aStateText := ['Day', 'Night', 'Holiday', 'Eco'],
        nRelinquishDefault := 1);
    nLocalMode : UDINT := 1;
END_VAR

fbBuildingMode.bEnPgm  := TRUE;
fbBuildingMode.nValPgm := nLocalMode;
fbBuildingMode();
```

## 7. 业务场景与实际价值

- **场景**:商办楼希望运维一键切「工作日 / 周末 / 节假日 / 节能」四种运行场景,切换后自动改变全楼空调时间表、灯光场景、电梯调度策略等。
- **价值**:一个 MV 包装「全楼模式」,所有下游对象都通过订阅 / 引用本 MV 自动跟随;运维只用改一个值。
- **替代方案对比**:用 4 个 BV 表达互斥模式需要 PLC 写互斥锁;用 AV 数字 1..4 失去枚举文本语义。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.1、§6.1.2(_5P)、§9.5(_5P + Critical 优先级临时占用)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_MI`(只读多态输入)、`FB_BACnet_MO` / `FB_BACnet_MO_5P` / `_IO5P` / `_RAW5P`(物理多态输出)、`FB_BACnet_MV_5P`(本 FB 后缀变体)
