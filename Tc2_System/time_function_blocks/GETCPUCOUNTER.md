# GETCPUCOUNTER

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Time function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/45035996304668939.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_GETCPUCOUNTER.xml`](../examples/P_Demo_GETCPUCOUNTER.xml) |

---

## 1. 功能简述

GETCPUCOUNTER 读取 64-bit CPU cycle counter。以 100 ns 为单位输出，独立于 CPU 内部时钟频率。本 FB 之所以是 FB 而非 FUNCTION，是因为要返回 2 个 UDINT 拼成 64 bit（IEC FUNCTION 只能返回单值）——`cpuCntLoDW` 是低 32 位、`cpuCntHiDW` 是高 32 位。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
(*none*)
END_VAR
```

无 VAR_INPUT。

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    cpuCntLoDW : UDINT;
    cpuCntHiDW : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `cpuCntLoDW` | `UDINT` | 64-bit 计数值的低 32 位。单位 100 ns。 |
| `cpuCntHiDW` | `UDINT` | 64-bit 计数值的高 32 位。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用语义**：调用即出值。返回的 64-bit 计数器随墙钟时间持续递增（与 `GETCPUACCOUNT` 不同——`GETCPUACCOUNT` 只在任务被调度时增长）。

**关键性质**：64-bit 计数器以 100 ns 为单位约 58 万年才回卷，工程上等同永不回卷；适合做长时间累计、跨任务时间戳标定、记录工件流转的时间戳。

**拼成 64-bit**：典型代码：
```iecst
fbCntr();
ulCntr64 := SHL(TO_ULINT(fbCntr.cpuCntHiDW), 32) OR TO_ULINT(fbCntr.cpuCntLoDW);
```
之后 `ulCntr64` 可减法做 100 ns 精度长间隔时间差。

**典型用法**：(1) 工件在产线各工位的精确时间戳；(2) 长任务（>429 s）的耗时测量（GETCPUACCOUNT 不够用）；(3) 跨任务事件时序对比。

**陷阱**：单独读 `cpuCntLoDW` 和 `cpuCntHiDW` 在低位回卷瞬间高位可能尚未更新，应做一次重读保护；或者每次都同一调用同时读两个输出（本 FB 设计本身已经保证同步刷新）。

## 4. 错误码 / 返回值

本 FB 不暴露错误输出。两个输出始终为当前 64-bit 计数器的低/高 32 位。

## 5. 使用注意 / 常见坑

- 拼 64-bit 时建议用 `SHL(TO_ULINT(hi), 32) OR TO_ULINT(lo)` 模式，避免直接 `lo + hi*2^32` 引入精度损失。（工程经验补充）
- 本 FB 给的是墙钟 CPU 时间，包含任务被高优先级抢占的等待时间；想计任务 CPU 执行时长用 `GETCPUACCOUNT`。
- 返回值代表系统启动以来 100 ns 数；不要把它当成 UTC 时间戳，那是 `F_GetSystemTime` 的活。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_GETCPUCOUNTER.xml`](../examples/P_Demo_GETCPUCOUNTER.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：包装线给每个工件打 100 ns 精度时间戳写入 MES，用于事后分析瓶颈工位耗时；24 h 连续运行用 64-bit 计数器无回卷。
- **价值**：替代用 `F_GetSystemTime`（系统时间，跨 NTP 同步会跳变）；CPU 计数器单调递增不受 NTP 影响。
- **替代方案对比**：`F_GetSystemTime` 适合人类时间戳；`GETCPUACCOUNT` 32-bit 太短；本 FB 长时间精确计时首选。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.7.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/45035996304668939.html
- **相关 FB / FC**：`GETCPUACCOUNT`（任务内 32-bit 计数）、`F_GetSystemTime`
