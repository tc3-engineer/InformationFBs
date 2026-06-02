# F_ARGISZERO

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `T_Arg help functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35272203.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_ARGISZERO.TcPOU`](../examples/P_Demo_F_ARGISZERO.TcPOU) |

---

## 1. 功能简述

`F_ARGISZERO` 检查一个 `T_Arg` 是否处于"空"状态：返回 `TRUE` 表示 `T_Arg` 的成员变量中**至少有一个为零**（典型情况是 `pData = 0` / `cbLen = 0` / `eType = 0`，即未初始化或被显式清零）。

业务用途是判定一个槽位是否被填过——例如 `T_ArgList` 中后面留白的槽位、构造一组参数时没塞够、或调用方传错。比手写 `IF arg.pData = 0 OR arg.cbLen = 0 THEN ...` 更直接。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_ARGISZERO : BOOL
VAR_INPUT
    arg : T_Arg;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `arg` | `T_Arg` | — | 待检查的参数描述符 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

### 返回值

`BOOL` —— `TRUE` = `arg` 的某个成员为零（视作"未初始化 / 空槽位"）；`FALSE` = 三字段都非零，arg 是有效的。

## 3. 行为说明

**触发**：每次调用即同步求值，无副作用，单 PLC 周期内完成。

**算法**（伪代码）：

```
RETURN (arg.eType = 0) OR (arg.cbLen = 0) OR (arg.pData = 0)
```

任一字段为零都判为"空"。最常见的场景是 `arg.pData = 0`——即调用方声明了 `arg : T_Arg;` 但没有调用任何 `F_<TYPE>` 给它绑定数据。

**与 `F_ARGCMP` 的关系**：`F_ARGISZERO(arg)` 等价于 `F_ARGCMP(typeSafe := FALSE, arg1 := arg, arg2 := <一个全零 T_Arg>) = 0`，但语义更清晰，性能也更好（不去读 `pData^`）。

## 4. 错误码 / 返回值

无独立错误码。返回 `TRUE` / `FALSE`。

## 5. 使用注意 / 常见坑

- **不要把"参数值是 0"误判为"参数为空"**。`F_INT(nZero)`（其中 `nZero := 0`）的返回 `T_Arg` 仍然非空——`eType / cbLen / pData` 都非零，只是 `pData^ = 0`。`F_ARGISZERO` 只看描述符不看值。
- **`pData = 0` 但 `cbLen > 0`** 的"半填"状态也判为空（合理，因为读 `pData^` 会崩）。
- **`T_Arg` 是 VAR_INPUT 传值**：函数收到的是描述符副本，不会动调用方的 `arg`。
- **没有 `arg.pData` 范围检查**。`F_ARGISZERO` 不会去 `pData^` 探测内存是否可读，只看指针值非零。如果 `pData = 16#DEAD`，函数照样返回 FALSE（不为零）但你 deref 时会崩。
- **常见混淆**：以为本函数能检测 `F_<TYPE>` 调用后是否成功——`F_<TYPE>` 总是返回非空 `T_Arg`，本函数主要是检测"用户根本没调用 F_<TYPE>"的情况。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_ARGISZERO.TcPOU`](../examples/P_Demo_F_ARGISZERO.TcPOU)

```iecst
// 场景：解析 T_ArgList 时按索引取槽位，越界 / 未填的槽位应跳过而不是 deref 崩溃。
// 价值：替代手写 IF arg.pData = 0 OR arg.cbLen = 0 THEN，一行更直观。
// 验证：把 argUnused 直接声明不赋值，把 argInUse 用 F_INT 绑定；
//       bCheck := TRUE 后观察 bUnusedIsEmpty = TRUE，bInUseIsEmpty = FALSE。
PROGRAM P_Demo_F_ARGISZERO
VAR
    nLiveValue        : INT := 42;
    argInUse          : T_Arg;       // 会被 F_INT 绑定
    argUnused         : T_Arg;       // 故意不绑定，模拟空槽位
    bInUseIsEmpty     : BOOL;        // 期望 FALSE
    bUnusedIsEmpty    : BOOL;        // 期望 TRUE
    bCheck            : BOOL;
END_VAR

argInUse := F_INT(nLiveValue);

IF bCheck THEN
    bInUseIsEmpty  := F_ARGISZERO(arg := argInUse);
    bUnusedIsEmpty := F_ARGISZERO(arg := argUnused);
    bCheck := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：遍历 `T_ArgList` 找有效槽位、参数收集流程的健全性检查、`EventLogger` 消息构造时检测缺失参数。
- **价值**：替代分散的 `pData = 0` / `cbLen = 0` 判断，命名直观，调用一行。
- **替代方案对比**：手写 `IF a.pData = 0 OR a.cbLen = 0 OR a.eType = 0 THEN`：能用，但读起来不如 `F_ARGISZERO(a)` 直白。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.10.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35272203.html
- **相关 FC**：`F_ARGCPY`、`F_ARGCMP`、`F_<TYPE>` 系列
