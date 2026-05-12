# start

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `METHOD` |
| Category | `FB_CalcHashValue` |
| Parent FB | [`FB_CalcHashValue`](FB_CalcHashValue.md) |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/12674253067.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_CalcHashValue_start.xml`](../examples/P_Demo_FB_CalcHashValue_start.xml) |

---

## 1. 功能简述

`start` 是 [`FB_CalcHashValue`](FB_CalcHashValue.md) 三段式 hash 计算的**初始化方法**。调用本方法的作用是：把内部 hash 上下文清零、选定本次计算使用的 hash 算法（通过 `hashMode` 参数从 `E_HashMode` 枚举里选）。

任何一次 hash 计算的第一步都必须调 `start`；之后才能调 `update` 喂数据，最后 `finish` 取结果。重新计算（同一实例的下一次 hash）也必须先重新调 `start` 重置状态。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD start : BOOL
VAR_INPUT
    hashMode : E_HashMode;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `hashMode` | `E_HashMode` | 指定本次计算使用的 hash 算法，如 `HashMode_Sha256` / `HashMode_Sha512`。完整可用值见 `E_HashMode` 枚举。模式一旦选定，本次计算的输出长度也就确定（SHA-256=32 字节，SHA-512=64 字节） |

### 返回值

`BOOL` —— PDF 显式声明为 `METHOD start : BOOL`。`TRUE` 表示初始化成功；`FALSE` 时具体错误条件未在 PDF 列出 ⚠️（典型可能为 `hashMode` 取值非法、内部分配失败）。

### VAR_IN_OUT

无。

## 3. 行为说明

调用瞬间发生的事情：

1. 检查 `hashMode` 合法性（属于 `E_HashMode` 枚举值）；非法则返回 `FALSE`。
2. 清空 FB 内部上下文（之前的 hash 累加状态、若有缓存的中间数据全部丢弃）。
3. 把所选算法的初始向量（initial vector，IV）写入内部状态——这是 hash 算法标准定义的"起始点"。
4. 返回 `TRUE` 表示状态机已就绪，等待后续 `update` / `finish`。

调用是同步、非阻塞、单周期内完成的——不会有 busy 等待，也不存在跨周期初始化。

**幂等性**：连续调用两次 `start`（相同或不同 `hashMode`）等价于"以最后一次 `start` 为准重新开始"——前一次 `start` 后到这次 `start` 前累积的 `update` 数据被丢弃。这一行为可用作"取消上一次 hash 计算"。

**与"零次 update + finish"组合**：调完 `start` 不调 `update` 直接 `finish` 是合法的——结果是空输入的 hash 值，数学上确定（SHA-256 空输入 = `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`）。

## 4. 错误码 / 返回值

| 返回 | 含义 |
|---|---|
| `TRUE` | 初始化成功，可以继续调 `update` / `finish` |
| `FALSE` | 初始化失败。⚠️ PDF / InfoSys 未列出具体失败情景。典型可能：`hashMode` 取值越界、内部资源分配失败 |

业务侧建议：`start` 返回 `FALSE` 时不要继续调 `update` / `finish`——内部状态可能未初始化。应当报警并停止本次 hash 计算。

## 5. 使用注意 / 常见坑

- 每次新 hash 计算前都要调一次 `start`——不能假设"finish 后内部状态会自动清"。PDF 没保证。
- `hashMode` 在运行时不能变：start 后再切换算法会让 update 喂入的数据按错误的算法处理，要切换必须重新 `start`。
- 检查返回值：`FALSE` 时跳过后续步骤，否则可能读到未初始化的 hash。
- `E_HashMode` 枚举的可用值与 `nHash` 缓冲区大小要对齐——SHA-256 → 32 字节，SHA-512 → 64 字节；缓冲区大小由 `finish` 的 `nHash` 决定，但要在 `start` 时就规划好。
- 不要在 hash 计算进行中再次 `start`——会丢弃上次的中间数据。如果是"取消上次"，正确做法是 `start` 一次新的（用作 reset）；如果是"继续上次"，则**不调 `start`** 直接接着 `update`。
- 调用频率：通常每次 hash 计算只调一次 `start`，不会高频调用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CalcHashValue_start.xml`](../examples/P_Demo_FB_CalcHashValue_start.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 单独演示 start() 初始化；完整三段流程见 FB_CalcHashValue.md 顶层例程
PROGRAM P_Demo_FB_CalcHashValue_start
VAR
    fbHashCalculator   : FB_CalcHashValue;
    eHashMode          : E_HashMode := E_HashMode.HashMode_Sha256;
    bStartInit         : BOOL := FALSE;
    bStartOk           : BOOL;
END_VAR

// 上升沿触发一次初始化
IF bStartInit THEN
    bStartInit := FALSE;
    bStartOk := fbHashCalculator.start(hashMode := eHashMode);
    // bStartOk = TRUE 后才能继续调 update / finish；
    // FALSE 时应报警并停止本次计算
END_IF
```

## 7. 业务场景与实际价值

- **场景**：每次新文件 / 新报文 hash 计算前的"开局"——选定算法、清空状态。这一步通常和业务逻辑里的"开始接收数据"事件配对。
- **价值**：把"复用 FB 实例" 变成可行——同一个 FB 实例可以为成百上千个文件分别计算 hash，靠 `start` 在每次开头重置。
- **替代方案对比**：
  - 每次新建 FB 实例：浪费内存且 PLC 不易动态分配
  - **本方法**：复用实例，每次开头 `start` 即可

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/12674253067.html
- **父 FB**：[`FB_CalcHashValue`](FB_CalcHashValue.md)
- **同 FB 其他方法**：[`update`](update.md) · [`finish`](finish.md)
- **相关枚举**：`E_HashMode`
