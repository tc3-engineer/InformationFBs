# FB_SoEReset

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_NcDrive` |
| Library Version | `1.2.9` |
| Type | `FUNCTION_BLOCK` |
| Category | `General SoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_NcDrive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ncdrive/2304974347.html |
| Verified | 2026-05-25 ✅ |
| InfoSys-checked | ✅ 2026-05-25 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoEReset.xml`](../examples/P_Demo_FB_SoEReset.xml) |

---

## 1. 功能简述

通过 SoE 参数 S-0-0099 对伺服驱动器执行**复位**的功能块（Function Block, FB）。把 NC 轴的轴引用（`AXIS_REF` 派生的 `NCTOPLC_AXIS_REF`）传进来，`bExecute` 上升沿触发后向对应驱动器下发 Sercos-over-EtherCAT（SoE）复位命令，用于清除驱动器侧的错误状态。

本 FB **只复位驱动器，不复位 NC 轴**。若驱动器复位后 NC 轴仍处于错误，需另外调用 Tc2_MC2 库的 `MC_Reset` 复位 NC 通道。

对多通道设备（如双通道 AX5000），必要时两个通道都要各自执行一次复位。

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
| `bExecute` | `BOOL` | — | 上升沿启动一次复位命令 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 命令执行允许的最长时间；复位最长可耗时 10 秒，故本 FB 实际须给到 10 s 超时 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis : NCTOPLC_AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `NCTOPLC_AXIS_REF` | NC 轴数据结构（`NcToPlc`，映射在 `%I*` 输入过程映像上）；本 FB 通过它定位到对应驱动器 |

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
| `bBusy` | `BOOL` | 命令激活后置 `TRUE`，直到收到反馈才复位；`bBusy = TRUE` 期间不接受新命令 |
| `bError` | `BOOL` | 在 `bBusy` 复位之后，若命令传输发生错误则置 `TRUE` |
| `iAdsErrId` | `UINT` | `bError = TRUE` 时返回上一条命令的 ADS 错误码 |
| `iSercosErrId` | `UINT` | `bError = TRUE` 时返回上一条命令的 Sercos 错误码 |

## 3. 行为说明

**触发与时序**：`bExecute` 上升沿启动复位，`bBusy` 立即变 `TRUE`，FB 向驱动器写 S-0-0099。复位最长可持续 10 秒（取决于错误类型），整个过程 `bBusy` 保持 `TRUE`；收到驱动器反馈后 `bBusy` 复位。若传输出错，在 `bBusy` 落下之后 `bError` 置 `TRUE`，并由 `iAdsErrId` / `iSercosErrId` 给出错误码。典型用法是 `bExecute := TRUE` 触发后，在 `NOT bBusy` 时把 `bExecute` 写回 `FALSE` 复位边沿。

**超时要求**：由于复位最长 10 秒，`tTimeout` 必须给足（默认 `DEFAULT_ADS_TIMEOUT` 偏小，工程上建议显式传 `T#10S` 或更大），否则会因超时报错而误判复位失败。

**AX5000 前置条件**：在 AX5000 的 EtherCAT 高级设置（Advanced Settings）中必须勾选 "Wait For WcState is OK" 标志，否则复位可能不可靠。

**与 NC 复位的区别**：本 FB **不执行 NC 复位**。它只清驱动器侧错误；NC 通道的错误（如跟随误差停机）需用 Tc2_MC2 库的 `MC_Reset(Axis)` 单独复位。两者职责分离，遇到"复位后轴仍报错"时要分清是驱动器错误还是 NC 错误。

**多通道设备**：双通道设备必要时需对两个通道各调用一次本 FB。

## 4. 错误码 / 返回值

本 FB 无函数返回值，错误通过 `bError = TRUE` 配合两个错误码输出表达：

| 输出 | 类型 | 含义 |
|---|---|---|
| `iAdsErrId` | `UINT` | ADS 传输层错误码（命令下发链路问题，如超时、轴未就绪、NetId 错误） |
| `iSercosErrId` | `UINT` | Sercos / SoE 协议层错误码（驱动器拒绝该 S-0-0099 操作时返回） |

⚠️ PDF 与 InfoSys 在本 FB 章节均未逐条列出 `iAdsErrId` / `iSercosErrId` 的具体数值含义。ADS 错误码总表见 Beckhoff InfoSys 通用 ADS Return Codes 主题；Sercos 错误码以驱动器手册（AX5000 SoE 参数文档）为准。

## 5. 使用注意 / 常见坑

- **超时必须给够 10 秒**：默认 `DEFAULT_ADS_TIMEOUT` 通常只有几秒，复位长耗时场景会误超时。工程经验补充：显式传 `T#10S`。
- **驱动器复位 ≠ NC 复位**：复位后轴仍报错时，记得再调 `MC_Reset`，别只盯着本 FB。
- **AX5000 漏勾 "Wait For WcState is OK"**：会导致复位行为不稳定，是常见配置坑。
- **多通道要各复位一次**：双通道设备只复位一个通道时，另一通道仍处于错误。
- **边沿触发，需手动复位 `bExecute`**：`bBusy` 落下后把 `bExecute` 写 `FALSE`，否则无法触发下一次复位。
- **`Axis` 是 VAR_IN_OUT 必须传引用**：传入映射在 `%I*` 上的 `NCTOPLC_AXIS_REF` 实例。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoEReset.xml`](../examples/P_Demo_FB_SoEReset.xml)

```iecst
// 场景：AX5000 伺服因瞬时过流报错停机，HMI 上操作员按"复位"按钮，需要清驱动器错误后重新使能
PROGRAM P_Demo_FB_SoEReset
VAR
    fbDriveReset      : FB_SoEReset;
    NcToPlcAxis AT %I*: NCTOPLC_AXIS_REF;      // NC 轴过程映像
    bResetRequest     : BOOL;                   // HMI 复位按钮
    rtReset           : R_TRIG;
    bResetBusy        : BOOL;
    bResetError       : BOOL;
    iAdsErr           : UINT;
    iSercosErr        : UINT;
END_VAR

rtReset(CLK := bResetRequest);
fbDriveReset(
    Axis     := NcToPlcAxis,
    sNetId   := '',
    bExecute := rtReset.Q,
    tTimeout := T#10S,
    bBusy        => bResetBusy,
    bError       => bResetError,
    iAdsErrId    => iAdsErr,
    iSercosErrId => iSercosErr
);
IF NOT bResetBusy THEN
    bResetRequest := FALSE;     // 复位边沿，准备下一次触发
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：伺服驱动器（典型 AX5000）发生过流、过压、编码器报警等驱动器侧错误后需要清错重启；产线换班复位、故障恢复流程的标准动作。
- **价值**：不用本 FB 时需要手工用 `FB_SoEWrite` 往 S-0-0099 写复位值并自己处理 SoE 时序与 10 秒超时；本 FB 把这套 SoE 复位流程封装成一个 `bExecute` 边沿，并分离出 ADS / Sercos 两路错误码，定位问题更快。
- **替代方案对比**：
  - 用 `FB_SoEWrite` 直接写 S-0-0099：通用但要自己组织时序与超时，易写错
  - 用 Tc2_MC2 `MC_Reset`：复位的是 **NC 轴**而非驱动器，作用层不同，不能互相替代
  - **本 FB**：驱动器侧 SoE 复位的首选封装

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_NcDrive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_NcDrive_EN.pdf) §3.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ncdrive/2304974347.html
- **相关 FB**：`FB_SoEWrite`（通用 SoE 写）、`MC_Reset`（Tc2_MC2，复位 NC 轴）、`FB_SoEAX5000SetMotorCtrlWord`（AX5000 抱闸控制）
