# finish

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
| Example | [`examples/P_Demo_FB_CalcHashValue_finish.TcPOU`](../examples/P_Demo_FB_CalcHashValue_finish.TcPOU) |

---

## 1. 功能简述

`finish` 是 [`FB_CalcHashValue`](FB_CalcHashValue.md) 三段式 hash 计算的"**收尾**"方法。它把之前所有 `update` 喂入的数据做最终运算（hash 算法标准的 "squeeze" 或 "finalize" 步骤），生成 hash 值并写入调用方提供的 `pHash` 指向的缓冲区。

调用 `finish` 后，FB 的内部上下文被视为**已消耗**——再次 `update` 或 `finish` 行为未定义；新一次计算必须重新 `start`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pHash : PVOID;
    nHash : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pHash` | `PVOID` | 指向输出缓冲区的内存起始地址。通常用 `ADR(aHashBytes)` 取一个 `ARRAY OF BYTE` 的地址。**类型不检查、长度不检查**——缓冲区不够大会越界写入相邻内存 |
| `nHash` | `UDINT` | 调用方告诉 FB"我的缓冲区有这么多字节可用"。FB 把所选 `hashMode` 决定的输出长度（SHA-256=32 / SHA-512=64 字节）写入，**必须 ≥ 算法实际输出长度**，否则越界 |

### 返回值

⚠️ 待人工确认。PDF 在 `finish` 节内省略了 `METHOD finish : <RET>` 头，仅给出 `VAR_INPUT` 与参数表；InfoSys 同样省略。按 `start` / `update` 的 `BOOL` 模式推断 finish 也返回 `BOOL`，但 PDF 未显式声明。**保守用法**：不强依赖返回值，调用后立刻在线检查 `pHash` 指向的缓冲区是否被写入预期长度的非零值。

### VAR_IN_OUT

无。

## 3. 行为说明

调用瞬间发生的事情：

1. 取出内部累加状态（之前所有 `update` 累积的 hash 上下文）。
2. 应用 hash 算法标准的 "padding + finalize" 步骤——对于 SHA 家族，这一步把累计字节数信息附加进去并做最后几轮运算。
3. 把最终的 hash 字节序列写入 `pHash` 指向的内存，长度由 `hashMode` 决定（SHA-256 = 32 字节，SHA-512 = 64 字节）。
4. 标记内部状态为"已消耗"——后续 `update` / `finish` 不应再被调用。

**关键不变式**：相同的 `start(hashMode)` + 相同的 `update` 序列 → 相同的 `finish` 输出。这是 hash 算法的确定性保证。

**调用时序约束**：
- 必须在 `start` 之后调用
- 之前可以有 0、1 或多次 `update`
- 调用后必须**重新 `start`** 才能开始下一次计算（不能跳过 `start` 直接再 `update`）

**写入语义**：FB 把 `nHash` 字节范围内的内存按 hash 算法实际输出长度填写。若 `nHash > 算法输出长度`，多余字节是否被清零 PDF 未明说 ⚠️——保守做法是缓冲区与算法输出长度精确匹配，不留余量。

**单周期同步完成**：finalize 步骤本身计算量小（不到 1 微秒级），不会跨周期。

## 4. 错误码 / 返回值

⚠️ 返回类型与失败语义均未在 PDF 显式列出（参见上面"返回值"说明）。可观察的失败迹象：

| 现象 | 推测原因 |
|---|---|
| `pHash` 指向的内存仍为 `start` 前的旧值 / 全 0 | finish 内部失败、或 `nHash` 太小导致 FB 拒绝写入 |
| 字节模式像 hash 但与同输入数据离线工具不一致 | 算法版本不同、字节序问题，或 `update` 阶段数据有污染 |

工程上建议：调用 `finish` 后立刻把 `pHash` 内容与已知的"参考 hash"对比一次（开发期验证），运行期则依靠协议层的 hash 一致性检查。

## 5. 使用注意 / 常见坑

- **缓冲区大小是头号杀手**：`nHash` 不够大 = 越界写入。SHA-256 必须 ≥ 32 字节，SHA-512 必须 ≥ 64 字节。**惯用法**：声明 `aHash : ARRAY[0..N-1] OF BYTE;` 然后 `nHash := SIZEOF(aHash);`。
- 必须在 `start` + 0 个及以上 `update` 之后调；不能在 `finish` 之后再调 `update` 或 `finish`。
- 不要试图"重读 hash"：finish 之后内部状态已消耗，再调 `finish` 行为未定义。要再用 hash 值，自己把字节数组拷贝出来。
- 字节序：PLC 的 `ARRAY OF BYTE` 是按地址递增存储的；通常 hash 输出按 big-endian 字节序写入（SHA 算法标准）。在与 PC / 服务器对比时双方都按字节序输出十六进制即可，不要做整数解读后再比较。
- `PVOID` 不检查类型：传 `ADR(nNotABuffer)`（一个 UDINT）也"合法"——但会把 hash 写入只有 4 字节的目标，越界。**始终用足够大的 `ARRAY OF BYTE`**。
- `finish` 后想做"链式 hash（hash 的 hash）"：必须重新 `start` + `update(ADR(aFirstHash), 32)` + `finish` 再得到外层 hash。**不能直接接着 `update`**。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CalcHashValue_finish.TcPOU`](../examples/P_Demo_FB_CalcHashValue_finish.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 单独演示 finish() 的"收尾取 hash"；完整三段见 FB_CalcHashValue.md
PROGRAM P_Demo_FB_CalcHashValue_finish
VAR
    fbHashCalculator   : FB_CalcHashValue;
    eHashMode          : E_HashMode := E_HashMode.HashMode_Sha256;
    sInputPayload      : STRING(80) := 'hash-this-payload';
    aHashOutBytes      : ARRAY[0..31] OF BYTE;          // SHA-256 = 32 字节
    bDoFullHashCycle   : BOOL := FALSE;
    bStartOk           : BOOL;
    bUpdateOk          : BOOL;
    bFinishOk          : BOOL;
END_VAR

IF bDoFullHashCycle THEN
    bDoFullHashCycle := FALSE;
    bStartOk  := fbHashCalculator.start(hashMode := eHashMode);
    bUpdateOk := fbHashCalculator.update(pData := ADR(sInputPayload),
                                          nData := LEN(sInputPayload));
    // finish 把 32 字节 hash 写入 aHashOutBytes
    bFinishOk := fbHashCalculator.finish(pHash := ADR(aHashOutBytes),
                                          nHash := SIZEOF(aHashOutBytes));
    // 在线 monitor aHashOutBytes 应是 32 个非全 0 字节
END_IF
```

## 7. 业务场景与实际价值

- **场景**：所有 hash 计算的"取结果"环节——大文件 hash、配方 hash、报文 hash 都用本方法收尾。
- **价值**：把"流式累积"的内部状态变成可用的 hash 字节数组——业务侧可以把这 32 / 64 字节存入文件、通过 ADS 发给 MES、做完整性比对。
- **替代方案对比**：
  - `F_GenerateHashValue` 的单次调用：等价于 `start + update(整段) + finish`，对小数据更简洁
  - **本方法**：分段式计算无可替代的最后一步

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §3.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/12674253067.html
- **父 FB**：[`FB_CalcHashValue`](FB_CalcHashValue.md)
- **同 FB 其他方法**：[`start`](start.md) · [`update`](update.md)
