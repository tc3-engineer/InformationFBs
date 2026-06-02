# FB_AX2000_Reference

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `AX200x Profibus` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59143563.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_AX2000_Reference.TcPOU`](../examples/P_Demo_FB_AX2000_Reference.TcPOU) |

---

## 1. 功能简述

AX2000 Profibus 伺服回参考 / 设定参考点 FB。可设定当前位置为参考点 (`bSetRefPoint`)，或启动 / 停止 homing 找参考点 (`bCalibrStart` / `bCalibrStop`)。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bSetRefPoint : BOOL;
    bCalibrStart : BOOL;
    bCalibrStop : BOOL;
    iCalVelo : WORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bSetRefPoint` | `BOOL` | 上升沿把当前位置设为参考点（零位）。 |
| `bCalibrStart` | `BOOL` | 上升沿启动 homing 找参考点。 |
| `bCalibrStop` | `BOOL` | 上升沿中止 homing。 |
| `iCalVelo` | `WORD` | homing 基础速度（最终速度 = iCalVelo × v-jog factor）。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bErr : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bErr` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |

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

`bSetRefPoint` 上升沿 → 把当前位置标记为参考点（零位）。`bCalibrStart` 上升沿 → 启动 homing：驱动器按内部配置的 homing 方法（限位回、Z 脉冲、原点感应器等）找参考点；速度由 `iCalVelo` × v-jog factor 决定。`bCalibrStop` 上升沿 → 中止 homing。完成 / 出错通过 `bBusy` 落回 + `bErr` 反映。与其它 AX2000 FB 一样，本 FB 通过 PZD 与驱动器交换，因此 `stPZDIN` / `stPZDOUT` 必须链到 System Manager 的 PZD 区，且必须循环调用。

## 4. 错误码 / 返回值

本 FB 无具体错误码表；状态由输出参数自行反映。具体错误语义需配合主站 / 现场总线设备手册查询。

## 5. 使用注意 / 常见坑

- AX2000 是 1990s-2000s 的 Kollmorgen 老型号伺服；现代工程基本用 AX5000 (EtherCAT) + Tc2/Tc3 NCI 替代。本系列 FB 仅用于维护老线。
- **`stPZDIN` / `stPZDOUT` 必须链到 System Manager 中 AX2000 在 Profibus 上的 PZD（过程数据）映射区**，否则数据交换不通。（工程经验补充）
- AX2000 通讯通过 Profibus FC310x / EL6731 主站；调用任何 AX2000 FB 前先确保 Profibus 主站本身已正常。（工程经验补充）
- 错误号 `iErrorId` 是 AX2000 驱动器返回的"驱动器错误号"，与 ADS 错误号无关。具体含义见 AX2000 / S300 手册的 Fault Code 表。（工程经验补充）
- homing 方法（用限位 / Z 脉冲 / 感应器）在驱动器侧配置，本 FB 不能切换方法。（工程经验补充）
- homing 可能撞到机械限位；调试时务必先观察 limit switch 信号正确接入。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_AX2000_Reference.TcPOU`](../examples/P_Demo_FB_AX2000_Reference.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：AX2000 印刷套筒维修后重新对零：先用 jog 移到接近原点 → `bCalibrStart` 让伺服找精确零位。
- **价值**：把 homing 流程做成程序接口，可在 HMI 一键触发。
- **替代方案对比**：
  - 手动 jog + 看尺读数：人工操作易错
  - 驱动器面板 homing：要打开机柜
  - **本 FB**：HMI 触发

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.3.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59143563.html
- **相关 FB / FC**：`FB_AX2000_AXACT`, `FB_AX2000_JogMode`, `FB_AX200X_Profibus`
