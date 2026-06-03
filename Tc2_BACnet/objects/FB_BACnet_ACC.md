# FB_BACnet_ACC

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Object · Accumulator` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_ACC.TcPOU`](../examples/P_Demo_FB_BACnet_ACC.TcPOU) |

---

## 1. 功能简述

代表 BACnet 标准里的「Accumulator」对象类型(BACnet Object_Type = 23 / Accumulator),用于累计型脉冲计数,典型场景是电度表 / 水表 / 燃气表的脉冲累计读数。Present_Value 是 `UDINT` 单调递增计数,带 `Scale` 缩放属性与 `Units` 工程单位,BMS 客户端通过 `Pulse_Rate` 周期采样得到瞬时流量。本对象类型在本库中仅基础类,无后缀变体。

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
| 计数 | `nVal` | `UDINT` | Present_Value(累计脉冲数,PLC 喂入) |
| 缩放 | `fScale` | `REAL` | Scale(每脉冲代表的工程量,如 0.001 kWh) |
| 单位 | `eUnit` | `E_BA_Unit` | Units(`eEnergy_kWh` 等) |
| 极限值 | `nMaxPresValue` | `UDINT` | Max_Pres_Value(溢出回 0 的上界) |
| 限值检测 | `fHighLimit` / `bHighLimitEnable` / `bEventDetectionEnable` / `nNotificationClass` / `aEventEnable` / `aEventMessageTextsConfig` | 同 AI | 累计超限报警(常用于「水表突增」诊断) |

## 3. 行为说明

FB_BACnet_ACC 每周期调用一次,PLC 把累计脉冲数写到 `nVal`(典型由 EL1262 等高速计数端子读出,或由 PLC 内部对 EL1809 脉冲输入做边沿计数)。库内部把 `nVal` 推到 BACnet stack 的 Present_Value,客户端通过 `ReadProperty(Pulse_Rate)` 取最近采样区间内的脉冲速率 — Pulse_Rate 由 stack 在两次读请求之间自动算 delta / time。`fScale` 让 BMS 端把脉冲数转回工程量(如 fScale := 0.001 表示每脉冲 = 0.001 kWh,1000 脉冲 = 1 kWh)。`nMaxPresValue` 设为 4294967295 时让 UDINT 自然溢出回 0,或设小值实现「达到 999999 后归零重计」语义。

## 4. 错误码 / 返回值

无返回值;`stStatusFlags` 暴露状态。⚠️ PDF + InfoSys 未列具体 BACnet error/reject 码。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **PLC 不要复位 `nVal`**:Accumulator 语义是「累计永不归零」,PLC 周期写小于上次的值会让 BMS 端的 Pulse_Rate 算成负数。
- **掉电要保住累计值**:`nVal` 需要走 PLC 的 VAR_RETAIN 持久化或 UPS 关机时写盘,否则掉电后归零会丢电量数据(工程经验补充)。
- **`fScale` 必须与 Units 一致**:工程单位 `eEnergy_kWh` 时 fScale 应该是 kWh/脉冲(如 0.001),写成 Wh/脉冲(如 1.0)BMS 显示会差 1000 倍。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_ACC.TcPOU`](../examples/P_Demo_FB_BACnet_ACC.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_ACC
VAR
    // 电度表累计读数,1 脉冲 = 0.001 kWh
    fbEnergyMeter : FB_BACnet_ACC := (
        sObjectName := 'EnergyMeter_AHU_3F',
        sDescription := 'AHU floor 3 power consumption',
        eUnit := E_BA_Unit.eEnergy_KilowattHours,
        fScale := 0.001,
        nMaxPresValue := 4294967295);     // UDINT 自然上界
    nMeterPulsesPlc : UDINT := 0;          // 从 EL1262 计数端子读出,PLC 内部累加
END_VAR

fbEnergyMeter.nVal := nMeterPulsesPlc;
fbEnergyMeter();
```

## 7. 业务场景与实际价值

- **场景**:每个空调机组装一只脉冲电度表,运维要在 BMS 上看每个机组累计电量与瞬时功率,做能效分析与计费分摊。
- **价值**:Accumulator 是 BACnet 标准的能源计量对象,BMS / 第三方能源管理软件都识别;直接暴露 `nVal` + `fScale` + `eUnit`,BMS 端的「瞬时功率」由 Pulse_Rate 自动算。
- **替代方案对比**:用 AV 暴露 `REAL` 累计值:失去 BACnet 标准的 Pulse_Rate / Scale 语义,BMS 看不到瞬时功率;能源管理软件可能不识别。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.1(ACC = Accumulator)、§3.2(Scale / Pulse_Rate / Max_Pres_Value 在 BACnet 标准属性表)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_PC`(脉冲转换,把累计脉冲转工程量)、`FB_BACnet_AI`(瞬时模拟量)
