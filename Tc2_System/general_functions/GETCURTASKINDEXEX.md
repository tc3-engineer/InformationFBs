# GETCURTASKINDEXEX

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `General functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31018507.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_GETCURTASKINDEXEX.xml`](../examples/P_Demo_GETCURTASKINDEXEX.xml) |

---

## 1. 功能简述

GETCURTASKINDEXEX 返回当前调用任务的索引：`-1` = Windows 上下文（非实时）、`0` = 实时上下文但非循环 PLC 任务（如 `FB_init` 初始化）、`1..n` = 循环 PLC 任务索引。比老版 `GETCURTASKINDEX` 多一层 Windows / 非循环上下文识别能力。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**返回值三态**：

- `-1`：Windows 上下文调用（如 HMI 写入触发的 PLC 函数、非实时线程）。
- `0`：实时上下文但**非**循环 PLC 任务——典型场景是 `FB_init` 方法的自动调用、初始化阶段。
- `1..n`：当前循环 PLC 任务的索引（与 SYSTEM 节点里的任务编号一致）。

**典型用法**：写库代码时根据上下文做不同行为——例如初始化阶段（返回 0）跳过实时校验，循环任务里才执行业务。HMI 触发的同步 PLC 函数（通过 ADS 进入 PLC 上下文）会返回 -1，业务可借此识别『不是我自己循环里调的』。

**与 `GETCURTASKINDEX` 区别**：老版 `GETCURTASKINDEX`（功能块，3.1.7 节）只返回循环任务索引 1..n，无法区分 Windows / FB_init 上下文，被本函数取代。新工程优先用本函数。

**实时性**：函数调用本身开销几十纳秒，可以放心在 PLC 循环里调用。

## 4. 错误码 / 返回值

本函数返回 `DINT`：`-1` Windows、`0` 实时非循环、`1..n` 循环任务索引。

## 5. 使用注意 / 常见坑

- **`-1` 不等于错误**：是 Windows 上下文的合法返回值，业务侧要明确区分。
- **`0` 不等于『任务 0』**：是『非循环实时上下文』的标记，与 `F_GetCpuCoreIndex(0)` 的『0 = 自身』语义不同。
- **频繁调用开销**：实时性敏感的循环里限频调用。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_GETCURTASKINDEXEX.xml`](../examples/P_Demo_GETCURTASKINDEXEX.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：编写通用库时根据上下文决定行为：`FB_init` 里返回 0 时跳过 ADS 调用（ADS 在 init 阶段不可用），循环任务里才发 ADS。
- **价值**：替代盲调用导致初始化阶段崩溃。
- **替代方案对比**：
  - 用 `GETCURTASKINDEX` 老版：分不清 -1 / 0。
  - 自己加 `bInited` 标志：可行但要状态机。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.1.18
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31018507.html
- **相关 FB / FC**：`F_GetCpuCoreIndex`, `F_GetTaskInfo`
