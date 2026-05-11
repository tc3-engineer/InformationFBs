# LTOF

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION_BLOCK` |
| Category | `Timer (LTIME)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/9007205317834763.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_LTOF.xml`](../examples/P_Demo_LTOF.xml) |

---

## 1. 功能简述

`LTOF` 是 `TOF` 的 **64 位 LTIME 版本**——断开延时定时器，纳秒精度，时长上限约 584 年。行为完全等同 `TOF`：`IN` 上升沿瞬间 `Q := TRUE`；下降沿后 `ET` 累加，到达 `PT` 时 `Q := FALSE`；`PT` 期间 `IN` 再次上升会取消延时断、`ET` 清零、`Q` 保持 TRUE。

使用场景集中在**高精度长延时**：μs 级伺服关机延时、跨日设备冷却、长周期信号滤波。

PT 类型 `LTIME`，字面量 `LTIME#250us`、`LTIME#10h`、`LTIME#100d`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    IN : BOOL;    (*starts timer with falling edge, resets timer with rising edge*)
    PT : LTIME;   (*time to pass before Q is reset*)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `IN` | `BOOL` | 上升沿：立即 `Q := TRUE`，`ET := LTIME#0`；下降沿：启动断开延时 |
| `PT` | `LTIME` | 断开延时时长，64 位纳秒 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q  : BOOL;    (*is FALSE, PT seconds after IN had a falling edge*)
    ET : LTIME;   (*elapsed time since falling edge at IN*)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q` | `BOOL` | `IN = TRUE` 时为 TRUE；`IN = FALSE` 且延时未到时仍为 TRUE；延时到时 `Q := FALSE` |
| `ET` | `LTIME` | 自 `IN` 下降沿起累加；到达 `PT` 后钳位；`IN` 重新上升清零 |

### VAR_IN_OUT

无。

## 3. 行为说明

整个时序逻辑与 `TOF` 完全镜像，仅时间分辨率与上限不同——LTIME 是 64 位无符号纳秒。`IN` 上升沿瞬间 `Q := TRUE` 且 `ET` 清零（同时复位正在进行的延时断）；`IN` 下降沿后 `ET` 开始累加纳秒，达到 `PT` 时 `Q := FALSE` 并钳位。`PT` 倒计时期间一旦 `IN` 又上升，本次延时断被立刻取消、`ET` 清零、`Q` 始终保持 TRUE——这是 TOF 系列的抗抖动核心：信号瞬时跳变不会引起虚假关闭。

实际精度受 PLC 任务周期约束：FB 在每次调用时才更新 ET，1 ms 任务下精度大约 1 ms；要发挥 LTOF 的 μs 优势需要 NC/CNC 级任务周期（典型 50–250 μs）。`LTIME` 与 `TIME` 不可隐式互转，传入 `PT := T#5s` 会编译失败，应写 `LTIME#5s` 或调用 `TIME_TO_LTIME`。生产现场如果 `IN` 信号源带高频抖动，PT 期间反复上升下降会导致定时器无限被复位 → "永远关不掉"，必须先在 IN 前加稳定化处理。

**关键差异**（与 `TOF` 比较）：

- 精度纳秒（实际受任务周期限制）
- 上限 584 年，跨年延时不溢出
- 类型 `LTIME` 不兼容 `TIME`
- 其他行为完全相同（立即通、延时断、可被打断、`IN` 抖动会无限延后关闭等）

## 4. 错误码 / 返回值

`LTOF` 是标准定时器，**无错误码、无 HRESULT**。

## 5. 使用注意 / 常见坑

- **精度由任务周期决定**：LTIME 类型本身纳秒，但 ET 累加在每次 FB 调用时进行——10 ms 任务下精度仍是 10 ms。
- **PT 类型必须 LTIME**：`PT := T#5s` 编译失败，应写 `PT := LTIME#5s` 或用 `TIME_TO_LTIME(T#5s)`。
- **`Q` 在 `IN` 下降后仍 TRUE 是设计意图**：与 TOF 同样易让新手误解为 bug。
- **`PT` 期间 `IN` 抖动延后关闭**：与 TOF 同样的"无限延后"风险，传感器抖动时建议在 IN 前再叠一层稳定化。
- **运行中改 PT 不重启**：仅改门限。
- **断电不保持**：内部状态非 retain，长延时跨断电场景必须用 RETAIN 自己保存。
- **TOF 够用就别强上 LTOF**：占用更多内存，毫秒级任务里没有精度优势。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LTOF.xml`](../examples/P_Demo_LTOF.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：伺服驱动器关机前需要在最后一个指令周期之后保持使能 250 微秒（让电流环
//       自然衰减）。LTOF 在 μs 任务里提供精确"指令结束后延时断使能"。
PROGRAM P_Demo_LTOF
VAR
    fbServoDisableDelay : LTOF;
    bDriveCmdActive     : BOOL;
    tCurrentDecayHold   : LTIME := LTIME#250US;
    bServoEnable        : BOOL;
    tDecayElapsed       : LTIME;
END_VAR

fbServoDisableDelay(
    IN := bDriveCmdActive,
    PT := tCurrentDecayHold,
    Q  => bServoEnable,
    ET => tDecayElapsed
);
```

## 7. 业务场景与实际价值

- **场景**：伺服 / 步进 μs 级关机滞后、长周期信号过滤（数小时级别）、跨年累计倒计时。
- **价值**：保留 TOF 简洁接口的同时获得纳秒分辨率和长上限，特别契合 NC/CNC 高速控制循环。
- **替代方案对比**：
  - **TOF**：常规毫秒场景，体积小
  - **手写 ULINT 累加**：约 15 行边界容易出错
  - **本 FB**：μs / 跨年场景标准

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §3.4.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/9007205317834763.html
- **相关 FB**：`TOF`（32 位）、`LTON`（接通延时 LTIME）、`LTP`（脉冲 LTIME）
