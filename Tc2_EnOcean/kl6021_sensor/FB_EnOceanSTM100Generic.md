# FB_EnOceanSTM100Generic

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EnOcean` |
| Library Version | `1.7.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `KL6021-0023 / Read STM100 generic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173267211.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EnOceanSTM100Generic.TcPOU`](../examples/P_Demo_FB_EnOceanSTM100Generic.TcPOU) |

---

## 1. 功能简述

为 KL6021-0023 体系下挂的某一个 EnOcean **STM100 模块**做"通用版"友好化解析——与已废弃的 `FB_EnOceanSTM100` 相比，本 FB **不做字段硬解码**，直接把 STM100 的 4 字节原始用户数据按厂家手册原样输出 `nDataBytes : ARRAY [0..3] OF BYTE`。

适用场景：STM100 基础模块 + 各厂商不同的协议变种（Eltako STM100、Thermokon SR-MDS 等）。各家的 4 字节具体含义不同，本 FB 把"识别 ID + 维护 watchdog + 字节抽取"做完，应用层按各自手册解码字节。**新工程推荐用本 FB 而不是固定字段版的 `FB_EnOceanSTM100`**。

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
| `bEnable` | `BOOL` | `FALSE` | 电平使能；FALSE 时所有输出清 0 |
| `tWatchdog` | `TIME` | — | watchdog 超时；STM100 周期发送，建议 `T#1h` 监控在线状态 |
| `nTransmitterId` | `UDINT` | — | 该 STM100 的 EnOcean ID |
| `stEnOceanReceivedData` | `ST_EnOceanReceivedData` | — | 必接 `fbEnOceanReceive.stEnOceanReceivedData` |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    nDataBytes : ARRAY [0..3] OF BYTE;
    bError     : BOOL := FALSE;
    nErrorId   : UDINT := 0;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `nDataBytes` | `ARRAY [0..3] OF BYTE` | STM100 模块本帧 4 字节原始数据。各字节含义参见**模块厂家手册**（Beckhoff 不在此做约定） |
| `bError` | `BOOL` | watchdog 超时 / 上游端子错时为 TRUE |
| `nErrorId` | `UDINT` | 错误号（KL6021-0023 错误码表） |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：电平触发。`bEnable = TRUE` 时每周期检查上游电报匹配 `nTransmitterId` → 把 4 字节原样填入 `nDataBytes` → 复位 watchdog。

**与 `FB_EnOceanSTM100`（outdated）的差异**：
- `FB_EnOceanSTM100` 硬编码假设 byte0=温度、byte1=设定值、byte2=旋钮、byte3=按键。若厂家协议不一致就字段错位。
- **本 FB** 把 4 字节交还给应用层自己按手册解码。给非标 STM100 / 厂家定制 STM100 / 通用 4 字节温湿度 sensor 留出灵活性。
- PDF 示例代码就是把 `nDataBytes[0..3]` 分别赋给 `nTemperature[]`、`nSetpoint[]`、`nStateRotarySwitch[]`、`nPresentSwitch[]` 之类的应用变量。

**watchdog**：STM100 是被动周期发送（典型 100-1000 秒间隔），与按键模块（PTM）不同——一定要开 watchdog，否则模块电池没电也察觉不到。`T#1h` 是常用阈值，过短会误报（STM100 发送间隔会因电压低而拉长）。

**字节解码示例**（Eltako STM100，仅参考——以您手头模块手册为准）：
- `nDataBytes[0]`：温度，0..255 线性映射到 0..40 °C（用 `F_Byte_to_Temp(byData := nDataBytes[0], minTemp := 0, maxTemp := 40)` 转 REAL）
- `nDataBytes[1]`：设定值偏移，0..255 → -100..+100
- `nDataBytes[2]`：旋钮位 + 在场按键 + 学习按键的复合位图
- `nDataBytes[3]`：状态字节（含 LRN bit）

**典型陷阱**：① 把本 FB 接到非 STM100 模块（如 PTM100）的电报 → ID 过滤还是会响应，但 4 字节是 PTM 协议含义，按 STM 手册解码就乱。② watchdog 设过短，模块低电压发送间隔拉长后误报"离线"。③ 没读手册直接用 `nDataBytes[0]` 当温度 INT，发现是 0..255 范围 → 需要先用 `F_Byte_to_Temp` 或自写线性变换。

## 4. 错误码 / 返回值

`bError = TRUE` 时 `nErrorId` 同 KL6021-0023 通用错误表（§4.1.1.3）：

| `nErrorId` | 含义 |
|---|---|
| `16#0000` | 无错 |
| `16#0001` | 校验错 |
| `16#0002` | Watchdog（模块超时未发送） |
| `16#0003` | KL6023 缓冲区溢出 |
| `16#0004` | 还没收到数据 |

## 5. 使用注意 / 常见坑

- **必读模块手册再解码 4 字节**。本 FB 不替你决定字节含义。各厂家可能微调位序与映射。
- **温度字节用 `F_Byte_to_Temp` 转 REAL**：Tc2_EnOcean 自带的 helper 函数，做 `byData / 255 * (maxTemp - minTemp) + minTemp` 的线性变换。
- **比 outdated 版灵活**：若手头是标准 STM100 + Beckhoff demo 字段排布，用 `FB_EnOceanSTM100` 一行接出来；若非标 / 厂家变种，必须用本 FB。
- **watchdog 设 1 小时是常用阈值**，太短的话 STM100 在低电压期间发送间隔会拉长（典型 240 秒 → 1500 秒）误触发。
- **多 STM100 实例并行**：与 PTM 类似，每模块一个 FB_EnOceanSTM100Generic 实例，共用上游 `FB_EnOceanReceive`。
- **学习时**：先开 `FB_EnOceanReceive` 临时观察 `stEnOceanReceivedData.nTransmitterId`，在 STM100 上按学习按键即可读到 ID；记下后写回程序的 `nTransmitterId`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EnOceanSTM100Generic.TcPOU`](../examples/P_Demo_FB_EnOceanSTM100Generic.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_EnOceanSTM100Generic
VAR
    fbEnOceanReceive : FB_EnOceanReceive;
    fbRoomSensor     : FB_EnOceanSTM100Generic;
    stEnOceanInData  AT %I* : ST_EnOceanInData;
    stEnOceanOutData AT %Q* : ST_EnOceanOutData;
    nSensorId        : UDINT := 16#000000C4;
    abRawBytes       : ARRAY [0..3] OF BYTE;
    rTempDegC        : REAL;
END_VAR
fbEnOceanReceive(bEnable := TRUE, stEnOceanInData := stEnOceanInData, stEnOceanOutData := stEnOceanOutData);
fbRoomSensor(
    bEnable               := NOT fbEnOceanReceive.bError AND fbEnOceanReceive.bEnable,
    tWatchdog             := T#1h,
    nTransmitterId        := nSensorId,
    stEnOceanReceivedData := fbEnOceanReceive.stEnOceanReceivedData,
    nDataBytes            => abRawBytes
);
rTempDegC := F_Byte_to_Temp(byData := abRawBytes[0], minTemp := 0, maxTemp := 40);
```

## 7. 业务场景与实际价值

- **场景**：自动化项目中遇到的 STM100 模块经常是厂家定制版（Eltako、Thermokon、Omnio、Distech 等），字节排布与 Beckhoff 标本 FB 设想不一致。例如：温湿度复合 sensor 把 byte2 用作湿度而不是旋钮档位；CO₂ + 温度 sensor 用 byte1 + byte2 凑 16-bit CO₂ ppm。
- **价值**：本 FB 不假设含义，给应用层留全部解码权。配合 `F_Byte_to_Temp` 这种 helper，可灵活适配任何 4 字节传感器。
- **替代方案对比**：
  - 用 `FB_EnOceanSTM100`：硬编码字段，不适合厂家变种
  - 直接读 `FB_EnOceanReceive.stEnOceanReceivedData.nData[]`：少了 ID 过滤 + watchdog，自己写 30 行重复代码
  - **本 FB**：在保留 ID 过滤 + watchdog 基础上把 4 字节原样给出，新项目首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf) §4.1.1.2.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173267211.html
- **相关**：`FB_EnOceanReceive`（上游必备）、`FB_EnOceanSTM100`（outdated 字段硬解码版）、`F_Byte_to_Temp`（字节→°C 转换）
