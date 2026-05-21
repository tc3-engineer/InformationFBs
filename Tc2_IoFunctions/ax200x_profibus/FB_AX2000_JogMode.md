# FB_AX2000_JogMode

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `AX200x Profibus` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59140491.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_AX2000_JogMode.xml`](../examples/P_Demo_FB_AX2000_JogMode.xml) |

---

## 1. 功能简述

AX2000 Profibus 伺服点动模式：以基础速度 (`iBasicVelo`) × 驱动器内部 v-jog mode 因子 持续运行。常用于调试期间手动移动轴。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart : BOOL;
    bStop : BOOL;
    iBasicVelo : INT;
    tTimeOut : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bStart` | `BOOL` | - | 上升沿启动点动。 |
| `bStop` | `BOOL` | - | 上升沿停止点动。 |
| `iBasicVelo` | `INT` | - | 基础速度（INT，单位由驱动器配置；最终速度 = iBasicVelo × v-jog factor）。 |
| `tTimeOut` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bErr : BOOL;
    bTimeOutErr : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bErr` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `bTimeOutErr` | `BOOL` | 布尔标志 `bTimeOutErr`。 |

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

`bStart` 上升沿启动点动；`bStop` 上升沿停止。点动期间通过 PZD 持续发送 jog 指令到驱动器；驱动器按 `iBasicVelo` × 内部 v-jog 因子计算实际速度。点动通常用于调试 / 维护，工程切换到自动后应该用 `FB_AX2000_AXACT`。`stPZDIN` / `stPZDOUT` IN_OUT 与 AXACT 一致：必须链到 PZD 区且循环调用。`bBusy` 表示命令处理中；`bErr` / `bTimeOutErr` 表示驱动器故障 / 通讯超时。

## 4. 错误码 / 返回值

本 FB 无具体错误码表；状态由输出参数自行反映。具体错误语义需配合主站 / 现场总线设备手册查询。

## 5. 使用注意 / 常见坑

- AX2000 是 1990s-2000s 的 Kollmorgen 老型号伺服；现代工程基本用 AX5000 (EtherCAT) + Tc2/Tc3 NCI 替代。本系列 FB 仅用于维护老线。
- **`stPZDIN` / `stPZDOUT` 必须链到 System Manager 中 AX2000 在 Profibus 上的 PZD（过程数据）映射区**，否则数据交换不通。（工程经验补充）
- AX2000 通讯通过 Profibus FC310x / EL6731 主站；调用任何 AX2000 FB 前先确保 Profibus 主站本身已正常。（工程经验补充）
- 错误号 `iErrorId` 是 AX2000 驱动器返回的"驱动器错误号"，与 ADS 错误号无关。具体含义见 AX2000 / S300 手册的 Fault Code 表。（工程经验补充）
- 点动模式仅供调试，正常工艺要用 `FB_AX2000_AXACT` 的 motion-task 模式。（工程经验补充）
- 实际速度 = `iBasicVelo` × v-jog factor，因子需在驱动器里配置；不要把 `iBasicVelo` 想当然作物理速度。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_AX2000_JogMode.xml`](../examples/P_Demo_FB_AX2000_JogMode.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：AX2000 维护：把轴点动到机械零位附近，工人按 HMI 上的 jog+ / jog- 按钮。
- **价值**：不用拆驱动器接调试软件即可手动移动轴。
- **替代方案对比**：
  - 用驱动器面板按钮：要打开机柜
  - Drive.exe 调试软件：要插串口 / 网线
  - **本 FB**：HMI 按钮即可

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.3.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59140491.html
- **相关 FB / FC**：`FB_AX2000_AXACT`, `FB_AX2000_Reference`, `FB_AX2000_Parameter`
