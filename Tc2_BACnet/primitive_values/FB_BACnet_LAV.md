# FB_BACnet_LAV

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Primitive Value · Large Analog Value (LREAL)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319320715.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_LAV.TcPOU`](../examples/P_Demo_FB_BACnet_LAV.TcPOU) |

---

## 1. 功能简述

代表 BACnet 标准里的「Large Analog Value (LREAL)」对象类型,Primitive Value 系列中的一个 — 用于把单个简单数据类型(整数 / 字符串 / 日期 / 时刻)直接暴露成可被 BMS 读写的 BACnet 对象,无需借助 AV / MV / String 之外的复杂对象类型。Primitive Value 对象本身没有命令优先级、没有 Status_Flags / Reliability,语义就是数据容器。本变体处理 64 位 LREAL(双精度浮点,8 字节),用于范围超过 REAL(32 位)精度的物理量(典型:累计能耗、累计运行时间秒数等高位精度需求)。PDF §6.1.2 把 10 种 Primitive Value 对象统一表述,§9.14 给完整声明 + 调用示例。

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
| 值 | `fValue` | `LREAL` | Present_Value 容器(PLC 与 BMS 双向读写) |

## 3. 行为说明

本 FB 每周期调用一次。PLC 把当前值写到值成员,库内部推到 BACnet stack 的 Present_Value;BMS 写下来的值通过同一成员反向取出,需要 PLC 端在条件分支里处理(PDF §6.3.1 一致原则)。Primitive Value 对象不带 Status_Flags / Reliability / 报警限,语义就是BACnet 标准化的简单值容器 — 适合把调度参数表中的字符串 / 数字 / 日期 / 时间字段一一暴露给 BMS 而不用更复杂的 AV / MV 对象。PDF §9.14 显示典型用法 — 同一周期里并列实例化多个不同类型的 Primitive Value 对象,各自喂入值后周期调用。

## 4. 错误码 / 返回值

无返回值;Primitive Value 对象没有 Status_Flags / Reliability,无错误码。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **改值用条件触发**:PLC 端周期写值会覆盖 BMS 端调整(PDF §6.3.1 一致原则)。
- **不要拿 Primitive Value 替代 AV / MV**:Primitive Value 没有命令优先级、Status_Flags、报警限,只适合纯数据容器。
- **Pattern 系列(DateP / DateTimeP / TimeP)的通配值是 255**:PDF §6.1.2 + §9.14 明确,255 表示任意值;例如 `nYear := 255` 表示任何年份。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_LAV.TcPOU`](../examples/P_Demo_FB_BACnet_LAV.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_LAV
VAR
    fbVal : FB_BACnet_LAV;
    val : LREAL := 42.3;
END_VAR
fbVal.fValue := val;
fbVal();
```

## 7. 业务场景与实际价值

- **场景**:累计运行小时数(REAL 精度只够 7 位有效数,运行 10000 小时后小数部分丢失;LAV 用 LREAL 解决)、高精度能量计量等。
- **价值**:Primitive Value 对象简单直接,BMS 端看到一个标准 BACnet 对象;比用 AV / String 更轻量(没有不必要的 Status_Flags 等属性)。
- **替代方案对比**:用 AV / String 暴露简单值:多了 BACnet 属性 BMS 用不上,占 router memory;Primitive Value 是 BACnet 标准为简单数据准备的轻量对象类型。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.2(Primitive Value 类型表)、§9.14(完整 Primitive Value 示例)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319320715.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:同 §6.1.2 中的其它 Primitive Value FB:`FB_BACnet_INT` / `LAV` / `String` / `Date` / `DateP` / `Time` / `TimeP` / `DateTime` / `DateTimeP`
