# DRAND

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `General function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30956427.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_DRAND.xml`](../examples/P_Demo_DRAND.xml) |

---

## 1. 功能简述

DRAND 生成一个 LREAL 类型的伪随机数。输入 INT 类型的种子 `Seed` 决定序列起点，输出 `Num` 是 `0.0 ... 1.0` 区间内的双精度浮点数。同一个 `Seed` 在不同会话中产生完全相同的序列，便于做可重现的离线仿真。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    Seed : INT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `Seed` | `INT` | - | 伪随机序列的初始种子。相同种子在不同会话中产生完全相同的序列，便于做可重现的离线仿真。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Num : LREAL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Num` | `LREAL` | 返回 `0.0 ... 1.0` 区间内的双精度伪随机数。内部线性同余发生器周期为 1075 个不同值。 |

### VAR_IN_OUT

无。

## 3. 行为说明

DRAND 是同步执行：每次被调用时立即根据当前内部状态推进一步并把结果写到 `Num`，没有 busy / done 流程，也无错误码。

种子 `Seed` 的语义类似 C 标准库 `srand()`：在第一次调用或种子值发生变化时被采纳为新的起点，之后每次调用按内部线性同余递推。如果业务需要不同 PLC 启动得到完全一致的随机数序列（例如做单元回归测试），每次都用相同 `Seed` 即可；如果需要每次启动不同序列，可用 `F_GetSystemTime()` 的低位作为种子。

生成的浮点数近似在 `[0.0, 1.0]` 区间均匀分布，但发生器内部只有约 1075 个不同状态值（PDF 描述），对密码学敏感场景（密钥生成、安全令牌）不可用；对仿真、压测、随机化定时等工程用途足够。

## 4. 错误码 / 返回值

本 FB 不暴露错误输出。`Num` 始终落在 `[0.0, 1.0]` 之间，使用方无需做范围判断。

## 5. 使用注意 / 常见坑

- 周期较短（约 1075 个不同状态），不能用于密码学随机性要求的场合。
- 把 `LREAL` 折算到整数区间时建议用 `TO_DINT(Num * TO_LREAL(nMax - nMin + 1)) + nMin`，避免边界溢出到 `nMax + 1`。（工程经验补充）
- 如果在多任务中各自实例化但用同一种子，多个实例的序列会同步，掩盖真实并发问题；不同任务应使用不同种子。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DRAND.xml`](../examples/P_Demo_DRAND.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：调试分拣线时需要给虚拟物料赋随机重量（300~500 g）做下游分流逻辑压力测试。不接真实秤的情况下用 DRAND 把每包重量随机化，但同一种子保证每次启动 PLC 都能复现完全相同的测试序列。
- **价值**：替代手写线性同余发生器（5~10 行容易写错系数）或借助上位机注入数据，一行调用即出值；同种子可复现，方便和上一轮调试结果做 diff。
- **替代方案对比**：手写 LCG 风险高；`F_GetSystemTime` 取时间戳做随机源不能保证均匀分布；DRAND 自带均匀分布 + 可控种子，是工程首选。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30956427.html
- **相关 FB / FC**：`F_GetSystemTime`（用时间戳作为不可重复的种子）
