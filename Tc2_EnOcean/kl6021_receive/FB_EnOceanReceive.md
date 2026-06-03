# FB_EnOceanReceive

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EnOcean` |
| Library Version | `1.7.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `KL6021-0023 / Receive base` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173259531.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EnOceanReceive.TcPOU`](../examples/P_Demo_FB_EnOceanReceive.TcPOU) |

---

## 1. 功能简述

KL6021-0023 EnOcean 接收端子的**根基（base）接收功能块**。本 FB 把 KL6021-0023 在 K-bus 链路上送进来的原始字节序列（`ST_EnOceanInData`），解析成已经分离出 transmitter ID、ORG/sensor type、4 个数据字节、状态字节、有效标志位的统一接收数据结构 `ST_EnOceanReceivedData`；同时驱动 KL6021-0023 的输出字节 `ST_EnOceanOutData`，完成端子内部状态机的握手。

应用层（例如 `FB_EnOceanPTM100` / `FB_EnOceanSTM250` 这些"按 transmitter 解析"的 FB）**全部都从本 FB 的 `stEnOceanReceivedData` 取数据**。整个 KL6021-0023 工程里**只能有一个 FB_EnOceanReceive 实例**（它独占该端子的 IO 映像），所有下游解析块共享其输出。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bEnable     : BOOL := FALSE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bEnable` | `BOOL` | `FALSE` | 电平触发使能：TRUE 时启动接收，FALSE 时停用并把所有输出复位为 0 / FALSE。整个 KL6021-0023 接收链需要本位为 TRUE 且 `bError` 为 FALSE 才工作 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bError                : BOOL := FALSE;
    nErrorId              : UDINT := 0;
    stEnOceanReceivedData : ST_EnOceanReceivedData;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bError` | `BOOL` | 出错时置 TRUE，下游 PTM/STM 解析块的 `bEnable` 通常接 `NOT fbEnOceanReceive.bError AND fbEnOceanReceive.bEnable` |
| `nErrorId` | `UDINT` | 错误号；见 §4 错误码表（与 KL6021-0023 共用一张表，含校验错、Watchdog、KL6023 缓冲区溢出等） |
| `stEnOceanReceivedData` | `ST_EnOceanReceivedData` | 已解析的接收数据结构（`bReceived` / `nLength` / `eEnOceanSensorType` / `nData[0..3]` / `nStatus` / `nTransmitterId`）。下游所有解析块 `stEnOceanReceivedData` 入口都连到这里 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stEnOceanInData  : ST_EnOceanInData;
    stEnOceanOutData : ST_EnOceanOutData;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `stEnOceanInData` | `ST_EnOceanInData` | 在 System Manager 里链接到 KL6021-0023 的**输入字节区**（端子 → PLC，1 字节状态 + 11 字节数据） |
| `stEnOceanOutData` | `ST_EnOceanOutData` | 在 System Manager 里链接到 KL6021-0023 的**输出字节区**（PLC → 端子，1 字节控制 + 11 字节数据）。本 FB 用来回写应答字节，维持端子内部状态机 |

## 3. 行为说明

**触发**：本 FB 是电平触发，不是边沿触发——`bEnable = TRUE` 持续保持时才连续运行。`FALSE → TRUE` 沿不需要清错也不需要握手，直接进入接收循环；`TRUE → FALSE` 沿立即把所有输出和 `stEnOceanReceivedData` 清零。

**内部时序**：每个 PLC 周期本 FB 都会读 `stEnOceanInData` 的 1 字节状态 + 11 字节数据；KL6021-0023 端子用串行字节流方式把来自空中的 EnOcean 电报"一帧一帧"送到 PLC，本 FB 负责拼帧（按内部协议长度字段）、做校验、抽出 transmitter ID（4 字节，对应空中模块的 EnOcean ID）和 sensor type（区分 PTM / STM 1-byte / STM 4-byte / CTM 四类传感器，见枚举 `E_EnOceanSensorType`），整理填入 `stEnOceanReceivedData`，同时通过 `stEnOceanOutData` 给端子回 ACK。

**数据可用性**：`stEnOceanReceivedData.bReceived` 在**收到一帧新数据时置 TRUE，只保持一个 PLC 周期**——所以下游解析块 `FB_EnOceanPTM100` 等必须每周期调用一次，否则可能错过本帧。该结构在两帧之间保持最后一次的内容不变。

**Watchdog**：本 FB 自身不带 watchdog；watchdog 监视在下游解析块（`FB_EnOceanPTM100` / `FB_EnOceanSTM*`）的 `tWatchdog` 参数上设置，本 FB 只关心 KL6021-0023 端子层错误（校验错 `0x0001`、KL6023 缓冲区溢出 `0x0003` 等）。

**典型连法**：单个 FB_EnOceanReceive 实例 + 多个 PTM / STM 解析实例并联，所有解析实例都把 `fbEnOceanReceive.stEnOceanReceivedData` 连到自身 `stEnOceanReceivedData` 入口；解析实例之间通过 `nTransmitterId` 区分到底处理空中哪台设备。

**典型陷阱**：① 忘记在 System Manager 里把 `stEnOceanInData` / `stEnOceanOutData` 链到 KL6021-0023 的 IO 字节区（链不上时 `bEnable = TRUE` 却收不到任何数据，`bReceived` 永远 FALSE）；② 同一 KL6021-0023 端子上跑两个 FB_EnOceanReceive 实例（端子的 ACK 字节会被双重写，状态机错乱）；③ 把 FB_EnOceanReceive 放到非 PLC 周期循环里调用（例如条件 IF 分支中），导致漏掉只持续一个周期的 `bReceived` 脉冲。

## 4. 错误码 / 返回值

`bError = TRUE` 时 `nErrorId` 取以下值（与 KL6021-0023 错误码表共用，PDF §4.1.1.3）：

| `nErrorId` | 名称（PDF） | 含义 |
|---|---|---|
| `16#0000` | No error | 无错（运行正常） |
| `16#0001` | Checksum error | EnOcean 帧校验错（空中受干扰 / 距离太远） |
| `16#0002` | Watchdog monitoring | 下游解析块的 watchdog 触发（在本 FB 这里出现时通常是下游已不接收） |
| `16#0003` | Buffer overflow (in the KL6023) | KL6023 收发器内部缓冲区溢出（事件密度过高或 PLC 周期太长来不及取） |
| `16#0004` | No data received yet from sensor receive | 还没收到任何数据（刚启动且尚无 EnOcean 模块发送） |

## 5. 使用注意 / 常见坑

- **每个 KL6021-0023 端子只能挂一个 FB_EnOceanReceive 实例**。本 FB 独占 IO 字节区与应答握手。多实例会让端子内部状态机错乱，下游所有数据失效。
- **必须在 System Manager 把 IO 链接做满**：`stEnOceanInData`（输入字节区）+ `stEnOceanOutData`（输出字节区）。漏一边 `bEnable = TRUE` 也无任何数据流，且没有明确报错（`nErrorId` 维持 `16#0004`）。
- **下游解析块的 `bEnable` 一律接 `NOT fbEnOceanReceive.bError AND fbEnOceanReceive.bEnable`**：本 FB 报错时下游应跟随失能，避免在错误状态下消费陈旧数据。
- **`bReceived` 只持续一个 PLC 周期**：所有下游解析块必须在主任务里每周期调用，不要放进条件分支或事件回调里，否则会丢帧。（工程经验补充）
- **PLC 任务周期建议 ≤ 20 ms**：EnOcean 电报一帧到端子后只在 IO 映像上停留有限的周期数，过长的 PLC 周期会让 KL6023 缓冲区频繁溢出（`nErrorId = 16#0003`）。
- **本 FB 不需要 watchdog 参数**：监控具体 transmitter 是否还活着的责任在下游 `FB_EnOceanPTM*` / `FB_EnOceanSTM*` 的 `tWatchdog` 上。
- **`bError = TRUE` 时 `stEnOceanReceivedData` 中数据不可信**：可能是上一帧残留也可能是部分填充，请先看 `bError`、再用数据。
- **使用 KL6021-0023 而不是 KL6581**：本 FB 是 KL6021-0023 体系的入口。KL6581 体系使用 `FB_KL6581` + `FB_Rec_*` 一套不同的 API，互相不通用。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EnOceanReceive.TcPOU`](../examples/P_Demo_FB_EnOceanReceive.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_EnOceanReceive
VAR
    fbEnOceanReceive : FB_EnOceanReceive;

    // —— 链到 KL6021-0023 IO 字节区 ——
    stEnOceanInData  AT %I* : ST_EnOceanInData;   // 链到 KL6021 输入区
    stEnOceanOutData AT %Q* : ST_EnOceanOutData;  // 链到 KL6021 输出区

    bEnableEnOceanRecv : BOOL := TRUE;

    // 状态观察
    bRecvBusError    : BOOL;
    nRecvErrId       : UDINT;
    nReceivedTransId : UDINT;
    bFrameJustArrived: BOOL;
END_VAR

fbEnOceanReceive(
    bEnable          := bEnableEnOceanRecv,
    stEnOceanInData  := stEnOceanInData,
    stEnOceanOutData := stEnOceanOutData
);

bRecvBusError     := fbEnOceanReceive.bError;
nRecvErrId        := fbEnOceanReceive.nErrorId;
nReceivedTransId  := fbEnOceanReceive.stEnOceanReceivedData.nTransmitterId;
bFrameJustArrived := fbEnOceanReceive.stEnOceanReceivedData.bReceived;
```

## 7. 业务场景与实际价值

- **场景**：使用老式 KL6021-0023 EnOcean 端子做无线接入的楼宇 / 工业现场。机柜里一片 KLxxx 端子，其中一片是 KL6021-0023，挂着 KL6023 收发器；空中有一批 PTM200 自发电按键、STM250 窗磁、STM100 温控等无线设备。本 FB 是 PLC 端"接进 EnOcean 报文"的第一步。
- **价值**：原始的 KL6021-0023 字节区只是裸 byte，没有协议解析；用 `FB_EnOceanReceive` 一次拼帧、抽 ID、抽 sensor type、做校验，下游应用直接拿 `stEnOceanReceivedData` 调用 `FB_EnOceanPTM100`/`FB_EnOceanSTM250` 等就能识别"这个 ID 是哪个按钮 / 窗磁"。不用自己写 EnOcean 协议解析。
- **替代方案对比**：
  - 直接读 KL6021-0023 字节区自写协议解析：要写 200+ 行字节拼帧 + transmitter ID 提取 + sensor type 识别 + ACK 回写，几乎重新发明本 FB；不推荐
  - 改用 KL6581 + `FB_KL6581`：KL6581 是更新一代端子（K-bus master 形态），如果工程是新建议选 KL6581 体系；本 FB 用于已经买了 KL6021-0023 的老线
  - 改用 EL6233-xxxx EtherCAT EnOcean 终端：EtherCAT 版本，需要替换硬件
  - **本 FB**：在不换硬件前提下，封装 KL6021-0023 的 EnOcean 协议层，是 KL6021-0023 体系的标准用法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf) §4.1.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173259531.html
- **相关**：`ST_EnOceanInData`（§4.2.1.2.2，KL6021-0023 输入字节区结构）、`ST_EnOceanOutData`（§4.2.1.2.3，KL6021-0023 输出字节区结构）、`ST_EnOceanReceivedData`（§4.2.1.2.1，解析后的接收结构）、`E_EnOceanSensorType`（§4.2.1.1.1，传感器类型枚举）、`FB_EnOceanPTM100`/`FB_EnOceanPTM200`/`FB_EnOceanSTM100`/`FB_EnOceanSTM100Generic`/`FB_EnOceanSTM250`（下游解析块）
