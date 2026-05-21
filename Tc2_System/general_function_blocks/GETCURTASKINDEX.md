# GETCURTASKINDEX

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `General function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30957963.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_GETCURTASKINDEX.xml`](../examples/P_Demo_GETCURTASKINDEX.xml) |

---

## 1. 功能简述

GETCURTASKINDEX 返回当前调用所在任务的索引（1..4）。**注意：本 FB 已过时**，建议改用 `GETCURTASKINDEXEX()` 函数。差别是 EX 版本能区分实时上下文（如 `FB_init` 初始化阶段）与周期 PLC 任务上下文。

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
    index : BYTE;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `index` | `BYTE` | 返回调用方任务的索引（取值 `1..4`）。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用语义**：调用即出值，无 busy / done 流程，无错误码。返回值 `index` 是 1..4 之间的整数，对应 TwinCAT 项目里 PLC Tasks 节点下任务的注册顺序。

**Outdated 警告**：本 FB 在 PDF 与 InfoSys 中都被明确标为「过时」，建议改用函数 `GETCURTASKINDEXEX()`。两者主要差别：(1) `FB_init` 方法在系统初始化阶段被自动调用，此时不在任何周期 PLC 任务上下文中——`GETCURTASKINDEX` 在这种实时初始化上下文中行为定义不清晰；`GETCURTASKINDEXEX` 在此场景会返回明确的『非任务上下文』指示。(2) `EX` 版本是函数（FUNCTION）而非功能块，无需实例化。

**典型用法**：在通用工具 FB 中根据当前任务索引选择全局缓冲区下标（每任务一份缓冲避免锁）；或在多任务部署的库代码中做日志打标方便排查问题任务。新代码应一律改用 `GETCURTASKINDEXEX`。

## 4. 错误码 / 返回值

本 FB 无错误输出。在合法上下文返回 `1..4`；在非任务上下文（如 FB_init）行为未定义——这也正是被 EX 版本取代的原因。

## 5. 使用注意 / 常见坑

- **Outdated**：新代码应改用 `GETCURTASKINDEXEX()` 函数；本 FB 仅保留兼容历史项目。
- 返回值范围 1..4 假设项目中最多 4 个 PLC 任务，超过会失效；现代项目多任务部署应直接用 EX 版本。
- 在 `FB_init` 等初始化上下文里调用结果不可靠。（PDF 与 InfoSys 一致警告）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_GETCURTASKINDEX.xml`](../examples/P_Demo_GETCURTASKINDEX.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：维护一个 8 年前的老项目，要在不大改架构的前提下读出当前任务索引做日志染色。
- **价值**：本 FB 是老项目用法，保留兼容；新项目一律用 `GETCURTASKINDEXEX`。
- **替代方案对比**：`GETCURTASKINDEXEX()`（函数）是首选；本 FB 仅在不想动老代码声明区时保留。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.1.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30957963.html
- **相关 FB / FC**：`GETCURTASKINDEXEX`（推荐替代）
