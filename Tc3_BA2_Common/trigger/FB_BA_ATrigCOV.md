# FB_BA_ATrigCOV

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Universal / Trigger` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785135627.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_BA_ATrigCOV.TcPOU`](../examples/P_Demo_FB_BA_ATrigCOV.TcPOU) |

---

## 1. 功能简述

任意类型变量的"值变化"边沿检测器（COV = Change Of Value）。把任何变量（BOOL / INT / REAL / 结构体等）通过 `xValue : ANY` 接入，FB 会在该变量与上次比较时不一致时把 `bQ` 置 TRUE 一个 PLC 周期。也支持外部 `bForce` 上升沿强制触发一次脉冲（用于人工请求订阅推送）。内部限制变量大小为 4 字节：超过 4 字节时 `bReady` 落 FALSE 并在 TwinCAT 输出窗口报错，只剩 `bForce` 仍可触发。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    xValue      : ANY;
    bForce      : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `xValue` | `ANY` | 被监视的变量（任何类型）。**总尺寸 ≤ 4 字节**——BOOL / BYTE / WORD / DWORD / INT / DINT / REAL / 短枚举 / 4-byte 结构 都支持；LREAL / LWORD / 字符串 / 大结构都会触发 `bReady = FALSE` 出错。 |
| `bForce` | `BOOL` | 上升沿强制产生一次 `bQ` 脉冲，不需要 `xValue` 真的变化。用于"按钮订阅请求"等场景。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bReady      : BOOL;
    bQ          : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bReady` | `BOOL` | `TRUE` = `xValue` 尺寸 ≤ 4 字节，FB 正常工作；`FALSE` = `xValue` 超过 4 字节，COV 检测停用（仅 `bForce` 仍可触发）。`bReady` 从 TRUE 变 FALSE 时 TwinCAT 输出窗口和错误列表会出现告警。 |
| `bQ` | `BOOL` | 触发输出：`xValue` 检测到值变化、或 `bForce` 上升沿时，置 TRUE 一个 PLC 周期。供下游 R\_TRIG / 队列 / 消息生成等使用。 |

### VAR_IN_OUT

无。

## 3. 行为说明

每周期内部把 `xValue` 当前 4 字节内容与上一周期保存的 4 字节比对：不一致则 `bQ := TRUE`，更新内部保存值；一致则 `bQ := FALSE`。`bForce` 上升沿独立产生一次 `bQ` 脉冲，与值变化判定 OR 在一起。首个周期由于没有"上次值"基准，行为是 FB 内部初始值（一般是 0）与 `xValue` 比较——如果 `xValue` 不为 0 则首周期就会触发 `bQ`，需要业务侧用 R\_TRIG 滤掉或忽略首周期。**4 字节限制**是 FB 内部 buffer 大小决定的硬限制；BACnet COV 订阅、楼宇报警事件、状态变化日志等都是典型的 4 字节场景（BOOL / 数值 / 短枚举）。`xValue` 是 ANY 类型——编译器在调用站自动把变量地址 + 大小描述符传入。`xValue.diSize > 4` 时 FB 把 `bReady` 落 FALSE 并停止值变化检测，但 `bForce` 仍生效。在线复用同一 FB 实例监视不同变量是 **不允许的**——内部"上次值"被覆盖会乱掉，每个被监视量都要一个独立 `FB_BA_ATrigCOV` 实例。

## 4. 错误码 / 返回值

本 FB 通过 `bReady` 报告"能否工作"，无独立错误码：

| `bReady` | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | `xValue` 尺寸 ≤ 4 字节，COV 正常 | 看 `bQ` 即可 |
| `FALSE` | `xValue` 尺寸 > 4 字节，COV 已停 | 检查 TwinCAT 输出窗口的告警；把 `xValue` 换成 ≤ 4 字节的标量或拆分监视；只在 `bForce` 上升沿需要 `bQ` 时可继续用 |

PDF / InfoSys 未列额外错误码。

## 5. 使用注意 / 常见坑

- **`xValue.diSize` 必须 ≤ 4**：LREAL（8 字节）、LWORD（8 字节）、STRING（≥ 81 字节）、大型 STRUCT 都会触发 `bReady = FALSE`。要监视 LREAL 时可拆成高 4 字节 + 低 4 字节两个 ATrigCOV 实例，或先把 LREAL 强制转 REAL（如果精度允许）。（工程经验补充）
- **首周期假触发**：上电后第一个周期，内部"上次值" buffer 是 0；如果监视的变量上电就不为 0，会触发一次 `bQ`。把 `bForce` 不动、`bQ` 接到一个 N+1 周期的 R\_TRIG 抑制即可；或者忽略首周期。（工程经验补充）
- **每个被监视量一个 FB 实例**：千万不要复用同一实例去监视不同变量——内部上次值会被覆盖。（工程经验补充）
- BACnet COV 订阅典型场景：把楼宇属性（温度 / 阀位 / 状态枚举）接 `xValue`，`bQ` 触发后调用 BACnet 推送 FB 把当前值发出去。本 FB 是 COV 订阅模式的核心节拍器。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_BA_ATrigCOV.TcPOU`](../examples/P_Demo_FB_BA_ATrigCOV.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：BACnet IP 楼宇网关：PLC 内有 50 个温度点要上报到 BMS。BACnet 协议有 COV（Change Of Value）订阅模式——只在数值变化时推送，减少网络带宽。每个点用一个 FB_BA_ATrigCOV 监视；`bQ` 触发后调用 BACnet 推送 FB。
- **价值**：把"值变化检测"从手写 IF + 上次值 buffer + 比较代码（每个点 5-10 行）简化成一行 FB 调用。50 个点 ≈ 节省 250-500 行重复代码。`bForce` 引脚还提供了"强制刷新"能力（BMS 上线时一次性请求所有点的当前值）。
- **替代方案对比**：
  - **手写 `IF xValue <> xLastValue THEN ...`**：每个变量得自己定义上次值变量、写 IF；可行但繁琐；
  - **R\_TRIG（仅 BOOL）**：只能监视 BOOL 边沿，不能监视 REAL / INT 的值变化；
  - **本 FB**：ANY 类型通用 + 内置 force 触发，是 BACnet 协议栈的标准基础块。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.2.2.2.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785135627.html
- **相关 FB**：`FB_BA_RFTrig`（双边沿 BOOL 触发，仅 BOOL）、`R_TRIG` / `F_TRIG`（IEC 标准上升 / 下降沿，仅 BOOL）
