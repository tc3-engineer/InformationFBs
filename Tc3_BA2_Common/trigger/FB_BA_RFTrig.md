# FB_BA_RFTrig

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Universal / Trigger` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785137547.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_BA_RFTrig.TcPOU`](../examples/P_Demo_FB_BA_RFTrig.TcPOU) |

---

## 1. 功能简述

布尔变量的双边沿检测器：在一个 FB 中同时给出"任意边沿（rising + falling）" `Q`、"上升沿" `Qr`、"下降沿" `Qf` 三个输出。等价于 IEC 标准 `R_TRIG` + `F_TRIG` 的合并版，但只需一个实例和一次调用，省一行代码。每个输出脉冲宽度为一个 PLC 周期。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bValue    :BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bValue` | `BOOL` | 被监视的布尔变量。FB 内部保存上一周期值用于边沿对比。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Q         :BOOL;
    Qr        :BOOL;
    Qf        :BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Q` | `BOOL` | 任意边沿（rising 或 falling）触发：`bValue` 与上次值不同时置 TRUE 一周期。 |
| `Qr` | `BOOL` | 仅上升沿（rising edge）触发：`bValue` 从 FALSE → TRUE 时置 TRUE 一周期，等价于 IEC 标准 `R_TRIG.Q`。 |
| `Qf` | `BOOL` | 仅下降沿（falling edge）触发：`bValue` 从 TRUE → FALSE 时置 TRUE 一周期，等价于 IEC 标准 `F_TRIG.Q`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

每个 PLC 周期：FB 把 `bValue` 当前值与内部保存的上次值比较，按变化情况设置三个输出——任意变化 → `Q := TRUE`，FALSE → TRUE → `Qr := TRUE`，TRUE → FALSE → `Qf := TRUE`。所有输出脉冲宽度恰好 1 周期；下一周期内部上次值被刷新为当前值，三个输出回 FALSE（除非该周期 `bValue` 又变化）。首周期：内部上次值初始为 FALSE。如果 `bValue` 上电就为 TRUE，则首周期会触发一次 `Qr` 和 `Q`——这与 IEC 标准 `R_TRIG` 的行为一致（标准 `R_TRIG` 首次调用如果 CLK = TRUE 也会触发）。**典型用法**：替换两个独立 `R_TRIG` + `F_TRIG` 实例（节省 1 个变量、1 行调用）；某些状态机需要同时响应升 / 降两种边沿（如"按钮按下后立即响应、松开时复位"），用本 FB 一次拿到两个输出。

## 4. 错误码 / 返回值

本 FB 无错误码、无返回值；输出是 3 个 BOOL 标志。

## 5. 使用注意 / 常见坑

- **每个被监视信号一个 FB 实例**：复用同一实例监视不同信号会让内部"上次值"互相覆盖。（工程经验补充）
- **首周期上电假触发**：上电时若 `bValue = TRUE`，首周期 `Qr` 会触发一次。处理方法：① 在 PLC 主循环加一个 `bFirstCycle` 标志，首周期忽略所有输出；② 或者业务侧用一个延时（如 R_TRIG 套两层）。这与 IEC 标准 `R_TRIG` 行为相同。
- **`Q` 与 `Qr` / `Qf` 同时触发**：上升沿时 `Q` 和 `Qr` 同时为 TRUE 一周期；下降沿时 `Q` 和 `Qf` 同时为 TRUE 一周期。三个输出不互斥。
- **要的是"持续电平"还是"边沿脉冲"**：本 FB 给"边沿脉冲"，每脉冲只 1 周期。要电平的话直接读 `bValue`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_BA_RFTrig.TcPOU`](../examples/P_Demo_FB_BA_RFTrig.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：办公楼大门红外感应：上升沿触发"开门 + 灯亮 + 启动通风"，下降沿触发"延时 30 秒后关灯 + 停通风"，任意边沿都需要写一条日志。一个 FB 给三个输出，省两个 FB 实例。
- **价值**：① 单实例替代 `R_TRIG + F_TRIG` 双实例（少 1 个变量、少 1 行调用）；② `Q` 输出直接给日志记录引脚——无需再 OR 两个边沿；③ 命名 `Q/Qr/Qf` 直观，比 IEC 标准 `R_TRIG.Q` 与 `F_TRIG.Q` 容易混淆少。
- **替代方案对比**：
  - **IEC `R_TRIG` + `F_TRIG` 两实例**：可行但要两个 FB 实例 + 两行调用 + 自己 OR 任意边沿；
  - **手写 IF + 上次值 buffer**：5 行代码、易写漏首周期；
  - **本 FB**：一行调用、三输出，专为楼宇控制日志 / 状态机简化设计。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.2.2.2.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785137547.html
- **相关 FB**：`FB_BA_ATrigCOV`（ANY 类型值变化检测）、IEC 标准 `R_TRIG`、`F_TRIG`
