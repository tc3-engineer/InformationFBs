# FB_SoEAX5000SetMotorCtrlWord

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_NcDrive` |
| Library Version | `1.2.9` |
| Type | `FUNCTION_BLOCK` |
| Category | `AX5000 SoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_NcDrive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ncdrive/2305415691.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoEAX5000SetMotorCtrlWord.TcPOU`](../examples/P_Demo_FB_SoEAX5000SetMotorCtrlWord.TcPOU) |

---

## 1. 功能简述

设置 AX5000 驱动器 **Motor Control Word（P-0-0096）**中抱闸控制位的功能块（Function Block, FB）。通过 `bForceLock`（强制锁闸，Bit 0）和 `bForceUnlock`（强制松闸）两个输入，可以**独立于驱动器 Enable** 地手动激活或释放电机抱闸。

正常情况下抱闸是随驱动器 Enable 自动控制的；本 FB 提供绕过 Enable 的手动控制能力。当 `bForceLock` 与 `bForceUnlock` 同时为 `TRUE` 时，`bForceLock`（锁闸）优先级更高。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId       : T_AmsNetId := '';
    bExecute     : BOOL;
    tTimeout     : TIME := DEFAULT_ADS_TIMEOUT;
    bForceLock   : BOOL;
    bForceUnlock : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | `''` | 目标控制器（IPC）的 AMS Network ID 字符串；空串 `''` 表示本机 |
| `bExecute` | `BOOL` | — | 上升沿启动一次设置命令 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 命令执行允许的最长时间 |
| `bForceLock` | `BOOL` | — | 独立于 Enable 激活抱闸（锁闸） |
| `bForceUnlock` | `BOOL` | — | 独立于 Enable 释放抱闸（松闸） |

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
    bBusy        : BOOL;
    bError       : BOOL;
    iAdsErrId    : UINT;
    iSercosErrId : UINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令激活后置 `TRUE`，直到收到反馈才复位；期间不接受新命令 |
| `bError` | `BOOL` | 在 `bBusy` 复位之后，若命令传输发生错误则置 `TRUE` |
| `iAdsErrId` | `UINT` | `bError = TRUE` 时返回上一条命令的 ADS 错误码 |
| `iSercosErrId` | `UINT` | `bError = TRUE` 时返回上一条命令的 Sercos 错误码 |

## 3. 行为说明

**触发与时序**：`bExecute` 上升沿启动设置，`bBusy` 立即置 `TRUE`，FB 把由 `bForceLock` / `bForceUnlock` 组合出的控制位写入 P-0-0096 的 Motor Control Word。收到反馈后 `bBusy` 复位；出错则 `bBusy` 落下后 `bError` 置 `TRUE`，由 `iAdsErrId` / `iSercosErrId` 给出错误码。每次改变锁/松闸意图都需要一次新的 `bExecute` 上升沿。

**优先级规则**：`bForceLock` 与 `bForceUnlock` 同时 `TRUE` 时，**`bForceLock`（锁闸）优先**——出于安全考虑抱闸保持锁定。

**与 Enable 的关系**：默认抱闸跟随驱动器 Enable 自动控制（使能→松闸，去使能→锁闸）。本 FB 是手动覆盖通道：`bForceLock` 可在使能状态下强制锁闸，`bForceUnlock` 可在去使能状态下强制松闸。两个输入都为 `FALSE` 时则交还给 Enable 自动控制。

**安全警示**：在轴带载（如垂直轴挂重物）时 `bForceUnlock` 强制松闸会导致负载下坠，必须确认机械安全后才使用。

## 4. 错误码 / 返回值

本 FB 无函数返回值，错误通过 `bError = TRUE` 配合两个错误码输出表达：

| 输出 | 类型 | 含义 |
|---|---|---|
| `iAdsErrId` | `UINT` | ADS 传输层错误码（命令下发链路问题） |
| `iSercosErrId` | `UINT` | Sercos / SoE 协议层错误码（驱动器拒绝写 P-0-0096 时返回） |

⚠️ PDF 与 InfoSys 在本 FB 章节均未逐条列出具体数值含义。ADS 错误码见 Beckhoff 通用 ADS Return Codes 主题；Sercos 错误码以 AX5000 SoE 参数手册为准。

## 5. 使用注意 / 常见坑

- **强制松闸会让负载下坠**：垂直/带载轴上 `bForceUnlock` 极危险，必须先确认机械有支撑或防坠措施。
- **同时锁+松时锁优先**：`bForceLock` 与 `bForceUnlock` 都为 `TRUE` 时抱闸保持锁定，别误以为"互相抵消"。
- **覆盖会脱离 Enable 自动逻辑**：手动控制期间抱闸不再随使能自动动作，调试完记得把两个输入清回 `FALSE`。
- **边沿触发**：每次改变意图都要新的 `bExecute` 上升沿，光改 `bForceLock` 电平而不重新触发无效。
- **`Axis` 是 VAR_IN_OUT 必须传引用**：传入映射在 `%I*` 上的 `NCTOPLC_AXIS_REF` 实例。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoEAX5000SetMotorCtrlWord.TcPOU`](../examples/P_Demo_FB_SoEAX5000SetMotorCtrlWord.TcPOU)

```iecst
// 场景：维护人员需要在驱动器去使能状态下手动松开电机抱闸，盘动联轴器检查机械
PROGRAM P_Demo_FB_SoEAX5000SetMotorCtrlWord
VAR
    fbSetMotorCtrl    : FB_SoEAX5000SetMotorCtrlWord;
    NcToPlcAxis AT %I*: NCTOPLC_AXIS_REF;
    bManualReleaseReq : BOOL;        // 维护"松闸"请求
    bForceLockReq     : BOOL;        // 维护"锁闸"请求（安全优先）
    rtApply           : R_TRIG;
    bApplyRequest     : BOOL;
    bBusy             : BOOL;
    bError            : BOOL;
    iAdsErr           : UINT;
    iSercosErr        : UINT;
END_VAR

rtApply(CLK := bApplyRequest);
fbSetMotorCtrl(
    Axis         := NcToPlcAxis,
    sNetId       := '',
    bExecute     := rtApply.Q,
    tTimeout     := DEFAULT_ADS_TIMEOUT,
    bForceLock   := bForceLockReq,
    bForceUnlock := bManualReleaseReq,
    bBusy        => bBusy,
    bError       => bError,
    iAdsErrId    => iAdsErr,
    iSercosErrId => iSercosErr
);
IF NOT bBusy THEN
    bApplyRequest := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：维护时去使能盘车需要手动松闸；安全场景下需在使能态强制锁闸；垂直轴的特殊抱闸时序控制。
- **价值**：不用本 FB 时要自己用 `FB_SoEWrite` 拼 P-0-0096 的位掩码并管时序；本 FB 把锁/松闸抽象成两个布尔输入，并内建"锁优先"的安全规则。
- **替代方案对比**：
  - 用 `FB_SoEWrite` 直接写 P-0-0096：通用但要自己算位、易写错优先级
  - 靠驱动器 Enable 自动控制：常规运行够用，但无法在去使能态主动松闸
  - **本 FB**：AX5000 手动抱闸控制的专用封装

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_NcDrive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_NcDrive_EN.pdf) §3.3.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ncdrive/2305415691.html
- **相关 FB**：`FB_SoEWrite`（通用 SoE 写）、`FB_SoEReset`（复位驱动器）
