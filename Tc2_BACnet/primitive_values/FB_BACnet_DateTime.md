# FB_BACnet_DateTime

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Primitive Value · DateTime` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319320715.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_DateTime.TcPOU`](../examples/P_Demo_FB_BACnet_DateTime.TcPOU) |

---

## 1. 功能简述

代表 BACnet 标准里的「Date and Time Value」对象类型,把完整时间戳(日期 + 时刻)暴露给 BMS。本库另提供 `FB_BACnet_DateTimeP`(Date and Time Pattern Value),组合 Date 和 Time 字段的通配以表达复杂模式。PDF §6.1.2 + §9.14 详细说明。

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
| 值 | `stValue` | `ST_BA_DateTime` | Present_Value 时间戳容器(`stDate : ST_BA_Date` + `stTime : ST_BA_Time`) |

### 后缀变体(PDF §6.1.2)

| 变体 | 增/删的成员 | 用途 |
|---|---|---|
| `FB_BACnet_DateTime` | — | 单时间戳,无通配 |
| `FB_BACnet_DateTimeP` | — | DateTime Pattern,日期 / 时刻字段都可通配,表达复杂模式如每年 5 月 1 日是周一的那年的每小时每分钟的第 11 秒 |

## 3. 行为说明

FB_BACnet_DateTime 每周期调用一次。`stValue` 嵌套 `stDate` 与 `stTime` 子结构,字段含义同 Date 和 Time 对象 — `stDate.nYear` 仍按 BACnet 标准从 1900 起算,各字段越界 stack 拒绝写入。Pattern 变体 `FB_BACnet_DateTimeP` 允许两者任一字段通配 — PDF §9.14 示例 `stDateTimePattern := (stDate := (nYear:=255, eMonth:=eMay, nDay:=eDay01, eDayOfWeek:=eMonday), stTime := (nHour:=255, nMinute:=255, nSecond:=11, nHundredths:=0))` 表达每年 5 月 1 日是周一的那年的每小时每分钟的第 11 秒 — 这种复合模式非常少见,主要给BACnet 标准 Schedule 的 Exception_Schedule 用。运行时改值要走条件触发分支,避免周期覆盖 BMS 端调整。

## 4. 错误码 / 返回值

无返回值;输入越界 stack 不接受。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **Pattern 变体很少用**:实际工程用单一 DateTime 直接给时间戳,Pattern 主要存在为 BACnet 标准完整性。
- **`stDate.nYear` 从 1900 起算**,容易写错。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_DateTime.TcPOU`](../examples/P_Demo_FB_BACnet_DateTime.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_DateTime
VAR
    fbBatchTimestamp : FB_BACnet_DateTime := (sObjectName := 'BatchTimestamp');
    stNow : ST_BA_DateTime := (
        stDate := (nYear := 126, eMonth := E_BA_MONTH.eJune,
                   nDay := E_BA_DAY.eDay03, eDayOfWeek := E_BA_WEEKDAY.eWednesday),
        stTime := (nHour := 14, nMinute := 30, nSecond := 0, nHundredths := 0));
END_VAR

fbBatchTimestamp.stValue := stNow;
fbBatchTimestamp();
```

## 7. 业务场景与实际价值

- **场景**:把批次开始时间戳、上次校时时刻等完整时间戳字段暴露给 BMS,做时序记录。
- **价值**:DateTime 是 BACnet 标准时间戳容器,BMS 识别;比拼字符串节省解析、自带时区中立语义。
- **替代方案对比**:拆 Date + Time 两个对象:BMS 端要原子读两次;DateTime 一次读取保证一致性。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.2(DateTime / DateTimeP 行)、§9.14(完整示例)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319320715.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_Date` / `DateP`(日期)、`FB_BACnet_Time` / `TimeP`(时刻)
