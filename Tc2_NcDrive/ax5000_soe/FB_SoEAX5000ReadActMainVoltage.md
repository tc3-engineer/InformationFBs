# FB_SoEAX5000ReadActMainVoltage

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_NcDrive` |
| Library Version | `1.2.9` |
| Type | `FUNCTION_BLOCK` |
| Category | `AX5000 SoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_NcDrive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ncdrive/2305388939.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoEAX5000ReadActMainVoltage.TcPOU`](../examples/P_Demo_FB_SoEAX5000ReadActMainVoltage.TcPOU) |

---

## 1. 功能简述

读取 AX5000 驱动器**当前主电源电压峰值**的功能块（Function Block, FB），对应厂商参数 P-0-0200。`bExecute` 上升沿触发后通过 SoE 通道异步读取，结果以伏特（V）为单位经 `fActualMainVoltage`（`LREAL`）返回，例如 `303.0` 表示 303.0 V。

轴/驱动器定位通过 `NCTOPLC_AXIS_REF` 轴引用完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId   : T_AmsNetId := '';
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | `''` | 目标控制器（IPC）的 AMS Network ID 字符串；空串 `''` 表示本机 |
| `bExecute` | `BOOL` | — | 上升沿启动一次读取命令 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 命令执行允许的最长时间 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis : NCTOPLC_AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `NCTOPLC_AXIS_REF` | NC 轴数据结构（映射在 `%I*` 输入过程映像）；本 FB 据此定位目标 AX5000 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy              : BOOL;
    bError             : BOOL;
    iAdsErrId          : UINT;
    iSercosErrId       : UINT;
    dwAttribute        : DWORD;
    fActualMainVoltage : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令激活后置 `TRUE`，直到收到反馈才复位；期间不接受新命令 |
| `bError` | `BOOL` | 在 `bBusy` 复位之后，若命令传输发生错误则置 `TRUE` |
| `iAdsErrId` | `UINT` | `bError = TRUE` 时返回上一条命令的 ADS 错误码 |
| `iSercosErrId` | `UINT` | `bError = TRUE` 时返回上一条命令的 Sercos 错误码 |
| `dwAttribute` | `DWORD` | 返回该 Sercos 参数的属性（attribute）字 |
| `fActualMainVoltage` | `LREAL` | 返回 AX5000 当前主电源电压峰值，单位 V（例：`303.0` = 303.0 V） |

## 3. 行为说明

**触发与时序**：`bExecute` 上升沿启动读取，`bBusy` 立即置 `TRUE`，FB 通过 SoE 异步读 P-0-0200。完成后 `bBusy` 复位，`fActualMainVoltage` 给出电压峰值（单位 V），同时 `dwAttribute` 返回该参数的 Sercos 属性字。若传输出错，`bBusy` 落下后 `bError` 置 `TRUE`，`iAdsErrId` / `iSercosErrId` 给出错误码。标准用法是触发后在 `NOT bBusy` 时把 `bExecute` 写回 `FALSE` 复位边沿，需要刷新读数时再次触发。

**数值单位**：返回值是峰值电压（peak value），直接以浮点伏特表示，PDF 给的样例是 303.0 对应 303.0 V，无需额外换算。

**用途**：可用于监测进线电压是否正常、判断是否欠压/过压风险，或在掉电检测逻辑中作为辅助判据。

## 4. 错误码 / 返回值

本 FB 无函数返回值，错误通过 `bError = TRUE` 配合两个错误码输出表达：

| 输出 | 类型 | 含义 |
|---|---|---|
| `iAdsErrId` | `UINT` | ADS 传输层错误码（命令下发链路问题） |
| `iSercosErrId` | `UINT` | Sercos / SoE 协议层错误码（驱动器拒绝读 P-0-0200 时返回） |

⚠️ PDF 与 InfoSys 在本 FB 章节均未逐条列出具体数值含义。ADS 错误码见 Beckhoff 通用 ADS Return Codes 主题；Sercos 错误码以 AX5000 SoE 参数手册为准。

## 5. 使用注意 / 常见坑

- **返回的是峰值电压**：不是有效值（RMS），做欠压判断时注意基准。
- **边沿触发非周期自动**：本 FB 一次 `bExecute` 读一次；需要持续监测要自己周期性重新触发。
- **`fActualMainVoltage` 类型是 `LREAL`**：例程里若用 `REAL` 变量接收会有隐式转换，工程经验补充建议用 `LREAL` 接。
- **`dwAttribute` 通常用不上**：日常监测只取 `fActualMainVoltage` 即可，`dwAttribute` 是参数元数据。
- **`Axis` 是 VAR_IN_OUT 必须传引用**：传入映射在 `%I*` 上的 `NCTOPLC_AXIS_REF` 实例。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoEAX5000ReadActMainVoltage.TcPOU`](../examples/P_Demo_FB_SoEAX5000ReadActMainVoltage.TcPOU)

```iecst
// 场景：HMI 上显示 AX5000 进线电压，操作员点"刷新"读一次当前主电源电压峰值
PROGRAM P_Demo_FB_SoEAX5000ReadActMainVoltage
VAR
    fbReadMainVoltage : FB_SoEAX5000ReadActMainVoltage;
    NcToPlcAxis AT %I*: NCTOPLC_AXIS_REF;
    bReadRequest      : BOOL;
    rtRead            : R_TRIG;
    bBusy             : BOOL;
    bError            : BOOL;
    iAdsErr           : UINT;
    iSercosErr        : UINT;
    fMainVoltage      : LREAL;        // 监视：当前主电源电压峰值 (V)
END_VAR

rtRead(CLK := bReadRequest);
fbReadMainVoltage(
    Axis     := NcToPlcAxis,
    sNetId   := '',
    bExecute := rtRead.Q,
    tTimeout := DEFAULT_ADS_TIMEOUT,
    bBusy              => bBusy,
    bError             => bError,
    iAdsErrId          => iAdsErr,
    iSercosErrId       => iSercosErr,
    fActualMainVoltage => fMainVoltage
);
IF NOT bBusy THEN
    bReadRequest := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：AX5000 进线电压监测、欠压/过压预警、与掉电检测配合判断电网状态、能耗与电能质量诊断。
- **价值**：不用本 FB 时要自己用 `FB_SoERead` 指定 P-0-0200 的 IDN 并解释返回的原始字节；本 FB 直接给出浮点伏特值，省去 SoE 参数寻址和单位换算。
- **替代方案对比**：
  - 用 `FB_SoERead` 读 P-0-0200：通用但要自己填 IDN、解析数据类型
  - 用 `FB_SoEReadDcBusVoltage`：读的是直流母线电压，物理量不同
  - **本 FB**：读 AX5000 进线峰值电压的专用封装

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_NcDrive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_NcDrive_EN.pdf) §3.3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ncdrive/2305388939.html
- **相关 FB**：`FB_SoERead`（通用 SoE 读）、`FB_SoEReadDcBusVoltage`（直流母线电压）、`FB_SoEAX5000SetMotorCtrlWord`（AX5000 抱闸控制）
