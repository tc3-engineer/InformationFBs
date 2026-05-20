# LPTSIGNAL

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `General functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31020043.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_LPTSIGNAL.xml`](../examples/P_Demo_LPTSIGNAL.xml) |

---

## 1. 功能简述

LPTSIGNAL 在 Centronics 并口（LPT 端口）的指定引脚上输出高 / 低电平。适用于用示波器观察 PLC 任务执行时序的低成本调试手段，或控制并口连接的简单外设。返回 `BOOL`：`TRUE` 调用成功，`FALSE` 失败。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    PortAddr : UINT;
    PinNo : INT;
    OnOff : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `PortAddr` | `UINT` | LPT 端口地址（16 位 I/O 空间）。LPT1 通常 `16#378`。 |
| `PinNo` | `INT` | 引脚号 0-7，对应数据线 D0-D7。 |
| `OnOff` | `BOOL` | TRUE 输出高；FALSE 输出低。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**端口地址**：`PortAddr` 是 LPT 端口 I/O 地址，典型 LPT1 = `16#378`、LPT2 = `16#278`。

**引脚号**：`PinNo` 0-7 对应数据线 D0-D7。

**电平**：`OnOff = TRUE` 输出高电平，`FALSE` 输出低电平。

**示例**：`LPTSIGNAL(16#378, 7, TRUE)` 把 LPT1 端口的 bit7（D7 引脚）拉高。

**底层实现**：本函数实际是 `F_IOPortWrite` 的封装，针对并口数据线做了简化。

**典型应用场景**：用外接示波器观测 PLC 任务的实际执行时序——在任务入口拉高、出口拉低，示波器看到的方波周期即为真实任务周期、占空比即为执行时间占比。这是低成本但极有效的实时性调试手段。

**与现代替代方案**：新工程优先用 EtherCAT 数字输出终端（如 EL2008）做时序观测，硬件兼容性更广；本函数仅在已有 LPT 接口的工控机上仍有用。

## 4. 错误码 / 返回值

本函数返回 `BOOL`：

| 返回值 | 含义 |
|---|---|
| `TRUE` | 调用成功 |
| `FALSE` | 调用失败（参数错误或硬件故障） |

## 5. 使用注意 / 常见坑

- **老硬件依赖**：现代工控机大多没有 LPT 物理端口；要调试时序优先用 EtherCAT 数字输出。（工程经验补充）
- **端口地址错误**：写到错误地址可能影响其他设备；查 BIOS 确认 LPT 实际地址。
- **实时性影响**：每次调用涉及 OS I/O，慎在高频循环里用。（工程经验补充）
- **多任务竞争**：同时写同一 LPT 端口会冲突，需要互斥保护。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LPTSIGNAL.xml`](../examples/P_Demo_LPTSIGNAL.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：用示波器观察 MAIN 任务的实际周期：在 MAIN 入口和出口各调一次 `LPTSIGNAL` 拉高 / 拉低 LPT D7，示波器上即可看到周期波形。
- **价值**：比加 print 日志直观；硬件级时序观察。
- **替代方案对比**：
  - EtherCAT 数字输出 + DO 终端：更现代但要硬件。
  - 加日志统计：精度差。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.1.19
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31020043.html
- **相关 FB / FC**：`F_IOPortRead`, `F_IOPortWrite`
