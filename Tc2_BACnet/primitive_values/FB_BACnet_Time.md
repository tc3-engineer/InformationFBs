# FB_BACnet_Time

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_BACnet` |
| Library Version | `1.1.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Primitive Value · Time` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319320715.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ chapter-overview-only |
| Status | `⚠️ chapter-overview-only` |
| Example | [`examples/P_Demo_FB_BACnet_Time.TcPOU`](../examples/P_Demo_FB_BACnet_Time.TcPOU) |

---

## 1. 功能简述

代表 BACnet 标准里的「Time Value」对象类型,把单个时刻(时 / 分 / 秒 / 百分之一秒)暴露给 BMS。本库另提供 `FB_BACnet_TimeP`(Time Pattern Value),使用通配 255 表示任意值以匹配每小时的第 42 分等模式。PDF §6.1.2 + §9.14 详细说明。

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
| 值 | `stValue` | `ST_BA_Time` | Present_Value 时刻容器(`nHour:0..23` / `nMinute:0..59` / `nSecond:0..59` / `nHundredths:0..99`;255 表示通配) |

### 后缀变体(PDF §6.1.2)

| 变体 | 增/删的成员 | 用途 |
|---|---|---|
| `FB_BACnet_Time` | — | 单时刻,无通配 |
| `FB_BACnet_TimeP` | — | Time Pattern,可用 255 通配某字段(如每小时第 42 分) |

## 3. 行为说明

FB_BACnet_Time 每周期调用一次。PLC 把 `ST_BA_Time` 结构写到 `stValue`,库内部推到 BACnet stack 的 Present_Value;范围:nHour 0..23,nMinute 0..59,nSecond 0..59,nHundredths 0..99(注意是百分秒,不是毫秒)。Pattern 变体 `FB_BACnet_TimeP` 把任意字段设 255 表示通配 — PDF §9.14 示例 `stTimePattern := (nHour := 255, nMinute := 42, nSecond := 0, nHundredths := 0)` 表示每小时第 42 分整点。BMS 端的 Schedule 对象与 Pattern 配合可表达复杂周期事件;运行时改值要走条件触发分支以免覆盖 BMS 端修改。

## 4. 错误码 / 返回值

无返回值;输入越界时 stack 不接受写入。

## 5. 使用注意 / 常见坑

- **每周期调用一次,且使用同一周期任务**:`fb<Name>()` 必须每个 PLC 循环调用且只调用一次。若条件性调用(`IF bX THEN fb(); END_IF`),BACnet 客户端读这个对象时会看到值停滞;若用不同周期任务,启动期同步会失败(PDF §6.4.1 / §6.4.2)。
- **属性初值放在变量声明里,运行时改属性用上升沿触发**:`IF bChanged THEN fb.sDescription := 'New'; END_IF`,不要每周期写,否则 BACnet 端写下来的值会被覆盖(PDF §6.3.1)。
- **router memory 默认 32 MB,按"每对象 ≈ 20 KB"估算总需求**(PDF §6.5)。占用 ≥ 60% 时库拒绝再建对象,日志窗有 router-memory 错误。
- **百分秒(`nHundredths`)的范围是 0..99 而不是 0..999**:对应 BACnet 标准的百分之一秒,不是毫秒。
- **Pattern 变体的通配 255 用于周期模式**:`FB_BACnet_TimeP` 与 BMS 端 Schedule 配合让 BMS 显示每小时第 N 分等模式而不必每分钟写一条记录。

## 6. 最小例程

> 配套可导入文件:[`examples/P_Demo_FB_BACnet_Time.TcPOU`](../examples/P_Demo_FB_BACnet_Time.TcPOU)

```iecst
PROGRAM P_Demo_FB_BACnet_Time
VAR
    fbLastBackupTime : FB_BACnet_Time := (sObjectName := 'LastBackupTime');
    stNow : ST_BA_Time := (
        nHour := 14, nMinute := 30, nSecond := 0, nHundredths := 0);
END_VAR

fbLastBackupTime.stValue := stNow;
fbLastBackupTime();
```

## 7. 业务场景与实际价值

- **场景**:把今日数据备份完成时刻、夜间维护开始时刻等单时刻字段暴露给 BMS。
- **价值**:Time 是 BACnet 标准的轻量时刻容器,BMS 识别;比字符串 '14:30:00' 节省解析。
- **替代方案对比**:用字符串:BMS 要解析无类型安全;用 DateTime:多余的日期字段。

## 8. 参考资料

- **PDF**:[TF8020_TC3_BACnet_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF8020_TC3_BACnet_EN.pdf) §6.1.2(Time / TimeP 行)、§9.14(完整示例)
- **InfoSys topic**:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319320715.html;命名规则:https://infosys.beckhoff.com/content/1033/tf8020_bacnetrev14/12319294987.html
- **相关 FB**:`FB_BACnet_Date` / `DateP`(日期)、`FB_BACnet_DateTime` / `DateTimeP`(组合)
