# DT_TO_PackMLTime

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `FUNCTION` |
| Category | `Conversion / Timestamp` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6302001931.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_DT_TO_PackMLTime.TcPOU`](../examples/P_Demo_DT_TO_PackMLTime.TcPOU) |

---

## 1. 功能简述

`DT_TO_PackMLTime` 把 IEC 标准日期时间类型 `DT`（DATE_AND_TIME）转换为 PackML 标准的 7 元素 `ARRAY [0..6] OF DINT` 时间数组。

`DT` 是 IEC 61131-3 标准日期+时间类型，秒精度，从 1970-01-01 起算（Unix epoch）。本函数解读为日历时刻（年/月/日/时/分/秒/毫秒，毫秒分量恒为 0 因为 DT 不带毫秒）写入 PackML PackTag。

## 2. 接口定义

### 函数签名

```iecst
FUNCTION DT_TO_PackMLTime : ARRAY [0..6] OF DINT;
```

### VAR_INPUT

```iecst
VAR_INPUT
    Input         : DT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Input` | `DT` | 要转换的日期时间（IEC 61131-3 标准 DATE_AND_TIME 类型，秒精度，从 1970-01-01 起算）|

### VAR_OUTPUT

无（结果通过 FUNCTION 返回值给出）。

### VAR_IN_OUT

无。

## 3. 行为说明

`DT_TO_PackMLTime` 把 IEC 日期时间值转换为 PackML 标准 7 元素 DINT 数组。

**DT 语义**：IEC 61131-3 标准日期+时间类型，秒精度，UTC 或本地时（语义由 PLC 配置决定）。字面值如 `DT#2026-06-03-14:30:45`。

**返回数组下标含义**：
- `[0]` = 年（如 2026）
- `[1]` = 月（1-12）
- `[2]` = 日（1-31）
- `[3]` = 时（0-23）
- `[4]` = 分（0-59）
- `[5]` = 秒（0-59）
- `[6]` = 毫秒（恒为 0，因 DT 不带毫秒精度）

**与 DCTIME64 转换对比**：
- DCTIME64：EtherCAT epoch（2000-01-01）+ 纳秒精度，多 PLC 同步首选。
- DT：Unix epoch（1970-01-01）+ 秒精度，标准 IEC 类型，单 PLC 场景常用。

**调用语义**：纯函数——同一输入永远返回同一输出。

**典型用例**：把 `Tc2_System.NT_GetTime` 返回的 `DT` 时间转成 PackML 数组写入报警时间戳；或把 HMI 用户输入的日期时间直接转给 PML_AdminTime 的 ExternalPackMLTime 输入。

## 4. 错误码 / 返回值

返回 `ARRAY [0..6] OF DINT`：转换后的 PackML 日历时刻数组（毫秒分量恒为 0）。

无错误返回——纯计算函数。

## 5. 使用注意 / 常见坑

- `DT` 是**秒精度**——返回数组 [6]（毫秒）始终为 0。需要毫秒精度请用 `TIMESTRUCT_TO_PackMLTime`（来源 TIMESTRUCT 带毫秒）或 `DCTIME64_TO_PackMLTime`（纳秒）。（工程经验补充）
- DT 是"时刻（timestamp）"语义，转换后数组的"年"是日历年份；与 LTIME/TIME 的"时长"转换不同。
- DT 是否是 UTC 还是本地时由 PLC 配置决定——多时区项目需注意。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DT_TO_PackMLTime.TcPOU`](../examples/P_Demo_DT_TO_PackMLTime.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：HMI 显示"上次维护时间"用 DT 类型存储（DT#2026-05-15-10:00:00），现在要把它写入 PackTags 的某个时间字段以供 MES 使用。调本函数一行转换。
- **价值**：DT 是 IEC 标准类型、PackML 是 7 元素 DINT——两者直接互转的标准化封装，应用层避免手写月份/日期边界。
- **替代方案对比**：手写 DT 转 DINT 数组——需要处理闰年、月份天数、epoch 偏移；本函数封装好、与 PackML 标准对齐。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.3.3.2.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6302001931.html
- **相关**：`DCTIME64_TO_PackMLTime`（EtherCAT 纳秒时间戳）、`TIMESTRUCT_TO_PackMLTime`（结构体毫秒时间戳）、`PML_AdminTime`、`Tc2_System.NT_GetTime`（获取 DT 当前时间）
