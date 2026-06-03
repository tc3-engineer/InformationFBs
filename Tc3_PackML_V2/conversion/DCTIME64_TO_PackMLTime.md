# DCTIME64_TO_PackMLTime

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_PackML_V2` |
| Library Version | `1.2.4` |
| Type | `FUNCTION` |
| Category | `Conversion / Timestamp` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6301977739.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_DCTIME64_TO_PackMLTime.TcPOU`](../examples/P_Demo_DCTIME64_TO_PackMLTime.TcPOU) |

---

## 1. 功能简述

`DCTIME64_TO_PackMLTime` 把 EtherCAT **分布式时钟（Distributed Clock）64 位时间戳类型** `DCTIME64` 转换为 PackML 标准的 7 元素 `ARRAY [0..6] OF DINT` 时间数组。

DCTIME64 是 EtherCAT 主站的纳秒精度统一时间戳（从 2000-01-01 起算的纳秒数），用于多 PLC、多 IO 间的高精度同步。本函数把它解读为日历时刻（年/月/日/时/分/秒/毫秒）写入 PackML PackTag。

## 2. 接口定义

### 函数签名

```iecst
FUNCTION DCTIME64_TO_PackMLTime : ARRAY [0..6] OF DINT;
```

### VAR_INPUT

```iecst
VAR_INPUT
    Input         : DCTIME64;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Input` | `DCTIME64` | EtherCAT 分布式时钟时间戳（从 2000-01-01 00:00:00 起算的纳秒数）|

### VAR_OUTPUT

无（结果通过 FUNCTION 返回值给出）。

### VAR_IN_OUT

无。

## 3. 行为说明

`DCTIME64_TO_PackMLTime` 把 EtherCAT 分布式时钟时间戳解读为"日历时刻"语义并按 PackML 标准 7 元素 DINT 数组拆解。

**DCTIME64 语义**：EtherCAT 标准时间戳，从 2000-01-01 00:00:00 UTC 起算的纳秒数（DC epoch）。64 位有符号整数，可表示约 ±292 年。

**返回数组下标含义**：年[0] / 月[1] / 日[2] / 时[3] / 分[4] / 秒[5] / 毫秒[6]——对应日历时刻分量（绝对时刻不是时长）。

**与 LTIME/TIME 转换的关键区别**：
- LTIME/TIME 输入是"时长（duration）"，输出数组的"年"是"流逝了多少年"。
- DCTIME64 输入是"时刻（timestamp）"，输出数组的"年"是"日历年份如 2026"。

**调用语义**：纯函数——同一输入永远返回同一输出。

**典型用例**：从 EtherCAT 主站读取分布式时钟时间戳作为生产事件的精确时间标记，转换后写入 `PackTags.Admin.Alarm[i].DateTime`（或类似 PackML 时间字段）以替代 PLC 本地系统时间（Windows 系统时间精度低、多 PLC 不同步）。

## 4. 错误码 / 返回值

返回 `ARRAY [0..6] OF DINT`：转换后的 PackML 日历时刻数组。

无错误返回——纯计算函数。

## 5. 使用注意 / 常见坑

- DCTIME64 是 EtherCAT 标准纳秒时间戳，**不是 Unix epoch**——epoch 起点是 2000-01-01。手写转换需注意此偏移。（工程经验补充）
- DCTIME64 是"时刻"语义，转换后数组的"年"是日历年份（如 2026）；与 LTIME/TIME 转换的"时长"语义不同。
- 想得到 EtherCAT 主站时钟，需要 EtherCAT 已配置 DC 同步（XAE 里勾选"Enable Distributed Clocks"）。
- 用于把 EtherCAT 高精度时钟标记到 PackML 报警/事件，可代替本地 Windows 系统时间，多 PLC 时间一致性自动解决。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DCTIME64_TO_PackMLTime.TcPOU`](../examples/P_Demo_DCTIME64_TO_PackMLTime.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：多台 EtherCAT PLC 协同生产，每台 PLC 的 Windows 系统时间不严格同步（可能漂移几百毫秒）。但 EtherCAT 分布式时钟（DC）实现了纳秒级同步。生产事件的时间戳改用 DCTIME64 + 本函数转换写入 PackML 报警字段，跨 PLC 事件时序就能精确对齐。MES 拿到的事件时间戳跨设备可比。
- **价值**：本函数提供 EtherCAT DC 与 PackML 时间标准的桥接，多 PLC 高精度同步场景必备。`PML_AdminTime.stOptions.ExternalPackMLTime` + 本函数即可让 PackML 走 EtherCAT 时钟而非 Windows 系统时间。
- **替代方案对比**：用本地系统时间——多 PLC 不同步、事件时序混乱；自己写 DCTIME64 → 日历时刻转换——epoch 偏移、闰年规则容易错；本函数封装好、标准化。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V2_EN.pdf) §2.3.3.2.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v2/6301977739.html
- **相关**：`DT_TO_PackMLTime` / `TIMESTRUCT_TO_PackMLTime`（其他时刻输入）、`LTIME_TO_PackMLTime`（时长输入）、`PML_AdminTime.stOptions.ExternalPackMLTime`、Tc2_EtherCAT 库相关 DC 函数

## 9. 待确认项 (⚠️)

- DCTIME64 是否含闰秒处理、负值（2000 年前）的行为 PDF + InfoSys 均未明确。
