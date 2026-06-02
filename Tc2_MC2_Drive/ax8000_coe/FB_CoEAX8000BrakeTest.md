# FB_CoEAX8000BrakeTest

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Drive` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `AX8000 CoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/11307290379.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_CoEAX8000BrakeTest.xml`](../examples/P_Demo_FB_CoEAX8000BrakeTest.xml) |

---

## 1. 功能简述

实现 **AX8000** 功能性抱闸测试（functional brake test）的功能块（Function Block, FB）。它把 AX8000 切到**转矩模式**（Cyclic Synchronous Torque Mode, CST），向驱动器下发 `Torque` 指定的转矩设定值，保持该转矩直到 `Timeout` 超时或收到 `Succeeded` 反馈。`Succeeded` 反馈通常由安全控制器送给 PLC——表示抱闸在测试转矩下确实保持住了。测试结束后 AX8000 恢复到原来的运行模式。

抱闸测试的目的：定期验证抱闸的保持能力是否还达标（抱闸会磨损）。若测试前抱闸未闭合、或抱闸保持不住测试转矩，AX8000 内置的速度限制（`VelocityLimit`）会阻止轴失控加速。

⚠️ **DANGER（来自 PDF）**：使用本 FB 时轴被切到 CST 模式，使用后（尤其错误情况后）轴可能仍停在 CST。这在提升轴上可能导致突然的非计划运动。务必：① 确保符合风险评估、② 用 `MC_ReadDriveOperationMode` 检查当前模式、③ 若不在位置相关模式（CSV/CSP），用 `MC_WriteDriveOperationMode` 直接或 `MC_Halt`/`MC_Stop` 间接转回 CSV/CSP（后者从 TwinCAT 3.1.4024.40 起），再次确认确实在位置模式，否则中止并做错误处理。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
     Execute       : BOOL;
     Succeeded     : BOOL;
     Torque        : LREAL;
     VelocityLimit : LREAL;
     Timeout       : TIME;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次抱闸测试 |
| `Succeeded` | `BOOL` | — | 抱闸在指定转矩下保持住的反馈，通常来自安全控制器 |
| `Torque` | `LREAL` | — | 测试应施加的转矩 [Nm] |
| `VelocityLimit` | `LREAL` | — | 转矩模式下防止失控加速的速度限制 |
| `Timeout` | `TIME` | — | 指定转矩保持的最长时间 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF` | 唯一标识系统中一根轴的数据结构，含位置、速度、错误状态等循环数据。**必须传引用**（VAR_IN_OUT 语义） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Busy    : BOOL;
    Error   : BOOL;
    ErrorID : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | FB 激活后置位，直到收到反馈才复位 |
| `Error` | `BOOL` | `Busy` 复位后若命令传输出错则置位 |
| `ErrorID` | `UDINT` | `Error = TRUE` 时返回 ADS 错误码 |

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次抱闸测试：FB 把 AX8000 切到 CST 模式，下发 `Torque` 转矩设定值，`Busy := TRUE`。转矩保持直到 ① `Succeeded` 收到（抱闸保持成功）或 ② `Timeout` 超时。测试结束后 FB 把 AX8000 设回原运行模式。整个过程**跨多个 PLC 周期**，必须每周期循环调用直到 `Busy` 落回 `FALSE`。

**`Succeeded` 的角色**：这是个**输入**（不是输出）——表示外部（通常安全控制器）确认抱闸在测试转矩下保持住了。测试逻辑等的就是这个反馈：收到 `Succeeded` 即认为抱闸合格，结束测试并恢复模式。

**`VelocityLimit` 的保护作用**：如果抱闸没闭合或保持不住测试转矩，轴在转矩驱动下会想加速，`VelocityLimit` 限制其速度防止失控——这是测试安全的关键参数，必须按机械情况合理设置。

**完成与出错收敛**：本 FB 无 `Done` 输出。成功判据是 **`Busy` 由 TRUE 落回 FALSE 且 `Error = FALSE`**（配合 `Succeeded` 判断抱闸是否合格）；出错则 `Busy` 复位后 `Error := TRUE`、`ErrorID` 给 ADS 错误码。

**模式恢复必须校验（DANGER）**：测试后务必用 `MC_ReadDriveOperationMode` 确认轴回到了位置模式（CSV/CSP），尤其在出错路径上——轴可能滞留 CST，提升轴在此状态下使能会突然运动。不在位置模式必须用 `MC_WriteDriveOperationMode` 转回或中止处理。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorID : UDINT` 输出。`ErrorID` 为 **ADS 错误码**（不是 NC 错误号、也不是 HRESULT）。抱闸是否合格由 `Succeeded` 输入是否在超时前收到来判断（非错误码）。

| 错误来源 | 含义 | 处理建议 |
|---|---|---|
| ADS 通信错误 | 与 AX8000 的 ADS 传输失败 | 检查 EtherCAT OP、`Axis` Link |
| 模式切换失败 / 不支持 | AX8000 无法切 CST、固件不满足 | 核对 AX8000 固件 v1.04 b0001、TwinCAT ≥ 4022.36/4024.15、库 ≥ V3.3.23.0、AX8000 配置（见 AX8000 功能描述） |

⚠️ PDF 与 InfoSys 在本 FB 章节未逐条列出具体 ADS 错误码，请参见 Beckhoff ADS Return Codes 总表。

**清错**：出错后**先确认轴的运行模式**（DANGER 段），处理完安全前提后才能重试。

## 5. 使用注意 / 常见坑

- **`Succeeded` 是输入不是输出**：它是外部（安全控制器）对"抱闸保持住了"的反馈，FB 等它来判定合格——别当成 FB 给出的结果。
- **测试后必须校验运行模式（DANGER）**：用 `MC_ReadDriveOperationMode` 确认回到 CSV/CSP，否则提升轴可能滞留 CST 突然运动。
- **`VelocityLimit` 必须合理设**：抱闸保持不住时它防失控，设太大失去保护意义。
- **测试前抱闸应闭合**：否则测试无意义，且依赖 `VelocityLimit` 兜底。
- **没有 `Done` 输出 + `Busy` 期间持续循环调用**：异步跨周期。
- **本 FB 把轴切 CST 是高风险操作**：必须纳入整体安全功能设计，配合安全控制器（工程经验补充）。
- **`AXIS_REF` 必须传引用**：`Axis` 是 VAR_IN_OUT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CoEAX8000BrakeTest.xml`](../examples/P_Demo_FB_CoEAX8000BrakeTest.xml)

```iecst
// 场景：定期对 AX8000 提升轴做功能性抱闸测试，验证抱闸保持能力
rtBrakeTestTrig(CLK := bStartBrakeTest);
fbBrakeTest(
    Execute       := rtBrakeTestTrig.Q,
    Succeeded     := bSafetyBrakeHeld,
    Torque        := lrTestTorque,
    VelocityLimit := lrSafetyVelocityLimit,
    Timeout       := T#5S,
    Axis          := axisLiftAxis,
    Busy          => bTestBusy,
    Error         => bTestError,
    ErrorID       => nTestErrorID
);
```

## 7. 业务场景与实际价值

- **场景**：起重/提升/堆垛等垂直轴的定期抱闸保持能力验证，常作为安全功能（防坠）的周期性自检。
- **价值**：用驱动器内置转矩模式+速度限制做受控抱闸测试，配合安全控制器形成闭环验证，无需额外机械加载装置。
- **替代方案对比**：
  - 人工挂重物测抱闸：危险、不可重复、无法自动化
  - 不测抱闸：抱闸磨损失效不可知，垂直轴有坠落风险
  - **本 FB**：AX8000 受控功能性抱闸测试的专用入口（须配安全设计）

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf) §4.5.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/11307290379.html
- **相关 FB**：`MC_ReadDriveOperationMode` / `MC_WriteDriveOperationMode`（测试后校验/恢复运行模式）、`FB_CoEAX8000BrakeControl`（AX8000 抱闸手动控制）、`MC_Halt` / `MC_Stop`（间接转回位置模式）
