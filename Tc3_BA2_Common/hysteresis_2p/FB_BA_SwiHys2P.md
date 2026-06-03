# FB_BA_SwiHys2P

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Universal / Hysteresis 2-Point-Control` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/13551664267.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_BA_SwiHys2P.TcPOU`](../examples/P_Demo_FB_BA_SwiHys2P.TcPOU) |

---

## 1. 功能简述

带"可调滞回宽度 + 滞回偏移 + 显式控制方向"的二点切换控制器。输入是设定值 `fSp` + 滞回宽度 `fHys` + 滞回偏移 `fHysOffs` + 控制方向 `bActn`；FB 内部按公式 `fSwiHi = fSp + fHys/2 + fHysOffs` / `fSwiLow = fSp - fHys/2 + fHysOffs` 计算上 / 下切换点，再按 `bActn` 决定切换逻辑。比 `FB_BA_Swi2P` 更适合"以设定值为中心做对称滞回"的场景（设定值在线变时切换点自动跟随）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bEn            : BOOL;
    fIn            : REAL;
    fSp            : REAL;
    fHys           : REAL;
    fHysOffs       : REAL;
    {attribute 'parameterUnit':= 's'}
    nDlyOn   : UDINT;// (0..BAComn_Global.udiMaxSecInMilli) switch-on delay (in [s])
    {attribute 'parameterUnit':= 's'}
    nDlyOff  : UDINT;// (0..BAComn_Global.udiMaxSecInMilli) switch-off delay (in [s])
    bActn          : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bEn` | `BOOL` | 总使能。`FALSE` 时 `bQ := FALSE`，延时清零。 |
| `fIn` | `REAL` | 输入值（被监视信号）。 |
| `fSp` | `REAL` | 设定值（setpoint）；切换点以此为中心。 |
| `fHys` | `REAL` | 滞回宽度（hysteresis width）。上 / 下切换点距离为 `fHys`。 |
| `fHysOffs` | `REAL` | 滞回偏移（hysteresis offset）。把整个滞回带相对 `fSp` 偏移。可正可负。 |
| `nDlyOn` | `UDINT` | 开通延时 `[s]`；上限 `BAComn_Global.udiMaxSecInMilli`（约 4294 秒 = 71 分钟）。 |
| `nDlyOff` | `UDINT` | 关断延时 `[s]`；上限同上。 |
| `bActn` | `BOOL` | 控制方向（显式）：`TRUE` ⇒ direct/synchronous（cooling mode，"测量值上升过上切换点开"）；`FALSE` ⇒ reverse/indirect（heating mode，"测量值下降过下切换点开"）。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bQ                 : BOOL;
    fSwiHi             : REAL;
    fSwiLow            : REAL;
    {attribute 'parameterUnit':= 's'}
    nRemTiDlyOn  : UDINT;// switch-on delay countdown (in [s])
    {attribute 'parameterUnit':= 's'}
    nRemTiDlyOff : UDINT;// switch-off delay countdown (in [s])
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bQ` | `BOOL` | 切换输出。 |
| `fSwiHi` | `REAL` | 上切换点 = `fSp + fHys/2 + fHysOffs`。 |
| `fSwiLow` | `REAL` | 下切换点 = `fSp - fHys/2 + fHysOffs`。 |
| `nRemTiDlyOn` | `UDINT` | 开通延时剩余秒数（倒计时）。 |
| `nRemTiDlyOff` | `UDINT` | 关断延时剩余秒数（倒计时）。 |

### VAR_IN_OUT

无。

⚠️ PDF VAR 区只列了 `VAR_INPUT` / `VAR_OUTPUT`，**没有 `FUNCTION_BLOCK FB_BA_SwiHys2P` 头行**——是 PDF 印刷遗漏；InfoSys 一致。编译器接受。本文档照 PDF 原样。

## 3. 行为说明

控制方向 `bActn = TRUE`（direct，制冷模式）：`fIn` 升过 `fSwiHi` ⇒ 开始 `nDlyOn` 倒计时，倒计时完 `bQ := TRUE`；`fIn` 降过 `fSwiLow` ⇒ 开始 `nDlyOff` 倒计时，倒计时完 `bQ := FALSE`。物理含义："温度高了开冷"。控制方向 `bActn = FALSE`（reverse，加热模式）：逻辑反——`fIn` 降过 `fSwiLow` 启动开通延时；`fIn` 升过 `fSwiHi` 启动关断延时。物理含义："温度低了开热"。设定值 `fSp` 可在线动态修改——上 / 下切换点 `fSwiHi` / `fSwiLow` 会自动跟随，无需停机重组态。滞回偏移 `fHysOffs` 可用于"非对称滞回"：例如要让开通点比关断点更敏感（更早开通），可设 `fHysOffs < 0`。`fHys / 2` 是上 / 下切换点离 `fSp` 的距离；推荐取实际测量噪声幅度的 2-3 倍。`bEn = FALSE` 时 `bQ := FALSE`，延时清零；下次启用从 FALSE 开始判定。

## 4. 错误码 / 返回值

本 FB 无错误码、无返回值。

| 现象 | 含义 | 处理建议 |
|---|---|---|
| `bQ` 持续 FALSE | `bEn = FALSE` 或 `fIn` 未到切换点 | 检查使能、`fSwiHi` / `fSwiLow` 是否合理 |
| `bQ` 频繁切换 | `fHys` 太小（< 测量噪声） | 加大 `fHys` 到噪声幅度的 2-3 倍 |
| 控制方向反 | `bActn` 设错 | `TRUE` = cooling，`FALSE` = heating |

PDF / InfoSys 未列错误码。

## 5. 使用注意 / 常见坑

- **`fHys` 是宽度不是半宽**：上下切换点距离 = `fHys`，每端距 `fSp` 是 `fHys/2`。组态时按测量噪声幅度的 2-3 倍设定（不是峰峰值）。（工程经验补充）
- **`fHysOffs` 偏移会"偏离"以 `fSp` 为中心的对称设计**：默认 `fHysOffs = 0` 时上下对称；`fHysOffs > 0` 整体上移；`< 0` 整体下移。常见用例：制冷模式（`bActn=TRUE`）要让开通点更早（更敏感），设 `fHysOffs < 0`。（工程经验补充）
- ⚠️ **PDF 没有 `FUNCTION_BLOCK FB_BA_SwiHys2P` 头行**——印刷遗漏。InfoSys 一致，编译器接受。
- **设定值在线变化时**：切换点 `fSwiHi` / `fSwiLow` 立即跟随，可能导致 `bQ` 立即翻转（无延时）。如要平滑过渡，外部给 `fSp` 先经 `FB_BA_RampLmt` 限速。（工程经验补充）
- **`nDlyOn` / `nDlyOff` 单位是秒**整数，上限受 `BAComn_Global.udiMaxSecInMilli` 限制（约 71 分钟）；更长延时需外部 TON。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_BA_SwiHys2P.TcPOU`](../examples/P_Demo_FB_BA_SwiHys2P.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：商用建筑会议室温控：HMI 设定温度 `fSp = 22 ℃`、滞回 `fHys = 1 ℃`（21.5℃ 开冷、22.5℃ 停冷）、`bActn = TRUE` 制冷模式。开冷延时 30 秒（防瞬态）、停冷延时 180 秒（避免压缩机短循环）。HMI 改设定值时 `fSp` 在线动态调整，切换点自动跟随。
- **价值**：相比 `FB_BA_Swi2P`（开通点 / 关断点独立配置），本 FB 用"中心 + 宽度"模式更适合人机界面（用户只输设定温度和"温度死区"，不操心两个独立阈值）。
- **替代方案对比**：
  - **手算 `fOn = fSp - fHys/2`、`fOff = fSp + fHys/2` 再喂 `FB_BA_Swi2P`**：可行但客户端要算两次；
  - **手写 IF + TON + 状态机**：约 20 行；
  - **本 FB**：BA 标准、用户视角友好。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.2.2.4.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/13551664267.html
- **相关 FB**：`FB_BA_Swi2P`（开通点 / 关断点独立配置版）、`FB_BA_PIDCtrl`（连续 PID）

## 9. 待确认项 (⚠️)

- PDF VAR 区缺 `FUNCTION_BLOCK FB_BA_SwiHys2P` 头行：是 PDF 印刷遗漏，InfoSys 与编译器一致地把 VAR_INPUT 视为 FB 主声明的一部分。
