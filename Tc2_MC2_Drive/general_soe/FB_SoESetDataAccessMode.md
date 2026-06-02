# FB_SoESetDataAccessMode

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Drive` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `General SoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/7608093195.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoESetDataAccessMode.TcPOU`](../examples/P_Demo_FB_SoESetDataAccessMode.TcPOU) |

---

## 1. 功能简述

设置 SoE 参数访问模式的功能块（Function Block, FB）。SoE 参数的"属性（Attribute）"与"值（Value）"默认是**并行（parallel）**访问的——这是较快的方式；但如果驱动器制造商不支持并行访问（常见于第三方 SoE 设备），可用本 FB 强制切到**顺序（sequential）**访问。

这是 `FB_SoERead` / `FB_SoEWrite` 的配套 FB：当那些 FB 在第三方设备上读写参数报 ADS 错误时，往往就是因为对方不支持并行访问，此时先用本 FB 切顺序模式，再重试读写即可成功。一般情况下并行更快，故仅在确认并行不被支持时才切顺序。

⚠️ **接口特例**：与库内其它 SoE FB 不同，本 FB **没有 `Axis : AXIS_REF` 输入/输出**（它设置的是 PLC 侧全局访问模式而非针对某根轴），且错误输出叫 `ErrId`（不是 `AdsErrId`/`SercosErrId`）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Execute : BOOL;
    Mode    : E_SoEDataAccessMode := E_SoEDataAccessMode.eSoEDataAccessMode_Parallel;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Execute` | `BOOL` | — | 上升沿触发一次模式设置 |
| `Mode` | `E_SoEDataAccessMode` | `eSoEDataAccessMode_Parallel` | 访问模式：`eSoEDataAccessMode_Parallel`（= 0，并行，较快，默认）/ `eSoEDataAccessMode_Sequencial`（= 1，顺序，较慢但兼容性好） |

> 本 FB 没有 `VAR_IN_OUT`（不带 `Axis`）。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Busy  : BOOL;
    Error : BOOL;
    ErrId : UINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | FB 激活后置位，直到收到反馈才复位 |
| `Error` | `BOOL` | `Busy` 复位后若命令传输出错则置位 |
| `ErrId` | `UINT` | `Error = TRUE` 时返回 ADS 错误码 |

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次模式设置：FB 把 `Mode` 应用到 SoE 参数访问层，`Busy := TRUE`，异步执行，**跨多个 PLC 周期**，必须每周期循环调用直到 `Busy` 落回 `FALSE`。

**完成与出错收敛**：本 FB 无 `Done` 输出。成功判据是 **`Busy` 由 TRUE 落回 FALSE 且 `Error = FALSE`**，此后 `FB_SoERead`/`FB_SoEWrite` 按新模式访问参数。出错则 `Busy` 复位后 `Error := TRUE`、`ErrId` 给 ADS 错误码。

**`Mode` 语义与决策**：
- `eSoEDataAccessMode_Parallel`（默认）：属性和值并行读取，速度快。Beckhoff 自家驱动器（AX5000 等）支持。
- `eSoEDataAccessMode_Sequencial`：属性和值顺序读取，慢一些但兼容性好。用于不支持并行的第三方 SoE 设备。

**典型用法时序**：默认就是并行，正常无需调用本 FB。只有当 `FB_SoERead`/`FB_SoEWrite` 在某第三方设备上报 ADS 错误、怀疑是并行不支持时，先用本 FB 切 `eSoEDataAccessMode_Sequencial`，再重试参数读写。设置一次即对后续访问生效，不必每次参数访问前都调。

**复位边沿**：`Busy = FALSE` 后把 `Execute` 拉回 `FALSE` 调一次复位 FB 内部状态。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrId : UINT` 输出。`ErrId` 为 **ADS 错误码**（不是 NC 错误号、也不是 HRESULT）。

| 错误来源 | 含义 | 处理建议 |
|---|---|---|
| ADS 通信错误 | 设置模式的 ADS 命令传输失败 | 检查 EtherCAT OP、ADS 路由 |

⚠️ PDF 与 InfoSys 在本 FB 章节未逐条列出具体 ADS 错误码，请参见 Beckhoff ADS Return Codes 总表。

**清错**：处理完外部原因后给 `Execute` 新上升沿重试；本 FB 无独立清错入口。

## 5. 使用注意 / 常见坑

- **正常用不到——只在第三方设备报并行不支持时才切顺序**：Beckhoff 自家驱动器默认并行即可，不要无谓切顺序拖慢访问。
- **本 FB 没有 `Axis`**：它设的是全局访问模式而非针对某轴，example 调用里不传 AXIS_REF——这是它和库内其它 SoE FB 的关键区别。
- **错误输出叫 `ErrId` 不是 `AdsErrId`**：写代码时别照搬 `FB_SoERead` 的输出名。
- **设一次即生效**：不必每次参数访问前都调；切了模式后保持即可。
- **没有 `Done` 输出 + `Busy` 期间持续循环调用**：异步跨周期，判完成靠 `Busy` 落回 FALSE。
- **`eSoEDataAccessMode_Sequencial` 拼写按 PDF 原文**（注意是 "Sequencial" 而非 "Sequential"），不要"纠正"成标准英文拼写，否则枚举名不匹配编译失败（工程经验补充）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoESetDataAccessMode.TcPOU`](../examples/P_Demo_FB_SoESetDataAccessMode.TcPOU)

```iecst
// 场景：第三方 SoE 设备不支持并行访问，FB_SoERead 报 ADS 错；切到顺序访问
rtModeTrig(CLK := bSetSeqModeReq);
fbSetAccessMode(
    Execute := rtModeTrig.Q,
    Mode    := eSoEDataAccessMode_Sequencial,
    Busy    => bModeBusy,
    Error   => bModeError,
    ErrId   => nModeErrId
);
```

## 7. 业务场景与实际价值

- **场景**：系统里接了不支持并行 SoE 访问的第三方伺服 / 编码器，`FB_SoERead`/`FB_SoEWrite` 报 ADS 错时的兼容性开关。
- **价值**：一个 FB 即可在并行/顺序两种访问模式间切换，让同一套参数访问代码兼容支持/不支持并行的不同厂商设备。
- **替代方案对比**：
  - 不切模式直接重试：第三方设备会一直报 ADS 错，读不出参数
  - 为第三方设备另写一套访问逻辑：重复且难维护
  - **本 FB**：标准兼容性开关，切一次后续访问统一适配

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf) §4.2.5，枚举 §5.9 `E_SoEDataAccessMode`
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/7608093195.html
- **相关 FB**：`FB_SoERead` / `FB_SoEWrite`（受本模式影响的参数访问）
