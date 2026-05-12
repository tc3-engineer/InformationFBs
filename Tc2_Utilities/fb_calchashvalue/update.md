# update

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
| Example | [`examples/P_Demo_FB_CalcHashValue_update.xml`](../examples/P_Demo_FB_CalcHashValue_update.xml) |

---

## 1. 功能简述

`update` 是 [`FB_CalcHashValue`](FB_CalcHashValue.md) 三段式 hash 计算的"**喂数据**"方法。在 `start` 之后、`finish` 之前的任意时刻，调用方调用本方法把一段输入数据"喂"进 hash 上下文。它可以**反复调用任意多次**，每次喂一段；FB 内部把所有喂入的数据当作一个连续的字节流参与 hash 计算。

典型用法之一：大文件分块读取并 hash——每读 64 KB 调一次 `update`，最后 `finish` 拿到整文件的 hash，避免把整个文件先加载进 PLC 内存。

## 2. 接口定义

### VAR_INPUT

```iecst
METHOD update : BOOL
VAR_INPUT
    pData : PVOID;
    nData : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pData` | `PVOID` | 指向本次喂入数据的内存起始地址。一般用 `ADR(<变量名>)` 取地址。`PVOID` 是无类型指针——传任何类型变量地址都合法，运行时不做类型检查 |
| `nData` | `UDINT` | 本次喂入数据的字节数。必须与 `pData` 指向的有效数据长度一致；过大将把后续相邻内存当作数据喂入（脏数据），过小则只 hash 前一段 |

### 返回值

`BOOL` —— PDF 显式声明为 `METHOD update : BOOL`。`TRUE` 表示喂入成功；`FALSE` 时具体错误条件未在 PDF 列出 ⚠️。

### VAR_IN_OUT

无。

## 3. 行为说明

调用瞬间发生的事情：

1. 把 `pData` 指向的 `nData` 字节内容输入到内部 hash 状态机（流式 hash 算法的标准 "absorb" 步骤）。
2. 更新内部累加状态——但不输出 hash（hash 输出只在 `finish` 中产生）。
3. 返回 `TRUE` 表示喂入成功。

**调用是同步的**：单 PLC 周期内完成 `nData` 字节的处理；不存在跨周期 busy 等待。

**多次调用的等价性**：以下两种调用产生相同 hash：
- 一次 `update(pData=ADR(a), nData=10)`，其中 `a` 是 10 字节
- 两次 `update(pData=ADR(a), nData=5)` 后再 `update(pData=ADR(a+5), nData=5)`

也就是说，"分块喂入"与"一次性喂入"对 hash 结果没区别——这是流式 hash 算法的标准性质，本 FB 完全遵守。

**调用顺序约束**：
- 必须先调 `start`；未 `start` 直接 `update` 行为未定义
- 在 `finish` 之前可调 0 次或多次 `update`
- `finish` 之后再调 `update` 行为未定义 ⚠️——重新算必须重新 `start`

**性能影响**：`update` 的执行时间与 `nData` 成正比——hash 算法本身是 O(N)。把 1 MB 一次性喂入会消耗当周期约 N 微秒（依 CPU 与算法而定）。**建议每周期不超过 64 KB**，大数据分多周期处理。

## 4. 错误码 / 返回值

| 返回 | 含义 |
|---|---|
| `TRUE` | 喂入成功，可以继续 `update` 或调 `finish` |
| `FALSE` | 喂入失败。⚠️ PDF / InfoSys 未列出具体失败情景。典型可能：未先 `start`、`pData = 0`（空指针）、`nData = 0` 的退化情况 |

业务侧建议：`update` 返回 `FALSE` 时不要继续调 `finish`——内部状态可能已被部分污染，应报警并以新一次 `start` 重头来过。

## 5. 使用注意 / 常见坑

- `nData` 一定要用**字节**数：`LEN(s)` 返回字符数，对 ASCII `STRING` 字符 = 字节，对 `WSTRING` 一个字符是 2 字节，搞错会少算一半数据。**`SIZEOF(...)`** 给的是变量分配的总字节数（包括 STRING 类型的 0 终止符占的字节），是另一种潜在坑。**最稳的做法**：明确知道喂多少字节就显式写常数。
- `pData` 指向的内存必须在 `update` 返回前都有效：典型反例 → 局部 STRING 取址后立刻被覆盖。用稳定的全局 / FB 内变量。
- 不要把不同类型的数据"串"在一起喂——hash 结果对**字节序列**敏感，喂入顺序、字节边界、对齐方式都影响结果。
- 单 PLC 周期内反复调 `update` 是合法的，但要注意累计 `nData` 不能让 PLC 周期超时。
- `nData = 0` 的调用 PDF 未明说行为——保守不调（hash 等价于不喂数据，等同跳过这次 `update`）。
- 多任务 / 多核并行调同一 FB 实例不安全——FB 是有状态的。要并行用多个 FB 实例。
- 喂入数据**不一定要等长**：可以第一次喂 1 字节、第二次喂 999 字节，hash 算法对分块边界不敏感。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CalcHashValue_update.xml`](../examples/P_Demo_FB_CalcHashValue_update.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 单独演示 update() 的"分段喂入"；完整三段见 FB_CalcHashValue.md
PROGRAM P_Demo_FB_CalcHashValue_update
VAR
    fbHashCalculator   : FB_CalcHashValue;
    eHashMode          : E_HashMode := E_HashMode.HashMode_Sha256;
    sChunk1            : STRING(80) := 'hello ';
    sChunk2            : STRING(80) := 'world';
    bDoTwoStepHash     : BOOL := FALSE;
    bStartOk           : BOOL;
    bUpdateOk1         : BOOL;
    bUpdateOk2         : BOOL;
END_VAR

// 演示：两次 update 合并喂入；与一次性 update('hello world') 等价
IF bDoTwoStepHash THEN
    bDoTwoStepHash := FALSE;
    bStartOk := fbHashCalculator.start(hashMode := eHashMode);
    bUpdateOk1 := fbHashCalculator.update(pData := ADR(sChunk1),
                                           nData := LEN(sChunk1));
    bUpdateOk2 := fbHashCalculator.update(pData := ADR(sChunk2),
                                           nData := LEN(sChunk2));
    // 之后调 finish() 取 hash（本例只演示 update）
END_IF
```

## 7. 业务场景与实际价值

- **场景**：大文件 / 大数据流分块 hash——本方法的核心价值。例如 PLC 通过 FB_FileRead 每 PLC 周期读 64 KB 工艺文件，每读完一段就 `update` 一次，文件读完后 `finish` 拿整体 hash。
- **价值**：相对于"先全部读到内存再 hash"，**节省内存**（不必为 100 MB 文件准备 100 MB 缓冲区）、**省周期时间**（hash 计算被均摊到每个周期）。
- **替代方案对比**：
  - 一次性 `F_GenerateHashValue`：要求数据已全在内存里，大文件场景不可行
  - 多次调 `F_GenerateHashValue`：每次返回的是"那一段的 hash"，**无法**简单串起来等价于"整体 hash"
  - **本方法**：流式 hash 的标准实现，无可替代

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/12674253067.html
- **父 FB**：[`FB_CalcHashValue`](FB_CalcHashValue.md)
- **同 FB 其他方法**：[`start`](start.md) · [`finish`](finish.md)
