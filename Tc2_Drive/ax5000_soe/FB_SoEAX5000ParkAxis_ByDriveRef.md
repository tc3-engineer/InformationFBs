# FB_SoEAX5000ParkAxis_ByDriveRef

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Drive` |
| Library Version | `1.4.8` |
| Type | `FUNCTION_BLOCK` |
| Category | `AX5000 SoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/11307039499.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoEAX5000ParkAxis_ByDriveRef.xml`](../examples/P_Demo_FB_SoEAX5000ParkAxis_ByDriveRef.xml) |

---

## 1. 功能简述

激活 / 解除 AX5000 通道"停泊"（Park）功能的功能块。被停泊（parked）的 AX5000 通道会被临时禁用。

在模块化机器概念里，某些电机（轴）可能并未实际接入。通过本 FB 把对应通道停泊（禁用），可以避免该通道因为没接电机而报错（例如反馈编码器缺失错误 / Feedback error）。需要时再用本 FB 解除停泊，让该通道恢复正常。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stDriveRef : ST_DriveRef;
    bExecute   : BOOL;
    bPark      : BOOL;
    tTimeout   : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stDriveRef` | `ST_DriveRef` | — | 驱动器引用结构。可在 System Manager 把 `ST_PlcDriveRef`（`AT %I*` 过程映像）链接到 PLC，再用 `F_CreateAmsNetId` 把 NetID 字节数组转字符串后逐字段填入。`nDriveNo` 决定停泊的是哪个通道 |
| `bExecute` | `BOOL` | — | 上升沿激活本 FB 执行一次停泊 / 解除；调用期间保持，完成后手动复位 |
| `bPark` | `BOOL` | — | 指定本次操作是停泊（`TRUE`，禁用该通道）还是解除停泊（`FALSE`，恢复该通道） |
| `tTimeout` | `TIME` | — | 命令执行允许的最长时间。PDF 该 FB 的 `tTimeout` 未给默认值（⚠️ 调用时必须显式赋值，建议用 `DEFAULT_ADS_TIMEOUT`） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy        : BOOL;
    bError       : BOOL;
    iAdsErrId    : UINT;
    iSercosErrId : UINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | FB 被激活时置位，直到收到驱动器反馈才复位 |
| `bError` | `BOOL` | 在 `bBusy` 复位之后，若命令传输出错则置位 |
| `iAdsErrId` | `UINT` | `bError` 置位时返回上一条命令的 ADS 错误码 |
| `iSercosErrId` | `UINT` | `bError` 置位时返回上一条命令的 Sercos 错误码 |

### VAR_IN_OUT

无。

## 3. 行为说明

本 FB 是 `bExecute` 上升沿驱动的异步命令型功能块：

1. **触发**：`bExecute` 上升沿时，FB 根据 `bPark` 的值向 `stDriveRef` 指向的 AX5000 通道下发停泊（`bPark = TRUE`）或解除停泊（`bPark = FALSE`）命令，置 `bBusy := TRUE`。
2. **执行中**：`bBusy` 保持 `TRUE`，FB 周期推进内部 ADS 状态机等待回执。期间不改输入。
3. **完成分支**：收到反馈后 `bBusy := FALSE`。无误则 `bError = FALSE`（通道状态已切换）；出错则 `bError := TRUE` 并给出 `iAdsErrId` / `iSercosErrId`。

**停泊语义**：停泊使该通道临时退出正常 Sercos 状态机（switch on disabled → ready → operation enabled 这条使能链），驱动器不再对该通道做反馈监控 / 报警，从而在没接电机时不产生错误。解除停泊后该通道重新参与正常状态机。

**通道选择**：AX5000 是双通道驱动器，停泊作用于 `stDriveRef.nDriveNo` 指定的那个通道（A = 0 / B = 1）。停泊一个通道不影响另一个。

**调用范式**：需要改变停泊状态时用新的 `bPark` 值给一个 `bExecute` 上升沿；`bBusy` 落下后补一次 `bExecute := FALSE` 收尾。`tTimeout` 必须显式赋值（PDF 无默认值）。

## 4. 错误码 / 返回值

| 输出 | 含义 | 处理建议 |
|---|---|---|
| `bError = FALSE`（`bBusy` 已落） | 停泊 / 解除命令成功 | 通道按 `bPark` 进入 / 退出停泊态 |
| `bError = TRUE` | 命令出错 | 读 `iAdsErrId` / `iSercosErrId` |
| `iAdsErrId`（UINT） | ADS 通讯层错误码 | 参考 "ADS Return Codes" 表 |
| `iSercosErrId`（UINT） | 驱动器返回的 Sercos 错误码 | 参考 AX5000 的 Sercos 错误码手册 |

PDF 未列出具体错误码表（⚠️ 待人工对照 AX5000 手册）。

## 5. 使用注意 / 常见坑

- **`tTimeout` 必须显式赋值**：本 FB 的 `tTimeout` 在 PDF 里**没有默认值**（与其它 SoE FB 不同），不赋值会用到未初始化的 `TIME`（`T#0s`）导致立即超时。建议传 `DEFAULT_ADS_TIMEOUT`。（PDF 接口 + 工程经验补充）
- **停泊前确认该通道确实不用**：停泊会禁用通道的反馈监控，若误把在用通道停泊，该轴将不响应任何运动指令。停泊应只用于"模块化机器里物理上没接电机"的通道。（PDF 场景）
- **停泊状态与配置要一致**：长期不接电机的通道，停泊只是运行期手段；更彻底的做法是在 ESI / 配置里就按单通道使用。停泊适合"同一硬件配置、按订单选配不同电机数量"的柔性产线。（工程经验补充）
- **解除停泊后要重新走使能链**：通道从停泊态恢复后回到 switch on disabled，需重新经 `FB_SoEDriveEnable` 等使能才能跑。（工程经验补充）
- **此 FB 仅适用于 AX5000**：停泊是 AX5000 特性，对其它型号无效。
- **`stDriveRef` 必须先初始化好**：例程用 `bInit` 守卫。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoEAX5000ParkAxis_ByDriveRef.xml`](../examples/P_Demo_FB_SoEAX5000ParkAxis_ByDriveRef.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_SoEAX5000ParkAxis_ByDriveRef
VAR
    fbParkAxis      : FB_SoEAX5000ParkAxis_ByDriveRef;
    rtrigPark       : R_TRIG;
    stPlcDriveRef   AT %I* : ST_PlcDriveRef;
    stDriveRef      : ST_DriveRef;
    bInit           : BOOL := TRUE;
    bDoPark         : BOOL := TRUE;                // TRUE=停泊该通道, FALSE=解除停泊
    bParkReq        : BOOL := FALSE;              // 在线置 TRUE 执行一次
    bParkBusy       : BOOL;
    bParkError      : BOOL;
    iAdsErr         : UINT;
    iSercosErr      : UINT;
END_VAR

// 初始化驱动器引用（nDriveNo 决定停泊哪个通道）
IF bInit THEN
    stDriveRef.sNetId     := F_CreateAmsNetId(stPlcDriveRef.aNetId);
    stDriveRef.nSlaveAddr := stPlcDriveRef.nSlaveAddr;
    stDriveRef.nDriveNo   := stPlcDriveRef.nDriveNo;
    stDriveRef.nDriveType := stPlcDriveRef.nDriveType;
    IF (stDriveRef.sNetId <> '') AND (stDriveRef.nSlaveAddr <> 0) THEN
        bInit := FALSE;
    END_IF;
END_IF;

rtrigPark(CLK := bParkReq);

// 单次调用形式：所有 VAR_INPUT 显式赋值；tTimeout 必须显式给（PDF 无默认值）
fbParkAxis(
    stDriveRef := stDriveRef,
    bExecute   := rtrigPark.Q AND NOT bInit,
    bPark      := bDoPark,
    tTimeout   := DEFAULT_ADS_TIMEOUT,
    bBusy        => bParkBusy,
    bError       => bParkError,
    iAdsErrId    => iAdsErr,
    iSercosErrId => iSercosErr
);

IF NOT bParkBusy AND NOT bInit THEN
    bParkReq := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：同一台设备按订单选配不同数量的电机轴（柔性 / 模块化产线）。没接电机的 AX5000 通道若不处理会报反馈缺失错误，导致整机无法运行。开机时把这些通道停泊即可让整机正常起来。
- **价值**：把"对指定通道下发停泊 / 解除 SoE 命令 + 异步状态机"封装成一个 `bPark` 布尔 + 触发的调用，无需手写停泊 IDN 时序。
- **替代方案对比**：
  - 给每种配置做一套独立的 TwinCAT 配置 / ESI：维护多套配置成本高
  - 物理上短接 / 加假负载骗过反馈检测：不安全、不规范
  - **本 FB**：运行期按实际接入情况动态停泊空闲通道，一套配置适配多种选配

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf) §4.2.5
- **InfoSys topic**：未在 `tcplclib_tc2_drive`（1033）英文树中检索到该 `_ByDriveRef` 变体的独立 topic 页；元信息中 `Source InfoSys` 指向的是 `tcplclib_tc2_mc2_drive` 下功能等价的 `FB_SoEAX5000ParkAxis`（非 ByDriveRef 变体，https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/11307039499.html ）作为最接近的官方参考。本 FB 接口以 PDF §4.2.5 为准。标 ⚠️ not-on-infosys
- **相关**：`FB_SoEAX5000ReadActMainVoltage_ByDriveRef`、`FB_SoEAX5000SetMotorCtrlWord_ByDriveRef`（同 AX5000 SoE 类）

## 9. 待确认项

- ⚠️ `tTimeout` 在 PDF 接口中无默认值，调用方必须显式赋值。
- ⚠️ InfoSys 英文树未收录该 `_ByDriveRef` 变体的独立 topic，无法做 PDF–InfoSys 逐字 diff，本文以 PDF §4.2.5 为准。
- ⚠️ `iAdsErrId` / `iSercosErrId` 取值表 PDF 未列。
