# FB_Rec_1BS

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EnOcean` |
| Library Version | `1.7.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `KL6581 / Receive 1BS (window contact)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173276299.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_Rec_1BS.TcPOU`](../examples/P_Demo_FB_Rec_1BS.TcPOU) |

---

## 1. 功能简述

KL6581 体系下的**门窗磁 / 1-byte 状态电报（ORG Field 6）接收 FB**。典型设备：EnOcean 门 / 窗磁触点，磁铁靠近时"关"、远离时"开"，并带学习按键（LRN）。本 FB 把 1BS 电报解码成 3 个布尔位：`bOpen`（开）、`bClose`（关）、`bLRN`（学习按键），应用层直接拿这三位用。

每个 1BS 设备一个 FB 实例，用 `dw_ID` 区分。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    str_KL6581 : STR_KL6581;
    byNode     : BYTE;
    dw_ID      : DWORD;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `str_KL6581` | `STR_KL6581` | — | 必接 `fbKL6581.str_KL6581`（共享状态结构） |
| `byNode` | `BYTE` | — | KL6583 节点过滤；`0` 收所有节点，`1..8` 只收对应节点 |
| `dw_ID` | `DWORD` | — | 1BS 设备的 EnOcean ID（4 字节） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bOpen    : BOOL;
    bClose   : BOOL;
    bLRN     : BOOL;
    by_Node  : BYTE;
    bReceive : BOOL := TRUE;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bOpen` | `BOOL` | 触点处于"开"状态（磁铁离开）时 TRUE |
| `bClose` | `BOOL` | 触点处于"关"状态（磁铁靠近）时 TRUE |
| `bLRN` | `BOOL` | 学习按键已按下时 TRUE |
| `by_Node` | `BYTE` | 接收到该电报的 KL6583 节点编号 |
| `bReceive` | `BOOL` | **反相脉冲**：新电报到达时 FALSE 一周期，其它时 TRUE |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：本 FB 不需显式 enable，每周期调用即可。`str_KL6581` 来自 FB_KL6581 共享结构，本 FB 内部根据 `dw_ID + byNode` 过滤匹配电报。

**1BS 协议解码**：EnOcean ORG Field 6 是 1-byte 状态电报，1 字节里位 0 = 触点状态（0 = open / 1 = close），位 3 = LRN bit（这是典型 EnOcean 协议定义，本 FB 内部完成解码）。`bOpen` 与 `bClose` 互斥（同一时刻只有一个为 TRUE）；`bLRN` 独立。

**`bReceive` 反相**：与 `FB_Rec_Generic` 一致，新电报到达时 `bReceive = FALSE` 仅一周期。

**两位互斥逻辑**：1BS 电报只传"当前状态"——开 → 关 时一帧报"关"，关 → 开 时一帧报"开"，期间不发心跳，所以 `bOpen / bClose` 保留最近一帧的状态。这点和 STM250 一样。

**上电首帧**：上电后到第一帧之前 `bOpen = bClose = FALSE`，不代表"门关 / 门开"，代表"未知"。应用层应在 HMI 上加"未确认"标签。

**典型陷阱**：① 把 `bReceive` 当数据有效（反了）。② 上电后未操作门窗就拿 `bClose = FALSE` 判"门开" → 实际是未收到帧的初始假象，误报安防。③ LRN 学习按键在某些厂家设备上是"短按"行为，`bLRN = TRUE` 仅持续到收到下一帧。

## 4. 错误码 / 返回值

本 FB 无显式 `bError` 输出。错误依赖上游 `fbKL6581.iErrorID`（参见 `FB_KL6581` §4）。

## 5. 使用注意 / 常见坑

- **首帧前状态未知**：用一个 `bConfirmed` 标志记录"是否已收到至少一帧"，未收到时所有报警 / 控制逻辑要旁路。
- **`bReceive` 反相**：用 `NOT fbRec1BS.bReceive` 取沿才是新帧到达。
- **`bOpen + bClose` 在第一帧到达前都是 FALSE**（不是 1 + 0 也不是 0 + 1）。
- **学习时**：现场按 1BS 设备的 LRN 学习按键，`bLRN = TRUE` 持续到下一帧；应用层借此触发"加入已知设备列表"流程。也可用 `FB_Rec_Teach_In` 监视全网 LRN 事件。
- **多个 1BS 设备**：各开本 FB 实例，`dw_ID` 各不同；共用 `str_KL6581`。
- **与 STM250 的差异**：STM250 是 KL6021-0023 体系下的等价设备；FB_Rec_1BS 是 KL6581 体系下的等价设备。两个 API 互不兼容。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_Rec_1BS.TcPOU`](../examples/P_Demo_FB_Rec_1BS.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_Rec_1BS
VAR
    fbKL6581       : FB_KL6581;
    fbWindowMagnet : FB_Rec_1BS;
    stKL6581Input  AT %I* : KL6581_Input;
    stKL6581Output AT %Q* : KL6581_Output;
    nWindowId      : DWORD := 16#01ABCDEF;
    bWindowOpen    : BOOL;
END_VAR
fbKL6581(bInit := TRUE, nIdx := 1, stKL6581_in := stKL6581Input, stKL6581_out := stKL6581Output);
fbWindowMagnet(
    str_KL6581 := fbKL6581.str_KL6581,
    byNode     := 0,
    dw_ID      := nWindowId,
    bOpen      => bWindowOpen
);
```

## 7. 业务场景与实际价值

- **场景**：办公楼 / 住宅窗户开闭监控驱动 HVAC（开窗时关空调省电）、入侵报警（夜间开窗触发）。1BS 门 / 窗磁是楼宇 EnOcean 设备里最便宜量最大的一类，遍地用。
- **价值**：直接拿 `bOpen` 接 HVAC 互锁，`bLRN` 接学习流程；不用读字节自己拆位。
- **替代方案对比**：
  - 用 `FB_Rec_Generic`：拿 1 字节数据自己拆位，多写 10 行
  - 用 STM250（在 KL6021-0023 体系下）：硬件不同，API 也不同
  - **本 FB**：KL6581 体系下门 / 窗磁的标准选项

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf) §4.1.2.2.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173276299.html
- **相关**：`FB_KL6581`（上游必备）、`FB_Rec_Generic`（通用通杀版）、`FB_Rec_Teach_In`/`FB_Rec_Teach_In_Ex`（学习按键 ID 抓取）、`FB_EnOceanSTM250`（KL6021-0023 等价 FB）
