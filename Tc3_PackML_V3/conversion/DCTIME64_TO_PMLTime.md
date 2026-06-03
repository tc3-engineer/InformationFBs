# DCTIME64_TO_PMLTime

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
| Example | [`examples/P_Demo_DCTIME64_TO_PMLTime.TcPOU`](../examples/P_Demo_DCTIME64_TO_PMLTime.TcPOU) |

---

## 1. 功能简述

`DCTIME64_TO_PMLTime` 把 EtherCAT 分布式时钟（Distributed Clock）64 位时间戳 `T_DCTIME64`（基于 2000-01-01 起算的纳秒）转换为 PackML 标准的 `ST_PMLDateAndTime` 结构体（`Year` / `Month` / `Day` / `Hour` / `Minute` / `Second` / `mSec`）。

**V3 与 V2 的关键差异**：V2 版本（`DCTIME64_TO_PackMLTime`）返回 `ARRAY [0..6] OF DINT` 数组；V3 改为返回**结构体** `ST_PMLDateAndTime`——按字段名访问、可读性更好。

主要用于多 PLC 时钟同步场景：EtherCAT 主站把 DC 时间分发到所有从站和 PLC，每个 PLC 拿到统一的 DCTIME64 后转成 PackML 时间结构写到本地 PackTags.Admin.PlcDateTime；这样 MES 收到的所有机器报警时间戳全部对齐。

## 2. 接口定义

### 函数签名

```iecst
FUNCTION DCTIME64_TO_PMLTime : ST_PMLDateAndTime
```

### VAR_INPUT

```iecst
VAR_INPUT
    Input         : DCTIME64;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Input` | `DCTIME64` | 要转换的时间（EtherCAT 分布式时钟 64 位纳秒戳，2000-01-01 epoch）|

### VAR_OUTPUT

无（结果通过 `FUNCTION` 返回值给出）。

### VAR_IN_OUT

无。

## 3. 行为说明

`DCTIME64_TO_PMLTime` 把"时刻（timestamp）"语义的 `T_DCTIME64` 转换为 PackML 标准 `ST_PMLDateAndTime` 结构体。`T_DCTIME64` 是 Beckhoff EtherCAT 主站分发的 64 位纳秒时间戳，epoch 是 2000-01-01 00:00:00 UTC。

**DCTIME64 epoch 重要差异**：与 UNIX epoch（1970-01-01）不同，DCTIME64 基于 2000-01-01——本函数内部完成 epoch 转换并填入结构体的日历字段。

**与 LTIME 转换对比**：
- `LTIME_TO_PMLTime`：把"时长"拆为流逝量（Year=流逝多少年）
- `DCTIME64_TO_PMLTime`：把"时刻"转为日历表示（Year=2026 等绝对值）

**返回结构体字段含义**：
- `Year` = 日历年份（如 2026）
- `Month` = 1-12
- `Day` = 1-31
- `Hour` = 0-23
- `Minute` = 0-59
- `Second` = 0-59
- `mSec` = 0-999

**调用语义**：纯函数——同一输入永远返回同一输出，无副作用。

**典型用法**：把 EtherCAT 主站调用 `F_GetCurDcTaskTime64()` 返回的 `T_DCTIME64` 时间戳一次性转成 PackML 结构，写入 PackTags.Admin.PlcDateTime 供 `FB_PMLAdminAlarm` 各方法使用。

## 4. 错误码 / 返回值

返回 `ST_PMLDateAndTime` 结构体：转换后的 PackML 日历时刻结构。

无错误返回——纯计算函数。极端时间值（如 2000 年之前或几百年之后）的行为 PDF 未列。

## 5. 使用注意 / 常见坑

- DCTIME64 是 UTC 时间——返回结构体也是 UTC。如果 HMI 要显示本地时间，调用方需自行加时区偏移。（工程经验补充）
- DCTIME64 的 epoch 是 2000-01-01，不是 UNIX 1970-01-01——本函数内部已处理，应用层不要再额外减 30 年。
- 与 V2 (`DCTIME64_TO_PackMLTime` 返回数组) 不兼容——升级时改字段访问。
- 多 PLC 同步场景下，EtherCAT DC 同步精度可达 100 ns 量级，全机时间戳完全对齐。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DCTIME64_TO_PMLTime.TcPOU`](../examples/P_Demo_DCTIME64_TO_PMLTime.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 详见 examples 目录下的 .TcPOU 文件
```

## 7. 业务场景与实际价值

- **场景**：一条产线 5 个 PLC + 50 个 EtherCAT 从站，要求所有报警时间戳精确到毫秒对齐（用于事件序列分析）。EtherCAT 主站统一分发 DC 时间，每个 PLC 用本函数把 DCTIME64 转成 PackML 时间结构写入 `PackTags.Admin.PlcDateTime`。MES 收到的所有报警时间戳全部同步，事件序列分析准确。
- **价值**：用本函数让 PackML 标准时间字段直接消费 EtherCAT 分布式时钟，多机时间一致性免费获得。不必自己维护 NTP 客户端或写时钟同步逻辑。
- **替代方案对比**：每个 PLC 用本地 Windows 时间 + NTP——精度毫秒级、且每个 PLC 时间戳不严格对齐；EtherCAT DC 是亚微秒级硬件同步。本函数是连接 EtherCAT DC 与 PackML 标准的关键桥梁。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_PackML_V3_EN.pdf) §4.1.2.1
- **InfoSys 参考 topic（返回类型）**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_packml_v3/16003245451.html （ST_PMLDateAndTime 数据结构 topic；V3 本 FUNCTION 自身 InfoSys topic 页面公网未检索到，故 InfoSys-checked 标 ⚠️ not-on-infosys）
- **相关**：`DT_TO_PMLTime`（IEC DT 输入）、`TIMESTRUCT_TO_PMLTime`（Beckhoff TIMESTRUCT 输入）、`FB_PMLAdminTime.stOptions.ExternalPackMLTime`、`Tc2_EtherCAT.F_GetCurDcTaskTime64`（获取 DCTIME64）、`ST_PMLDateAndTime`

## 9. 待确认项 (⚠️)

- 2000 年之前或极远未来的 DCTIME64 值的转换行为 PDF 未列。
- V3 InfoSys 本 FUNCTION 自身 topic URL 未在公网检索结果中找到，已标 `⚠️ not-on-infosys`。
