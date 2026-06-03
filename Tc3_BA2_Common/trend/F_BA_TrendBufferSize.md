# F_BA_TrendBufferSize

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION` |
| Category | `Functions / Types / Trend` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785580811.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_BA_TrendBufferSize.TcPOU`](../examples/P_Demo_F_BA_TrendBufferSize.TcPOU) |

---

## 1. 功能简述

根据采样间隔、保留时长、值类型计算趋势缓冲区所需的字节数。返回 UDINT。用于"按目标存储时长反算环形缓冲区大小"的容量规划。

## 2. 接口定义

### 完整声明

```iecst
FUNCTION F_BA_TrendBufferSize : DINT
VAR_IN_OUT
  aBuffer    : ARRAY [*] OF ST_BA_TrendEntry;
END_VAR
```

### VAR_IN_OUT 引脚

| 名称 | 类型 | 说明 |
|---|---|---|
| `aBuffer` | `ARRAY [*] OF ST_BA_TrendEntry` | 趋势数据缓冲数组（用 `ARRAY[*]` 接受任意定长）。本 FC 计算该数组应该开多大才够装 `tRetentionTime` 时长。 |


## 3. 行为说明

根据采样间隔、保留时长、值类型计算趋势缓冲区所需的字节数。返回 UDINT。用于"按目标存储时长反算环形缓冲区大小"的容量规划。 双向（IN_OUT）引脚：`aBuffer`，必须在调用方持有变量地址（不能传字面量）。 本 FC 是 *无状态* 的纯函数：每次调用独立计算结果，不维护任何内部历史；多任务 / 多线程调用安全；可在 PRG / FB / METHOD / 表达式中任意位置使用。 典型工程场景："温度趋势保留 7 天、每分钟采一次"——本 FC 算出需要分配多大的 `ARRAY OF ST_BA_TrendEntry` 缓冲。

## 4. 错误码 / 返回值

本 FC 返回类型为 `DINT`。

本 FC 返回 `DINT`：负值表示判定结果偏小、正值表示偏大、0 表示相等 / 无差异。具体语义按 §1 功能简述。

## 5. 使用注意 / 常见坑

- 调用前必须确认 `Tc3_BA2_Common` 库已 reference（版本 ≥ 1.0.2）。
- FC 类无状态，多线程 / 多 task 调用安全；GVL 是常量集合，运行时只读。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_BA_TrendBufferSize.TcPOU`](../examples/P_Demo_F_BA_TrendBufferSize.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**："温度趋势保留 7 天、每分钟采一次"——本 FC 算出需要分配多大的 `ARRAY OF ST_BA_TrendEntry` 缓冲。
- **价值**：替代手算 `7 * 24 * 60 * SIZEOF(ST_BA_TrendEntry)`；FC 内部考虑了带 event 标记的额外字段开销。
- **替代方案对比**：手算公式，易漏 ST_BA_TrendEntryEvent 的额外字段（与本 FC/GVL 相比，体现统一化 / 跨平台正确性 / 代码量节省等优势）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.1.3.6.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785580811.html
- **相关枚举 / 结构**：见 PDF §4.1（DUTs）
