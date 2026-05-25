# FB_SoEReset

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Drive` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `General SoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2305845515.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoEReset.xml`](../examples/P_Demo_FB_SoEReset.xml) |

---

## 1. 功能简述

复位驱动器（执行 SoE 参数 `S-0-0099`，"复位类故障"命令）的功能块（Function Block, FB）。它清除驱动器侧的故障状态，让伺服从故障态恢复到可使能态。

⚠️ **重要区分**：本 FB 执行的是**驱动器复位**，**不执行 NC 复位**。如果还需要把 NC 轴从 Errorstop 拉回 Standstill，要另外调用 `Tc2_MC2` 库的 `MC_Reset`。两者职责不同：`FB_SoEReset` 清驱动器硬件故障，`MC_Reset` 清 NC 通道软件故障。

复位可能耗时——PDF 明确**超时须设 10 秒**（默认 `Timeout := T#10s`），因为某些故障的复位最长可达 10 秒。对 AX5000，EtherCAT 高级设置里的 "Wait For WcState is OK" 必须勾选。多通道设备必要时两个通道都要各做一次复位。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NetId   : T_AmsNetID := '';
    Execute : BOOL;
    Timeout : TIME := T#10s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NetId` | `T_AmsNetID` | `''` | 含 NC 所在 PC 的 AMS NetId 字符串；空串表示本机 |
| `Execute` | `BOOL` | — | 上升沿触发一次复位 |
| `Timeout` | `TIME` | `T#10s` | FB 执行允许的最大时间；因复位最长可达 10 秒，须保持 10 秒（不要改小） |

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
    Busy        : BOOL;
    Error       : BOOL;
    AdsErrId    : UINT;
    SercosErrId : UINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | FB 激活后置位，直到收到反馈才复位 |
| `Error` | `BOOL` | `Busy` 复位后若命令传输出错则置位 |
| `AdsErrId` | `UINT` | `Error = TRUE` 时返回最后一条命令的 ADS 错误码 |
| `SercosErrId` | `UINT` | `Error = TRUE` 时返回最后一条命令的 Sercos 错误码 |

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次驱动器复位：FB 向驱动器写 `S-0-0099` 复位命令，`Busy := TRUE`，异步执行，**跨多个 PLC 周期**，且因为复位本身耗时（最长 10 秒），`Busy` 可能保持较久，必须每周期循环调用直到 `Busy` 落回 `FALSE`。

**完成与出错收敛**：本 FB 无 `Done` 输出。成功判据是 **`Busy` 由 TRUE 落回 FALSE 且 `Error = FALSE`**，此后驱动器故障被清除。出错则 `Busy` 复位后 `Error := TRUE`，`AdsErrId`/`SercosErrId` 给错误码。

**与 NC 复位的协作时序**：典型清错流程是——先 `FB_SoEReset` 清驱动器硬件故障 → 成功后再 `MC_Reset(Axis)` 把 NC 轴拉回 Standstill → 然后才能 `MC_Power` 重新使能并发运动命令。只清一边（只 `FB_SoEReset` 或只 `MC_Reset`）往往无法完全恢复。

**超时不要改小**：默认 10 秒是 PDF 要求；改小可能在复位还没完成时就超时报错，造成"复位失败"的假象。

**复位边沿**：`Busy = FALSE` 后把 `Execute` 拉回 `FALSE` 调一次复位 FB 内部状态。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` 输出，分 `AdsErrId : UINT`（ADS 错误码）与 `SercosErrId : UINT`（Sercos 错误码）两路。

| 错误路 | 含义 | 处理建议 |
|---|---|---|
| `AdsErrId` ≠ 0 | ADS 通道错误：超时（可能 Timeout 设太小）、设备不可达 | 确认 `Timeout = T#10s`、EtherCAT OP、AX5000 勾了 "Wait For WcState is OK" |
| `SercosErrId` ≠ 0 | Sercos 服务错误：复位命令被拒、故障无法清除 | 故障可能是硬件性的（需断电或检修），持续报错需查驱动器诊断信息 |

⚠️ PDF 与 InfoSys 未逐条列出具体 ADS / Sercos 错误码数值。见 Beckhoff ADS Return Codes 总表与驱动器 Sercos 文档。

**清错**：本 FB 本身就是清驱动器错的工具；若它自己报错且原因排除后，给 `Execute` 新上升沿重试。

## 5. 使用注意 / 常见坑

- **`Timeout` 必须保持 10 秒**：PDF 明确要求，改小会在复位完成前误报超时。
- **驱动器复位 ≠ NC 复位**：本 FB 只清驱动器；NC 轴 Errorstop 要另调 `MC_Reset`。完整恢复通常两者都要。
- **AX5000 需勾 "Wait For WcState is OK"**：EtherCAT 高级设置里，否则复位可能不稳定。
- **多通道设备可能要两通道各复位一次**：PDF 提示。
- **没有 `Done` 输出 + `Busy` 期间持续循环调用**：异步且耗时，判完成靠 `Busy` 落回 FALSE。
- **复位不解决硬件根因**：若故障是过流/过温/编码器损坏等硬件问题，复位后会立即重现，需检修而非反复复位（工程经验补充）。
- **`AXIS_REF` 必须传引用**：`Axis` 是 VAR_IN_OUT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoEReset.xml`](../examples/P_Demo_FB_SoEReset.xml)

```iecst
// 场景：驱动器报故障后，先清驱动器错（本 FB），再 MC_Reset 清 NC 错
rtResetTrig(CLK := bDriveResetReq);
fbSoEReset(
    NetId   := '',
    Execute := rtResetTrig.Q,
    Timeout := T#10S,
    Axis    := axisServo,
    Busy    => bResetBusy,
    Error   => bResetError,
    AdsErrId    => nResetAdsErr,
    SercosErrId => nResetSercosErr
);
```

## 7. 业务场景与实际价值

- **场景**：伺服报警后的自动/手动恢复流程、批处理开始前清掉残留故障、远程诊断中尝试软复位。
- **价值**：用一个 FB 程序化清除驱动器故障，配合 `MC_Reset` 形成标准"两段式清错"恢复流程，免去人工进驱动器界面操作。
- **替代方案对比**：
  - 在驱动器 / DriveManager 手动复位：人工、无法远程/自动化
  - 只用 `MC_Reset`：只清 NC 软件态，驱动器硬件故障还在，使能仍失败
  - **本 FB + `MC_Reset`**：分别清驱动器和 NC，标准完整恢复

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf) §4.2.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2305845515.html
- **相关 FB**：`MC_Reset`（Tc2_MC2 库，NC 复位）、`MC_Power`（复位后使能）、`FB_SoERead`（读故障诊断参数）
