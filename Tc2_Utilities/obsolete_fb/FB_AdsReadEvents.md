# FB_AdsReadEvents

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `[obsolete]` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3524194955.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified · deprecated` |
| Example | [`examples/P_Demo_FB_AdsReadEvents.xml`](../examples/P_Demo_FB_AdsReadEvents.xml) |

---

## 1. 功能简述

⚠️ **本 FB 已弃用**。PDF 明确写 "Available up to TwinCAT 3.1 Build 4024"——更新到 Build 4024 之后的 TwinCAT 系统不应再调本 FB。**新代码请用 Tc3_EventLogger 库提供的 `FB_TcAlarm` / `FB_TcMessage` 加 `FB_TcEventLogger` 监听器**，那一套替代旧的 ADS 轮询接口。

`FB_AdsReadEvents` 通过 ADS 查询旧版 EventLogger 的"当前活动消息"列表，把它们填入一个大小为 80 的 `aEvents` 数组，方便绑定到可视化的 Event table 控件做事件展示。FB 内部按 `tRefreshTime` 周期重读，按 `nLanguageId` 决定取哪种语言的消息文本，按 `eDateAndTimeFormat` 决定时间戳显示风格。

**文本长度限制**（PDF 明确）：消息文本 ≤ 255 字符可完整输出；256–1023 字符会被截断；> 1023 字符直接报错。这是该旧接口被淘汰的关键原因之一——TC3 现代事件可以远超这个长度。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId             : T_AMSNetId;
    bReadEvents        : BOOL;
    nLanguageId        : DWORD;
    eDateAndTimeFormat : E_DateAndTimeFormat;
    tRefreshTime       : TIME;
    tTimeout           : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sNetId` | `T_AMSNetId` | 目标控制器的 AmsNetId。空字符串代表本机 |
| `bReadEvents` | `BOOL` | 使能读消息。下降沿同时复位 `bError` / `nErrorId`（PDF 明确） |
| `nLanguageId` | `DWORD` | 语言 ID（决定取哪种语言的消息文本） |
| `eDateAndTimeFormat` | `E_DateAndTimeFormat` | 时间戳格式：`de_De`（dd.MM.yyyy hh:mm:ss 24h）/ `en_GB`（dd/MM/yyyy hh:mm:ss 12h）/ `en_US`（MM/dd/yyyy hh:mm:ss 12h） |
| `tRefreshTime` | `TIME` | 消息查询周期。设短了 ADS 负担重，设长了延迟大 |
| `tTimeout` | `TIME` | ADS 超时阈值。超时会触发 `bError` |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    aEvents         : ARRAY[1..80] OF ST_ReadEvent;
    nNumberOfEvents : UDINT;
    bBusy           : BOOL;
    bDone           : BOOL;
    bError          : BOOL;
    nErrorId        : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `aEvents` | `ARRAY[1..80] OF ST_ReadEvent` | 读到的消息数组。最多 80 条，超出部分被丢弃。`ST_ReadEvent` 包含事件 ID / 文本 / 时间戳等字段（详见 `ST_ReadEvent` 类型文档） |
| `nNumberOfEvents` | `UDINT` | 实际填入 `aEvents` 的条数。0 表示当前无活动消息 |
| `bBusy` | `BOOL` | 一次 ADS 查询执行中为 `TRUE` |
| `bDone` | `BOOL` | FB 当前不忙、至少完成过一次查询时为 `TRUE` |
| `bError` | `BOOL` | 出错时 `TRUE` |
| `nErrorId` | `UDINT` | ADS 错误号（详见 Tc2_Utilities ADS 错误号表） |

### VAR_IN_OUT

无。

## 3. 行为说明

`bReadEvents := TRUE` 时 FB 进入周期性查询模式。每个 `tRefreshTime` 周期 FB 发起一次 ADS 读到目标控制器的 EventLogger，把当前活动消息填入 `aEvents`。`bBusy` 标记正在通讯中，`bDone` 在拿到回执后翻 `TRUE`。下一个 `tRefreshTime` 周期到达后再发起一次新的读取。

**`bReadEvents` 下降沿**特殊行为（PDF 明确）：使能撤销时 FB 不仅停止读取，**同时把 `bError` / `nErrorId` 复位**。这便于业务侧用"重新使能"作为简易复位手段——不像很多 FB 需要单独的 `bReset`。

`nNumberOfEvents` 反映本次查询填入的消息数。`aEvents[1..nNumberOfEvents]` 是有效数据，`aEvents[nNumberOfEvents+1..80]` 是上一次的残留值或未初始化（**不要**索引到 `nNumberOfEvents` 以外）。

**长度截断**：单条消息文本 ≤ 255 字符 → 完整；256-1023 字符 → 截断到 255；> 1023 字符 → FB 报错（`bError := TRUE`，`nErrorId` 反映具体码 ⚠️ PDF 未给精确值）。

**ADS 超时**：`tTimeout` 期满未收到回执也会触发 `bError`。通讯不稳的远程链路应把 `tTimeout` 调大。

**与 Tc3_EventLogger 的关系**：本 FB 是 TC2 时代的 EventLogger 客户端接口；TwinCAT 3 Build 4024 之后的 EventLogger 已经重做（基于 IEvent 接口、UTF-8 消息、无 80 条上限、无字符长度上限）。新接口在 Tc3_EventLogger 库——本 FB 不能读新 EventLogger 的事件。**新工程一律去 Tc3_EventLogger**。

## 4. 错误码 / 返回值

`bError` / `nErrorId` 输出对：

| `bError` | 含义 |
|---|---|
| `FALSE` | 通讯正常 |
| `TRUE` | 出错，`nErrorId` 给出具体码 |

⚠️ PDF 标注错误码"详见 Tc2_Utilities ADS 错误号表 §410 节"，本文档未具体列出每个码——常见可能：
- `0x745` (1861) ADS timeout
- `0x701-0x70F` 系列 ADS 调用语义错误（NETID 错、目标无 EventLogger 服务等）
- 文本超 1023 字符触发的内部检查错（PDF 未列具体码 ⚠️）

## 5. 使用注意 / 常见坑

- **本 FB 已弃用** —— 新代码改用 **Tc3_EventLogger** 库的 `FB_TcAlarm` / `FB_TcMessage`，更现代、无长度限制、支持 UTF-8。本文档仅为维护 TwinCAT 3.1 Build 4024 之前的旧工程而保留。
- **80 条上限是硬限制**：现场事件多于 80 条时后续被丢弃 → 漏报警。要展示全部事件改用 Tc3_EventLogger 的现代查询接口。
- **字符长度坑**：256+ 字符消息会被默默截断（除非 > 1023 报错）。配方 / 故障描述这种长文本不适合用本 FB。
- **`tRefreshTime` 不能太短**：每周期触发一次 ADS 全量查询，对目标控制器负担不小。建议 ≥ 500 ms。
- **`bReadEvents` 下降沿复位错误**：这是省了 `bReset` 引脚的设计，但也意味着"我只是想暂停一下"时会丢错误信息。需保留错误状态请自己用业务变量缓存。
- **跨网络读取要把 `tTimeout` 调大**：远程链路的 ADS 抖动可能让默认值（通常 5 s）也不够，看到 `bError` + `nErrorId` 是超时码先调大试试。
- **`aEvents` 索引从 1 开始**：与 IEC 习惯一致，但 C / Python 出身的工程师容易写 `aEvents[0]` 导致越界。
- **新事件先到 / 旧事件先到无保证**：PDF 未约束 `aEvents` 内的事件顺序——业务侧要按时间戳排序请自己排。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_AdsReadEvents.xml`](../examples/P_Demo_FB_AdsReadEvents.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：维护一个 TwinCAT 3.1 Build 4022 的旧产线，HMI 用一个 Event Table
//       控件显示当前活动报警。本 FB 是把控制器 EventLogger 里的活动消息
//       拉到 PLC 端的标准接口——尽管已弃用，旧工程仍要继续维护。
//
// 价值：保留旧工程的事件展示功能。如果是新工程，请改用 Tc3_EventLogger。
//
// 验证：登录后置 bEnableEventQuery := TRUE，nReportedEvents 应反映目标控
//       制器当前活动报警数；触发一个测试报警（在另一个程序里调旧版 ADSLOG
//       或事件发布）→ nReportedEvents 应在 1-2 个 tRefreshTime 内增加。
//       撤销 bEnableEventQuery → bQueryError 与 nQueryErrorId 复位为 0。
PROGRAM P_Demo_FB_AdsReadEvents
VAR
    fbAdsReadEvents       : FB_AdsReadEvents;
    sLocalNetId           : T_AMSNetId := '';          // 本机
    bEnableEventQuery     : BOOL := FALSE;             // 在线 TRUE 开始查询
    nLanguageId           : DWORD := 1033;             // en_US
    eTimeFormat           : E_DateAndTimeFormat := E_DateAndTimeFormat.en_US;
    tRefreshPeriod        : TIME := T#1S;
    tAdsTimeout           : TIME := T#5S;
    aActiveEvents         : ARRAY[1..80] OF ST_ReadEvent;
    nReportedEvents       : UDINT;
    bQueryBusy            : BOOL;
    bQueryDone            : BOOL;
    bQueryError           : BOOL;
    nQueryErrorId         : UDINT;
END_VAR

fbAdsReadEvents(
    sNetId             := sLocalNetId,
    bReadEvents        := bEnableEventQuery,
    nLanguageId        := nLanguageId,
    eDateAndTimeFormat := eTimeFormat,
    tRefreshTime       := tRefreshPeriod,
    tTimeout           := tAdsTimeout,
    aEvents            => aActiveEvents,
    nNumberOfEvents    => nReportedEvents,
    bBusy              => bQueryBusy,
    bDone              => bQueryDone,
    bError             => bQueryError,
    nErrorId           => nQueryErrorId
);
```

## 7. 业务场景与实际价值

- **场景**：仅适用于维护 TwinCAT 3.1 Build 4024 **之前**的旧产线 / 旧 HMI 工程。这类工程通常因为关联了大量 visualization / 报表 / MES 接口，整体迁移代价高，所以原地维护。
- **价值**：维护性——让旧工程继续工作，不要求大改造。
- **替代方案对比**：
  - **新工程**：用 Tc3_EventLogger 的 `FB_TcAlarm` / `FB_TcMessage` + `FB_TcEventLogger` 订阅机制，无 80 条上限、无字符长度限制、支持多语言、与 TwinCAT HMI 原生集成
  - **半新工程**（同时维护旧 + 新事件）：旧逻辑用本 FB，新逻辑用 Tc3_EventLogger；两套并行，HMI 各显示一块
  - **TC2 老工程**：本 FB 是唯一接口

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3524194955.html
- **替代库**：`Tc3_EventLogger` —— 现代事件订阅接口
- **相关类型**：`ST_ReadEvent`（事件结构体）、`E_DateAndTimeFormat`（时间戳格式枚举）
