# FB_BACnet_Date

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Primitive Value · Date` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319320715.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_Date.TcPOU`](../examples/P_Demo_FB_BACnet_Date.TcPOU) |

---

## 1. 功能简述

代表 BACnet 标准里的「Single Date Value」对象类型(Primitive Value 之一)。把单个日期(年-1900 / 月 / 日 / 星期)暴露给 BMS。本库另提供 `FB_BACnet_DateP`(Date Pattern Value),使用通配 255 / Unspecified 表示任意值以匹配任何年份的某月某日等模式。PDF §6.1.2 + §9.14 详细说明。

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
| 值 | `stValue` | `ST_BA_Date` | Present_Value 日期容器(`nYear/eMonth/nDay/eDayOfWeek`,nYear 从 1900 起,255 表示通配) |

### 后缀变体(PDF §6.1.2)

| 变体 | 增/删的成员 | 用途 |
|---|---|---|
| `FB_BACnet_Date` | — | 单日值,无通配 |
| `FB_BACnet_DateP` | — | Date Pattern,可用 255 / Unspecified 通配某字段(如任意年份的圣诞节) |

## 3. 行为说明

FB_BACnet_Date 每周期调用一次。PLC 把 `ST_BA_Date` 结构写到 `stValue`,库内部推到 BACnet stack 的 Present_Value。`nYear` 字段按 BACnet 标准从 1900 起算(`nYear := 122` 表示 2022);`nDay` 可用 32(月末)/ 33(奇数日)/ 34(偶数日)等通配值;`eMonth` 可用 eOddMonths(奇数月)/ eEvenMonths(偶数月);`eDayOfWeek` 用 `eFriday` 等具体星期或 `Unspecified` 表示任意。Pattern 变体 `FB_BACnet_DateP` 把所有字段都允许用通配,PDF §9.14 示例 `stDatePattern := (nYear := 255, eMonth := eDecember, nDay := eDay24, eDayOfWeek := Unspecified)` 表示每年圣诞节,无论星期几。具体日期要保证 `eDayOfWeek` 与给定日期实际匹配,否则 BACnet 标准要求 stack 拒绝。

## 4. 错误码 / 返回值

无返回值。⚠️ PDF + InfoSys 未列具体 error 常量;输入非法时 stack 不接受写入。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **`nYear` 从 1900 起**:`nYear := 122` = 2022,容易写错。
- **`eDayOfWeek` 要与日期匹配**:`stValue := (nYear := 122, eMonth := eDecember, nDay := eDay02, eDayOfWeek := eFriday)` — 2022-12-02 确实是周五,写错星期 BACnet stack 会拒绝。
- **Pattern 变体的 255 等于任意**:`FB_BACnet_DateP` 用 nYear=255 表达任意年,DateP 适合节假日匹配。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_Date.TcPOU`](../examples/P_Demo_FB_BACnet_Date.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_Date
VAR
    fbBatchStartDate : FB_BACnet_Date := (
        sObjectName := 'BatchStartDate');
    stToday : ST_BA_Date := (
        nYear := 126, eMonth := E_BA_MONTH.eJune,
        nDay := E_BA_DAY.eDay03, eDayOfWeek := E_BA_WEEKDAY.eWednesday);
END_VAR

fbBatchStartDate.stValue := stToday;
fbBatchStartDate();
```

## 7. 业务场景与实际价值

- **场景**:把上次维护日期、当前生产批次的批次日期等单日字段暴露给 BMS,无需用 DateTime 包含时间字段。
- **价值**:Date 是 BACnet 标准的轻量日期容器,BMS 端识别;比用字符串 '2026-06-03' 节省解析并自带 nYear 等结构化字段。
- **替代方案对比**:用字符串:BMS 要解析,无类型安全;用 DateTime:多余的时间字段。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.2(Date / DateP 行)、§9.14(完整 Date / DateP / Time / TimeP / DateTime / DateTimeP 示例)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319320715.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_Time` / `TimeP`(时刻)、`FB_BACnet_DateTime` / `DateTimeP`(日期 + 时刻);Schedule 对象使用 `F_BA_DateVal` 帮助函数
