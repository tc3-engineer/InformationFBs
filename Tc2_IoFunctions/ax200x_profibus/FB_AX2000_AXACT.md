# FB_AX2000_AXACT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `AX200x Profibus` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59138955.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_AX2000_AXACT.xml`](../examples/P_Demo_FB_AX2000_AXACT.xml) |

---

## 1. 功能简述

AX2000 Profibus 伺服轴动作命令 FB：启动 / 停止 / 短停 / 错误复位、设定速度 / 位置 / motion-task。**必须循环调用**（必须每个 PLC 周期调用一次，PDF 明确说明）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    iVelocity : DWORD;
    iPosition : DINT;
    imotion_tasknumber : WORD;
    imotion_blocktype : WORD;
    bStart : BOOL;
    bStop : BOOL;
    bShortStop : BOOL;
    bErrorResume : BOOL;
    tTimeOut : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `iVelocity` | `DWORD` | - | 目标速度（典型单位 μm/s 或者驱动器配置的工程单位）。 |
| `iPosition` | `DINT` | - | 目标位置（典型单位 μm 或度，依驱动器配置）。 |
| `imotion_tasknumber` | `WORD` | - | 驱动器内存里预存的 motion-task 块编号；若用直接指令则忽略。 |
| `imotion_blocktype` | `WORD` | - | motion-task 类型（位运算 flag，可选项参见 AX2000 手册）。 |
| `bStart` | `BOOL` | - | 上升沿向驱动器发 start 命令。 |
| `bStop` | `BOOL` | - | 上升沿正常停车，并把驱动器置 disable。 |
| `bShortStop` | `BOOL` | - | 上升沿短停，但保持 enable。 |
| `bErrorResume` | `BOOL` | - | 上升沿复位 AX2000 错误（不复位 PLC-Profibus 之间的 TimeOut 错）。 |
| `tTimeOut` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy : BOOL;
    bError : BOOL;
    bTimeOutErr : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bError` | `BOOL` | TRUE = AX2000 驱动器报故障；具体故障号需读驱动器 PNU。 |
| `bTimeOutErr` | `BOOL` | TRUE = PLC ↔ 驱动器之间的 ADS / Profibus 通讯超时。 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stPZDIN : ST_PZD_IN;
    stPZDOUT : ST_PZD_OUT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stPZDIN` | `ST_PZD_IN` | Profibus 过程数据：驱动器 → PLC 方向；链到 System Manager 中 AX2000 的 PZD IN 区。 |
| `stPZDOUT` | `ST_PZD_OUT` | Profibus 过程数据：PLC → 驱动器方向；链到 System Manager 中 AX2000 的 PZD OUT 区。 |

## 3. 行为说明

本 FB 是 AX2000 的核心动作接口，必须循环调用让 PZD 过程数据保持实时刷新到驱动器。`bStart` 上升沿发动作命令；动作类型由其它输入位决定：`iVelocity` / `iPosition` 表示直接 motion 指令的速度与目标位置；`imotion_tasknumber` / `imotion_blocktype` 用于调驱动器内已存的 motion-task；`bStop` 上升沿正常停车并禁能；`bShortStop` 短停（保持使能）；`bErrorResume` 复位 AX2000 错误。`bBusy = TRUE` 直到驱动器接受命令；`bError` 表示驱动器报错（具体故障码不在本 FB 输出，需读驱动器 PNU）；`bTimeOutErr` 表示 PLC 与驱动器之间的 ADS / Profibus 超时。`stPZDIN` / `stPZDOUT` 是 IN_OUT 的 Profibus 过程数据结构，必须在 System Manager 中链到 AX2000 站的 PZD 区域，且每周期循环调用本 FB 才能让数据流动。

## 4. 错误码 / 返回值

本 FB 无具体错误码表；状态由输出参数自行反映。具体错误语义需配合主站 / 现场总线设备手册查询。

## 5. 使用注意 / 常见坑

- AX2000 是 1990s-2000s 的 Kollmorgen 老型号伺服；现代工程基本用 AX5000 (EtherCAT) + Tc2/Tc3 NCI 替代。本系列 FB 仅用于维护老线。
- **`stPZDIN` / `stPZDOUT` 必须链到 System Manager 中 AX2000 在 Profibus 上的 PZD（过程数据）映射区**，否则数据交换不通。（工程经验补充）
- AX2000 通讯通过 Profibus FC310x / EL6731 主站；调用任何 AX2000 FB 前先确保 Profibus 主站本身已正常。（工程经验补充）
- 错误号 `iErrorId` 是 AX2000 驱动器返回的"驱动器错误号"，与 ADS 错误号无关。具体含义见 AX2000 / S300 手册的 Fault Code 表。（工程经验补充）
- **必须每周期循环调用**：本 FB 是 PZD 数据交换的载体，不调用驱动器会丢失通讯心跳进入超时故障。
- 改运行模式（如位置 ↔ 速度）必须先 `bStop` 让驱动器禁能，不能在运动中改。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_AX2000_AXACT.xml`](../examples/P_Demo_FB_AX2000_AXACT.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：AX2000 老线运动控制：印刷套筒定位伺服，上电后等位置就绪信号 → bStart 发位置指令到 12000 μm。
- **价值**：把 PROFIDRIVE 状态机 + PZD 编码全部封装；业务侧只关心 motion 指令。
- **替代方案对比**：
  - 直接读写 PZD 字节：协议繁琐
  - 现代 NCI + EL72xx：投资大但更可靠
  - **本 FB**：维护老线必用

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.3.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59138955.html
- **相关 FB / FC**：`FB_AX2000_Parameter`, `FB_AX2000_Reference`, `FB_AX200X_Profibus`
