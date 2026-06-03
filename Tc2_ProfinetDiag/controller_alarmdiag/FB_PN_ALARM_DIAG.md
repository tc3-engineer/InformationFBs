# FB_PN_ALARM_DIAG

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_ProfinetDiag` |
| Library Version | `1.0.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `controller_alarmdiag` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/14966249099.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_PN_ALARM_DIAG.TcPOU`](../examples/P_Demo_FB_PN_ALARM_DIAG.TcPOU) |

---

## 1. 功能简述

读取 PROFINET 设备诊断报警（diagnosis alarm）的功能块。每个实例提供一个 PLC 硬件输入 `PnIoBoxDiag`，须在 TwinCAT 中链接到被诊断设备的 `PnIoBoxDiag` 输入；该 WORD 状态字发生变化即表示设备有新的诊断报警挂起。报警成功读出后设备的报警状态会被自动复位。每个 PROFINET 设备需各调用一次本功能块，运行索引 `iNrAlarms` 表示本次从缓冲区读出了多少条诊断报警。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  bEnable : BOOL;
  NETID   : T_AmsNetId;
  PORT    : T_AmsPort;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bEnable` | `BOOL` | 功能块使能。 |
| `NETID` | `T_AmsNetId` | 控制器（PROFINET Controller）的 AMS Net ID。本机控制器填空串 `''`。 |
| `PORT` | `T_AmsPort` | 控制器与设备通讯所用的 ADS 端口（port = Device ID + 1000hex）。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  bBusy                   : BOOL;
  stAlarmDiagData         : ST_PN_AlarmDiagData;
  bError                  : BOOL;
  iErrorID                : UDINT;
  iNrAlarms               : INT;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bBusy` | `BOOL` | 功能块使能后该输出置位，并一直保持到收到设备反馈为止。`bBusy = TRUE` 期间不接受输入端的新命令（不响应新的触发）。 |
| `stAlarmDiagData` | `ST_PN_AlarmDiagData` | 诊断报警通过该结构输出。只要 PLC 输入上存在状态位 `0x0010`（至少一个 AlarmCR 收到诊断报警），每个周期就通过该结构输出一条报警。结构含时间戳、站名、诊断明细 `ST_PN_Diag` 与用户数据标志。 |
| `bError` | `BOOL` | 命令传输过程中发生错误时，在 `bBusy` 复位（落沿）之后置位该输出。 |
| `iErrorID` | `UDINT` | `bError` 置位时返回 ADS 错误号（见 §4 错误码表）。 |
| `iNrAlarms` | `INT` | 本次读出的报警条数。 |

### VAR_IN_OUT

无。

## 3. 行为说明

本功能块为电平使能型（不同于库内多数边沿触发的 FB）。`bEnable = TRUE` 期间功能块持续工作：当链接的 `PnIoBoxDiag` 硬件输入（WORD）发生变化、且其中状态位 `0x0010` 置位（表示至少一个 AlarmCR 收到诊断报警）时，功能块逐条把诊断缓冲区里的报警通过 `stAlarmDiagData` 输出，每个 PLC 周期输出一条，并用 `iNrAlarms` 累计已读条数。`bBusy` 在等待 ADS 反馈期间为 TRUE，其间不接受新命令。所有挂起报警读完后，设备侧的报警状态被自动复位，`PnIoBoxDiag` 随之回到无报警值。

**链接要求**：`PnIoBoxDiag`（`AT %I* : WORD`）是硬件输入变量，必须在 TwinCAT I/O 映射里手动链接到对应 PROFINET 设备的 `PnIoBoxDiag`，否则 PLC 永远收不到「有新报警」的通知。**逐条读出**：一个设备可能同时挂多条报警，需保持 `bEnable = TRUE` 连续多个周期，逐个周期把 `stAlarmDiagData` 取走（建议每周期把结构拷入环形缓冲或报警列表）。**出错处理**：传输出错时 `bError` 在 `bBusy` 落沿后置位，`iErrorID` 给出 ADS 错误号。

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

- **`PnIoBoxDiag` 必须链接**：这是本 FB 区别于其它 FB 的关键——它带一个 `AT %I*` 硬件输入。漏链接会导致功能块「看不到」设备报警，表现为永远读不到诊断数据。
- **每设备一实例**：报警状态复位是按设备进行的，多设备务必各用一个实例并各自链接 `PnIoBoxDiag`。
- **逐周期取数**：报警是逐条、逐周期通过 `stAlarmDiagData` 输出的，HMI/记录逻辑要在每个周期把结构内容搬走，否则会漏读后续报警。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_PN_ALARM_DIAG.TcPOU`](../examples/P_Demo_FB_PN_ALARM_DIAG.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_PN_ALARM_DIAG
VAR
    fbAlarmDiag      : FB_PN_ALARM_DIAG;        // 诊断报警读取实例
    bDiagEnable      : BOOL := FALSE;           // 在线置 TRUE 开始监听本设备报警
    stDiag           : ST_PN_AlarmDiagData;     // 解析后的可读诊断数据
    bDiagBusy        : BOOL;
    bDiagError       : BOOL;
    nDiagErrId       : UDINT;
    iAlarmCount      : INT;                      // 本次读出的报警条数
    // 注：实际工程中 PnIoBoxDiag 由 TwinCAT I/O 映射链接到设备硬件输入，
    //     无法在纯 ST 例程里赋值，此处仅演示输出端的在线观察。
END_VAR

// 电平使能型：bDiagEnable 保持 TRUE 期间持续监听并逐条输出报警
fbAlarmDiag(
    bEnable := bDiagEnable,
    NETID   := '',                 // 本机控制器
    PORT    := 16#1001,            // 示例：Device ID 1 -> 1 + 16#1000
    bBusy   => bDiagBusy,
    stAlarmDiagData => stDiag,
    bError  => bDiagError,
    iErrorID => nDiagErrId,
    iNrAlarms => iAlarmCount
);

// 工程中应在此把 stDiag 拷入报警列表 / 推 HMI（每周期取一条）
// IF iAlarmCount > 0 THEN ... 记录 stDiag.sNameOfStation / stDiag.ST_Diag.nSlot ...
```

## 7. 业务场景与实际价值

- **场景**：一条产线上挂了若干 PROFINET 从站（如 EL663x 网关后的 IO、第三方 PN 设备）。当某个从站发生断线、模块拔出、通道短路等故障时，PROFINET 会发出诊断报警。运维需要在 HMI 上实时看到「哪个站、哪个槽、什么类型」的报警明细。
- **价值**：不用本 FB 就得自己用 `ADSREAD` 去读 PROFINET 控制器的诊断索引、再手工解析二进制诊断帧（`ST_PN_DiagMessage` 300 字节裸数据）。本 FB 把「监听 `PnIoBoxDiag` 触发 → 读诊断帧 → 解析为可读结构 `ST_PN_AlarmDiagData`（含站名、槽号、报警类型）→ 复位报警状态」整条链路封装好，业务侧只需读结构字段。
- **替代方案对比**：System Manager 的 Diag History 只能在工程师电脑上看，无法进 PLC 逻辑联动；自己写 `ADSREAD` 解析诊断帧工作量大且易错。本 FB 是把诊断接入 PLC 逻辑（联动声光报警、停机保护）的标准做法。

## 8. 参考资料

- **PDF**：[`TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_ProfinetDiag_EN.pdf) 第 3.1.1.1 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_profinetdiag/14966249099.html
- **相关 FB / FC**：`FB_PN_READ_PORT_DIAG`（读端口诊断）、`ST_PN_AlarmDiagData` / `ST_PN_Diag` / `ST_PN_DiagMessage`（诊断数据结构）
