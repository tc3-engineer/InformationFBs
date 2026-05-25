# FB_SoEAX5000SetMotorCtrlWord_ByDriveRef

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Drive` |
| Library Version | `1.4.8` |
| Type | `FUNCTION_BLOCK` |
| Category | `AX5000 SoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_drive/2307573899.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoEAX5000SetMotorCtrlWord_ByDriveRef.xml`](../examples/P_Demo_FB_SoEAX5000SetMotorCtrlWord_ByDriveRef.xml) |

---

## 1. 功能简述

设置 AX5000 电机控制字（Motor Control Word，`P-0-0096`）中抱闸（机械刹车）强制位的功能块。本 FB 可单独控制 ForceLock 位（Bit 0，强制抱闸）和 ForceUnlock 位（强制松闸），从而**脱离 Enable** 单独控制电机抱闸的开合。

正常情况下，抱闸是随驱动器 Enable 自动控制的（使能即松闸，去使能即抱闸）。用 ForceLock 可在不去使能的情况下强制抱闸，用 ForceUnlock 可在不使能的情况下强制松闸。两者同时置位时，ForceLock（抱闸）优先级更高。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stDriveRef   : ST_DriveRef;
    bExecute     : BOOL;
    tTimeout     : TIME := DEFAULT_ADS_TIMEOUT;
    bForceLock   : BOOL;
    bForceUnlock : BOOL
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stDriveRef` | `ST_DriveRef` | — | 驱动器引用结构。可在 System Manager 把 `ST_PlcDriveRef`（`AT %I*` 过程映像）链接到 PLC，再用 `F_CreateAmsNetId` 把 NetID 字节数组转字符串后逐字段填入 |
| `bExecute` | `BOOL` | — | 上升沿激活本 FB 执行一次写控制字；调用期间保持，完成后手动复位 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 命令执行允许的最长时间。`DEFAULT_ADS_TIMEOUT` 是 Tc2_System 全局常量（典型 5 秒） |
| `bForceLock` | `BOOL` | — | 脱离 Enable 强制抱闸（激活机械刹车）。与 `bForceUnlock` 同时为 `TRUE` 时本位优先 |
| `bForceUnlock` | `BOOL` | — | 脱离 Enable 强制松闸（释放机械刹车） |

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

本 FB 是 `bExecute` 上升沿驱动的异步写参数型功能块：

1. **触发**：`bExecute` 上升沿时，FB 把 `bForceLock` / `bForceUnlock` 组合编码进电机控制字 `P-0-0096`（ForceLock = Bit 0），通过 SoE 写入 `stDriveRef` 指向的 AX5000，置 `bBusy := TRUE`。
2. **执行中**：`bBusy` 保持 `TRUE`，FB 周期推进 ADS 状态机等待回执。期间不改输入。
3. **完成分支**：收到反馈后 `bBusy := FALSE`。无误则 `bError = FALSE`（控制字已写入）；出错则 `bError := TRUE` 并给出 `iAdsErrId` / `iSercosErrId`。

**抱闸优先级语义**：`bForceLock` 与 `bForceUnlock` 同时为 `TRUE` 时，ForceLock 优先 —— 即抱闸激活（安全侧优先，宁可抱住也不误松）。两者都为 `FALSE` 时恢复"抱闸随 Enable 自动控制"的默认行为。

**IDN 寻址语义**：`P-0-0096` 是 AX5000 厂商参数（P 参数集）。本 FB 内部固定该 IDN，调用方只提供 `stDriveRef` 和两个强制位。

**调用范式**：每次想改变抱闸强制状态，就用新的 `bForceLock` / `bForceUnlock` 组合给一个 `bExecute` 上升沿写一次；`bBusy` 落下后补一次 `bExecute := FALSE` 收尾。这不是持续输出，写一次后驱动器保持该控制字直到下次写入。

## 4. 错误码 / 返回值

| 输出 | 含义 | 处理建议 |
|---|---|---|
| `bError = FALSE`（`bBusy` 已落） | 控制字成功写入 | 抱闸按 ForceLock/ForceUnlock 组合动作 |
| `bError = TRUE` | 写入出错 | 读 `iAdsErrId` / `iSercosErrId` |
| `iAdsErrId`（UINT） | ADS 通讯层错误码 | 参考 "ADS Return Codes" 表 |
| `iSercosErrId`（UINT） | 驱动器返回的 Sercos 错误码 | 参考 AX5000 的 Sercos 错误码手册 |

PDF 与 InfoSys 均未列出具体错误码表（⚠️ 待人工对照 AX5000 手册）。

## 5. 使用注意 / 常见坑

- **强制松闸有安全风险**：`bForceUnlock` 在轴未使能（无力矩保持）的情况下松开机械刹车，垂直轴 / 悬挂负载会因重力下坠。**仅在确认负载安全或有外部支撑时使用**，并配合急停链评估。（工程经验补充）
- **同时置位时 ForceLock 赢**：`bForceLock` 和 `bForceUnlock` 都为 `TRUE` 时是抱闸，不是松闸。这是安全侧设计，但容易让人误以为"两个都给就松开"。（PDF 原话）
- **默认行为是随 Enable 自动控制**：不需要强制时把两个位都给 `FALSE`，否则会一直覆盖驱动器自身的抱闸逻辑。常见坑是调试时强制松闸忘了复位，导致正式运行时抱闸不动作。（工程经验补充）
- **这是写一次保持，不是周期电平**：写一次控制字后驱动器保持该状态，不需要每周期重写；但状态变更要重新触发 `bExecute`。
- **此 FB 仅适用于 AX5000**：`P-0-0096` 是 AX5000 厂商参数，对其它型号无效。
- **`stDriveRef` 必须先初始化好**：例程用 `bInit` 守卫等过程映像就绪。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoEAX5000SetMotorCtrlWord_ByDriveRef.xml`](../examples/P_Demo_FB_SoEAX5000SetMotorCtrlWord_ByDriveRef.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_SoEAX5000SetMotorCtrlWord_ByDriveRef
VAR
    fbSetCtrlWord   : FB_SoEAX5000SetMotorCtrlWord_ByDriveRef;
    rtrigSet        : R_TRIG;
    stPlcDriveRef   AT %I* : ST_PlcDriveRef;
    stDriveRef      : ST_DriveRef;
    bInit           : BOOL := TRUE;
    bForceBrakeLock   : BOOL := FALSE;             // 在线置 TRUE：强制抱闸
    bForceBrakeUnlock : BOOL := FALSE;             // 在线置 TRUE：强制松闸(注意安全!)
    bSetReq         : BOOL := FALSE;               // 在线置 TRUE 写一次控制字
    bSetBusy        : BOOL;
    bSetError       : BOOL;
    iAdsErr         : UINT;
    iSercosErr      : UINT;
END_VAR

// 初始化驱动器引用
IF bInit THEN
    stDriveRef.sNetId     := F_CreateAmsNetId(stPlcDriveRef.aNetId);
    stDriveRef.nSlaveAddr := stPlcDriveRef.nSlaveAddr;
    stDriveRef.nDriveNo   := stPlcDriveRef.nDriveNo;
    stDriveRef.nDriveType := stPlcDriveRef.nDriveType;
    IF (stDriveRef.sNetId <> '') AND (stDriveRef.nSlaveAddr <> 0) THEN
        bInit := FALSE;
    END_IF;
END_IF;

rtrigSet(CLK := bSetReq);

// 单次调用形式：所有 VAR_INPUT 显式赋值
fbSetCtrlWord(
    stDriveRef   := stDriveRef,
    bExecute     := rtrigSet.Q AND NOT bInit,
    tTimeout     := DEFAULT_ADS_TIMEOUT,
    bForceLock   := bForceBrakeLock,
    bForceUnlock := bForceBrakeUnlock,
    bBusy        => bSetBusy,
    bError       => bSetError,
    iAdsErrId    => iAdsErr,
    iSercosErrId => iSercosErr
);

IF NOT bSetBusy AND NOT bInit THEN
    bSetReq := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：维护 / 装配工位需要在驱动器未使能时手动盘动电机轴（如更换工件、对刀），要先强制松闸；或者诊断时要确认抱闸机械动作是否正常，单独控制抱闸开合。
- **价值**：把"按位编码电机控制字 `P-0-0096` + 写 SoE + 异步状态机"封装成两个布尔位的一次调用，业务侧不必记 Bit 0 是 ForceLock、不必手拼控制字。
- **替代方案对比**：
  - 用 `FB_SoEWrite` 自己写 `P-0-0096`：要自己查位定义、拼控制字
  - 通过去使能让抱闸自动落下：但那样无法在"未使能仍松闸"的维护工况下盘轴
  - **本 FB**：两个明确命名的强制位，安全优先级内置（ForceLock 赢），适合做维护 / 诊断面板的抱闸控制

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf) §4.2.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_drive/2307573899.html
- **相关**：`FB_SoEAX5000ReadActMainVoltage_ByDriveRef`、`FB_SoEAX5000ParkAxis_ByDriveRef`（同 AX5000 SoE 类）

## 9. 待确认项

- ⚠️ `iAdsErrId` / `iSercosErrId` 取值表 PDF/InfoSys 均未列；`P-0-0096` 除 Bit 0 (ForceLock) 外的位定义需查 AX5000 手册。
