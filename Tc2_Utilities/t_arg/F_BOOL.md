# F_BOOL

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `T_Arg help functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35259915.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_BOOL.TcPOU`](../examples/P_Demo_F_BOOL.TcPOU) |

---

## 1. 功能简述

`F_BOOL` 是 `T_Arg`（参数描述结构体）的**辅助打包函数**。给定一个 `BOOL` 类型的变量，返回一个 `T_Arg` 结构体，里面记录了该变量的**类型枚举**（`eType`，本函数固定为 `BOOL` 对应的常量）、**字节长度**（`cbLen`，本类型 = 1 字节）以及**指向原始数据的指针**（`pData = ADR(in)`）。

为什么 `Tc2_Utilities` 给每个基本类型都准备了一只 `F_<TYPE>`：IEC 61131-3 结构化文本（ST）**没有可变参数（variadic args）**，所以 Beckhoff 把"把一组任意类型变量打包成可变参数"的工程问题用 `T_Arg` + `F_<TYPE>` 系列解决。典型链路是：业务侧用 `F_BOOL(x) / F_INT(n) / F_LREAL(f) / ...` 把每个实参打包成 `T_Arg`，再用 `F_PutInArg` 把若干 `T_Arg` 串成 `T_ArgList`，最后传给 `EventLogger`、`ADS Message`、`FB_FormatString2` 等下游消费者。下游通过 `T_Arg.eType` 知道每个槽位的类型、通过 `pData + cbLen` 直接读到原始字节，避免 ST 不支持变长参数的痛点。

本函数对应 `BOOL` 类型（布尔位）。

## 2. 接口定义

### VAR_INPUT

无（本函数没有传值输入）。

### VAR_IN_OUT

```iecst
FUNCTION F_BOOL : T_Arg
VAR_IN_OUT
    in : BOOL;
END_VAR
```

| 名称 | 类型 | 方向 | 说明（中文） |
|---|---|---|---|
| `in` | `BOOL` | `VAR_IN_OUT` | 待打包的原始变量。函数会取该变量的地址 `ADR(in)` 写入返回 `T_Arg.pData`，所以**必须**通过引用传递（VAR_IN_OUT），不能传字面量 |

### VAR_OUTPUT

无。

### 返回值

`T_Arg` —— 描述输入变量的 `T_Arg` 结构体（包含 `eType`、`cbLen`、`pData` 三个核心字段）。

## 3. 行为说明

**触发**：每次调用即同步求值，无内部状态，无副作用，单 PLC 周期内完成。

**算法**（伪代码）：

```
F_BOOL.eType  := eValueType_BOOL     /* 在 E_ArgType 枚举中对应 BOOL 的常量 */
F_BOOL.cbLen  := SIZEOF(BOOL)        /* 本类型 = 1 字节 */
F_BOOL.pData  := ADR(in)                  /* 指向原变量内存 */
```

返回的 `T_Arg` 是一个**轻量级描述符**，本身**不复制**原变量数据，只持有指针。因此返回的 `T_Arg` 在原变量 `in` 仍存活的时间内有效；一旦 `in` 走出作用域（例如本调用所在的 POU 实例的扫描周期结束、或者 `in` 是其他 FB 的临时局部变量），`T_Arg.pData` 就**悬空**，下游再读到的内容就是垃圾。

**典型使用链路**：

```
xLevelOk : BOOL;
argList : T_ArgList;
...
F_PutInArg(arg := F_BOOL(xLevelOk), nIdx := 0, putState := PUTARG_INIT, args := argList);
F_PutInArg(arg := F_DINT(nOther),                 nIdx := 1, putState := PUTARG_ADD,  args := argList);
// 然后把 argList 喂给 EventLogger / ADS 消息 / 格式化字符串
```

**与 `P<TYPE>_TO_<TYPE>` 的对称性**：`P<TYPE>_TO_<TYPE>` 把"指针 → 值"（解引用），`F_<TYPE>` 把"值 → T_Arg 描述符"（含指针），两者一起构成 wire 解包/打包的对称工具集。

## 4. 错误码 / 返回值

无独立错误码，无 `bError` / `nErrorId`。返回的 `T_Arg` 总是**合法填充**（三个字段都被赋值），无失败分支。

如果下游消费者（`F_PutInArg`、`EventLogger`、`FB_FormatString2` 等）报错，常见根因是 `T_Arg.pData` 指向的变量已经失效，**不是**本函数本身的错误。

## 5. 使用注意 / 常见坑

- **不能传字面量**。`F_BOOL(TRUE)` 之类的写法编译报错——VAR_IN_OUT 必须传可寻址左值。要传常量，先赋给一个临时变量再传。
- **生命期陷阱**。返回的 `T_Arg.pData` 是原变量地址。如果在一个函数里返回 `F_BOOL(localVar)`，离开函数后 `localVar` 已被回收，下游再用就读到栈垃圾。安全做法：在 POU 实例的稳定变量（VAR）上调用，不要在 FUNCTION 的临时局部变量上调用。
- **不复制数据**。`T_Arg` 是描述符不是拷贝。如果业务侧在调用后改了 `in`，下游下次读 `T_Arg.pData^` 会读到**新值**——这有时是想要的（监控量），有时不是（参数快照）。要快照请显式 `F_ARGCPY` 到另一个 `T_Arg`。
- **类型必须严格匹配**。`F_BOOL` 不能用来打包 `BYTE` 即使大小一样：下游会按 `eType = BOOL` 解读语义，错配会让 EventLogger / 格式化串拿到错误的渲染结果。
- **`F_PVOID` 特别注意**：传入的是 `PVOID`（指针本身），下游拿到的是"指向指针的指针"，需要二次解引用；用得不准容易理解成"指针指向的对象"。
- **不要在循环里高频构造然后丢弃**。虽然 `T_Arg` 很小，但如果用 `T_ArgList` 配合，丢弃的 `T_Arg` 实例可能让 `pData` 突然失效。最佳实践是建一组持久的 `T_Arg` 槽位、按需重新填充。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_BOOL.TcPOU`](../examples/P_Demo_F_BOOL.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
// 场景：在事件日志/格式化字符串中把一个 BOOL 业务量打包成 T_Arg，
//       再用 F_PutInArg 串入参数列表，供下游 EventLogger 渲染消息。
// 价值：替代手写填 T_Arg.eType / cbLen / pData 三个字段；
//       配合 F_PutInArg 形成"变长参数"机制，绕过 ST 无 variadic 的限制。
// 验证：在线写 xLevelOk 为示例值，bPackArg := TRUE，
//       观察 argDescriptor.cbLen 等于 SIZEOF(BOOL)、argDescriptor.pData 非 0。
PROGRAM P_Demo_F_BOOL
VAR
    xLevelOk                        : BOOL := TRUE;  // 业务量
    bPackArg                        : BOOL;       // 在线置 TRUE 触发一次打包
    argDescriptor                   : T_Arg;      // 打包后的描述符
END_VAR

IF bPackArg THEN
    // 单次调用：返回的 T_Arg 含 eType / cbLen / pData，可立即喂给 F_PutInArg
    argDescriptor := F_BOOL(xLevelOk);
    bPackArg := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：把 `BOOL` 业务量（布尔位）作为可变参数喂给 `Tc3_EventLogger`、`Tc2_System.FB_FormatString2`、`Tc2_System.ADSWRITE` 等下游消费者；或者用作 ADS Notification 自定义消息的字段打包。
- **价值**：ST 无 variadic args 的"原罪"由 `T_Arg` + `F_<TYPE>` 系列彻底掩盖。调用方写 `F_PutInArg(F_INT(n), ...)` 就像写 C 的 `printf("%d", n)`；不用自己维护类型标签 / 长度 / 指针三件套。
- **替代方案对比**：
  - 手写 `arg.eType := ...; arg.cbLen := SIZEOF(...); arg.pData := ADR(...);`：能用，三行写三遍容易错（cbLen 漏改、eType 选错）。
  - 直接传指针 `ADR(x)` 给下游：下游不知道类型 / 长度，需要额外通道告知，破坏了 `T_Arg` 抽象。
  - **本函数**：一行调用、类型枚举自动选对、长度自动填、与 `F_PutInArg` 链式调用最干净。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.10.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35259915.html
- **相关 FC**：`F_PutInArg`（把 `T_Arg` 串入 `T_ArgList`）、`F_ARGCPY`（拷贝 `T_Arg` 含数据快照）、`F_ARGCMP`（两个 `T_Arg` 比较）、`F_ARGISZERO`（检查 `T_Arg` 是否被初始化）、`P<TYPE>_TO_<TYPE>`（反向，指针→值）
