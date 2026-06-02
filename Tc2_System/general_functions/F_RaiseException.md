# F_RaiseException

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `General functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/18097973515.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_RaiseException.TcPOU`](../examples/P_Demo_F_RaiseException.TcPOU) |

---

## 1. 功能简述

F_RaiseException 在 PLC 代码中主动抛出一个运行时异常，异常码由 `ExceptionCode`（来自 `__SYSTEM.ExceptionCode` 枚举或自定义 `UDINT`）指定。在 `__TRY` 块外抛会被 TwinCAT 异常处理捕获并停止 PLC；在 `__TRY` 内可被 `__CATCH` 捕获。用于实现自定义错误流程、断言失败、不可恢复错误中止。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    ExceptionCode : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `ExceptionCode` | `UDINT` | 异常码（`UDINT`）。可用 `__SYSTEM.ExceptionCode` 枚举或自定义 `UDINT` 值。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**`__TRY` 内 vs 外**：

- `__TRY` 块外抛出：异常进入 TwinCAT 全局异常处理，PLC 停止执行。
- `__TRY` 块内抛出：可在 `__CATCH(exc)` 块中捕获并处理，PLC 不停。

**异常码**：可用 `__SYSTEM.ExceptionCode` 枚举（如 `RTSEXCPT_DIVIDEBYZERO`），也可自定义 `UDINT` 值。

**典型用法**：在断言失败（如关键参数越界、状态机进入不可达分支）时主动抛异常，让 PLC 显式停在错误现场而不是隐蔽继续。

**控制流影响**：调用本函数后控制流立即转移到最近的 `__CATCH` 块或全局异常处理器；调用点之后的代码**不会执行**。所以本函数不需要返回值——它要么终止任务要么进入捕获块。

**与 IEC 11 标准的关系**：`__TRY` / `__CATCH` / `__FINALLY` / `__ENDTRY` 是 CODESYS / TwinCAT 拓展，不是 IEC 61131-3 标准，跨厂商不可移植。

## 4. 错误码 / 返回值

本函数无返回值（抛异常后控制流转移）。

## 5. 使用注意 / 常见坑

- **`__TRY` 外抛出会立刻停 PLC**：必须确保 demo / 测试代码包裹在 `__TRY` / `__CATCH` 里，否则一抛异常生产环境直接停机。
- **异常码冲突**：自定义码建议在高位段（如 `16#80000000+`）避免与 TwinCAT 内置 `__SYSTEM.ExceptionCode` 冲突。（工程经验补充）
- **捕获后状态恢复**：`__CATCH` 内可读 `__SYSTEM.LastException` 检查；处理完需主动恢复局部状态。（工程经验补充）
- **与 `bError` / `nErrId` 共存**：业务可恢复错误用 `bError`，不可恢复或编程错误才用本函数。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_RaiseException.TcPOU`](../examples/P_Demo_F_RaiseException.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：在状态机进入『不可能到达』的 default 分支时主动 `F_RaiseException`，让 PLC 显式停在现场，便于事后分析比静默继续更好。
- **价值**：替代 `printf` 日志 + 静默继续的弱断言；真正强制中止。
- **替代方案对比**：
  - `bError := TRUE` + 业务流程跳转：可恢复错误用这个。
  - `RETURN`：静默退出，调试难。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.1.12
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/18097973515.html
