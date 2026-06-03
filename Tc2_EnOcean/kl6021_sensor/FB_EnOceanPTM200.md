# FB_EnOceanPTM200

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EnOcean` |
| Library Version | `1.7.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `KL6021-0023 / Read PTM200` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173264139.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EnOceanPTM200.TcPOU`](../examples/P_Demo_FB_EnOceanPTM200.TcPOU) |

---

## 1. 功能简述

为 KL6021-0023 体系下挂的某一个 EnOcean **PTM200 / PTM250 自发电按键模块**做友好化解析。本 FB 上游接 `FB_EnOceanReceive` 的 `stEnOceanReceivedData`，按 `nTransmitterId` 过滤指定模块的电报，把 4 个按键的状态展开成 `bSwitches : ARRAY [0..3] OF BOOL`。

PTM200/250 与 PTM100 的差异：**只有 4 键**（PTM100 是 8 键），但**支持同时按下两键**（用于"按住调光"或"双键场景"）。每接入一个 PTM200/250 模块都要创建一个独立实例，用 `nTransmitterId` 区分。

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
| `bEnable` | `BOOL` | `FALSE` | 电平使能，一般接 `NOT fbEnOceanReceive.bError AND fbEnOceanReceive.bEnable` |
| `tWatchdog` | `TIME` | — | 监视超时；本时间内必须有新电报否则报错。`T#0s` 停用 watchdog |
| `nTransmitterId` | `UDINT` | — | 要响应的 PTM200/250 模块 EnOcean ID（4 字节） |
| `stEnOceanReceivedData` | `ST_EnOceanReceivedData` | — | 必接 `fbEnOceanReceive.stEnOceanReceivedData` |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bSwitches : ARRAY [0..3] OF BOOL;
    bError    : BOOL := FALSE;
    nErrorId  : UDINT := 0;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bSwitches` | `ARRAY [0..3] OF BOOL` | PTM200/250 上 4 键的当前状态。最多两键同时为 TRUE（PTM200/250 协议特性） |
| `bError` | `BOOL` | watchdog 超时 / 上游端子错时为 TRUE |
| `nErrorId` | `UDINT` | 错误号（KL6021-0023 错误码表） |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：电平触发。`bEnable = TRUE` 期间每个 PLC 周期检查上游电报，匹配 `nTransmitterId` 时按 PTM200 协议解码 4 键并刷新 `bSwitches`，同时复位 watchdog。

**PTM200/250 协议特性**：支持"按下"与"释放"两种事件（与 PTM100 不同）。`bSwitches` 在收到"按下"电报后为相应位 TRUE，收到"释放"电报后清 0。如果同时按下两个键，两位会同时为 TRUE。

**watchdog 语义**：与 PTM100 相同——`T#0s` 停用，非零值时该时间内无匹配电报报 `16#0002` 错。PTM200/250 按一下发"按下"+"释放"两帧，没人操作就不发，多数场景 `T#0s` 合适。

**`bSwitches` 与"实时按住"语义**：PTM200/250 的"按下"和"释放"电报让 `bSwitches` 接近实时按住电平——比 PTM100 好用很多。但仍要注意：电波被遮挡导致释放电报丢失时 `bSwitches` 会"卡死"在按下，可借助 `tWatchdog` 间接发现（10 秒不变化则疑似异常）。

**典型陷阱**：① 误把 PTM200/250 接入 `FB_EnOceanPTM100` 实例 → 协议解码错位，键位混乱。② 把 PTM200/250 实例的 `bSwitches[]` 当成长时间按住信号控制电机持续点动 → 一旦释放帧丢失会"飞车"，应额外加超时保护。

## 4. 错误码 / 返回值

`bError = TRUE` 时 `nErrorId` 取值与 §4.1.1.3 通用错误表一致：

| `nErrorId` | 含义 | 处理建议 |
|---|---|---|
| `16#0000` | 无错 | — |
| `16#0001` | 校验错 | 信号干扰或距离过远 |
| `16#0002` | Watchdog | 设置时间内无匹配电报，模块可能离场 |
| `16#0003` | KL6023 缓冲区溢出 | PLC 周期太长或电报密度过高 |
| `16#0004` | 还没收到任何数据 | 启动初期，按一下按键即清除 |

## 5. 使用注意 / 常见坑

- **每个 PTM200/250 模块对应一个实例**，共用上游 `FB_EnOceanReceive`。
- **同模块支持 4 + 4 摇杆**：PTM200 物理上是两个双向摇杆（上 / 下），映射到 4 键位。`bSwitches[0]/[1]` 通常对应摇杆 1 的上/下，`[2]/[3]` 对应摇杆 2。具体映射看模块手册（Eltako / PEHA / Omnio 等厂商可能不同）。（工程经验补充）
- **用于调光**：常见用法是"按住一键调光"——本 FB 的 `bSwitches` 在按下时 TRUE，在释放时 FALSE，可以直接驱动一个 RAMP 计数器。但仍要 `t_DimSafetyTimeout := T#3S`，电波丢失时强制停止调光。（工程经验补充）
- **不要把 PTM200 与 PTM250 区别对待**：两者 EnOcean 协议层一致，本 FB 同时支持。
- **`tWatchdog := T#0s` 适合按键场景**，非零值适合监视固定位置按键模块"是否还在线"。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EnOceanPTM200.TcPOU`](../examples/P_Demo_FB_EnOceanPTM200.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_EnOceanPTM200
VAR
    fbEnOceanReceive : FB_EnOceanReceive;
    fbDimmer         : FB_EnOceanPTM200;
    stEnOceanInData  AT %I* : ST_EnOceanInData;
    stEnOceanOutData AT %Q* : ST_EnOceanOutData;
    nDimmerId        : UDINT := 16#000000C6;
    abDimmerBtns     : ARRAY [0..3] OF BOOL;
END_VAR

fbEnOceanReceive(
    bEnable          := TRUE,
    stEnOceanInData  := stEnOceanInData,
    stEnOceanOutData := stEnOceanOutData
);
fbDimmer(
    bEnable               := NOT fbEnOceanReceive.bError AND fbEnOceanReceive.bEnable,
    tWatchdog             := T#0s,
    nTransmitterId        := nDimmerId,
    stEnOceanReceivedData := fbEnOceanReceive.stEnOceanReceivedData,
    bSwitches             => abDimmerBtns
);
```

## 7. 业务场景与实际价值

- **场景**：办公室 / 酒店客房调光开关。PTM200 摇杆按住向上 = 升亮、向下 = 降暗，松开停止。比 PTM100 适合连续调节类操作。也常见用于"卷帘上 / 下 / 停"场景。
- **价值**：把摇杆按下 / 释放协议解码 + watchdog 监视封装为单 FB；应用层直接看 4 位数组就能搞调光、卷帘、空调风速等连续调节工艺。
- **替代方案对比**：
  - 有线摇杆 + DI 端子：要墙线，已建场景不可改
  - 用 PTM100：8 键单按，不能"按住"，不适合调光
  - 用 STM100 旋钮：纯调位置，不能上 / 下增减
  - **本 FB**：4 键双按 + 按住松开协议，是 EnOcean 调光场景的首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf) §4.1.1.2.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173264139.html
- **相关**：`FB_EnOceanReceive`（上游必备）、`FB_EnOceanPTM100`（8 键单按变种）、`ST_EnOceanReceivedData`
