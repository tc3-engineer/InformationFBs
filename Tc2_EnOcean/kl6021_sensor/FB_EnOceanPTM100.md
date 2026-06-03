# FB_EnOceanPTM100

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EnOcean` |
| Library Version | `1.7.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `KL6021-0023 / Read PTM100` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173262603.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EnOceanPTM100.TcPOU`](../examples/P_Demo_FB_EnOceanPTM100.TcPOU) |

---

## 1. 功能简述

为 KL6021-0023 体系下挂的某一个 EnOcean **PTM100 自发电按键模块**做"友好化"解析。本 FB 上游接 `FB_EnOceanReceive` 的 `stEnOceanReceivedData`，按 `nTransmitterId` 过滤出指定 PTM100 模块的电报，直接把 8 个按键的当前状态展开成 `bSwitches : ARRAY [0..7] OF BOOL`，应用程序拿数组就能直接判按键。

PTM100 与 PTM200 / PTM250 的区别：PTM100 一次只能按下一个按键，但支持 **8 个按键**（PTM200/250 一次能按两个但只 4 键）。每接入一个 PTM100 模块都要创建一个独立实例，用 `nTransmitterId` 区分。

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
| `bEnable` | `BOOL` | `FALSE` | 电平使能；TRUE 时运行，FALSE 时所有输出复位为 0/FALSE。一般接 `NOT fbEnOceanReceive.bError AND fbEnOceanReceive.bEnable` |
| `tWatchdog` | `TIME` | — | 监视超时；本时间内必须有新电报到达否则 `bError` 置位。`T#0s` 表示停用 watchdog（电池模块离线判断常用 30 分钟到 24 小时） |
| `nTransmitterId` | `UDINT` | — | 要响应的 PTM100 模块 EnOcean ID（4 字节，模块出厂铭牌或学习时获取） |
| `stEnOceanReceivedData` | `ST_EnOceanReceivedData` | — | 接收数据结构，必接到上游 `fbEnOceanReceive.stEnOceanReceivedData`，本 FB 从中过滤匹配 `nTransmitterId` 的电报 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bSwitches : ARRAY [0..7] OF BOOL;
    bError    : BOOL := FALSE;
    nErrorId  : UDINT := 0;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bSwitches` | `ARRAY [0..7] OF BOOL` | PTM100 上 8 个按键的当前状态。同一时刻 PTM100 只能按下一个，所以正常情况下数组里至多一位为 TRUE |
| `bError` | `BOOL` | 出错时置 TRUE，常见是 watchdog 超时（模块没在 `tWatchdog` 内发新电报） |
| `nErrorId` | `UDINT` | 错误号（共用 KL6021-0023 错误码表，§4） |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：电平触发。`bEnable = TRUE` 持续保持时每个 PLC 周期都查 `stEnOceanReceivedData`：若 `bReceived = TRUE` 且 `nTransmitterId` 匹配自身配置，把数据字节按 PTM100 协议解码到 `bSwitches`，并重置 watchdog 计时。

**时序与状态机**：
1. `bEnable = TRUE` 后内部 watchdog 计时启动（如果 `tWatchdog > T#0s`）。
2. 每个 PLC 周期检查上游 `bReceived` 与 `nTransmitterId`；匹配 → 解码 → 更新 `bSwitches` → 复位 watchdog。
3. PTM100 按键释放后**没有显式"全部松开"电报**，本 FB 仅在收到下一帧时才知道按键变化——所以 `bSwitches` 反映的是"最近一次电报的按键状态"，不是"实时持续按下状态"。如要测脉冲，应用层应自己用 R_TRIG 取上升沿。
4. `tWatchdog` 内若没有新匹配电报 → `bError := TRUE`、`nErrorId := 16#0002`（Watchdog monitoring）、`bSwitches` 清 0。
5. 之后任何一帧匹配电报到达自动清错并重新输出按键。
6. `bEnable := FALSE` → 立即清所有输出、清错、停 watchdog。

**watchdog 用途**：自发电 PTM100 不带电池，按一下发一次电报，长时间不按是正常的——所以 `tWatchdog := T#0s`（停用）在很多场景下是合适的。watchdog 有意义的场景是"用 PTM100 做周期性心跳信号"或"判断按键模块物理离场（电报方向变更）"。

**典型陷阱**：① 多个 PTM100 共用同一 `nTransmitterId` → 无法区分；模块出厂前已分配唯一 ID。② 漏接上游 `stEnOceanReceivedData` → `bSwitches` 永远 FALSE 且 watchdog 一直超时报错。③ 把 `bEnable` 直接接 TRUE 而不监控上游 `bError` → 上游端子错误时本 FB 仍尝试解析陈旧数据。

## 4. 错误码 / 返回值

`bError = TRUE` 时 `nErrorId` 取以下值（共用 KL6021-0023 错误码表，PDF §4.1.1.3）：

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0001` | 校验错（上游 KL6021 端子层透传上来） | 检查 EnOcean 信号是否受干扰、模块距离是否过远 |
| `16#0002` | Watchdog monitoring | `tWatchdog` 内没有匹配 `nTransmitterId` 的新电报；可能模块离线、电池没电（PTM100 自发电不算，应用层重置 `bEnable` 一次） |
| `16#0003` | KL6023 缓冲区溢出 | 上游缓冲溢出，PLC 周期可能过长 |
| `16#0004` | 还没收到任何数据 | 刚启动；正常按键后会自动消失 |

## 5. 使用注意 / 常见坑

- **每个 PTM100 模块对应一个 FB_EnOceanPTM100 实例**。共用一个上游 FB_EnOceanReceive。
- **`bEnable` 必须接上游健康状态**：`bEnable := NOT fbEnOceanReceive.bError AND fbEnOceanReceive.bEnable`。否则上游端子级出错时本 FB 拿不到新数据，但 `bSwitches` 不会主动清 0 直到 watchdog 超时。
- **`bSwitches` 不是"实时按下状态"**：PTM100 按键松开没有专门的"零电报"，`bSwitches` 反映最近一帧的按键。如要"按下时 TRUE / 松开时 FALSE"语义，需要在 `bSwitches` 上接 R_TRIG / F_TRIG 自己整形。（工程经验补充）
- **`tWatchdog := T#0s` 用于 PTM100 这种被动按键场景**：PTM100 是手动按才发，不按时没有电报很正常，开 watchdog 会一直误报错。需要心跳的设备是 STM 系列温控之类。
- **同一空中区域多个 PTM100**：用不同 `nTransmitterId` 各开一个 FB 实例。`nTransmitterId` 在 PTM100 模块出厂时已固化，可在模块"learn"时由 FB_EnOcean_Search / FB_Rec_Teach_In 学到（不过那两个在 KL6581 体系下）。在 KL6021-0023 体系下学 ID 一般是用一次 `FB_EnOceanReceive` + 观察 `stEnOceanReceivedData.nTransmitterId`。（工程经验补充）
- **不要把 FB_EnOceanPTM100 与 FB_EnOceanPTM200 混用同一模块**：协议字节布局不同。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EnOceanPTM100.TcPOU`](../examples/P_Demo_FB_EnOceanPTM100.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_EnOceanPTM100
VAR
    fbEnOceanReceive : FB_EnOceanReceive;
    fbPTM100_A       : FB_EnOceanPTM100;
    stEnOceanInData  AT %I* : ST_EnOceanInData;
    stEnOceanOutData AT %Q* : ST_EnOceanOutData;
    nMyPTM100Id      : UDINT := 16#000000C4;   // 模块铭牌或学习得到
    abButtonStates   : ARRAY [0..7] OF BOOL;
END_VAR

fbEnOceanReceive(
    bEnable          := TRUE,
    stEnOceanInData  := stEnOceanInData,
    stEnOceanOutData := stEnOceanOutData
);

fbPTM100_A(
    bEnable               := NOT fbEnOceanReceive.bError AND fbEnOceanReceive.bEnable,
    tWatchdog             := T#0s,
    nTransmitterId        := nMyPTM100Id,
    stEnOceanReceivedData := fbEnOceanReceive.stEnOceanReceivedData,
    bSwitches             => abButtonStates
);
```

## 7. 业务场景与实际价值

- **场景**：会议室 / 走廊照明开关 / 仓库巡检确认按钮。布线成本高或现有墙面无法开槽布线，采用 EnOcean PTM100 自发电按键贴墙即可——按一下按键自身的压电产生几毫焦能量发送一帧电报，电池零维护。8 键 PTM100 适合"场景模式选择面板"（全亮 / 调光 / 关灯 / 报警 4 组 × 2 键）。
- **价值**：把"识别 transmitter ID / 按 PTM100 协议解码 8 键 / 维护 watchdog"封装为单 FB。应用层只看 `bSwitches[]`，与有线按键无差异。
- **替代方案对比**：
  - 有线按键 + KL1xxx DI 端子：成本低，但要布线 + 开墙，已建工程不可能改
  - 蓝牙 / Wi-Fi 按键：需电池且要 IT 网络配合，工业现场不常用
  - PTM200/250：少 4 键但支持双键同按，适合场景模式 + 调光（按住）
  - **本 FB**：PTM100 是 8 键单按场景的标准选项

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf) §4.1.1.2.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173262603.html
- **相关**：`FB_EnOceanReceive`（上游必备）、`FB_EnOceanPTM200`（4 键双按变种）、`ST_EnOceanReceivedData`（接收结构）、`E_EnOceanSensorType`（PTM/STM 类型枚举）
