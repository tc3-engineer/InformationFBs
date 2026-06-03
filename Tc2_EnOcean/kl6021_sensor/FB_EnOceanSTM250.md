# FB_EnOceanSTM250

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EnOcean` |
| Library Version | `1.7.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `KL6021-0023 / Read STM250` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173268747.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EnOceanSTM250.TcPOU`](../examples/P_Demo_FB_EnOceanSTM250.TcPOU) |

---

## 1. 功能简述

为 KL6021-0023 体系下挂的某一个 EnOcean **STM250 窗 / 门磁模块**做友好化解析。STM250 是带磁簧（reed contact）的开关传感器，加一个磁铁——磁铁与传感器接近时 reed contact 闭合（窗 / 门关），分开时断开（开）。模块还带一个学习按键。本 FB 把这两位状态直接出 `bState`（reed 是否闭合）+ `bLearn`（学习按键是否按下）。

每个 STM250 模块对应一个独立实例，用 `nTransmitterId` 区分。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bEnable               : BOOL := FALSE;
    tWatchdog             : TIME;
    nTransmitterId        : UDINT;
    stEnOceanReceivedData : ST_EnOceanReceivedData;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bEnable` | `BOOL` | `FALSE` | 电平使能 |
| `tWatchdog` | `TIME` | — | watchdog 超时；STM250 仅在状态变化时发，且没人开关时长时间不发，建议 `T#0s`（停用） |
| `nTransmitterId` | `UDINT` | — | 该 STM250 模块的 EnOcean ID（4 字节） |
| `stEnOceanReceivedData` | `ST_EnOceanReceivedData` | — | 必接 `fbEnOceanReceive.stEnOceanReceivedData` |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bState   : BOOL;
    bLearn   : BOOL;
    bError   : BOOL := FALSE;
    nErrorId : UDINT := 0;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bState` | `BOOL` | STM250 上的 reed contact 闭合（窗 / 门关）时 TRUE；断开（窗 / 门开）时 FALSE |
| `bLearn` | `BOOL` | 学习按键被按下时 **FALSE**（注意 PDF 描述就是这样：reverse-active）。其他时候 TRUE |
| `bError` | `BOOL` | watchdog 超时 / 上游错时 TRUE |
| `nErrorId` | `UDINT` | 错误号（KL6021-0023 错误码表） |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：电平触发。STM250 是事件触发型——reed contact 状态变化（窗 / 门打开或关闭）才发一帧，状态保持时不发，所以 watchdog 应慎用。`bState` 反映最近一帧的 reed 状态。

**事件 vs watchdog**：与按键 PTM 类似，STM250 没人动时长期不发，开 watchdog 会一直误超时。**`tWatchdog := T#0s` 是默认推荐**。如果想监视模块离线 / 电池没电，可以借鉴"心跳冗余"：用另一组冗余 STM250 配合或 + 定期手动测试程序。

**`bLearn` 的反向语义**：PDF 描述是"learn 按键被激活时 `bLearn` 变为 FALSE"——与一般"按下 = TRUE"逻辑相反。原因是 EnOcean 协议中 STM250 的 LRN 位在按下时是 0，未按是 1，本 FB 直通该 bit 没做反相。**应用层用 `NOT fbSTM250.bLearn` 取"学习按键按下"语义更直观**。（工程经验补充）

**初始状态**：刚加电时 `bState` 保持 FALSE 直到收到第一帧。第一次操作 STM250 时即可获得真实状态。

**典型陷阱**：① 用 `tWatchdog := T#1h` → 1 小时没人开关窗就报错；门窗状态稳定不变是常态，不要用 watchdog。② 直接拿 `bLearn = TRUE` 判学习按下 → 反了，要 `NOT bLearn`。③ 多个 STM250 共用一个 FB 实例 → 不可能（用 `nTransmitterId` 区分要分别建实例）。

## 4. 错误码 / 返回值

`bError = TRUE` 时 `nErrorId` 同 KL6021-0023 通用错误表（§4.1.1.3）：

| `nErrorId` | 含义 |
|---|---|
| `16#0000` | 无错 |
| `16#0001` | 校验错 |
| `16#0002` | Watchdog（一般场景不开） |
| `16#0003` | KL6023 缓冲区溢出 |
| `16#0004` | 还没收到数据（刚启动且未操作） |

## 5. 使用注意 / 常见坑

- **`tWatchdog := T#0s`**：STM250 状态不变不发，长时间稳定开 / 关属正常，开 watchdog 会一直误报。
- **`bLearn` 反相语义**：按下学习时 `bLearn = FALSE`。
- **初始状态未知**：上电后到第一次操作之前 `bState` 是 FALSE，不代表"窗关闭"。可在 HMI 上加"未确认"标签直到收到第一帧。
- **磁铁安装位置**：STM250 是磁簧式，磁铁与传感器对齐距离要 ≤ 模块手册规定（通常 8-15 mm），太远会反复触发"已开 → 已关"。（工程经验补充）
- **报警逻辑用上升沿触发**：例如"窗开 = 触发警报"用 `F_TRIG(bState)`（关 → 开沿），不要用 `NOT bState` 电平，避免上电时"未收到帧而 bState = FALSE"被误判为窗开。
- **多个窗 / 门并列**：常见做法是用一片 KL6021-0023 + 数十个 STM250 + 各自一个 FB_EnOceanSTM250 实例。也可以混插 PTM200 / STM100 等其它 EnOcean 设备共用同一 KL6021。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EnOceanSTM250.TcPOU`](../examples/P_Demo_FB_EnOceanSTM250.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_EnOceanSTM250
VAR
    fbEnOceanReceive : FB_EnOceanReceive;
    fbBack门         : FB_EnOceanSTM250;
    stEnOceanInData  AT %I* : ST_EnOceanInData;
    stEnOceanOutData AT %Q* : ST_EnOceanOutData;
    nBackDoorId      : UDINT := 16#000008CA;
    bBackDoorClosed  : BOOL;
END_VAR
fbEnOceanReceive(bEnable := TRUE, stEnOceanInData := stEnOceanInData, stEnOceanOutData := stEnOceanOutData);
fbBack门(
    bEnable               := NOT fbEnOceanReceive.bError AND fbEnOceanReceive.bEnable,
    tWatchdog             := T#0s,
    nTransmitterId        := nBackDoorId,
    stEnOceanReceivedData := fbEnOceanReceive.stEnOceanReceivedData,
    bState                => bBackDoorClosed
);
```

## 7. 业务场景与实际价值

- **场景**：仓库后门 / 应急通道窗的开闭监视。无法布线（开/关动作磨损线缆），传统方案要装机械开关 + 拖线。STM250 + 一块磁铁，零布线、自发电、电池寿命 10 年以上。
- **价值**：把磁簧状态 + 学习按键 + 模块识别 + 上游健康度联动封装为单 FB；应用层一个 `bState` 就拿到门窗状态，配合 F_TRIG 即可触发报警 / 灯效 / SCADA 事件。
- **替代方案对比**：
  - 机械接近开关 + KL1xxx DI：要布线，开关本身寿命有限
  - Hall sensor 接 KL3xxx AI：成本高且需电源
  - 用 4G/Wi-Fi 门磁：需电池 + 网络，工业现场不可靠
  - **本 FB**：低成本、无线、零维护，是 EnOcean 门窗监视场景的事实标准

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf) §4.1.1.2.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173268747.html
- **相关**：`FB_EnOceanReceive`（上游必备）、`FB_EnOceanPTM200`（用按键变种门磁开关时）、`FB_Rec_1BS`（KL6581 体系等价的门磁接收）
