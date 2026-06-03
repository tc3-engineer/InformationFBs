# FB_BACnet_AV

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Object · Analog Value` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_AV.TcPOU`](../examples/P_Demo_FB_BACnet_AV.TcPOU) |


---

## 1. 功能简述

代表 BACnet 标准里的「Analog Value」对象类型(BACnet Object_Type = 2 / Analog Value)。语义上是**虚拟模拟值**,典型用于设定点(temperature setpoint)、控制参数、计算结果等"非物理 I/O 但需要被 BMS 读写"的 `REAL` 量。基础类支持 BACnet 16 个命令优先级槽位,行为与 AO 相同;此外有四种变体:`_5P`(5 优先级槽位简化版,楼控通用)、`_Setp`(纯 setpoint,可写但不分优先级,last-writer-wins)、`_EventSetp`(Setp + Event Reporting)、`_Disp`(只读)(PDF §6.1.1 + §6.1.2)。

## 2. 接口定义

> PDF §6.1.1 / §6.1.2 把所有「无后缀」对象 FB 集中描述,**未**针对单个 FB 列 `VAR_INPUT` / `VAR_OUTPUT` 区。下表把 §6.1.1 / §6.1.2 / §9.1 / §9.5 / §9.7 / §9.10 / §9.12 出现的可初始化成员按 BACnet 标准属性分类。

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

> ⚠️ PDF/InfoSys 均未给出独立 `VAR_OUTPUT` 区;成员见下表。

### VAR_IN_OUT

无。

### 关键属性 / 成员

| 类别 | FB 成员 | 类型 | 含义 |
|---|---|---|---|
| 基本 | `iParent` / `sObjectName` / `sDescription` | `I_BACnet_View` / `STRING(*)` | 同 AI |
| 单位 / 量程 | `eUnit` / `fMinPresValue` / `fMaxPresValue` / `fResolution` | `E_BA_Unit` / `REAL` | 工程单位 + 量程 |
| Setp 类专属 | `fValue` | `REAL` | `_Setp` / `_EventSetp` 上 PLC 端写入的 Present_Value(last writer wins,无优先级) |
| 命令型(基础类 + `_5P`) | `bEnPgm` / `fValPgm` | `BOOL` / `REAL` | PLC 在 Program 优先级写值 |
| `_5P` 增 | `bEnSfty` / `fValSfty` / `bEnCrit` / `fValCrit` / `bEnManLoc` / `fValManLoc` / `bEnManualOperator` / `fValManualOperator` | 同 AO_5P | 5 优先级槽位 |
| 命令型 | `fRelinquishDefault` | `REAL` | 全槽位 NULL 时回退值 |
| 报警限 | `fHighLimit` / `fLowLimit` / `fDeadband` / `bHighLimitEnable` / `bLowLimitEnable` / `nTimeDelay` / `nTimeDelayNormal` / `bEventDetectionEnable` / `nNotificationClass` / `aEventEnable` / `aEventMessageTextsConfig` / `eNotifyType` | 同 AI | Intrinsic Reporting |

### 后缀变体(PDF §6.1.2)

| 变体 | 增/删的成员 | 用途 |
|---|---|---|
| `FB_BACnet_AV` | — | 基础类:可命令(16 优先级);PLC 用 `bEnPgm + fValPgm` |
| `FB_BACnet_AV_5P` | 增 5 优先级槽位(同 `FB_BACnet_AO_5P`) | 楼控多优先级场景 |
| `FB_BACnet_AV_Setp` | 删除 Priority_Array、Relinquish_Default;`fValue` 写入即 Present_Value | "Last writer wins" 的 setpoint(PDF §6.1.2) |
| `FB_BACnet_AV_EventSetp` | `_Setp` + 启用 Event Reporting | Setp + 支持报警(PDF §6.1.2) |
| `FB_BACnet_AV_Disp` | Present_Value 只读 | 只读显示(PDF §6.1.2) |

## 3. 行为说明

基础类 `FB_BACnet_AV` 的运行机制与 `FB_BACnet_AO` 完全一致:Present_Value 取 16 优先级槽位中最高的非 NULL 值,全空回退 `fRelinquishDefault`;PLC 通过 `bEnPgm` / `fValPgm` 占用 Program 优先级,BMS 用 `WriteProperty(Present_Value, ..., priority := N)` 占其它槽位。差别仅在语义:AO 通常绑物理输出端子,AV 是"虚拟值"(setpoint / 计算结果 / 控制参数)。`_Setp` 变体砍掉优先级机制,Present_Value 就是最后一次写入 `fValue`(PLC 端或 BMS 端皆可),BMS 写下来的值不会被 PLC 立刻覆盖——前提是 PLC 端 `fValue` 只在条件分支里写(PDF §6.3.1 强调的"declare-then-conditionally-write"模式)。`_EventSetp` 在 `_Setp` 基础上启用 Intrinsic Reporting(`fHighLimit` / `fLowLimit` / `bEventDetectionEnable` 全启)。`_Disp` 等价 Present_Value 只读,PLC 写 `fValue`,BMS 只能读。

## 4. 错误码 / 返回值

无返回值;语义与 FB_BACnet_AI §4 一致。

⚠️ PDF + InfoSys 均未在本对象类型节列出具体 error/reject 码。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **命令优先级(commandable 对象)**:`_5P` 系列在 BACnet 16 个优先级中取 5 个槽位(LifeSafety=1 / Critical=5 / ManLocal=7 / ManOperator=8 / Program=15,默认值见 `BACnet_Param`),用 `bEnSfty` / `bEnCrit` / `bEnManLoc` / `bEnPgm` / `bEnManualOperator` 配对的 `f|b|nVal*` 写槽位。`bEn*` 由 TRUE 转 FALSE 等价于写 NULL(释放该槽位)。全部 16 槽位都为 NULL 时取 `fRelinquishDefault` / `bRelinquishDefault` / `nRelinquishDefault`(PDF §6.2.1 / §9.5 / §9.6)。
- **不写槽位也要每周期调用 FB**:库内部用周期调用驱动写值锁存到 BACnet stack;只置 `bEnPgm := TRUE` 而不调用 FB,值不会被发布。
- **`_Setp` 不能用 `bEnPgm + fValPgm`**:`_Setp` 砍掉优先级,只用 `fValue := <val>`;混淆会编译报"成员不存在"。
- **`_Setp` 的"last writer wins"语义**:PLC 端每周期写 `fValue := 20.0` 会覆盖 BMS 刚写的 22.0。正确做法:`IF bResetSetpoint THEN fbSp.fValue := 20.0; bResetSetpoint := FALSE; END_IF`(PDF §9.1 + §6.3.1)。
- **Loop 对象常以 AV_Setp / AV 配套使用**:PI 回路用 `FB_BACnet_Loop_Ref` 引用一个 AV_Setp 做 setpoint,可被 BMS 修改;另一个 AI 做 process,本 FB 做 output(PDF §9.7)。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_AV.TcPOU`](../examples/P_Demo_FB_BACnet_AV.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_AV
VAR
    // 房间温度设定点:_Setp 变体,BMS 可写,PLC 周期读
    fbRoomSetp : FB_BACnet_AV_Setp := (
        sObjectName := 'RoomSetp_3F_East',
        sDescription := 'Floor 3 East zone temperature setpoint',
        eUnit := E_BA_Unit.eTemperature_DegreesCelsius,
        fValue := 22.0);                 // 默认 22°C
    fSetpUsedByPid : REAL;
END_VAR

fbRoomSetp();                            // 每周期调用一次
fSetpUsedByPid := fbRoomSetp.fValue;     // 把当前 setpoint 喂给 PID
```

## 7. 业务场景与实际价值

- **场景**:每个区房间温度设定点要让操作员从 BMS 上设置(早班 22°C / 晚班 26°C);PLC 内部 PID 控温要读取这个设定点。100 间房 → 100 个 AV_Setp 实例。
- **价值**:用 `_Setp` 一行声明 + 默认值,BMS 直接 WriteProperty 即可改;PLC 端只用读 `fbXxx.fValue`,无需关心"是不是 BMS 在写"。换成基础类 AV + 优先级,需要 PLC 也写 Program 优先级,反而把行为搞复杂。
- **替代方案对比**:
  - 用全局 `REAL` + ADS 暴露:跨厂商 BMS 不能读
  - 用基础类 `FB_BACnet_AV`:可命令优先级,但 setpoint 场景不需要
  - 用 `_5P` 变体:适合"PID 输出"等需要多优先级覆盖的虚拟值,setpoint 场景过于复杂

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.1、§6.1.2(_5P / _Setp / _EventSetp / _Disp)、§9.1(setpoint 初始化模式)、§9.5(_5P 优先级)、§9.7(Loop 配 AV_Setp)、§9.10(报警限)、§9.12(用 AV 触发 trendlog / 报警)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_AO`(物理模拟输出)、`FB_BACnet_AI`(物理模拟输入)、`FB_BACnet_Loop_Ref`(用 AV_Setp 做 setpoint)、`FB_BACnet_AV_5P` / `_Setp` / `_EventSetp` / `_Disp`(本 FB 后缀变体)
