# FB_BACnet_PC

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Object · Pulse Converter` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ infer-from-naming-convention` |
| Example | [`examples/P_Demo_FB_BACnet_PC.TcPOU`](../examples/P_Demo_FB_BACnet_PC.TcPOU) |

---

## 1. 功能简述

代表 BACnet 标准里的「Pulse Converter」对象类型(BACnet Object_Type = 24 / Pulse Converter),把累计脉冲(典型来源 ACC 对象 / 物理脉冲计数器)转成已乘以 Scale 的工程量。典型场景:电度表把累计脉冲转累计 kWh、累计水量。本对象类型在本库中仅基础类,无后缀变体。Status: ⚠️ PDF 仅在 §6.1.1 表中列出 PC 一行,未给出独立示例;本文档基于 BACnet 标准 PulseConverter 对象语义 + 本库命名规则推导成员列表。

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
| 工程量 | `fVal` | `REAL` | Present_Value(已经乘了 Scale 的工程量,如 kWh) |
| 缩放 | `fScale` | `REAL` | Scale(每脉冲对应的工程量) |
| 单位 | `eUnit` | `E_BA_Unit` | Units |
| 量程 | `fMinPresValue` / `fMaxPresValue` | `REAL` | 量程 |
| 调整 | `fAdjustValue` | `REAL` | Adjust_Value(BMS 写入后让 Present_Value 回到该值,用于校正) |
| 限值检测 | `fHighLimit` / `bHighLimitEnable` / `bEventDetectionEnable` / `nNotificationClass` / `aEventEnable` / `aEventMessageTextsConfig` | 同 AI | 累计超限报警 |

## 3. 行为说明

FB_BACnet_PC 每周期调用一次。PLC 把已经换算好的累计工程量(如累计 kWh)写到 `fVal`,BACnet stack 把它推到 Present_Value。与 Accumulator 的差别:Accumulator 暴露的是原始脉冲数 + Scale,由 BMS 端把 nVal × Scale 得到工程量;Pulse Converter 已经在 PLC 端做了乘法,Present_Value 直接是 kWh。Adjust_Value 是 PC 独有的属性:BMS 写 Adjust_Value 时 stack 把当前 Present_Value 调整为该值(用于「年度抄表后清零重计」或「换表后从已有累计值继续」)。PDF 未给独立示例,用法上参照 §9.16(数组初始化模式)与 §6.3.1(条件性写属性)。

## 4. 错误码 / 返回值

无返回值。⚠️ PDF + InfoSys 未列具体 BACnet error/reject 码;本对象类型也未在 §9 给出示例,典型行为参照 BACnet 标准定义。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **PC vs ACC**:PC 暴露的是已换算工程量,适合 BMS 端直接显示;ACC 暴露的是脉冲计数,适合 BMS 端做「瞬时流量」分析(Pulse_Rate)。
- **`fVal` 单调递增**:与 ACC 一样,不要复位;BMS 通过 Adjust_Value 校正而不是直接写 Present_Value。
- **掉电持久化必做**:用 VAR_RETAIN 保住 `fVal` 上次值(工程经验补充,与 ACC 同)。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_PC.TcPOU`](../examples/P_Demo_FB_BACnet_PC.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_PC
VAR
    // 把累计脉冲直接换算成 kWh,BMS 上看到的就是 kWh
    fbEnergyConv : FB_BACnet_PC := (
        sObjectName := 'EnergyKwh_AHU_3F',
        sDescription := 'AHU floor 3 cumulative energy (kWh)',
        eUnit := E_BA_Unit.eEnergy_KilowattHours,
        fScale := 0.001,
        fMinPresValue := 0.0,
        fMaxPresValue := 1.0E9);
    fEnergyKwhPlc : REAL := 0.0;        // PLC 把脉冲 × 0.001 后送来
END_VAR

fbEnergyConv.fVal := fEnergyKwhPlc;
fbEnergyConv();
```

## 7. 业务场景与实际价值

- **场景**:同 ACC,但 BMS 端只关心 kWh 显示,不需要瞬时 Pulse_Rate;PLC 端已经做好脉冲到工程量的乘法。
- **价值**:把 ACC 的「脉冲数 + Scale 分两个属性」折叠成「已经换算的工程量」,BMS 端读 Present_Value 即可直接显示,无需在画面里写公式。
- **替代方案对比**:用 ACC + BMS 端公式更标准化但 BMS 端复杂;用 AV 暴露 fVal 失去「累计永不归零」语义且不能用 Adjust_Value 校表。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.1(PC = Pulse Converter)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_ACC`(累计脉冲计数)、`FB_BACnet_AI`(瞬时模拟量)
