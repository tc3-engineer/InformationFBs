# F_BIGTYPE

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `T_Arg help functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35261451.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_BIGTYPE.TcPOU`](../examples/P_Demo_F_BIGTYPE.TcPOU) |

---

## 1. 功能简述

`F_BIGTYPE` 是 `F_<TYPE>` 系列的"通用兜底"版：当待打包的数据不是基本类型（BOOL/INT/REAL...）而是**结构体、数组或任意长度内存块**时，无法直接 `F_INT(...)`，就用本函数手动指定地址 + 长度构造 `T_Arg`。

存在意义：基本类型 `F_<TYPE>` 系列覆盖了所有 IEC 标量，结构体 / 数组没有专用函数。`F_BIGTYPE` 提供"按字节"打包通道——调用方用 `ADR(myStruct)` 取地址、`SIZEOF(myStruct)` 取长度，返回的 `T_Arg.eType` 会被填成"通用结构体"枚举值，下游消费者按字节流处理（例如 ADS Notification 把整段结构体作为可变参数发送）。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_BIGTYPE : T_Arg
VAR_INPUT
    pData : POINTER TO BYTE;
    cbLen : DWORD;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pData` | `POINTER TO BYTE` | — | 待打包数据的首地址。通常用 `ADR(myStructOrArray)` 取得 |
| `cbLen` | `DWORD` | — | 该数据在内存中占用的字节数。通常用 `SIZEOF(myStructOrArray)` 取得 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

### 返回值

`T_Arg` —— 描述符，其 `pData = pData`，`cbLen = cbLen`，`eType = eValueType_<通用结构体>`（具体枚举值由 `Tc2_Utilities` 内部 `E_ArgType` 定义）。

## 3. 行为说明

**触发**：每次调用即同步求值，无副作用，单 PLC 周期内完成。

**算法**（伪代码）：

```
F_BIGTYPE.eType := eArgType_BIGTYPE
F_BIGTYPE.cbLen := cbLen
F_BIGTYPE.pData := pData
```

与 `F_<TYPE>` 不同，本函数让调用方**自己负责**地址和长度，因此可以打包：

- 任意结构体：`F_BIGTYPE(pData := ADR(stRecipe), cbLen := SIZEOF(stRecipe))`
- 任意数组：`F_BIGTYPE(pData := ADR(aSamples), cbLen := SIZEOF(aSamples))`
- 一段内存区间：`F_BIGTYPE(pData := pBufferStart, cbLen := nValidBytes)`

下游消费者拿到 `T_Arg` 后，按 `cbLen` 直接 `MEMCPY` 或字节扫描；没有"类型语义"概念，纯字节流。

**与下游的协议**：使用 `EventLogger` / `FB_FormatString2` 等格式化下游时，必须约定结构体布局（offset / size / endianness），否则下游解析会错位。常见做法是结构体里嵌一个版本号 / magic，下游先校验再解析。

## 4. 错误码 / 返回值

无独立错误码。返回值总是合法构造的 `T_Arg`。如果调用方传错 `pData` / `cbLen`，下游解析会出错但本函数本身不会失败。

## 5. 使用注意 / 常见坑

- **padding 字节**：结构体里编译器为对齐插入的 padding 字节会一起被复制 / 比较。在不同编译选项（pack、align）下结构体大小可能变化，跨平台时要 `{attribute 'pack_mode' := '1'}` 显式声明。
- **指针成员浅拷**：如果结构体内部含有指针字段（`POINTER TO X`），`F_BIGTYPE` 只打包指针值不打包指针指向的对象。下游收到后 `pData^` 拿到指针副本，再 deref 必须保证原对象生命周期未结束。
- **`cbLen` 错填**：填小了→下游读不全数据；填大了→下游读到越界垃圾。务必用 `SIZEOF(...)` 而不是手动写常量。
- **不要打包栈临时变量**：返回 `T_Arg.pData` 持有的是地址，原数据在调用所在函数返回后失效。打包必须在 POU 实例的稳定 VAR 上做。
- **大对象建议先快照**：如果原数据可能在下游消费前被修改，必须用 `F_ARGCPY` 拷到另一个等大稳定缓冲，再把 `F_BIGTYPE` 指向那个缓冲。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_BIGTYPE.TcPOU`](../examples/P_Demo_F_BIGTYPE.TcPOU)

```iecst
// 场景：把一个配方结构体（多字段：编号 + 温度 + 时长 + 状态）作为一个整体
//       打包成 T_Arg，喂给 EventLogger 当报警上下文，或者写入 ADS 自定义消息。
// 价值：结构体没有专用 F_<TYPE>，本函数提供按字节通道；调用方只需 ADR+SIZEOF。
// 验证：在线写 stCurrentRecipe.nRecipeId := 7、bPackRecipe := TRUE；
//       下一周期 argRecipe.cbLen 应等于 SIZEOF(stCurrentRecipe)、pData 非 0。
TYPE ST_Recipe :
STRUCT
    nRecipeId        : UDINT;
    fTargetTempC     : LREAL;
    tHoldDuration    : TIME;
    bIsActive        : BOOL;
END_STRUCT
END_TYPE

PROGRAM P_Demo_F_BIGTYPE
VAR
    stCurrentRecipe  : ST_Recipe;
    argRecipe        : T_Arg;
    bPackRecipe      : BOOL;
END_VAR

IF bPackRecipe THEN
    // 单次完整调用：把整个结构体地址 + 长度交给 F_BIGTYPE
    argRecipe := F_BIGTYPE(pData := ADR(stCurrentRecipe),
                           cbLen := SIZEOF(stCurrentRecipe));
    bPackRecipe := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：把配方 / 报警上下文 / 历史样本数组作为一个整体送给 `EventLogger` / `ADS 自定义消息`；或在测试代码里把一个结构体序列化进 `T_ArgList`。
- **价值**：填补 `F_<TYPE>` 只覆盖标量的不足，让"复杂数据→T_Arg"也走同一条管线。
- **替代方案对比**：手写 `arg.eType := xxx; arg.pData := ADR(s); arg.cbLen := SIZEOF(s);` —— 能用，但 `eType` 取什么值需要查 `E_ArgType`；本函数自动选对。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.10.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35261451.html
- **相关 FC**：`F_<TYPE>` 系列（基本类型版本）、`F_ARGCPY`（快照拷贝）
