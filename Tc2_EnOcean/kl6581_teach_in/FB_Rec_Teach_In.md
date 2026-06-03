# FB_Rec_Teach_In

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EnOcean` |
| Library Version | `1.7.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `KL6581 / Teach-in receive` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173291659.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_Rec_Teach_In.TcPOU`](../examples/P_Demo_FB_Rec_Teach_In.TcPOU) |

---

## 1. 功能简述

KL6581 体系下的 **EnOcean 学习按键事件接收 FB**——监控空中所有按下"learn"按键的 EnOcean 电报，并将设备 ID 与节点号输出。若设备 `bLearnType = TRUE`（仅少数现代 EnOcean 设备支持），还能进一步在 `str_Teach_In` 结构里读出 manufacturer ID、设备 type 和 profile（典型 4-byte teach-in 电报字段）。

适用场景：现场施工时一只设备贴墙后操作员按设备的学习按键，PLC 立即获取该设备的 `dw_ID` 并自动加入设备清单——比手动抄 EnOcean ID 容易得多。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart     : BOOL;
    byNode     : BYTE;
    str_KL6581 : STR_KL6581;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 电平：TRUE 开启监听，FALSE 关闭 |
| `byNode` | `BYTE` | — | KL6583 节点过滤：`0` 监听全部，`1..8` 只听对应节点 |
| `str_KL6581` | `STR_KL6581` | — | 必接 `fbKL6581.str_KL6581` |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bLearnType   : BOOL;
    by_Node      : BYTE;
    dw_ID        : DWORD;
    str_Teach_In : STR_Teach_In;
    bReceive     : BOOL := TRUE;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bLearnType` | `BOOL` | TRUE 时 `str_Teach_In` 含有可用的厂商 ID + type + profile 信息（仅少数设备支持） |
| `by_Node` | `BYTE` | 报学习事件的 KL6583 节点编号（PDF 描述 "Number of EnOcean® devices found"，但实际语义是接收到电报的节点号） |
| `dw_ID` | `DWORD` | 按下学习按键的设备 EnOcean ID（4 字节） |
| `str_Teach_In` | `STR_Teach_In` | 仅 `bLearnType = TRUE` 时有效；含 `nManufacturerID (WORD) / nTYPE (BYTE) / nProfile (BYTE)`（EEP 4-byte teach-in 电报解码） |
| `bReceive` | `BOOL` | **反相脉冲**，学习事件到达时 FALSE 一周期 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bStart` 电平。TRUE 期间监听所有 EnOcean 电报，识别其中 "LRN" 位标记的电报。

**LRN bit 检测**：EnOcean 协议在 1BS/4BS 电报里都有一个 LRN 位（由设备按学习按键时设置）。本 FB 监听到 LRN = 1 的电报就把 ID + 节点输出。

**`bLearnType` 区分新旧 teach-in 协议**：
- `bLearnType = FALSE`：旧式 LRN 电报，只有 ID 没有详细 EEP 信息
- `bLearnType = TRUE`：4-byte teach-in 电报，含 manufacturer + type + profile 三字段。可解析为 EnOcean EEP（Equipment Profile）

**输出保持语义**：`dw_ID` 在收到下一个 LRN 电报前保持上次的值；用 `NOT bReceive` 取沿才知道"刚到一帧"。

**典型陷阱**：
- `by_Node` 字段 PDF 描述写的是 "Number of EnOcean® devices found"——这是 PDF 描述错误（与 FB_EnOcean_Search 的同名字段混淆）。实际值是接收到该 LRN 电报的 KL6583 节点编号。本仓库已点明。
- 期望"自动加入设备列表"——本 FB 只通知一次事件，应用层要自己写"加入数据库"逻辑。
- 与 `FB_Rec_Teach_In_Ex` 的差异：Ex 版多检查"是否 EEP 4-byte 格式"，输出的 `str_Teach_In` 是 `STR_Teach`（含 Function 而不是 Profile）。新代码用 Ex 版（PDF 与 v3.4.6.0+ 起推荐）。

## 4. 错误码 / 返回值

本 FB 无显式错误输出。依赖上游 `fbKL6581.iErrorID`。

## 5. 使用注意 / 常见坑

- **`by_Node` 实际是节点号**（PDF 描述有误，本仓库点明）。
- **`bLearnType = FALSE` 时 `str_Teach_In` 无效**：不要把 `str_Teach_In.nManufacturerID` 当真。
- **首次按住 LRN 才有事件**：设备的"持续按住学习按键"行为各厂家不同，多数仅在按下瞬间发一帧 LRN 电报。
- **典型工程做法**：调试期间打开本 FB，用户走到每个 EnOcean 设备按 LRN 按键，HMI 自动列设备 ID + 节点号，工程师顺手把 ID 写入项目变量。
- **多 KL6583 节点**：`byNode := 0` 收全部；若想分节点抓 ID 可各开实例。
- **优先用 Ex 版**：`FB_Rec_Teach_In_Ex` 检查电报是否 EEP 格式，输出 `STR_Teach`（含 `nFunc` 而不是 `nProfile`），是新工程的首选。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_Rec_Teach_In.TcPOU`](../examples/P_Demo_FB_Rec_Teach_In.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_Rec_Teach_In
VAR
    fbKL6581       : FB_KL6581;
    fbTeach        : FB_Rec_Teach_In;
    stKL6581Input  AT %I* : KL6581_Input;
    stKL6581Output AT %Q* : KL6581_Output;
    bDoLearn       : BOOL := TRUE;
    nLastLearnedId : DWORD;
END_VAR
fbKL6581(bInit := TRUE, nIdx := 1, stKL6581_in := stKL6581Input, stKL6581_out := stKL6581Output);
fbTeach(
    bStart     := bDoLearn,
    byNode     := 0,
    str_KL6581 := fbKL6581.str_KL6581,
    dw_ID      => nLastLearnedId
);
```

## 7. 业务场景与实际价值

- **场景**：施工 / 调试现场把新 EnOcean 设备贴到墙上后，工程师按设备的 LRN 按键，PLC 立即列出该设备 4-byte ID 与所在 KL6583 节点。然后工程师把 ID 复制到对应 `FB_Rec_*` 实例的 `dw_ID` 中。比拿着设备铭牌抄 ID 直观。
- **价值**：免去查铭牌；某些工业设备 ID 印在背面拆下来才能看，调试期更显价值。
- **替代方案对比**：
  - 用 `FB_Rec_Generic` 监听特定 ID：先得知道 ID 才能用
  - 用 `FB_EnOcean_Search` 全网扫：列所有有发送的设备，不区分学习事件
  - **本 FB**：专门抓 LRN 事件，明确"新设备入网"语义
  - 用 `FB_Rec_Teach_In_Ex`：新版，推荐用于新工程

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf) §4.1.2.4.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173291659.html
- **相关**：`FB_KL6581`（上游必备）、`FB_Rec_Teach_In_Ex`（新版，推荐）、`FB_EnOcean_Search`（全网扫描）、`STR_Teach_In`（输出结构 §4.2.2.2.7）

## 9. 待确认项 ⚠️

- `by_Node` 字段 PDF 描述写为 "Number of EnOcean® devices found"，与 FB_EnOcean_Search 的 `iDevices` 字段描述混淆。实际语义是"接收到该 LRN 电报的 KL6583 节点编号"。本仓库依协议常识与同类 FB（`FB_Rec_Generic` 等）的 `by_Node` 语义判定为节点号；如对工程结果有影响请以 InfoSys 后续修订为准。
