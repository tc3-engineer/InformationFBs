# PLARGE_TO_LARGE

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `P[TYPE]_TO_[TYPE] converting functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35304331.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_PLARGE_TO_LARGE.TcPOU`](../examples/P_Demo_PLARGE_TO_LARGE.TcPOU) |

---

## 1. 功能简述

`PLARGE_TO_LARGE` 是一个**指针解引用辅助函数**。给定一个指向 `LARGE` 类型变量的指针 `POINTER TO T_LARGE_INTEGER`，函数读取该地址处存放的内容并以 `LARGE` 返回。等价于 ST 中手写的 `pIn^`，但被封装成一次函数调用，便于在不能直接对指针解引用的语境（例如把指针解引用结果直接作为另一个函数的实参、或在某些受限的表达式位置）使用。

为什么 `Tc2_Utilities` 给每一种基本类型都准备了一只 `P<TYPE>_TO_<TYPE>`：在工业现场常见的场景是**接收 wire 数据后从字节流中按地址偏移取值**（Modbus 寄存器响应、CAN 报文、ADS Raw、TCP 二进制协议）。调用方一般先用 `ADR` / `pData + offset` 计算到字段起始地址，再用本系列函数按业务字段类型把这块内存解读为 `LARGE`，避免手写 `pAt := pBase + 4; nVal := pAt^;` 易错的指针算术。

本函数对应 `LARGE` 类型（Beckhoff 96 位整数（结构体）；取值范围 12 字节）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION PLARGE_TO_LARGE : LARGE
VAR_INPUT
    in : POINTER TO T_LARGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `POINTER TO T_LARGE_INTEGER` | — | 要解引用的指针；指向已分配的 `LARGE` 变量的首地址。调用方通常用 `ADR(myVar)` 或 `pBase + nOffset` 计算得到 |

### VAR_OUTPUT

无（FUNCTION 仅有返回值）。

### VAR_IN_OUT

无。

### 返回值

`LARGE` —— 把 `in` 视作 `POINTER TO T_LARGE_INTEGER` 解引用，把目标地址上的内存按 `LARGE` 解读后返回的副本。

## 3. 行为说明

**触发**：每次调用即同步求值，没有内部状态、没有副作用、没有阻塞，单 PLC 周期内完成。

**算法**（伪代码）：

```
return MEMORY[in .. in + SIZEOF(LARGE) - 1]   /* 按 LARGE 解读 */
```

实现层面就是 `PLARGE_TO_LARGE := in^;`——把指针在当前 PLC 实例内存空间里指向的 `SIZEOF(LARGE)` 字节按目标类型解读后赋给返回值。Beckhoff 把这层薄包装单独提供出来，意义在于：
- **当某些上下文不允许写 `pX^`**（例如某些库函数把指针当不透明 handle 传入、或代码生成器在拼装表达式时不便加 `^`），可以用 `PLARGE_TO_LARGE(pX)` 替代。
- **配合 `T_Arg`/`F_<TYPE>` 系列、以及 `P<TYPE>_TO_<TYPE>` 反向使用**，可以让"指针→值"和"值→T_Arg"两步代码风格统一，在 ADS 消息打包/拆包流程里读起来更整齐。

**字节序**：本函数**不做字节序转换**，直接按本机字节序（PLC x86/x64/ARM 都是小端）读内存。如果数据来自大端协议（Modbus TCP、CAN over Profinet），需要先经过 `Tc2_Utilities` 里的 `BE32_TO_HOST` 之类的字节序转换函数处理后再喂给本函数，否则取出来的是字节翻转过的错误值。

**安全性**：本函数**不校验** `in` 是否为有效指针。`in = 0`（NULL）或指向未分配/已释放内存时**会触发访问违例**，导致 PLC 进入异常停机（PageFault / AccessViolation）。调用方必须保证 `in` 在调用瞬间是有效的、且目标地址上至少有 `SIZEOF(LARGE)` 字节是可读的。

## 4. 错误码 / 返回值

无独立错误码、无 `bError` / `nErrorId`。返回值就是从 `in^` 读到的 `LARGE` 内容。"零返回"或"全 FF 返回"**不能**用来判定"出错"——它就是字面意义上的字节内容。

## 5. 使用注意 / 常见坑

- **NULL 指针不检查**。`PLARGE_TO_LARGE(0)` 不会返回 0、不会报错，会**直接让 PLC 崩溃**。调用前必须自检：`IF pData <> 0 THEN nVal := PLARGE_TO_LARGE(pData); END_IF;`。
- **类型必须严格对齐**。如果实际内存是 `ULARGE`（同宽不同语义）或更小的类型，会读出错误甚至越界。手写 wire 解码时要按协议规范确认字段宽度后再选用对应的 `P<TYPE>_TO_<TYPE>`。
- **字节序坑**。本函数按本机字节序读取，与对端协议字节序不一定一致。Modbus、IEC 61850 等大端协议必须先字节序转换。
- **指针存活期**。如果 `in` 指向的是另一个 POU 的临时局部变量、或刚被释放的动态内存，函数返回之后下一个周期内存内容可能已经被覆盖。安全做法是只在指针的生命周期内解引用、立即把返回值保存到稳定变量。
- **不是字节复制**。对 `LARGE` 这种 Beckhoff 96 位整数（结构体），处理器会按对齐方式整块加载；如果 `in` 不是 `SIZEOF(LARGE)` 对齐的（例如直接指向打包结构体的奇数偏移字段），在 ARM 平台上可能触发对齐异常。x86/x64 大多容忍，但性能也会下降。
- **与 `pIn^` 完全等价**。如果当前上下文可以直接写 `pIn^`，就没必要绕一圈调用本函数。本函数的存在更多是为了在表达式位置 / 函数实参位置 / 受限语境里替代解引用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_PLARGE_TO_LARGE.TcPOU`](../examples/P_Demo_PLARGE_TO_LARGE.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：从一段二进制 wire 缓冲区里按字段偏移取出 LARGE 值（典型来源：
//       Modbus/TCP 寄存器响应、CAN 报文、ADS Raw 读回字节流）。
// 价值：避免手写 pBase + nOffset + 强制类型转换的指针算术；一行调用即取值。
// 验证：在线把 lgRealValue 写为示例值，bExtractField := TRUE，
//       观察 lgRealValue_extracted 在下一个周期等于 lgRealValue。
PROGRAM P_Demo_PLARGE_TO_LARGE
VAR
    lgRealValue              : LARGE;   // 模拟 wire 缓冲区里的目标字段
    pLARGEField                        : POINTER TO T_LARGE_INTEGER;                // 业务侧先算好的字段地址
    bExtractField                        : BOOL;                       // 在线置 TRUE 触发一次解析
    lgRealValue_extracted    : LARGE;                    // 解析后的副本，用于业务逻辑
END_VAR

// 业务代码一般在收到 wire 数据后就计算字段地址（例：pBase + 协议偏移）；
// 此处用 ADR 模拟，等价于"指针已经指向有效内存"
pLARGEField := ADR(lgRealValue);

IF bExtractField AND pLARGEField <> 0 THEN
    // 关键调用：避免手写解引用，统一风格更便于和 BE/LE 字节序转换函数串联
    lgRealValue_extracted := PLARGE_TO_LARGE(pLARGEField);
    bExtractField := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：解析 Modbus/TCP 寄存器响应、CAN 报文、Profinet 自定义 PDU、ADS Raw 读回字节流时，从某个**已知偏移**取出 `LARGE` 类型字段。也用于把 retain 区或 NC 数据缓冲区里的某块内存按业务类型读出。
- **价值**：替代手写 `pField := ADR(buf) + nOff; nVal := pField^;` 两行指针算术，降低出错风险（少打一个 `^`、少写一个强转）。与 `Tc2_Utilities` 字节序转换函数（`BE16/32_TO_HOST` 等）配合，整段 wire 解码代码风格统一。
- **替代方案对比**：
  - 直接写 `nVal := pX^`：可行，但在表达式位置 / 函数实参位置 / 代码生成器场景下不够灵活。
  - `MEMCPY(ADR(nVal), pX, SIZEOF(LARGE))`：能用，但绕远路、性能差、可读性低。
  - **本函数**：语义清晰、一次调用即解引用、与 InfoSys 文档术语一致、配合 `F_<TYPE>`（值→T_Arg）形成对称的"指针→值/值→T_Arg"对。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.6.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35304331.html
- **相关 FC**：`F_<TYPE>` 系列（把 `LARGE` 值打包成 `T_Arg`）、`BE16_TO_HOST` / `BE32_TO_HOST`（字节序转换）、`ULARGE` 对照（同宽相关类型）
