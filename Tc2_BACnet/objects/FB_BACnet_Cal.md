# FB_BACnet_Cal

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Object · Calendar` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_Cal.TcPOU`](../examples/P_Demo_FB_BACnet_Cal.TcPOU) |

---

## 1. 功能简述

代表 BACnet 标准里的「Calendar」对象类型(BACnet Object_Type = 6 / Calendar)。维护一张 `Date_List`,Schedule 对象可引用该 Calendar 来判断今天是不是节假日 / 例外日,对应做不同时段动作。Date_List 中每项可以是单日(`eDate`)、日期区间(`eDateRange`)、或日 / 周 / 月组合(`eWeekNDay`)。PDF §9.11 给完整示例。本对象类型本库仅基础类。

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
| 日期表 | `aDateList` | `ARRAY OF ST_BA_DateValChoice` | Date_List(每项含 `eType` 与 `uDate`) |
| 当前匹配状态 | `bPresVal`(只读) | `BOOL` | Present_Value(今天是否在 Date_List 中,stack 自动算) |

## 3. 行为说明

FB_BACnet_Cal 每周期调用一次。stack 每天 0 点自动判断今天是否落在 Date_List 任一项:`eDate` 比较单日;`eDateRange` 落在起止日期之间;`eWeekNDay` 按「第 N 个星期 M」(如「2 月第 1 个周五」)等模式匹配。匹配则 Present_Value = TRUE。Schedule 对象通过 `aCalendar` 引用本 Cal,在 Cal.PresVal=TRUE 那天用 `aEntry` 替换默认 Weekly_Schedule(PDF §9.11 示例)。三种日期项可在同一 Cal 中混用,且月份 / 日期支持 BACnet 标准的奇偶通配:Month=13(奇数月)/ 14(偶数月)、Day=32(月末)/ 33(奇数日)/ 34(偶数日)。

## 4. 错误码 / 返回值

无返回值。`bPresVal` 读出当前匹配状态;无错误码。⚠️ PDF + InfoSys 未列具体 error 常量。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **`aDateList` 长度上限受 BACnet_Param 控制**:超长会被 truncated,通常 100 个日期项够大多数项目用。
- **`eWeekNDay` 用于中国春节 / 母亲节等浮动节假日**:用单日 `eDate` 每年都要更新,用 WeekNDay 一次设好;Day=32 表示月末,适合每月最后一个工作日财务系统切换。
- **修改 Date_List 用条件触发**:`IF bUpdateCalendar THEN fbCal.aDateList[0].uDate := ...; END_IF`;周期写会覆盖 BMS 端调整(PDF §6.3.1 规则)。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_Cal.TcPOU`](../examples/P_Demo_FB_BACnet_Cal.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_Cal
VAR
    fbHolidayCal : FB_BACnet_Cal := (
        sObjectName := 'PublicHolidays',
        aDateList := [
            (eType := E_BA_DateValChoice.eDate,
             uDate := F_BA_DateVal(2026, E_BA_Month.eOctober, 1))
        ]);
    bIsHolidayToday : BOOL;
END_VAR

fbHolidayCal();
bIsHolidayToday := fbHolidayCal.bPresVal;
```

## 7. 业务场景与实际价值

- **场景**:楼控项目要按节假日不开空调 / 灯光按节能时段运行,运维一次配好全年节假日表,Schedule 自动按 Calendar 切换。
- **价值**:BACnet 标准的节假日表,Schedule 引用一行解决;BMS 端可远程改节假日,无需停 PLC。
- **替代方案对比**:用 PLC 内部 BOOL 数组手写判断今天是不是节假日:跨年要重写,且 BMS 看不到。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.1(Cal = Calendar)、§9.11(Calendar + Schedule 完整示例)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319319179.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_SchedA` / `SchedB` / `SchedM`(引用本 Cal 做例外日程)、`FB_BACnet_Date` / `DateP`(单日 / 日期模式原语对象)
