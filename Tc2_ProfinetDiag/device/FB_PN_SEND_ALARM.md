# FB_PN_SEND_ALARM

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_ProfinetDiag` |
| Library Version | `1.0.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `device` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/15588711819.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PN_SEND_ALARM.TcPOU`](../examples/P_Demo_FB_PN_SEND_ALARM.TcPOU) |

---

## 1. 功能简述

（设备侧）向 PROFINET 控制器发送一条报警。通过 `PN_ALARM_Typ`（枚举 `E_PN_ALARM_TYP`，预定义报警类型）、`PN_slotNumber`（槽号）、`PN_SubSlotNumber`（子槽号）指定报警内容，上升沿触发发送。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  bStart           : BOOL;
  NETID            : T_AmsNetId;
  PORT             : T_AmsPort;
  PN_ALARM_Typ     : E_PN_ALARM_TYP;
  PN_slotNumber    : WORD;
  PN_SubSlotNumber : WORD;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bStart` | `BOOL` | 上升沿（FALSE→TRUE）触发功能块执行一次。 |
| `NETID` | `T_AmsNetId` | 控制器（PROFINET Controller）的 AMS Net ID。本机控制器填空串 `''`。 |
| `PORT` | `T_AmsPort` | 控制器与设备通讯所用的 ADS 端口（port = Device ID + 1000hex）。 |
| `PN_ALARM_Typ` | `E_PN_ALARM_TYP` | 报警类型，取自枚举 `E_PN_ALARM_TYP`（含 `PN_ALARM_PROCESS`、`PN_ALARM_PULL`、`PN_ALARM_PLUG` 等预定义类型）。 |
| `PN_slotNumber` | `WORD` | 槽号（slot number）。 |
| `PN_SubSlotNumber` | `WORD` | 子槽号（subslot number）。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  bBusy                   : BOOL;
  bError                  : BOOL;
  iErrorID                : UDINT;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBusy` | `BOOL` | 功能块使能后该输出置位，并一直保持到收到设备反馈为止。`bBusy = TRUE` 期间不接受输入端的新命令（不响应新的触发）。 |
| `bError` | `BOOL` | 命令传输过程中发生错误时，在 `bBusy` 复位（落沿）之后置位该输出。 |
| `iErrorID` | `UDINT` | `bError` 置位时返回 ADS 错误号（见 §4 错误码表）。 |

### VAR_IN_OUT

无。

## 3. 行为说明

本功能块是基于 ADS 的异步功能块，内部维护「空闲 → 忙 → 完成」三态状态机。`bStart` 由 FALSE 变为 TRUE 的上升沿触发一次操作：触发后 `bBusy` 立即置 TRUE，功能块通过 ADS 把请求发往 PROFINET 控制器（由 `NETID` 与 `PORT` 寻址到目标设备）；收到设备应答后 `bBusy` 落回 FALSE，此时 （无数据输出，仅发送反馈） 才有效，若过程出错则 `bError` 在 `bBusy` 落沿之后置 TRUE、`iErrorID` 给出 ADS 错误号。`bBusy = TRUE` 期间功能块忽略输入端的任何新触发，必须等到本次完成才能再次发起。

**调用周期**：必须在每个 PLC 周期持续调用本实例（不是只在触发那一帧调一次），否则内部 ADS 状态机无法推进、`bBusy` 不会落沿。**清错语义**：错误状态保持到下一次 `bStart` 上升沿被接受时才更新，因此读 `bError`/`iErrorID` 要在 `bBusy` 落沿之后、下一次触发之前读。**电平 vs 边沿**：`bStart` 保持高电平不会反复执行，只在跳变沿触发一次；要重复操作必须先把 `bStart` 拉回 FALSE 再拉高。

**设备 → 控制器方向**：本 FB 是设备端主动向控制器报警（与 `FB_PN_ALARM_DIAG` 读报警方向相反）。**报警定位**：用 `PN_slotNumber` / `PN_SubSlotNumber` 告诉控制器是哪个槽/子槽出的问题，报警类型取 `E_PN_ALARM_TYP` 枚举值。**典型场景**：模块拔出（`PN_ALARM_PULL`）、插入（`PN_ALARM_PLUG`）、过程报警（`PN_ALARM_PROCESS`）等。

## 4. 错误码 / 返回值

`iErrorID` 在 `bError = TRUE` 时返回 ADS 错误号（`bError = FALSE` 时无意义）。下表摘自 PDF §5.1「ADS Return Codes」的常见取值：

| `iErrorID` (dec) | Hex | 名称 | 含义 / 处理建议 |
|---|---|---|---|
| `0` | `0x0` | `ERR_NOERROR` | 无错误，操作成功；读取输出结果 |
| `6` | `0x6` | `ERR_TARGETPORTNOTFOUND` | 目标端口未找到——`PORT` 错误，或目标 ADS 服务未启动/不可达。检查 `PORT` 与设备状态 |
| `7` | `0x7` | `ERR_TARGETMACHINENOTFOUND` | 目标设备未找到——AMS 路由不存在。检查 `NETID` 与路由表 |
| `16` | `0x10` | `ERR_LOWINSTLEVEL` | 授权等级过低（许可证问题） |
| `1280` | `0x500` | `ROUTERERR_NOLOCKEDMEMORY` | 路由锁定内存不足 |
| `1792`+ | `0x700`+ | 一般 ADS 错误 | 命令相关错误（如设备拒绝、参数非法）；可对照 PDF §5.1「General ADS error codes」一节查全 |

> 完整 ADS 返回码表（Global / Router / General ADS / RTime 四组）参见 PDF §5.1 章节。⚠️ PDF 与 InfoSys 均未给出本库各 FB 专属的错误码子集，上表为 ADS 通用码。

## 5. 使用注意 / 常见坑

- **方向是「发」不是「收」**：设备端用本 FB 主动报警；控制器端用 `FB_PN_ALARM_DIAG` 读报警。
- **报警类型用枚举**：`PN_ALARM_Typ` 必须取 `E_PN_ALARM_TYP` 中的值，不要硬填裸数字。
- **槽/子槽要对应真实模块位置**，否则控制器侧无法正确定位报警源。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PN_SEND_ALARM.TcPOU`](../examples/P_Demo_FB_PN_SEND_ALARM.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_PN_SEND_ALARM
VAR
    fbSendAlarm   : FB_PN_SEND_ALARM;
    bSendReq      : BOOL := FALSE;            // 在线上升沿触发发送报警
    eAlarmType    : E_PN_ALARM_TYP := PN_ALARM_PROCESS;  // 过程报警
    wSlot         : WORD := 1;                // 报警所在槽号
    wSubSlot      : WORD := 1;                // 报警所在子槽号
    bBusy         : BOOL;
    bErr          : BOOL;
    nErrId        : UDINT;
END_VAR

// 上升沿触发；设备端向控制器发一条过程报警（槽1/子槽1）
fbSendAlarm(
    bStart := bSendReq,
    NETID  := '',
    PORT   := 16#1001,
    PN_ALARM_Typ := eAlarmType,
    PN_slotNumber := wSlot,
    PN_SubSlotNumber := wSubSlot,
    bBusy  => bBusy,
    bError => bErr,
    iErrorID => nErrId
);
```

## 7. 业务场景与实际价值

- **场景**：用 EL6631-0010 / CCAT 做 PROFINET 设备时，设备端检测到内部异常（如某模块被拔出、过程量越限），需要主动向上级 PROFINET 控制器报警，让上位系统记录并响应。
- **价值**：把 PROFINET 报警发送封装为一次调用，设备端只需选报警类型 + 槽号即可，免去手工拼报警帧。
- **替代方案对比**：自己拼 PROFINET 报警帧经 ADS 发送工作量大；本 FB 用枚举 + 槽号一次发出。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf) 第 3.2.3 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/15588711819.html
- **相关 FB / FC**：`FB_PN_ALARM_DIAG`（控制器侧读报警）、`E_PN_ALARM_TYP`（报警类型枚举）
