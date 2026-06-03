# DT_TO_PMLTime

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V3` |
| Library Version | `1.0.0` |
| Type | `FUNCTION` |
| Category | `Conversion / Timestamp` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16003245451.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_DT_TO_PMLTime.TcPOU`](../examples/P_Demo_DT_TO_PMLTime.TcPOU) |

---

## 1. 功能简述

`DT_TO_PMLTime` 把 IEC 标准日期时间类型 `DT`（`DATE_AND_TIME`）转换为 PackML 标准的 `ST_PMLDateAndTime` 结构体（`Year` / `Month` / `Day` / `Hour` / `Minute` / `Second` / `mSec`）。

**V3 与 V2 的关键差异**：V2 版本（`DT_TO_PackMLTime`）返回 `ARRAY [0..6] OF DINT` 数组；V3 改为返回**结构体** `ST_PMLDateAndTime`——按字段名访问、可读性更好。

`DT` 是 IEC 61131-3 标准日期+时间类型，秒精度，从 1970-01-01 起算（UNIX epoch）。本函数解读为日历时刻（年/月/日/时/分/秒/毫秒，毫秒分量恒为 0 因为 DT 不带毫秒精度）写入 PackML PackTag。

## 2. 接口定义

### 函数签名

```iecst
FUNCTION DT_TO_PMLTime : ST_PMLDateAndTime
```

### VAR_INPUT

```iecst
VAR_INPUT
    Input         : DATE_AND_TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Input` | `DATE_AND_TIME` | 要转换的日期时间（IEC 61131-3 标准 DATE_AND_TIME 类型，秒精度，UNIX epoch 1970-01-01 起算）|

### VAR_OUTPUT

无（结果通过 `FUNCTION` 返回值给出）。

### VAR_IN_OUT

无。

## 3. 行为说明

`DT_TO_PMLTime` 把 IEC 日期时间值转换为 PackML 标准 `ST_PMLDateAndTime` 结构体。

**DT 语义**：IEC 61131-3 标准日期+时间类型（别名 `DATE_AND_TIME`），秒精度，UTC 或本地时（语义由 PLC 配置决定）。字面值如 `DT#2026-06-03-14:30:45`。

**返回结构体字段含义**：
- `Year` = 日历年份（如 2026）
- `Month` = 1-12
- `Day` = 1-31
- `Hour` = 0-23
- `Minute` = 0-59
- `Second` = 0-59
- `mSec` = 恒为 0（DT 不带毫秒精度）

**与 DCTIME64 转换对比**：
- DCTIME64：EtherCAT epoch（2000-01-01）+ 纳秒精度，多 PLC 同步首选。
- DT：UNIX epoch（1970-01-01）+ 秒精度，标准 IEC 类型，单 PLC 场景常用。

**调用语义**：纯函数——同一输入永远返回同一输出。

**典型用法**：把 `Tc2_System.NT_GetTime` 返回的 `DT` 时间转成 PackML 结构写入报警时间戳；或把 HMI 用户输入的日期时间直接转给 `FB_PMLAdminTime` 的 `stOptions.ExternalPackMLTime` 输入。

## 4. 错误码 / 返回值

返回 `ST_PMLDateAndTime` 结构体：转换后的 PackML 日历时刻结构（`mSec` 分量恒为 0）。

无错误返回——纯计算函数。

## 5. 使用注意 / 常见坑

- `DT` 是**秒精度**——返回结构体 `mSec` 字段始终为 0。需要毫秒精度请用 `TIMESTRUCT_TO_PMLTime`（来源 TIMESTRUCT 带毫秒）或 `DCTIME64_TO_PMLTime`（纳秒）。（工程经验补充）
- DT 是"时刻（timestamp）"语义——结构体的 `Year` 是日历年份；与 LTIME/TIME/ULINT 的"时长"转换不同。
- DT 是否是 UTC 还是本地时由 PLC 配置决定——多时区项目需注意。
- 与 V2 (`DT_TO_PackMLTime` 返回数组) 不兼容——升级时改字段访问。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DT_TO_PMLTime.TcPOU`](../examples/P_Demo_DT_TO_PMLTime.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：HMI 显示"上次维护时间"用 DT 类型存储（`DT#2026-05-15-10:00:00`），现在要把它写入 PackTags 的某个时间字段以供 MES 使用。调本函数一行转换。
- **价值**：DT 是 IEC 标准类型、PackML V3 用结构体——两者直接互转的标准化封装，应用层避免手写月份/日期边界。字段名访问更安全。
- **替代方案对比**：手写 DT 转结构体——需要处理闰年、月份天数、epoch 偏移；本函数封装好、与 PackML 标准对齐。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.1.2.2
- **InfoSys 参考 topic（返回类型）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16003245451.html （ST_PMLDateAndTime 数据结构 topic；V3 本 FUNCTION 自身 InfoSys topic 页面公网未检索到，故 InfoSys-checked 标 ⚠️ not-on-infosys）
- **相关**：`DCTIME64_TO_PMLTime`（EtherCAT 纳秒时间戳）、`TIMESTRUCT_TO_PMLTime`（结构体毫秒时间戳）、`FB_PMLAdminTime`、`Tc2_System.NT_GetTime`（获取 DT 当前时间）、`ST_PMLDateAndTime`

## 9. 待确认项 (⚠️)

- V3 InfoSys 本 FUNCTION 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
