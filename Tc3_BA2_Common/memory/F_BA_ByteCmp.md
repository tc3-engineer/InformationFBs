# F_BA_ByteCmp

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION` |
| Category | `Functions / Memory` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785176971.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_BA_ByteCmp.TcPOU`](../examples/P_Demo_F_BA_ByteCmp.TcPOU) |

---

## 1. 功能简述

把指定内存区（`pValue` 起始，长度 `nSize`）按字节与基准字节 `nCompare` 比较。返回 DINT：-1 表示发现某字节小于基准、+1 表示发现某字节大于基准、0 表示区内全部字节都等于基准。`pValue = 0` 或 `nSize = 0` 时直接返回 -1。

## 2. 接口定义

### 完整声明

```iecst
FUNCTION F_BA_ByteCmp : DINT
VAR_INPUT
  pValue    : PVOID;
  nSize     : UXINT;
  nCompare  : BYTE;
END_VAR
```

### VAR_INPUT 引脚

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `pValue` | `PVOID` | - | 指向被检查内存区起始的指针. |
| `nSize` | `UXINT` | - | 内存区长度. |
| `nCompare` | `BYTE` | - | 比较基准字节. |

### VAR_IN_OUT

无。


## 3. 行为说明

把指定内存区（`pValue` 起始，长度 `nSize`）按字节与基准字节 `nCompare` 比较。返回 DINT：-1 表示发现某字节小于基准、+1 表示发现某字节大于基准、0 表示区内全部字节都等于基准。`pValue = 0` 或 `nSize = 0` 时直接返回 -1。 接入参数：`pValue`, `nSize`, `nCompare`。每个参数的类型与默认值见 §2 接口定义。 本 FC 是 *无状态* 的纯函数：每次调用独立计算结果，不维护任何内部历史；多任务 / 多线程调用安全；可在 PRG / FB / METHOD / 表达式中任意位置使用。 典型工程场景：检查一段 buffer 是否全是 `0x00`（未初始化检测）或全是 `0xFF`（擦除标志位）。

## 4. 错误码 / 返回值

本 FC 返回类型为 `DINT`。

本 FC 返回 `DINT`：负值表示判定结果偏小、正值表示偏大、0 表示相等 / 无差异。具体语义按 §1 功能简述。

## 5. 使用注意 / 常见坑

- 调用前必须确认 `Tc3_BA2_Common` 库已 reference（版本 ≥ 1.0.2）。
- FC 类无状态，多线程 / 多 task 调用安全；GVL 是常量集合，运行时只读。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_BA_ByteCmp.TcPOU`](../examples/P_Demo_F_BA_ByteCmp.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：检查一段 buffer 是否全是 `0x00`（未初始化检测）或全是 `0xFF`（擦除标志位）。
- **价值**：比 `MEMCMP` 更轻量（不用第二个 buffer），适合"全 0 / 全 FF / 全单字节模式"快速判定。
- **替代方案对比**：`FOR i := 0 TO nSize-1 DO IF arr[i] <> nCompare THEN ... END_FOR;` 手写约 5 行（与本 FC/GVL 相比，体现统一化 / 跨平台正确性 / 代码量节省等优势）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.1.2.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785176971.html
- **相关枚举 / 结构**：见 PDF §4.1（DUTs）
