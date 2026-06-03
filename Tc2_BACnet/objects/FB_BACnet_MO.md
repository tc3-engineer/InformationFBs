# FB_BACnet_MO

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Object · Multistate Output` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_MO.TcPOU`](../examples/P_Demo_FB_BACnet_MO.TcPOU) |

---

## 1. 功能简述

代表 BACnet 标准里的「Multistate Output」对象类型(BACnet Object_Type = 14 / Multistate Output)。语义上是可写、支持命令优先级的多态输出,典型用于阀位档位(0/25/50/75/100%)、运行档位选择(`Stop`/`Cool`/`Heat`/`Fan`)等枚举型物理输出。本库提供基础类 + `_5P`(5 优先级)+ `_IO5P`(`_5P` 接 K-bus 端子)+ `_RAW5P`(`_5P` raw 值由 PLC 自算)四个变体。PDF §9.5 示例 `fbMO5P` / `fbMOIO5P` / `fbMORaw5P` 给出三者声明对照。

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
| 基本信息 | `iParent` / `sObjectName` / `sDescription` / `sDeviceType` | `I_BACnet_View` / `STRING(*)` | DPAD + 名称 |
| 状态枚举 | `aStateText` | `ARRAY[1..*] OF STRING(*)` | State_Text(同 MI) |
| Present_Value 命令(基础类 + `_5P`) | `bEnPgm` / `nValPgm` | `BOOL` / `UDINT` | PLC 在 Program 优先级写值;FALSE 释放槽位 |
| `_5P` 增 | `bEnSfty/nValSfty` / `bEnCrit/nValCrit` / `bEnManLoc/nValManLoc` / `bEnManualOperator/nValManualOperator` | `BOOL` / `UDINT` | 5 优先级槽位 |
| 回退 | `nRelinquishDefault` | `UDINT` | 16 槽位全 NULL 时回退值 |
| 报警 | `aAlarmValues` / `aFaultValues` / `bEventDetectionEnable` / `nNotificationClass` / `aEventEnable` / `aEventMessageTextsConfig` | 同 MI | Intrinsic Reporting |

### 后缀变体(PDF §6.1.2)

| 变体 | 增/删的成员 | 用途 |
|---|---|---|
| `FB_BACnet_MO` | — | 基础类,16 优先级 |
| `FB_BACnet_MO_5P` | 5 优先级槽位 | 楼控多优先级场景 |
| `FB_BACnet_MO_IO5P` | `_5P` + `nRawVal AT %Q* : USINT` | 5 优先级 + 写 K-bus 端子 |
| `FB_BACnet_MO_RAW5P` | `_5P` + `nRawVal : USINT` | 5 优先级 + raw 值 PLC 自算(常用于「输出多态值到非标硬件」) |

## 3. 行为说明

运行机制与 FB_BACnet_BO 类似但 Present_Value 是 `UDINT` 而非 `BOOL`,优先级机制完全相同 — 对 BACnet 16 优先级槽位轮询取最高的非 NULL 值。基础类用 `bEnPgm := TRUE` + `nValPgm := <1..N>` 占 Program 优先级(默认槽 16,可在 BACnet_Param 改);`_5P` 把 5 个常用优先级(LifeSafety / Critical / ManLocal / ManOperator / Program)搬成 PLC 内 boolean+UDINT 引脚。全 16 槽位为 NULL 时取 `nRelinquishDefault`。`aAlarmValues` / `aFaultValues` 列出哪些 Present_Value 值要触发 alarm / fault 事件,stack 自动管理状态切换与 NC 路由。PDF §9.5 末尾示例显示 `fbMV5P.bEnCrit := TRUE; fbMV5P.nValCrit := 3;` 这种占用 Critical 优先级临时写状态 3 的典型用法。`_IO5P` / `_RAW5P` 把 Present_Value 自动写到端子通道 / PLC 自定义 raw 值,适合多态启动器(4 档马达控制器等)。

## 4. 错误码 / 返回值

无返回值。⚠️ PDF + InfoSys 未列具体 BACnet error/reject 码。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **命令优先级(commandable 对象)**:`_5P` 系列在 BACnet 16 个优先级中取 5 个槽位(LifeSafety=1 / Critical=5 / ManLocal=7 / ManOperator=8 / Program=15,默认值见 `BACnet_Param`),用 `bEnSfty` / `bEnCrit` / `bEnManLoc` / `bEnPgm` / `bEnManualOperator` 配对的 `f|b|nVal*` 写槽位。`bEn*` 由 TRUE 转 FALSE 等价于写 NULL(释放该槽位)。全部 16 槽位都为 NULL 时取 `fRelinquishDefault` / `bRelinquishDefault` / `nRelinquishDefault`(PDF §6.2.1 / §9.5 / §9.6)。
- **不写槽位也要每周期调用 FB**:库内部用周期调用驱动写值锁存到 BACnet stack;只置 `bEnPgm := TRUE` 而不调用 FB,值不会被发布。
- **`nValPgm := 0` 是无效值**:多态值合法是 1..N(N = `aStateText` 长度),写 0 会被 stack reject 或导致客户端读到无效状态。
- **`_IO5P` 写 K-bus 端子的 USINT raw 值**:典型用于 4 档马达启动器,每个档位对应 USINT 编码 1..4。
- **使用 `_RAW5P` 时 PLC 要把 nVal 转成 `nRawVal`**:库不会自动 1:1 映射,因为多态值与硬件编码不一定一致(可能多态值 1 对应端子代码 16)。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_MO.TcPOU`](../examples/P_Demo_FB_BACnet_MO.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_MO
VAR
    // 空调四档运行模式输出:Stop/Cool/Heat/Fan
    fbModeCmd : FB_BACnet_MO_5P := (
        sObjectName := 'ModeCmd_AHU_3F',
        aStateText := ['Stop', 'Cool', 'Heat', 'Fan'],
        nRelinquishDefault := 1);            // 全释放回退到 Stop
    nAutoModeCmd : UDINT := 2;               // PLC 算的当前指令
END_VAR

fbModeCmd.bEnPgm  := TRUE;
fbModeCmd.nValPgm := nAutoModeCmd;
fbModeCmd();
```

## 7. 业务场景与实际价值

- **场景**:小型 AHU 四档运行模式(Stop/Cool/Heat/Fan)输出,PLC 根据温差自动切换,BMS 可手动覆盖(运维试机时强制开 Fan 测试风机)。
- **价值**:用一个 MO_5P 代替「4 个 BO 拼接互斥锁」,优先级让 PLC 自动+BMS 手动解耦。
- **替代方案对比**:用 4 个 BO + 互斥锁需要 PLC 端写一堆「如果 BMS 写了 BO1 则把 BO2/3/4 都关」的胶水代码;MO 一行搞定。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.1、§6.1.2(_5P / _IO5P / _RAW5P)、§9.5(_5P 优先级控制)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_MI`(只读多态输入)、`FB_BACnet_MV` / `FB_BACnet_MV_5P`(虚拟多态值)、`FB_BACnet_MO_5P` / `_IO5P` / `_RAW5P`(本 FB 后缀变体)
