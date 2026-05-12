# F_ARGCPY

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `T_Arg help functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35269131.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_ARGCPY.xml`](../examples/P_Demo_F_ARGCPY.xml) |

---

## 1. 功能简述

`F_ARGCPY` 把一个 `T_Arg`（描述符 + 指向源数据的指针）"实拷贝"到另一个 `T_Arg`：函数会按 `src.cbLen` 字节把 `src.pData^` 的内容复制到 `dest.pData^` 指向的内存，并同步 `eType` / `cbLen`。返回成功复制的字节数（`UDINT`），若任一参数无效返回 0。

存在意义是：`F_<TYPE>` 打包出的 `T_Arg` 只持有指针不持有数据，遇到"我需要把当前参数保存下来，原变量后续会变"的场景（消息排队、快照、日志缓存）就必须用本函数做**深拷贝**，否则下游读到的是后续被覆盖过的新值而不是当时的快照。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION F_ARGCPY : UDINT
VAR_INPUT
    typeSafe : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `typeSafe` | `BOOL` | — | `TRUE` = 类型安全（要求 `dest.eType = src.eType` 才执行拷贝，否则返回 0）。`FALSE` = 类型无关（只看 `cbLen`，类型不同也可强拷） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    dest : T_Arg;
    src  : T_Arg;
END_VAR
```

| 名称 | 类型 | 方向 | 说明（中文） |
|---|---|---|---|
| `dest` | `T_Arg` | `VAR_IN_OUT` | 目标 `T_Arg`，函数会按 `src.cbLen` 字节往 `dest.pData^` 写入内容并同步 `eType`/`cbLen` |
| `src`  | `T_Arg` | `VAR_IN_OUT` | 源 `T_Arg`，提供原始字节 |

### 返回值

`UDINT` —— 实际成功复制的字节数；若类型 / 长度不匹配或任一 `pData = 0`，返回 0。

## 3. 行为说明

**触发**：每次调用即同步求值，无副作用，单 PLC 周期内完成。

**算法**（伪代码）：

```
IF dest.pData = 0 OR src.pData = 0 OR src.cbLen = 0 THEN RETURN 0
IF typeSafe AND dest.eType <> src.eType THEN RETURN 0
n := MIN(dest.cbLen, src.cbLen)      /* 不溢出目标缓冲 */
MEMCPY(dest.pData, src.pData, n)
dest.eType := src.eType
dest.cbLen := n
RETURN n
```

**`typeSafe = TRUE`** 时严格要求两边 `eType` 一致（例如不能把 `F_INT` 拷到 `F_DINT`），保护"类型语义不被混淆"；**`FALSE`** 时绕过类型检查，按字节强拷，常用于"我知道两个 T_Arg 的底层布局兼容（同宽同对齐），就要强行覆盖"。

**`dest` 必须已经预分配过缓冲**：通常先用 `F_<TYPE>(local)` 把一个本地稳定变量打包进 `dest`，让 `dest.pData = ADR(local)` 指向自己的缓冲区，然后再 `F_ARGCPY` 把 `src` 的内容拷进来——这样 `src` 即使后续失效，`local` 仍然保留快照。

## 4. 错误码 / 返回值

返回 0 表示拷贝失败（`pData = 0`、类型不匹配、长度为零）；返回 > 0 表示成功复制了 N 字节。无独立错误码。

## 5. 使用注意 / 常见坑

- **`dest` 必须已绑定到一块足够大的稳定缓冲**。如果只 `dest : T_Arg;` 不初始化，`dest.pData = 0`，本函数返回 0 不会爆炸但也什么都没拷。最佳实践是先 `dest := F_<TYPE>(myLocal);` 让 `dest.pData` 指到本地变量地址。
- **`MIN(dest.cbLen, src.cbLen)` 截断**：当 `dest` 缓冲比 `src` 小（例如把 LREAL 拷到 INT 槽位），函数只拷 `dest.cbLen` 字节，超出部分丢失。返回值小于 `src.cbLen` 即可识别"被截断"。
- **`typeSafe` 命名易误解**：`TRUE` 是"类型必须匹配"，不是"拷贝过程安全"；两种模式都不会读越界 `dest`。
- **拷贝后 `src.pData` 仍指向原内存**：本函数只复制数据，不会动 `src`；下次再调用 `F_ARGCPY` 用同一个 `src` 仍然有效。
- **不要拷贝包含指针的结构体**。如果 `src` 是 `F_BIGTYPE` 打包的含内嵌指针的 struct，深拷只复制内嵌指针值不复制指针指向的对象，得到的是浅拷贝。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_ARGCPY.xml`](../examples/P_Demo_F_ARGCPY.xml)

```iecst
// 场景：把"当前周期采集到的报警温度参数"快照保存到日志缓冲区，
//       原变量在下一个周期会被新数据覆盖，但日志里要保留首次出现的瞬时值。
// 价值：直接 dest := src 是浅拷（只复制描述符，pData 仍指原变量），
//       下一周期 dest.pData^ 跟着原变量变化。F_ARGCPY 是深拷，独立于原变量。
// 验证：在线写 fAlarmTempLive := 95.0、bSnapshot := TRUE；
//       再改 fAlarmTempLive := 25.0；观察 fAlarmTempSnapshot 仍为 95.0。
PROGRAM P_Demo_F_ARGCPY
VAR
    fAlarmTempLive       : LREAL := 0.0;     // 实时温度（持续变化）
    fAlarmTempSnapshot   : LREAL := 0.0;     // 快照缓冲（自有内存）
    argLive              : T_Arg;             // 指向 fAlarmTempLive
    argSnapshot          : T_Arg;             // 指向 fAlarmTempSnapshot
    nBytesCopied         : UDINT;             // 拷贝字节数（应 = 8）
    bUseTypeSafeCopy     : BOOL := TRUE;      // 默认类型安全
    bSnapshot            : BOOL;              // 在线置 TRUE 触发一次拷贝
END_VAR

argLive     := F_LREAL(fAlarmTempLive);
argSnapshot := F_LREAL(fAlarmTempSnapshot);   // 先把 snapshot 绑定到自己的内存

IF bSnapshot THEN
    nBytesCopied := F_ARGCPY(typeSafe := bUseTypeSafeCopy,
                             dest := argSnapshot,
                             src  := argLive);
    bSnapshot := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：消息队列 / 报警日志 / 历史记录——把瞬时参数快照保存，避免原变量后续变化污染日志。
- **价值**：把"浅拷会跟着原变量变"这个 T_Arg 用法的最大坑用一行 `F_ARGCPY` 修掉，且自带类型保护开关。
- **替代方案对比**：手写 `MEMCPY(dest.pData, src.pData, src.cbLen)`：能用，但忘了同步 `dest.eType` / `dest.cbLen` 是下游解码错位的常见原因。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.10.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35269131.html
- **相关 FC**：`F_ARGCMP`（比较）、`F_ARGISZERO`（判空）、`F_<TYPE>` 系列（构造源 / 绑定目标缓冲）
