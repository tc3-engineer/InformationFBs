# F_BA_GetUsedEntryCount

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION` |
| Category | `Functions / Memory` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785287051.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_BA_GetUsedEntryCount.TcPOU`](../examples/P_Demo_F_BA_GetUsedEntryCount.TcPOU) |

---

## 1. 功能简述

在 ARRAY 中扫描查找第一个等于"未使用标记值 `xUnusedVal`"的元素，返回从下界 `nLowerBound` 起到达该位置前的元素数。元素步长由 `xUnusedVal` 的字节大小决定。`pArray = 0` 或 `xUnusedVal.diSize = 0` 时返回 0。

## 2. 接口定义

### 完整声明

```iecst
FUNCTION F_BA_GetUsedEntryCount : DINT
VAR_INPUT
  pArray         : PVOID;
  nLowerBound    : DINT;
  nUpperBound    : DINT;
  xUnusedVal     : ANY;
END_VAR
```

### VAR_INPUT 引脚

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `pArray` | `PVOID` | - | 指向数组所在内存区起始的指针 to be examined is located. |
| `nLowerBound` | `DINT` | - | 数组下界. |
| `nUpperBound` | `DINT` | - | 数组上界. |
| `xUnusedVal` | `ANY` | - | 元素值等于此处指定值时被视为"未使用", it is considered "unused". |

### VAR_IN_OUT

无。


## 3. 行为说明

在 ARRAY 中扫描查找第一个等于"未使用标记值 `xUnusedVal`"的元素，返回从下界 `nLowerBound` 起到达该位置前的元素数。元素步长由 `xUnusedVal` 的字节大小决定。`pArray = 0` 或 `xUnusedVal.diSize = 0` 时返回 0。 接入参数：`pArray`, `nLowerBound`, `nUpperBound`, `xUnusedVal`。每个参数的类型与默认值见 §2 接口定义。 本 FC 是 *无状态* 的纯函数：每次调用独立计算结果，不维护任何内部历史；多任务 / 多线程调用安全；可在 PRG / FB / METHOD / 表达式中任意位置使用。 典型工程场景：动态数组类容器（如调度条目数组）每槽位有"未用 = 0xFF"约定；本 FC 一行得到当前已用槽位数。

## 4. 错误码 / 返回值

本 FC 返回类型为 `DINT`。

本 FC 返回 `DINT`：负值表示判定结果偏小、正值表示偏大、0 表示相等 / 无差异。具体语义按 §1 功能简述。

## 5. 使用注意 / 常见坑

- 调用前必须确认 `Tc3_BA2_Common` 库已 reference（版本 ≥ 1.0.2）。
- FC 类无状态，多线程 / 多 task 调用安全；GVL 是常量集合，运行时只读。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_BA_GetUsedEntryCount.TcPOU`](../examples/P_Demo_F_BA_GetUsedEntryCount.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：动态数组类容器（如调度条目数组）每槽位有"未用 = 0xFF"约定；本 FC 一行得到当前已用槽位数。
- **价值**：一行调用替代 FOR 循环扫描，且自动按 ANY 类型尺寸适配（不用手写不同类型不同步长的循环）。
- **替代方案对比**：`FOR i := nLowerBound TO nUpperBound DO IF arr[i] = unusedVal THEN EXIT; END_IF; END_FOR; cnt := i - nLowerBound;` 约 5 行（与本 FC/GVL 相比，体现统一化 / 跨平台正确性 / 代码量节省等优势）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.1.2.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785287051.html
- **相关枚举 / 结构**：见 PDF §4.1（DUTs）
