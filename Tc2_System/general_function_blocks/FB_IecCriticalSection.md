# FB_IecCriticalSection

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `General function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/9007201580758155.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_IecCriticalSection.TcPOU`](../examples/P_Demo_FB_IecCriticalSection.TcPOU) |

---

## 1. 功能简述

FB_IecCriticalSection 把多任务对共享变量的修改序列化为「关键段（critical section）」。通过方法 `Enter()` 进入、`Leave()` 退出，保证同一时刻只有一个 PLC 任务持有该段。其他任务调用 `Enter()` 时被 TwinCAT 调度器以无忙等方式挂起，直到段被释放后按优先级顺序进入。常用于多任务读写同一全局结构体、缓冲区、文件句柄的场景。

## 2. 接口定义

### VAR_INPUT

```iecst
(* 本 FB 没有 VAR_INPUT；操作通过两个方法完成 *)
METHOD Enter : BOOL
METHOD Leave : BOOL
```

无 VAR_INPUT。

### VAR_OUTPUT

```iecst
(* 本 FB 没有 VAR_OUTPUT *)
```

无 VAR_OUTPUT。

### VAR_IN_OUT

无。本 FB 通过 `Enter()` 与 `Leave()` 方法操作，没有 VAR_INPUT / VAR_OUTPUT 引脚。

## 3. 行为说明

**实例化要求**：被保护的共享对象对应一个 FB_IecCriticalSection 实例，且必须声明在全局变量（`VAR_GLOBAL`）里让所有竞争任务能看见同一把锁；声明在某任务局部变量里等于没锁。

**Enter() 语义**：返回 TRUE 时已成功占有关键段，调用方可以放心读写共享数据；返回 FALSE 表示运行时不支持本 FB（旧版本 Windows CE 或更早 TwinCAT 版本），或另一任务停在断点导致调度器决定不阻塞当前任务以保证 I/O 刷新。`Enter()` 阻塞过程不消耗 CPU（非忙等），低优先级任务等待时其他任务仍可被调度。

**Leave() 语义**：必须在退出关键段时调用，否则等待任务永久阻塞。返回 TRUE 表示释放成功；返回 FALSE 表示运行时不支持或当前任务未通过 `Enter()` 占有过该段，属编程错误。

**陷阱**：关键段内代码必须尽量短，否则等待任务被拖到周期超限；Windows CE 要 TwinCAT v3.1.4022.29 及以后；优先于 `TestAndSet()`：后者无阻塞但可能整周期无法进入关键段。

## 4. 错误码 / 返回值

`Enter()` / `Leave()` 返回 `BOOL`：TRUE = 成功，FALSE = 运行时不支持或调用上下文错误（见行为说明）。本 FB 无独立错误码字段。

## 5. 使用注意 / 常见坑

- 实例必须是全局变量，否则多个任务各有一把锁等于没锁。
- 关键段内代码必须短小，否则会拖累等待任务的周期。
- Windows CE 要求 TwinCAT >= 3.1.4022.29；旧版本两个方法直接返回 FALSE，多任务保护失效。
- `Enter()` 与 `Leave()` 必须严格配对；建议用 `IF fbCS.Enter() THEN ... fbCS.Leave(); END_IF;` 而非提前 RETURN 跳过 `Leave()`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_IecCriticalSection.TcPOU`](../examples/P_Demo_FB_IecCriticalSection.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：1 ms 周期的快速运动控制任务和 10 ms 周期的通讯任务同时读写同一个轨迹缓冲 `arrTrajectoryBuf`；不加锁时通讯任务写到一半运动任务切入读会拿到半新半旧数据导致执行畸变。
- **价值**：在读写两侧各自包一层 `Enter()/Leave()`，由调度器保证原子访问；替代手写 `WHILE bLock DO END_WHILE` 忙等待方案，省 CPU 且不会饥饿低优先级任务。
- **替代方案对比**：`TestAndSet`（同库）只是单次试锁，未拿到锁就返回 FALSE 要应用层重试；本 FB 的 `Enter()` 在锁未到时主动让出 CPU，是 Beckhoff 推荐的首选。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/9007201580758155.html
- **相关 FB / FC**：`TestAndSet`（非阻塞替代）
