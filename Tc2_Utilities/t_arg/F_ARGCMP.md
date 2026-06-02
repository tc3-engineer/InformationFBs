# F_ARGCMP

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `T_Arg help functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35270667.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_ARGCMP.TcPOU`](../examples/P_Demo_F_ARGCMP.TcPOU) |

---

## 1. 功能简述

`F_ARGCMP` 比较两个 `T_Arg` 描述符并返回一个 `DINT` 表示它们的相对关系。两个 `T_Arg` 一旦都用 `F_<TYPE>` 系列打包过（持有 `eType` / `cbLen` / `pData`），就可以用本函数做"类型安全比较"或"类型独立比较"，结果按"第一个不同字节出现在哪个字段"分级返回。

存在意义是：在 `T_Arg`/`T_ArgList` 的世界里，调用方很少直接读原始 `pData^`——通常通过本函数判断两组参数是否一致（例如做 EventLogger 消息去重、参数列表回放校验、单元测试）。手写"先比 eType，再比 cbLen，再 MEMCMP 比 pData^" 的代码容易漏 corner case，本函数把整段逻辑封装。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_ARGCMP : DINT
VAR_INPUT
    typeSafe : BOOL;
    arg1     : T_Arg;
    arg2     : T_Arg;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `typeSafe` | `BOOL` | — | `TRUE` = 类型安全比较（`eType` 必须一致才继续比 `cbLen` / 内容）。`FALSE` = 类型无关比较（即使 `eType` 不同也比较底层字节，常用于"按值"比较） |
| `arg1` | `T_Arg` | — | 待比较的第一个参数描述符 |
| `arg2` | `T_Arg` | — | 待比较的第二个参数描述符 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

### 返回值

`DINT` —— 按 PDF / InfoSys 描述的"第一个不同字节出现的字段（类型 / 长度 / 值）"分级：

| 返回值 | 含义 |
|---|---|
| `-3` | `arg1` 的 `cbLen` 小于 `arg2.cbLen` |
| `-2` | `arg1` 的 `eType` 小于 `arg2.eType` |
| `-1` | `arg1` 的内容（`pData^`）小于 `arg2` 的内容 |
| `0`  | 两者完全相等（类型 / 长度 / 内容三者一致） |
| `+1` | `arg1` 的内容大于 `arg2` 的内容 |
| `+2` | `arg1` 的 `eType` 大于 `arg2.eType` |
| `+3` | `arg1` 的 `cbLen` 大于 `arg2.cbLen` |

## 3. 行为说明

**触发**：每次调用即同步求值，无副作用，单 PLC 周期内完成。

**算法**（伪代码）：

```
IF typeSafe AND arg1.eType <> arg2.eType THEN
    /* 类型不一致直接报相对大小，按 eType 比较 */
    RETURN signum(arg1.eType - arg2.eType) * 2
END_IF
IF arg1.cbLen <> arg2.cbLen THEN
    RETURN signum(arg1.cbLen - arg2.cbLen) * 3
END_IF
/* 类型 + 长度都一致，按字节比较内容 */
cmp := MEMCMP(arg1.pData, arg2.pData, arg1.cbLen)
IF cmp = 0 THEN RETURN 0
ELSE RETURN signum(cmp)
END_IF
```

**`typeSafe` 的语义**：`TRUE` 时把 `eType` 当作比较的首要维度，类型不一致就先报 ±2；`FALSE` 时跳过 `eType` 检查，只看 `cbLen` 和原始字节，这样 `F_INT(5)` 和 `F_DINT(5)` 在 `FALSE` 模式下因为 `cbLen` 不同还是会报 ±3；只有 `F_INT(5)` 和 `F_UINT(5)` 这种"长度相同字节内容相同"的对才会回 0。

**约束**：`arg1.pData` 与 `arg2.pData` 必须都指向**有效内存**，且至少各自有 `cbLen` 字节可读。若任一为 0 或越界，行为未定义（PDF 未明说但工程上经验是会触发访问违例）。

## 4. 错误码 / 返回值

无独立错误码 / `bError`。返回值就是比较结果（七档）。若返回值落在 ±3 / ±2 / ±1 / 0 之外说明输入参数被破坏（不应出现）。

## 5. 使用注意 / 常见坑

- **`typeSafe` 容易理解反**：`TRUE` 是"类型必须一致才算相等候选"（严格），`FALSE` 是"类型不一致也能比"（宽松）。命名容易让人以为 TRUE 才"安全"，但**两种都可能崩溃**——崩溃的根源是 `pData` 失效，与 `typeSafe` 无关。
- **`pData` 必须仍然有效**。`T_Arg` 是描述符不持有数据，比较时会真的去 `pData^` 读字节；若原变量已离开作用域、或重新赋值过，比较结果就不可信。
- **不能比对 `F_BIGTYPE` 打包的结构体差异语义**。`F_BIGTYPE` 返回的 `T_Arg.cbLen = SIZEOF(struct)`，按字节比较意味着任何 padding 差异、reserved 字节都会影响结果。建议比较结构体时先 `MEMSET(adr, 0, sizeof)` 再赋值，确保 padding 为零。
- **`F_PVOID` 比较的是指针值本身**，不是指针指向对象的内容。两个不同的 `T_Arg` 打包同一对象的不同指针时，`F_ARGCMP` 仍认为它们 `arg1.pData^ <> arg2.pData^`。
- **不要用 `F_ARGCMP` 做 hash key**：返回 ±3/±2/±1/0/+1/+2/+3 是有序信号，不是 hash。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_ARGCMP.TcPOU`](../examples/P_Demo_F_ARGCMP.TcPOU)

```iecst
// 场景：EventLogger 消息去重——同样的 (eventId, param) 二元组连续上报多次时，
//       只保留第一次。每次新消息到达，先用 F_ARGCMP 比较新参数和上一条的参数。
// 价值：替代手写"先比 eType，再比 cbLen，再 MEMCMP 数据"的三段比较逻辑。
// 验证：在线写 nValueA、nValueB 不同 → 观察 nCmpResult 非 0；
//       写两者相同 → nCmpResult = 0。
PROGRAM P_Demo_F_ARGCMP
VAR
    nValueA            : INT := 100;        // 模拟"上一条消息的参数"
    nValueB            : INT := 100;        // 模拟"本条消息的参数"
    argA, argB         : T_Arg;             // 两个待比的描述符
    bUseTypeSafeCmp    : BOOL := TRUE;      // 默认开启类型安全比较
    nCmpResult         : DINT;              // F_ARGCMP 的七档结果
    bCompare           : BOOL;
END_VAR

argA := F_INT(nValueA);
argB := F_INT(nValueB);

IF bCompare THEN
    nCmpResult := F_ARGCMP(typeSafe := bUseTypeSafeCmp, arg1 := argA, arg2 := argB);
    bCompare := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：EventLogger 消息去重、参数列表回放校验、单元测试断言"两组参数相等"。
- **价值**：把 `T_Arg` 的三字段比较包成一行，自动处理类型 / 长度 / 内容三层，结果带方向（±）便于排序。
- **替代方案对比**：手写 `IF a.eType = b.eType AND a.cbLen = b.cbLen AND MEMCMP(a.pData, b.pData, a.cbLen) = 0 THEN`：能用，但少一个 `signum` 就只能判等不能排序。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.10.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35270667.html
- **相关 FC**：`F_ARGCPY`（拷贝 `T_Arg` 含数据快照）、`F_ARGISZERO`（判空）、`F_<TYPE>` 系列（构造 `T_Arg`）
