# FB_SoEExecuteCommand_ByDriveRef

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Drive` |
| Library Version | `1.4.8` |
| Type | `FUNCTION_BLOCK` |
| Category | `General SoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_drive/2307546763.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoEExecuteCommand_ByDriveRef.xml`](../examples/P_Demo_FB_SoEExecuteCommand_ByDriveRef.xml) |

---

## 1. 功能简述

执行 SoE（Sercos over EtherCAT）驱动器命令（Command）的通用功能块。Sercos 协议里部分 IDN 是"命令型参数"（Procedure Command），不是简单的读写值，而是触发驱动器内部执行一段过程（如归零、换相检测、参数固化等）。本 FB 给定一个命令 IDN，向驱动器下发"启动该命令"，并等待执行回执。

命令 IDN 通过 `nIdn`（`WORD`）传入，配合 IDN 编码常量使用，例如 `P_0_IDN + 160` 表示厂商参数 `P-0-0160`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stDriveRef : ST_DriveRef;
    nIdn       : WORD;
    bExecute   : BOOL;
    tTimeout   : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stDriveRef` | `ST_DriveRef` | — | 驱动器引用结构。可在 System Manager 把 `ST_PlcDriveRef`（`AT %I*` 过程映像）链接到 PLC，再用 `F_CreateAmsNetId` 把 NetID 字节数组转字符串后逐字段填入 |
| `nIdn` | `WORD` | — | 本 FB 要执行的命令所对应的参数号（IDN）。例如 `P_0_IDN + 160` 表示 `P-0-0160` |
| `bExecute` | `BOOL` | — | 上升沿触发一次命令执行；调用期间保持，完成后手动复位 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 命令执行允许的最长时间。`DEFAULT_ADS_TIMEOUT` 是 Tc2_System 全局常量（典型 5 秒） |

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

1. **触发**：`bExecute` 上升沿时，FB 把 `nIdn` 指定的命令 IDN 作为目标，向 `stDriveRef` 指向的驱动器下发"执行命令"，置 `bBusy := TRUE`。
2. **执行中**：`bBusy` 保持 `TRUE`，FB 周期推进内部 ADS 状态机并跟踪驱动器命令执行状态直到回执。期间不改输入。
3. **完成分支**：收到反馈后 `bBusy := FALSE`。无误则 `bError = FALSE`（命令执行完成）；出错则 `bError := TRUE` 并给出 `iAdsErrId` / `iSercosErrId`。

**IDN 寻址语义**：SoE 参数用 IDN 标识，分标准参数（S，对应常量 `S_0_IDN`）和厂商参数（P，对应 `P_0_IDN`）。`nIdn` 是 16 位编码，常量基址加编号即得目标，如 `P_0_IDN + 160` = `P-0-0160`。命令型 IDN 需查具体驱动器手册确认哪些是 Procedure Command。

**命令 vs 读写**：本 FB 触发的是"过程命令"，驱动器收到后启动一段内部流程，可能持续一段时间；与单纯读写参数值（`FB_SoERead` / `FB_SoEWrite`）语义不同。命令是否真正执行成功，除看 `bError`，必要时还要读命令状态参数（部分驱动器提供 command state IDN）。

**调用范式**：每周期调用实例推进状态机；`bBusy` 落下后补一次 `bExecute := FALSE` 调用收尾。

## 4. 错误码 / 返回值

| 输出 | 含义 | 处理建议 |
|---|---|---|
| `bError = FALSE`（`bBusy` 已落） | 命令成功送达并被驱动器接受 | 必要时再读命令状态确认执行结果 |
| `bError = TRUE` | 命令传输出错 | 读 `iAdsErrId` / `iSercosErrId` |
| `iAdsErrId`（UINT） | ADS 通讯层错误码 | 参考 "ADS Return Codes" 表 |
| `iSercosErrId`（UINT） | 驱动器返回的 Sercos 错误码（如命令不被支持、当前状态不允许执行） | 参考驱动器型号的 Sercos 错误码 / IDN 手册 |

PDF 与 InfoSys 均未列出具体错误码表（⚠️ 待人工对照具体驱动器型号）。

## 5. 使用注意 / 常见坑

- **`nIdn` 用 IDN 编码常量拼，不要手填裸数字**：用 `P_0_IDN + 160` 这种形式而非直接写一个十六进制 `WORD`，避免把标准参数（S）和厂商参数（P）的基址搞混导致寻址错。（PDF 示例即用 `P_0_IDN + 160`）
- **命令 IDN 必须查驱动器手册**：哪些 IDN 是"可执行命令"由具体驱动器决定，对非命令型 IDN 下发执行会返回 Sercos 错误。本库不内置命令清单。
- **命令执行有前置状态要求**：很多过程命令（如换相、归零）只能在驱动器特定状态下执行（如未使能 / 已使能）。状态不对时 `bError` 置位、Sercos 错误码指明"当前状态不允许"。先确认驱动器处在允许状态再触发。（工程经验补充）
- **`stDriveRef` 必须先初始化好**：上电初期过程映像未刷新（`sNetId` 空 / `nSlaveAddr = 0`）时触发会指向错误目标，例程用 `bInit` 守卫。（工程经验补充）
- **命令完成要收尾**：`bBusy` 落下后补一次 `bExecute := FALSE` 调用，否则下次上升沿无法识别。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoEExecuteCommand_ByDriveRef.xml`](../examples/P_Demo_FB_SoEExecuteCommand_ByDriveRef.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_SoEExecuteCommand_ByDriveRef
VAR
    fbExecuteCommand : FB_SoEExecuteCommand_ByDriveRef;
    rtrigExec        : R_TRIG;
    stPlcDriveRef    AT %I* : ST_PlcDriveRef;
    stDriveRef       : ST_DriveRef;
    bInit            : BOOL := TRUE;
    nCmdIdn          : WORD;                        // 目标命令 IDN
    bExecReq         : BOOL := FALSE;               // 在线置 TRUE 触发命令
    bExecBusy        : BOOL;
    bExecError       : BOOL;
    iAdsErr          : UINT;
    iSercosErr       : UINT;
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

// 目标命令 IDN：P-0-0160（厂商参数基址 P_0_IDN + 160）
nCmdIdn := P_0_IDN + 160;

rtrigExec(CLK := bExecReq);

// 单次调用形式：所有 VAR_INPUT 显式赋值
fbExecuteCommand(
    stDriveRef := stDriveRef,
    nIdn       := nCmdIdn,
    bExecute   := rtrigExec.Q AND NOT bInit,
    tTimeout   := DEFAULT_ADS_TIMEOUT,
    bBusy        => bExecBusy,
    bError       => bExecError,
    iAdsErrId    => iAdsErr,
    iSercosErrId => iSercosErr
);

IF NOT bExecBusy AND NOT bInit THEN
    bExecReq := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：需要在运行期间触发 AX5000 的某个过程命令（如重新换相检测、参数固化到 EEPROM、归零等），让 PLC 程序（而非调试器）按流程自动下发命令。
- **价值**：把"按 IDN 下发 Sercos 过程命令 + 异步状态机 + 超时"封装成一次上升沿调用，业务侧只提供命令 IDN 和触发信号，无需手写命令控制字时序。
- **替代方案对比**：
  - 自己用 `FB_SoEWriteCommandControl` + 状态轮询：要管命令控制字（启动/中断）和命令状态字的完整时序
  - 在 Drive Manager 手动点命令：只能调试，不能进生产逻辑
  - **本 FB**：通用命令封装，给个 IDN 就能触发，适合做成自动调试 / 维护流程的一环

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf) §4.1.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_drive/2307546763.html
- **相关**：`FB_SoEReset_ByDriveRef`、`FB_SoEWritePassword_ByDriveRef`（同 General SoE 类）；`P_0_IDN` / `S_0_IDN`（IDN 编码常量）

## 9. 待确认项

- ⚠️ `iAdsErrId` / `iSercosErrId` 取值表 PDF/InfoSys 均未列；可执行命令 IDN 清单由具体驱动器型号决定，需查厂商手册。
