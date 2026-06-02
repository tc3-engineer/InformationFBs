# TestAndSet

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `General functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31023115.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_TestAndSet.TcPOU`](../examples/P_Demo_TestAndSet.TcPOU) |

---

## 1. 功能简述

TestAndSet 是一个原子操作：检查 BOOL 标志 `Flag` 是否为 FALSE；若是，把它设为 TRUE 并返回 TRUE（拿到锁）；若已经是 TRUE，直接返回 FALSE（锁已被占）。整个操作不会被其他任务打断，可实现轻量级信号量 / 互斥锁，用于多任务共享数据保护。

## 2. 接口定义

### VAR_INPUT

无（本函数仅一个 `VAR_IN_OUT` 参数）。

### VAR_OUTPUT

无（结果通过 `BOOL` 返回值传出，见 §4）。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Flag : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Flag` | `BOOL` | 要原子测试并置位的 BOOL 标志（必须是变量引用，不能是表达式）。`FALSE` = 空闲、可被占；`TRUE` = 已被占。调用后若返回 `TRUE`，本函数已将 `Flag` 由 `FALSE` 置为 `TRUE`（拿到锁）；若返回 `FALSE`，`Flag` 已是 `TRUE` 保持不变（锁已被别人持有）。 |

## 3. 行为说明

**原子语义**：本函数在硬件层面用 CPU 原子指令实现，保证『读 → 比 → 写』三步不可中断。多任务同时调用时仅一个能拿到锁。

**典型用法**：临界区保护——拿锁 → 操作共享数据 → 还锁（手动 `Flag := FALSE;`）。

**`Flag` 是 `VAR_IN_OUT`**：必须传一个实际变量（通常 `VAR_GLOBAL`），不能传表达式。

**与信号量的关系**：本函数是『一次性锁』，不带计数；要实现可重入或计数信号量需要自己封装。

**释放是普通赋值**：业务侧主动 `myFlag := FALSE` 即释放锁，**无对应的『TestAndClear』**。

## 4. 错误码 / 返回值

本函数返回 `BOOL`，**两个返回值都是正常控制流，没有"调用失败"语义**——业务侧必须把 `FALSE` 当成"锁被别人占了，本周期跳过"而不是错误：

| 返回值 | 含义 |
|---|---|
| `TRUE` | 调用前 `Flag = FALSE`（空闲），本函数已原子地把 `Flag` 置为 `TRUE`——**拿到锁**，可以进入临界区 |
| `FALSE` | 调用前 `Flag = TRUE`（已被别人占），`Flag` 保持不变——**没拿到锁**，本周期请跳过临界区，下次再试（典型 mutex 竞争路径，**非错误**） |

## 5. 使用注意 / 常见坑

- **忘记释放锁导致死锁**：拿了锁不还，其他任务永远拿不到。建议把 `TestAndSet` + 临界操作 + `Flag := FALSE` 放在一个 IF 块里，避免 RETURN / 异常路径漏掉释放。
- **非可重入**：同一任务再次拿同一锁会返回 FALSE（自己锁自己），不像 Windows CriticalSection。
- **不能跨 PLC**：仅本地 CPU 内有效，跨 PLC 共享变量请用 ADS 锁或文件锁。
- **长时间持锁损害实时性**：临界区代码要短小，长时间持锁会阻塞其他任务。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_TestAndSet.TcPOU`](../examples/P_Demo_TestAndSet.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：MAIN 任务（1 ms 周期）和 SLOW 任务（100 ms 周期）共享一个工艺参数结构体；用 `TestAndSet` 保护更新过程，防止 SLOW 任务读到 MAIN 写一半的脏数据。
- **价值**：替代关中断 / 禁任务调度；比 `__SLEEP` 节省 CPU。
- **替代方案对比**：
  - 关中断：影响 OS 调度。
  - 双缓冲 + 原子指针交换：性能更好但代码复杂。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.1.20
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31023115.html
