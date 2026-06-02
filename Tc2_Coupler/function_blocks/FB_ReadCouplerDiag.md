# FB_ReadCouplerDiag

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Coupler` |
| Library Version | `1.1.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_coupler/42594315.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_ReadCouplerDiag.TcPOU`](../examples/P_Demo_FB_ReadCouplerDiag.TcPOU) |

---

## 1. 功能简述

读取 BC / BK 耦合器面板上**错误 LED 闪烁码（flash code）**的"第一序列"与"第二序列"，把它从耦合器内部经 2-byte PLC interface 取回到 PLC，结果填到 `ST_CouplerDiag` 结构里。闪烁码是 Beckhoff K-bus 耦合器表达故障原因的标准方式：长闪 = 错误类别，停顿，短闪 = 错误位置（例如哪个端子位置坏了）；用本 FB 后操作员不必趴在机柜旁数 LED 闪几下、查表对照说明书，PLC 程序可以直接解析数字、在 HMI 上显示中文故障消息。

**关键前提**：本 FB 通过现场总线（Profibus / Lightbus / EtherCAT 等）把数据从耦合器搬回 PLC，**只有现场总线本身仍能正常传输数据时才能用**。如果耦合器整个掉线、现场总线断了，本 FB 也读不到东西——这时只能现场看 LED。它专门用来诊断 K-bus 侧 / 端子侧的故障，不诊断现场总线侧故障。

**典型用法**：在 PLC 周期里监视耦合器 status byte 的 K-bus error 位；位置 1 → 上升沿触发本 FB → 读到 `stDiag` 后查表把 flash code 翻译成可读的故障消息推给 HMI 显示给操作员。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stState    : PLCINTFSTRUCT;
    bExecute   : BOOL;
    tTimeout   : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stState` | `PLCINTFSTRUCT` | — | 2-byte PLC interface 状态字（耦合器 → PLC）；必须在 System Manager 链接到耦合器 PLC interface 的 status word |
| `bExecute` | `BOOL` | — | 上升沿触发一次诊断数据读取 |
| `tTimeout` | `TIME` | — | 整次读取允许的最大时长。建议 ≥ T#2S（要读两段闪烁码，串行进行） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    stCtrl  : PLCINTFSTRUCT;
    bBusy   : BOOL;
    bError  : BOOL;
    nErrId  : UDINT;
    stDiag  : ST_CouplerDiag;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stCtrl` | `PLCINTFSTRUCT` | 2-byte PLC interface 控制字（PLC → 耦合器）；链接到耦合器 PLC interface 的 control word |
| `bBusy` | `BOOL` | FB 激活后置 TRUE，读完或超时回 FALSE |
| `bError` | `BOOL` | 错误发生时在 `bBusy` 下降之后置 TRUE |
| `nErrId` | `UDINT` | `bError = TRUE` 时的错误号，见下方错误码表 |
| `stDiag` | `ST_CouplerDiag` | 诊断结果结构体（详见 Tc2_Coupler §5.3）。含两个 `ST_FlashCode` 序列，每个序列两个字段（错误类别字节 + 错误位置字节），可对照 BC/BK 耦合器手册附录"Flash code table"翻译成具体故障描述 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿启动一次读取。`bBusy := TRUE` 直到两段闪烁码都从耦合器读回到 `stDiag`，或 `tTimeout` 到时强制结束。

**内部时序**：
1. `bExecute` 上升沿 → `bBusy := TRUE`，FB 驱动 `stCtrl` 经 2-byte PLC interface 发送"请求 flash code 第一序列"的命令。
2. 等耦合器在 `stState` 中应答并把第一段闪烁码（错误类别字节）放在数据通道里返回。FB 读出后填入 `stDiag.stFirstFlashCode`。
3. 紧接着 FB 再发"请求第二序列"命令，读回错误位置字节，填入 `stDiag.stSecondFlashCode`。
4. 两段都读完 → `bBusy := FALSE`，`bError := FALSE`，`nErrId := 0`。
5. 期间任一步在 `tTimeout` 内未应答 → `bError := TRUE`，`nErrId := 16#300`，`bBusy := FALSE`，`stDiag` 中未读完的字段保留旧值。

**闪烁码含义示例**（对照耦合器手册）：
- 第一序列长闪 4 次 + 第二序列 0 次 = "K-bus command error"（K-bus 协议错误）
- 第一序列 4 长闪 + 第二序列 n 短闪 = "第 n 个端子之后通信中断"（端子位置错误，n=1..N）
- 具体表请查 BC / BK 系列手册的 "LED diagnosis" 章节

**读取时机**：耦合器**已经检测到错误**时才能读到有意义的 flash code。错误未发生时本 FB 读回的是"无错"（全 0）或上一次错误的残留。所以代码里通常先检查 `stState` 的 K-bus error 位，置位时才调用本 FB。

**与 CouplerReset 的关系**：`CouplerReset` 会**清掉**耦合器内部的 flash code 缓存。如果想读 flash code 又想复位耦合器，必须**先读后复位**；顺序反了就读不到具体故障原因，只能看到 "no error"。

## 4. 错误码 / 返回值

本 FB 无 HRESULT 返回；通过 `bError` / `nErrId` 表达错误（PDF §3.3 错误号表）：

| `nErrId` | 含义 | 常见原因 |
|---|---|---|
| `0` | 无错（FB 自身执行正常；具体设备故障看 `stDiag`） | — |
| `16#100` | 2-byte PLC interface 通信初始化失败 | `stState` / `stCtrl` 没在 System Manager 链接；耦合器未启用 2-byte interface |
| `16#200` | 通信过程中错误 | 读取期间总线异常 / 帧损坏 |
| `16#300` | 超时 | `tTimeout` 设得过短；现场总线本身已断（耦合器读不回数据） |
| `16#400` | 寄存器号参数错 | 本 FB 不暴露寄存器号给用户，几乎遇不到 |
| `16#500` | 表号参数错 | 同上 |

## 5. 使用注意 / 常见坑

- **错误必须先存在才能读出**。在 K-bus 健康时调用本 FB 得到的是全 0，不要把"全 0 = FB 不工作"。诊断逻辑应是：先看 `stState.Byte0` 中的 K-bus error 位，**这一位置 1 才调用本 FB**。
- **触发顺序：先读 flash code，再 CouplerReset**。`CouplerReset` 会清掉耦合器内部的诊断缓存。许多团队按了"一键清错"，结果 HMI 上看不到任何故障原因，对维修人员排查反而帮倒忙。
- **`stState` / `stCtrl` 必须链接到 2-byte PLC interface**。配置成 0-byte interface 时本 FB 永远 `bBusy = TRUE`，到 `tTimeout` 报 `16#100`。Profibus / Lightbus 在 System Manager 配置；Interbus S 需 KS2000 离线打开 2-byte interface。
- **现场总线本身断了，本 FB 无能为力**。`bError = TRUE` 且 `nErrId = 16#300` 时，不一定是耦合器故障，可能是总线物理层断了——这时还是要去现场看红绿 LED。
- **`tTimeout` 不要短于 2 秒**。两段闪烁码读取是串行的，每段需要在耦合器侧响应，过短会误超时。
- **解析 `stDiag` 要对照具体耦合器型号的手册**。BC9000 / BK3120 / BK5120 等的 flash code 表略有差异，库里没有内置翻译；推荐写一个 lookup case 把 (type, position) → 中文故障描述。（工程经验补充）
- **不要每个 PLC 周期都触发**。`bExecute` 用上升沿，每个故障事件只读一次就够了；周期性触发会让本 FB 一直在和耦合器握手，浪费总线带宽且对原工艺通讯有影响。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_ReadCouplerDiag.TcPOU`](../examples/P_Demo_FB_ReadCouplerDiag.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：BK5120（Lightbus 耦合器）+ 一串 KLxxx 端子。当 K-bus error 位置位时，
//       自动读耦合器面板 LED 的两段闪烁码并送到 HMI 显示具体故障原因（例如
//       "第 7 号端子之后 K-bus 中断"），让维修人员不必到现场看 LED 数闪几下。
//
// 价值：把读 2-byte PLC interface 协议、两段闪烁码串行读取、超时管理这套封装为
//       一次调用。HMI 直接拿 nFirstFlashType / nSecondFlashPos 两个数显示。
//
// 验证：登录后人为拔掉某个端子（例如端子 7）→ 观察 stCouplerStatus.Byte0 的
//       K-bus error 位被置 1 → 内部 R_TRIG 触发 fbReadDiag 一次 → 几秒后
//       bReadingDiag 回 FALSE，nFirstFlashType / nSecondFlashPos 应分别
//       为 4 和 7（手册对应"K-bus 通信中断 + 端子 7 之后"），bReadError = FALSE。
PROGRAM P_Demo_FB_ReadCouplerDiag
VAR
    fbReadDiag                  : FB_ReadCouplerDiag;
    rTrigKbusErr                : R_TRIG;

    // —— 链到耦合器 2-byte PLC interface ——
    stCouplerStatus     AT %I*  : PLCINTFSTRUCT;
    stCouplerControl    AT %Q*  : PLCINTFSTRUCT;

    bKbusErrorDetected          : BOOL;          // = stCouplerStatus.Byte0.0
    bTriggerReadDiagOnce        : BOOL;
    tDiagReadTimeout            : TIME := T#3S;

    bReadingDiag                : BOOL;
    bReadError                  : BOOL;
    nReadErrId                  : UDINT;
    stDiagResult                : ST_CouplerDiag;

    // 解析后供 HMI 显示
    nFirstFlashType             : BYTE;
    nSecondFlashPos             : BYTE;
END_VAR

// 监视 K-bus error 位（典型在 stState 的 Byte0 bit0；具体位号查耦合器手册）
bKbusErrorDetected := stCouplerStatus.Byte0.0;

// K-bus error 上升沿才触发一次读取，避免周期性反复读
rTrigKbusErr(CLK := bKbusErrorDetected);
IF rTrigKbusErr.Q THEN
    bTriggerReadDiagOnce := TRUE;
END_IF

// 单次调用形式：执行完后必须把 bExecute 复位以备下次上升沿
fbReadDiag(
    stState  := stCouplerStatus,
    bExecute := bTriggerReadDiagOnce,
    tTimeout := tDiagReadTimeout,
    stCtrl   => stCouplerControl,
    bBusy    => bReadingDiag,
    bError   => bReadError,
    nErrId   => nReadErrId,
    stDiag   => stDiagResult
);

// 完成后清触发；提取两段闪烁码供 HMI（具体字段名以 ST_CouplerDiag 实际定义为准）
IF NOT bReadingDiag AND bTriggerReadDiagOnce THEN
    bTriggerReadDiagOnce := FALSE;
    nFirstFlashType  := stDiagResult.stFirstFlashCode.nErrorType;
    nSecondFlashPos  := stDiagResult.stSecondFlashCode.nErrorPosition;
END_IF
```

## 7. 业务场景与实际价值

- **场景**：BC / BK 耦合器在役系统出现 K-bus 故障（端子掉电、端子坏、K-bus 接线松动）。运维需要在 HMI / SCADA 上看到"是哪一段闪烁码 / 哪个端子故障"，而不是只看到一个笼统的"K-bus error"位。典型行业：印刷、灌装、汽车焊装、纺织、卷烟机。
- **价值**：取消现场看 LED 数闪几下的操作；HMI 上直接显示"端子 7 之后 K-bus 中断"等可执行的维修指示，平均故障定位时间从 5-10 分钟降到 30 秒内。还可以把诊断日志写进归档系统供事后分析。
- **替代方案对比**：
  - 现场看 LED：传统方式，受机柜位置限制，操作员要趴下数闪烁次数对照说明书
  - 改用 EtherCAT + EL 端子 + 内置诊断：现代方案，可靠性更好，但要换硬件
  - 只看 PLC 的 K-bus error 单 bit：知道有问题但不知道是哪个端子，仍要现场排查
  - **本 FB**：在不换硬件前提下把"现场看 LED"这个操作搬进 PLC，HMI 显示，是 BC/BK 时代的标准做法

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Coupler_EN.pdf) §3.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_coupler/42594315.html
- **相关**：`PLCINTFSTRUCT`（§5.1）、`ST_CouplerDiag`（§5.3，两段 `ST_FlashCode`）、`ST_FlashCode`（§5.6）、`CouplerReset`（清错前必须先读本 FB 以免诊断信息丢失）、`E_CouplerErrType`（§5.2，错误类别枚举）
