# FB_SoEAX5000ReadActMainVoltage_ByDriveRef

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Drive` |
| Library Version | `1.4.8` |
| Type | `FUNCTION_BLOCK` |
| Category | `AX5000 SoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_drive/2307572363.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoEAX5000ReadActMainVoltage_ByDriveRef.xml`](../examples/P_Demo_FB_SoEAX5000ReadActMainVoltage_ByDriveRef.xml) |

---

## 1. 功能简述

读取 AX5000 伺服驱动器当前主电源电压峰值的功能块。本 FB 通过 SoE 读取厂商参数 `P-0-0200`，返回 AX5000 直流母线 / 主电源的当前峰值电压（以 V 为单位的 `REAL`），同时返回该 Sercos 参数的属性字 `dwAttribute`。

典型用途是监视供电是否正常（欠压 / 过压判断），或在掉电检测、母线电压诊断逻辑里读取实时电压。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    stDriveRef : ST_DriveRef;
    bExecute   : BOOL;
    tTimeout   : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stDriveRef` | `ST_DriveRef` | — | 驱动器引用结构。可在 System Manager 把 `ST_PlcDriveRef`（`AT %I*` 过程映像）链接到 PLC，再用 `F_CreateAmsNetId` 把 NetID 字节数组转字符串后逐字段填入 |
| `bExecute` | `BOOL` | — | 上升沿激活本 FB 执行一次读取；调用期间保持，完成后手动复位 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 命令执行允许的最长时间。`DEFAULT_ADS_TIMEOUT` 是 Tc2_System 全局常量（典型 5 秒） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy              : BOOL;
    bError             : BOOL;
    iAdsErrId          : UINT;
    iSercosErrId       : UINT;
    dwAttribute        : DWORD;
    fActualMainVoltage : REAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | FB 被激活时置位，直到收到驱动器反馈才复位 |
| `bError` | `BOOL` | 在 `bBusy` 复位之后，若命令传输出错则置位 |
| `iAdsErrId` | `UINT` | `bError` 置位时返回上一条命令的 ADS 错误码 |
| `iSercosErrId` | `UINT` | `bError` 置位时返回上一条命令的 Sercos 错误码 |
| `dwAttribute` | `DWORD` | 返回该 Sercos 参数（`P-0-0200`）的属性字（含数据长度、定点小数位等编码信息） |
| `fActualMainVoltage` | `REAL` | 返回 AX5000 当前主电源电压峰值，例如 `303.0` 表示 303.0 V |

### VAR_IN_OUT

无。

## 3. 行为说明

本 FB 是 `bExecute` 上升沿驱动的异步读取型功能块：

1. **触发**：`bExecute` 上升沿时，FB 向 `stDriveRef` 指向的 AX5000 通过 SoE 读取 `P-0-0200`，置 `bBusy := TRUE`。
2. **执行中**：`bBusy` 保持 `TRUE`，FB 周期推进内部 ADS 状态机等待驱动器返回数据。期间不改输入。
3. **完成分支**：收到反馈后 `bBusy := FALSE`。无误则 `bError = FALSE`，此时 `fActualMainVoltage` 给出电压峰值、`dwAttribute` 给出参数属性；出错则 `bError := TRUE` 并给出 `iAdsErrId` / `iSercosErrId`，电压输出无效。

**IDN 寻址语义**：`P-0-0200` 是 AX5000 厂商参数（P = product/manufacturer 参数集）。本 FB 内部已固定该 IDN，调用方只提供 `stDriveRef`。

**单次读 vs 周期读**：本 FB 是单次触发读取，不是周期刷新。要持续监视电压，需周期性给 `bExecute` 上升沿（如每 1 秒触发一次，配合完成后收尾）。如果需要极高频实时电压，应改用过程数据（PDO）映射而非 SoE 服务通道。（工程经验补充）

**调用范式**：每周期调用实例推进状态机；`bBusy` 落下后补一次 `bExecute := FALSE` 调用收尾，下次再触发即可重新读。

## 4. 错误码 / 返回值

| 输出 | 含义 | 处理建议 |
|---|---|---|
| `bError = FALSE`（`bBusy` 已落） | 读取成功 | 使用 `fActualMainVoltage` 值 |
| `bError = TRUE` | 读取出错 | 读 `iAdsErrId` / `iSercosErrId`，此时电压输出无效 |
| `iAdsErrId`（UINT） | ADS 通讯层错误码 | 参考 "ADS Return Codes" 表 |
| `iSercosErrId`（UINT） | 驱动器返回的 Sercos 错误码 | 参考 AX5000 的 Sercos 错误码 / IDN 手册 |

PDF 与 InfoSys 均未列出具体错误码表（⚠️ 待人工对照 AX5000 手册）。

## 5. 使用注意 / 常见坑

- **`fActualMainVoltage` 是峰值不是有效值**：PDF 明确返回的是峰值（peak value），不要当成 RMS 直接和铭牌额定电压比较。如三相 230 V RMS 峰值约 325 V。（PDF 原话 + 工程经验补充）
- **只在 `bError = FALSE` 且 `bBusy` 已落时才读 `fActualMainVoltage`**：执行中或出错时电压输出是旧值 / 无效值，误用会导致欠压误判。（工程经验补充）
- **不要用本 FB 做高频实时电压采样**：SoE 服务通道是非周期通讯，单次读有几个周期延迟。掉电瞬间的快速电压跌落检测应用 PDO（过程数据）映射的母线电压通道。（工程经验补充）
- **`stDriveRef` 必须先初始化好**：上电初期过程映像未刷新时触发会指向错误目标，例程用 `bInit` 守卫。（工程经验补充）
- **此 FB 仅适用于 AX5000**：`P-0-0200` 是 AX5000 厂商参数，对其它型号驱动器读这个 IDN 会返回 Sercos 错误。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoEAX5000ReadActMainVoltage_ByDriveRef.xml`](../examples/P_Demo_FB_SoEAX5000ReadActMainVoltage_ByDriveRef.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_FB_SoEAX5000ReadActMainVoltage_ByDriveRef
VAR
    fbReadVoltage   : FB_SoEAX5000ReadActMainVoltage_ByDriveRef;
    rtrigRead       : R_TRIG;
    stPlcDriveRef   AT %I* : ST_PlcDriveRef;
    stDriveRef      : ST_DriveRef;
    bInit           : BOOL := TRUE;
    bReadReq        : BOOL := FALSE;               // 在线置 TRUE 读一次电压
    bReadBusy       : BOOL;
    bReadError      : BOOL;
    iAdsErr         : UINT;
    iSercosErr      : UINT;
    dwAttr          : DWORD;
    fMainVoltage    : REAL;                        // 在线 monitor：主电源峰值电压(V)
    bUnderVoltage   : BOOL;                        // 简单欠压判断结果
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

rtrigRead(CLK := bReadReq);

// 单次调用形式：所有 VAR_INPUT 显式赋值
fbReadVoltage(
    stDriveRef := stDriveRef,
    bExecute   := rtrigRead.Q AND NOT bInit,
    tTimeout   := DEFAULT_ADS_TIMEOUT,
    bBusy              => bReadBusy,
    bError             => bReadError,
    iAdsErrId          => iAdsErr,
    iSercosErrId       => iSercosErr,
    dwAttribute        => dwAttr,
    fActualMainVoltage => fMainVoltage
);

// 读取成功后才做欠压判断（峰值 < 250V 视为欠压示例阈值）
IF NOT bReadBusy AND NOT bReadError AND NOT bInit THEN
    bUnderVoltage := fMainVoltage < 250.0;
    bReadReq := FALSE;                             // 收尾，便于下次再触发
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：监视 AX5000 主供电是否正常（欠压会导致力矩不足 / 报警），或在掉电检测逻辑里读实时母线电压，作为是否触发紧急停机 / 数据保存的依据。
- **价值**：把"读 `P-0-0200` + 解析 REAL + 异步状态机 + 超时"封装成一次上升沿调用，业务侧只需触发信号即可拿到电压值，无需手写 SoE 读时序。
- **替代方案对比**：
  - 用 `FB_SoERead` 自己读 `P-0-0200`：要自己处理 IDN、数据类型转换、属性字解析
  - PDO 映射母线电压通道：实时性最好但占过程数据带宽，且不是所有配置都映射了该通道
  - **本 FB**：专为 `P-0-0200` 封装，按需读取，适合低频电压监视 / 诊断

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Drive_EN.pdf) §4.2.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_drive/2307572363.html
- **相关**：`FB_SoEAX5000SetMotorCtrlWord_ByDriveRef`、`FB_SoEAX5000ParkAxis_ByDriveRef`（同 AX5000 SoE 类）；`FB_SoERead`（通用 SoE 读）

## 9. 待确认项

- ⚠️ `iAdsErrId` / `iSercosErrId` 取值表 PDF/InfoSys 均未列；`dwAttribute` 各 bit 含义需查 Sercos 参数属性编码规范 / AX5000 手册。
