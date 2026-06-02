# FB_AX200X_Profibus

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `AX200x Profibus` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59145099.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_AX200X_Profibus.TcPOU`](../examples/P_Demo_FB_AX200X_Profibus.TcPOU) |

---

## 1. 功能简述

AX2000 综合 FB：整合 AXACT + JogMode + Reference 的功能（不含参数读写）。所有 motion / jog / homing 的入口都在这里，按 `iRunningMode` 切换：0 = Digital speed，1 = Motiontask，2 = JogMode，3 = Calibration。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bInit : BOOL;
    bMode_DigitalSpeed : BOOL;
    iDigitalSpeed : DWORD;
    iVelocity : DWORD;
    iPosition : DINT;
    iRunningMode : BYTE;
    imotion_tasknumber : WORD;
    imotion_blocktype : WORD := 16#2000;
    iJogModeBasicValue : INT;
    iCalVelo : WORD;
    bSetRefPoint : BOOL;
    bStart : BOOL;
    bStop : BOOL;
    bShortStop : BOOL;
    iSlaveAddress : BYTE;
    iFC310xDeviceId : WORD;
    bErrorResume : BOOL;
    tTimeOut : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bInit` | `BOOL` | - | 上升沿初始化驱动器到指定 operation mode。 |
| `bMode_DigitalSpeed` | `BOOL` | - | 初始化时是否切到 Digital speed 模式（否则默认 positioning）。 |
| `iDigitalSpeed` | `DWORD` | - | Digital speed 模式下的直接速度指令。 |
| `iVelocity` | `DWORD` | - | Motiontask 模式下的运行速度。 |
| `iPosition` | `DINT` | - | Motiontask 模式下的目标位置。 |
| `iRunningMode` | `BYTE` | - | 0=Digital speed, 1=Motiontask, 2=JogMode, 3=Calibration。 |
| `imotion_tasknumber` | `WORD` | - | 无符号整数 `imotion_tasknumber`。 |
| `imotion_blocktype` | `WORD` | `16#2000` | 无符号整数 `imotion_blocktype`。 |
| `iJogModeBasicValue` | `INT` | - | JogMode 基础速度。 |
| `iCalVelo` | `WORD` | - | Calibration (homing) 基础速度。 |
| `bSetRefPoint` | `BOOL` | - | 上升沿设当前为参考点。 |
| `bStart` | `BOOL` | - | 上升沿触发一次执行；调用期间保持高电平，完成后由用户决定何时回 FALSE 准备下次触发。 |
| `bStop` | `BOOL` | - | 布尔标志 `bStop`。 |
| `bShortStop` | `BOOL` | - | 布尔标志 `bShortStop`。 |
| `iSlaveAddress` | `BYTE` | - | 无符号整数 `iSlaveAddress`。 |
| `iFC310xDeviceId` | `WORD` | - | 无符号整数 `iFC310xDeviceId`。 |
| `bErrorResume` | `BOOL` | - | 布尔标志 `bErrorResume`。 |
| `tTimeOut` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    iErrID : DWORD;
    bTimeOutErr : BOOL;
    bInitOK : BOOL;
    iactPosition : DINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bError` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `iErrID` | `DWORD` | 无符号整数 `iErrID`。 |
| `bTimeOutErr` | `BOOL` | 布尔标志 `bTimeOutErr`。 |
| `bInitOK` | `BOOL` | 布尔标志 `bInitOK`。 |
| `iactPosition` | `DINT` | 有符号整数 `iactPosition`。 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stPZDIN : ST_PZD_IN;
    stPZDOUT : ST_PZD_OUT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stPZDIN` | `ST_PZD_IN` | 参数 `stPZDIN`（类型 `ST_PZD_IN`）。 |
| `stPZDOUT` | `ST_PZD_OUT` | 参数 `stPZDOUT`（类型 `ST_PZD_OUT`）。 |

## 3. 行为说明

`bInit` 上升沿在驱动器内部置 operation mode 2（positioning）作为初始化。`iRunningMode` 切换当前动作类型：0 = Digital speed（用 `iDigitalSpeed` 直接给速度），1 = Motiontask（执行 `imotion_tasknumber` 内存中存的 motion 块），2 = JogMode（用 `iJogModeBasicValue` 点动），3 = Calibration（用 `iCalVelo` homing）。`bStart` / `bStop` / `bShortStop` / `bErrorResume` 与 AXACT 一致。`bMode_DigitalSpeed` 初始化时把驱动器置入 Digital speed 模式而非默认的 positioning 模式。本 FB 内部循环调用 AXACT/JogMode/Reference 的功能，外部只需要调本一个 FB。

## 4. 错误码 / 返回值

本 FB 无具体错误码表；状态由输出参数自行反映。具体错误语义需配合主站 / 现场总线设备手册查询。

## 5. 使用注意 / 常见坑

- AX2000 是 1990s-2000s 的 Kollmorgen 老型号伺服；现代工程基本用 AX5000 (EtherCAT) + Tc2/Tc3 NCI 替代。本系列 FB 仅用于维护老线。
- **`stPZDIN` / `stPZDOUT` 必须链到 System Manager 中 AX2000 在 Profibus 上的 PZD（过程数据）映射区**，否则数据交换不通。（工程经验补充）
- AX2000 通讯通过 Profibus FC310x / EL6731 主站；调用任何 AX2000 FB 前先确保 Profibus 主站本身已正常。（工程经验补充）
- 错误号 `iErrorId` 是 AX2000 驱动器返回的"驱动器错误号"，与 ADS 错误号无关。具体含义见 AX2000 / S300 手册的 Fault Code 表。（工程经验补充）
- **本 FB 是综合接口，便于新工程使用**；维护时若发现某一动作有问题，可拆分调用单独的 AXACT/JogMode/Reference 来排查。（工程经验补充）
- 参数读写不在本 FB 内——需要 `FB_AX2000_Parameter` 配套。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_AX200X_Profibus.TcPOU`](../examples/P_Demo_FB_AX200X_Profibus.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：AX2000 新接入工程：用一个 FB 涵盖 motion 全功能，业务程序按 iRunningMode 切动作类型。
- **价值**：单一接口，减少业务程序中维护多个 AX2000 FB 实例的复杂度。
- **替代方案对比**：
  - 分别用 AXACT / JogMode / Reference 三个 FB：灵活但更多代码
  - **本 FB**：综合接口

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.3.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59145099.html
- **相关 FB / FC**：`FB_AX2000_AXACT`, `FB_AX2000_JogMode`, `FB_AX2000_Reference`, `FB_AX2000_Parameter`
