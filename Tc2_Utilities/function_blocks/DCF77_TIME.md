# DCF77_TIME

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/34972939.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_DCF77_TIME.xml`](../examples/P_Demo_DCF77_TIME.xml) |

---

## 1. 功能简述

DCF77_TIME 解码 DCF77 长波时间信号脉冲序列，把每分钟一次的德国标准时间广播（PTB 法兰克福 77.5 kHz）还原成日期 / 时刻，并保持 PLC 内置软时钟与之每分钟对齐。适用于楼宇时钟、铁路时刻牌等需要可追溯校准的场合。

本 FB 是经典 DCF77 解码器：依赖外部硬件接收模块每秒提供一个数字脉冲（200 ms 表示 0、100 ms 表示 1），FB 内部用一个 PLC 周期级的时间窗采样脉冲长度，按 DCF77 协议把 59 秒的报文位拼成完整时间帧。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    DCF_PULSE : BOOL;
    RUN : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `DCF_PULSE` | `BOOL` | 输入布尔标志：`DCF_PULSE`。具体语义见 §3 行为说明。 |
| `RUN` | `BOOL` | 输入布尔标志：`RUN`。具体语义见 §3 行为说明。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY : BOOL;
    ERR : BOOL;
    ERRID : UDINT;
    ERRCNT : UDINT;
    READY : BOOL;
    CDT : DATE_AND_TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | 输出布尔标志：`BUSY`。具体语义见 §3 行为说明。 |
| `ERR` | `BOOL` | 输出布尔标志：`ERR`。具体语义见 §3 行为说明。 |
| `ERRID` | `UDINT` | 无符号整数输出：`ERRID`。 |
| `ERRCNT` | `UDINT` | 无符号整数输出：`ERRCNT`。 |
| `READY` | `BOOL` | 输出布尔标志：`READY`。具体语义见 §3 行为说明。 |
| `CDT` | `DATE_AND_TIME` | 夏令时标志：TRUE = CEST 夏令时，FALSE = CET 标准时。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**信号流**：`DCF_INPUT` 接入解调后的二进制脉冲（高有效）。FB 内部以 PLC 周期为粒度测量每个脉冲的高电平时长：高电平 100 ms 解为 bit `0`、200 ms 解为 bit `1`。第 59 秒缺脉冲（同步标记）→ 触发本帧解析。

**输出节奏**：每分钟整点（第 0 秒）`DCF_TIME_VALID = TRUE` 一个 PLC 周期，同时 `DCF_DATE_AND_TIME` 装载新解码的日期时间。其他时间 `DCF_TIME_VALID = FALSE`，但 `DCF_DATE_AND_TIME` 保留上一帧值。

**`CDT` 输出**：1 = 当前为夏令时（CEST），0 = 标准时（CET）。`CHANGE_DT` 输出在切换前的最后 1 小时为 TRUE，提示业务侧准备处理跳变。

**状态恢复**：信号丢失（连续 N 秒无脉冲）→ `DCF_TIME_VALID` 不再为 TRUE，需要等下一帧完整接收。

## 4. 错误码 / 返回值

本 FB 无显式错误输出。状态可以通过 `bBusy` / `bValid` / `bDone` 等过程信号间接判断。

## 5. 使用注意 / 常见坑

- **只能用在德语区 / 中欧**：DCF77 信号传播范围约 2000 km。中国、北美使用要换 BPC / WWVB 接收模块及对应解码 FB。
- 解调脉冲必须按 DCF77 标准（100 ms / 200 ms 占空），不同接收模块输出极性 / 电平不同——上电要先用示波器确认。（工程经验补充）
- **首次有效输出要等 ≥ 1 分钟**：报文 59 位，需完整接到一次同步标记后才输出。重启 PLC 期间业务时钟应另有兜底（用 RTC_EX2）。
- 夏令时切换期 03:00 重复 / 跳过 1 小时，业务代码做时间戳差值时必须按 `DT` 类型用 UTC 计算，不能直接相减。（工程经验补充）
- PLC 周期太长（> 50 ms）会丢失脉冲沿，建议在 ≤ 10 ms 的任务里调用本 FB。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DCF77_TIME.xml`](../examples/P_Demo_DCF77_TIME.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：楼宇大堂电子时钟显示，要保证误差 < 1 秒并自动处理欧洲夏令时切换；用 DCF77 接收模块 + 本 FB 解码。
- **价值**：替代自写状态机解析 59 位 DCF77 报文 + 校验位 + 同步标记，约省 80 行代码。
- **替代方案对比**：
  - 用 SNTP / NTP 网络时间：需要互联网，机柜内 OT 网段不一定通，且抗干扰差。
  - **本 FB**：纯硬件信号、抗电磁干扰、欧盟内合法可追溯。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/34972939.html
- **相关 FB**：`DCF77_TIME_EX`, `RTC_EX2`, `FB_LocalSystemTime`
