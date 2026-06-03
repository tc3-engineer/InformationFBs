# FB_Rec_Generic

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EnOcean` |
| Library Version | `1.7.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `KL6581 / Receive generic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173274763.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_Rec_Generic.TcPOU`](../examples/P_Demo_FB_Rec_Generic.TcPOU) |

---

## 1. 功能简述

KL6581 体系下的**通用 EnOcean 电报接收 FB**。本 FB 通过共享 `str_KL6581` 与 `FB_KL6581` 通信，按 `dw_ID`（EnOcean transmitter ID）+ `byNode`（KL6583 节点过滤）筛选目标电报，把 4 字节用户数据原样输出（`ar_Value`）以及节点号、状态字段、ORG 类型。

用本 FB 时**应用层自己按手册解码 4 字节**——任何 EnOcean ORG 类型都能接，灵活但需要自己懂协议。对常用类型（1BS 门磁、RPS 开关 / 窗把手）有专用 FB（`FB_Rec_1BS` / `FB_Rec_RPS_Switch` / `FB_Rec_RPS_Window_Handle`）做了便利解码。

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
| `str_KL6581` | `STR_KL6581` | — | 必接 `fbKL6581.str_KL6581`（上游主端子 FB 的共享结构） |
| `byNode` | `BYTE` | — | KL6583 节点过滤：`0` 表示接收所有 KL6583 的电报；`1..8` 表示只接收对应节点的电报（KL6581 下最多 8 个 KL6583） |
| `dw_ID` | `DWORD` | — | 要接收的 EnOcean transmitter ID（4 字节） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    ar_Value   : ARRAY [0..3] OF BYTE;
    by_Node    : BYTE;
    by_STATE   : BYTE;
    bReceive   : BOOL := TRUE;
    EnOceanTyp : E_EnOcean_Org;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `ar_Value` | `ARRAY [0..3] OF BYTE` | EnOcean 用户数据 4 字节，应用层按设备手册解码 |
| `by_Node` | `BYTE` | 接收到该电报的 KL6583 节点编号（1..8） |
| `by_STATE` | `BYTE` | EnOcean STATE 字段（含重复计数、状态位等，按 EnOcean 协议格式） |
| `bReceive` | `BOOL` | **新电报到达时该位置 FALSE，仅持续一个 PLC 周期**；其它时间保持 TRUE。注意这是**反相**语义，不要直接当"数据有效"标志 |
| `EnOceanTyp` | `E_EnOcean_Org` | EnOcean ORG 字段（PTM/STM1B/STM4B/CTM/MODEM/MODEM_ACK） |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：本 FB 不需要显式 enable。只要 `str_KL6581` 接上 `FB_KL6581` 主端子，本 FB 每周期被调用就会监视共享结构，匹配 `dw_ID + byNode` 的电报到达时把数据填进输出。

**`bReceive` 的反相脉冲**：PDF 描述是"On receiving an EnOcean® telegram this value is set to FALSE for one cycle"——电报到达时**为 FALSE**（不是 TRUE）持续一周期。这是 PDF 一贯的反相约定，与 FB_EnOceanReceive 的 `stEnOceanReceivedData.bReceived = TRUE` 语义相反。**应用层用 `NOT fbRec.bReceive` 当"新电报到达"沿**。

**通用过滤逻辑**：
1. 共享 `str_KL6581` 上一周期来自 FB_KL6581 的最新接收信息中的 `by_Node` 和 `dw_ID` 与本 FB 的 `byNode/dw_ID` 比较；匹配（或 `byNode = 0`）→ 进入数据填充；
2. 把 `str_KL6581.ar_DB[0..3]` → `ar_Value[0..3]`，`by_ORG` → `EnOceanTyp`，`by_STATE` → `by_STATE`，并把 `bReceive` 翻 FALSE 一周期；
3. 不匹配 → 不动输出（保留上一帧值），`bReceive = TRUE`。

**与 FB_Rec_1BS / RPS_Switch 的关系**：那些 FB 是本 FB 的"专门化"——`FB_Rec_1BS` 把 4 字节解码为 `bOpen/bClose/bLRN`（窗磁专用），`FB_Rec_RPS_Switch` 解码为 `STR_EnOceanSwitch`（4 键面板专用）。如果你的设备落在那些常用类型里，用专门 FB 更直接；本 FB 适合**未知 ORG 类型 / 厂家定制 / 不知道是什么但先收下看 4 字节**的场景。

**典型陷阱**：① 误把 `bReceive = TRUE` 当作"数据有效"——实际反过来，TRUE 是"没数据 / 空闲"。② 漏接 `str_KL6581` → 本 FB 永远收不到电报。③ `dw_ID := 16#0` → 由于 EnOcean ID 不可能是 0，本 FB 将永远不匹配；应用层应填正确的 4 字节 transmitter ID。④ `byNode := 1..8` 但电报实际来自 node 3，且本 FB 填的是 1 → 收不到。多 KL6583 节点工程要么各开实例要么用 `byNode := 0` 收全部。

## 4. 错误码 / 返回值

本 FB 无显式 `bError / nErrorId` 输出。错误由上游 `FB_KL6581.iErrorID` 集中反映：

| 上游 `iErrorID` | 影响 |
|---|---|
| `KL6581_NoComWithKL6581 (16#11)` | 端子失联，本 FB 收不到任何电报 |
| `KL6581_Switch_to_Stopp (16#13)` | KL6583 链路停了，本 FB 收不到 |
| `KL6581_No_KL6853_Found (16#15)` | 无 KL6583 节点，本 FB 收不到 |

监控应做在 `fbKL6581.iErrorID` 上，不在本 FB。

## 5. 使用注意 / 常见坑

- **`bReceive` 是反相脉冲**（FALSE = 新电报到达，仅一周期）。要让逻辑看起来正常，用 `NOT fbRec.bReceive` 取沿。**这是本 FB 最易踩的坑**。（工程经验补充）
- **`dw_ID` 必填且必准**：EnOcean ID 是 4 字节模块铭牌或学习获得，不能为 0。
- **`byNode := 0` 收全部** 是工程里偷懒做法（不关心来自哪个 KL6583 节点）；要做"区域识别"才需要分节点。
- **不解码不要直接当业务数据用**：`ar_Value` 是 4 byte 原始数据，必须按 EnOcean EEP profile 或厂家手册解码。例如温度通常用 `F_Byte_to_Temp`。
- **`EnOceanTyp` 有助于动态识别**：如果工程里事先不知道某 ID 是按键还是温控，可先读 `EnOceanTyp`：5=PTM 按键 / 6=STM 1byte 门磁 / 7=STM 4byte 温控 / 8=CTM。
- **本 FB 不替你做"按下 / 释放沿"检测**：4 byte 原始里的"按下"在 RPS 协议里是 nybble bit，没人替你拆，用 `FB_Rec_RPS_Switch` 更省事。
- **多实例**：每个要监视的 transmitter ID 各开一个本 FB 实例，共享 `str_KL6581` 即可。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_Rec_Generic.TcPOU`](../examples/P_Demo_FB_Rec_Generic.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_Rec_Generic
VAR
    fbKL6581         : FB_KL6581;
    fbRecGen         : FB_Rec_Generic;
    stKL6581Input    AT %I* : KL6581_Input;
    stKL6581Output   AT %Q* : KL6581_Output;
    nUnknownDeviceId : DWORD := 16#01234567;
    abValue          : ARRAY [0..3] OF BYTE;
    eOrgType         : E_EnOcean_Org;
    rTrigRcv         : R_TRIG;
    bNewFrame        : BOOL;
END_VAR
fbKL6581(bInit := TRUE, nIdx := 1, stKL6581_in := stKL6581Input, stKL6581_out := stKL6581Output);
fbRecGen(
    str_KL6581 := fbKL6581.str_KL6581,
    byNode     := 0,
    dw_ID      := nUnknownDeviceId,
    ar_Value   => abValue,
    EnOceanTyp => eOrgType
);
rTrigRcv(CLK := NOT fbRecGen.bReceive);
bNewFrame := rTrigRcv.Q;
```

## 7. 业务场景与实际价值

- **场景**：工程调试初期"我有一个 EnOcean 模块但不知道是什么"——可以先用本 FB 把任意 ID 的电报收下来，看 4 字节原始 + ORG 类型，再决定下一步用哪个专用 FB。也用于厂家自定义协议（温湿度二合一 sensor、CO₂ + VOC sensor 之类）。
- **价值**：在不知具体设备类型前提下做"先收下再分析"。配合 `EnOceanTyp` 输出可在 HMI 上显示"接收到 PTM 按键电报 / 4byte 温控电报"等类型识别信息，便于现场调试。
- **替代方案对比**：
  - 用专用 `FB_Rec_*` 系列：已知设备类型时更直接、字段已解码
  - **本 FB**：未知 / 厂家变种 / 调试场景必备

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf) §4.1.2.2.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173274763.html
- **相关**：`FB_KL6581`（上游必备）、`FB_Rec_1BS`（门磁专用）、`FB_Rec_RPS_Switch`（按键专用）、`FB_Rec_RPS_Window_Handle`（窗把手专用）、`E_ENOCEAN_ORG`（ORG 类型枚举）、`STR_KL6581`（共享状态结构）
