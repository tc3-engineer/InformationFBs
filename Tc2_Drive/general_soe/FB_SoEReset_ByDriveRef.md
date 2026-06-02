# FB_SoEReset_ByDriveRef

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Drive` |
| Library Version | `1.4.8` |
| Type | `FUNCTION_BLOCK` |
| Category | `General SoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_drive/2307542283.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoEReset_ByDriveRef.TcPOU`](../examples/P_Demo_FB_SoEReset_ByDriveRef.TcPOU) |

---

## 1. 功能简述

复位 SoE（Sercos over EtherCAT）伺服驱动器错误状态的功能块。本 FB 通过 Sercos 参数 `S-0-0099`（Reset class 1 diagnostics，复位 C1D 报警）向驱动器下发复位命令，把驱动器从故障态拉回可运行态。对于多通道设备（如 AX5000 双通道），必要时每个通道都要各自复位一次。

注意：本 FB 只复位驱动器侧的 Sercos 错误，**不会**触发 NC（运动控制）轴的复位，NC 侧复位需另用 `MC_Reset`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stDriveRef : ST_DriveRef;
    bExecute   : BOOL;
    tTimeout   : TIME := T#10s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stDriveRef` | `ST_DriveRef` | — | 驱动器引用结构。可在 TwinCAT System Manager 中把 `ST_PlcDriveRef`（过程映像，带 `AT %I*`）直接链接到 PLC，再把其中的 NetID 字节数组用 `F_CreateAmsNetId` 转成字符串，逐字段填进 `ST_DriveRef`（含 `sNetId` / `nSlaveAddr` / `nDriveNo` / `nDriveType`） |
| `bExecute` | `BOOL` | — | 上升沿触发一次复位命令。调用期间保持，命令完成（`bBusy` 转 `FALSE`）后再手动复位为 `FALSE` |
| `tTimeout` | `TIME` | `T#10s` | 命令执行允许的最长时间。**必须给到 10 秒**：根据错误类型，复位过程最长可能耗时 10 秒，给太短会误判超时 |

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
| `bBusy` | `BOOL` | FB 被激活（命令下发中）时置位，直到收到驱动器反馈才复位。`TRUE` 期间不要改输入 |
| `bError` | `BOOL` | 在 `bBusy` 复位之后，若命令传输过程中发生错误则置位 |
| `iAdsErrId` | `UINT` | `bError` 置位时，返回上一条命令的 ADS 错误码 |
| `iSercosErrId` | `UINT` | `bError` 置位时，返回上一条命令的 Sercos 错误码 |

### VAR_IN_OUT

无。

## 3. 行为说明

本 FB 是典型的异步命令型功能块，靠 `bExecute` 上升沿驱动一次性动作：

1. **触发**：在 `bExecute` 检测到上升沿，FB 把 `stDriveRef` 解析出的目标（NetID + 从站地址 + 通道号）作为 SoE 写入对象，向 `S-0-0099` 下发复位命令，同时把 `bBusy` 置 `TRUE`。
2. **执行中**：`bBusy` 保持 `TRUE`，期间 FB 反复被周期调用以推进内部 ADS 状态机并等待驱动器回执。此阶段不可改变输入参数。
3. **完成分支**：收到驱动器反馈后 `bBusy` 复位为 `FALSE`。若传输无误，`bError` 保持 `FALSE`，复位成功；若出错，`bError` 置 `TRUE`，并在 `iAdsErrId` / `iSercosErrId` 给出错误码。

**寻址语义**：SoE 驱动参数用 IDN（Identification Number）寻址，形如 `S-0-0099`（S = 标准参数，0 = 参数集，0099 = 编号）。本 FB 内部已写死目标 IDN，调用方只需提供 `stDriveRef` 指明是哪台驱动器。

**调用范式**：必须每周期调用本 FB 实例以推进状态机；命令完成后用一次 `bExecute := FALSE` 的调用收尾（见例程），下次再上升沿即可重新触发。多通道设备每个通道需独立实例分别复位。

**典型用法**：驱动器报 C1D 故障（如过流、过温恢复后），操作员按"复位"按钮，PLC 给本 FB 一个 `bExecute` 上升沿，把驱动器从故障态清回待命态，再走 enable 流程重新使能。

## 4. 错误码 / 返回值

| 输出 | 含义 | 处理建议 |
|---|---|---|
| `bError = FALSE`（且 `bBusy` 已落） | 复位命令成功送达并被驱动器接受 | 可继续 enable 流程 |
| `bError = TRUE` | 命令传输出错 | 读 `iAdsErrId` 与 `iSercosErrId` 定位 |
| `iAdsErrId`（UINT） | ADS 通讯层错误码（如目标不可达、超时） | 参考 Beckhoff "ADS Return Codes" 表 |
| `iSercosErrId`（UINT） | 驱动器返回的 Sercos 错误码 | 参考对应驱动器（如 AX5000）的 Sercos 错误码 / IDN 诊断手册 |

PDF 与 InfoSys 均未逐条列出 `iAdsErrId` / `iSercosErrId` 的具体取值表。ADS 码查通用 "ADS Return Codes"；Sercos 码查驱动器厂商手册的诊断章节（⚠️ 待人工对照具体驱动器型号）。

## 5. 使用注意 / 常见坑

- **`tTimeout` 不要小于 10 秒**：PDF 明确指出复位最长可能要 10 秒，默认值就是 `T#10s`。改小了会在驱动器还在复位时就误报超时。
- **多通道设备每通道单独复位**：AX5000 等双通道驱动器，A、B 通道是各自独立的 SoE 设备，复位一个不影响另一个；两个都报错就要两个实例分别复位。（PDF 原话）
- **本 FB 不复位 NC 轴**：复位完驱动器后，如果该轴挂在 NC 下，NC 侧的轴错误仍在，还要调 `MC_Reset`。只调本 FB 会出现"驱动器好了但 NC 轴还报错"。（PDF 明确：An NC reset will not be performed）
- **`stDriveRef` 必须先初始化好再触发**：`sNetId` 为空串或 `nSlaveAddr = 0` 说明过程映像还没刷上来（上电初期），此时触发会指向错误目标。例程里用 `bInit` 守卫等 `sNetId <> ''` 且 `nSlaveAddr <> 0` 才允许执行。（工程经验补充）
- **命令完成要收尾**：`bBusy` 落下后要补一次 `bExecute := FALSE` 的调用，否则下个上升沿无法识别。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoEReset_ByDriveRef.TcPOU`](../examples/P_Demo_FB_SoEReset_ByDriveRef.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_SoEReset_ByDriveRef
VAR
    fbSoEReset      : FB_SoEReset_ByDriveRef;
    rtrigReset      : R_TRIG;                       // bExecute 仅取上升沿
    stPlcDriveRef   AT %I* : ST_PlcDriveRef;        // 链接到 System Manager 的驱动器过程映像
    stDriveRef      : ST_DriveRef;                  // 解析出的驱动器引用
    bInit           : BOOL := TRUE;                 // 等过程映像刷上来再放行
    bResetReq       : BOOL := FALSE;                // 在线置 TRUE 触发复位
    bResetBusy      : BOOL;                         // 在线 monitor
    bResetError     : BOOL;
    iAdsErr         : UINT;
    iSercosErr      : UINT;
END_VAR

// 初始化：把过程映像里的 NetID 字节数组转成字符串，逐字段填入 stDriveRef
IF bInit THEN
    stDriveRef.sNetId     := F_CreateAmsNetId(stPlcDriveRef.aNetId);
    stDriveRef.nSlaveAddr := stPlcDriveRef.nSlaveAddr;
    stDriveRef.nDriveNo   := stPlcDriveRef.nDriveNo;
    stDriveRef.nDriveType := stPlcDriveRef.nDriveType;
    IF (stDriveRef.sNetId &lt;&gt; '') AND (stDriveRef.nSlaveAddr &lt;&gt; 0) THEN
        bInit := FALSE;                             // 过程映像已就绪，放行
    END_IF;
END_IF;

rtrigReset(CLK := bResetReq);

// 单次调用形式：所有 VAR_INPUT 显式赋值；tTimeout 必须给足 10 秒
fbSoEReset(
    stDriveRef := stDriveRef,
    bExecute   := rtrigReset.Q AND NOT bInit,
    tTimeout   := T#10S,
    bBusy        => bResetBusy,
    bError       => bResetError,
    iAdsErrId    => iAdsErr,
    iSercosErrId => iSercosErr
);

// 命令完成后收尾：bBusy 落下且请求标志还在，则清请求让 FB 复位
IF NOT bResetBusy AND NOT bInit THEN
    bResetReq := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：AX5000 伺服驱动器在过流 / 过温 / 反馈故障恢复后停在 C1D 故障态，需要在 PLC 程序里（而不是只在 TwinCAT Scope/调试器里）一键复位，让操作员按面板按钮就能清错重启。
- **价值**：把"向 `S-0-0099` 写复位命令 + ADS 异步状态机 + 超时管理"封装成一个上升沿触发的调用，业务侧只需提供驱动器引用和一个按钮信号。
- **替代方案对比**：
  - 自己用 `FB_SoEWrite` / ADS 写 `S-0-0099`：要自己管 IDN 编码、异步状态机、10 秒超时，约 20+ 行
  - 在 TwinCAT 工程里手动用 Drive Manager 复位：只能调试时人工点，不能进生产 PLC 逻辑
  - **本 FB**：专为 `S-0-0099` 复位封装，一次上升沿搞定，适合做成 HMI 复位按钮的后端

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf) §4.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_drive/2307542283.html
- **相关**：`FB_SoEExecuteCommand_ByDriveRef`（通用 SoE 命令）、`FB_SoEWritePassword_ByDriveRef`（同 General SoE 类）、`MC_Reset`（NC 轴复位，配套）

## 9. 待确认项

- ⚠️ `iAdsErrId` / `iSercosErrId` 的具体取值表 PDF 与 InfoSys 均未列出，需对照通用 ADS Return Codes 与具体驱动器型号的 Sercos 错误码手册。
