# F_BA_MemSetEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION` |
| Category | `Functions / Memory` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785290891.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_BA_MemSetEx.TcPOU`](../examples/P_Demo_F_BA_MemSetEx.TcPOU) |

---

## 1. 功能简述

把 `xValue` 重复填充到 `pDestAddr` 起始、长度 `nDestSize` 的内存区。前提：`nDestSize` 必须是 `xValue.diSize` 的整数倍——否则不填充并返回 0。返回 UDINT = 实际拷贝的字节数。

## 2. 接口定义

### 完整声明

```iecst
FUNCTION F_BA_MemSetEx : UDINT
VAR_INPUT
  pDestAddr    : PVOID;
  nDestSize    : UDINT;
  xValue       : ANY;
END_VAR
```

### VAR_INPUT 引脚

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `pDestAddr` | `PVOID` | - | 填充区域的目标地址. |
| `nDestSize` | `UDINT` | - | 填充区域的尺寸. |
| `xValue` | `ANY` | - | 填充值 |

### VAR_IN_OUT

无。


## 3. 行为说明

把 `xValue` 重复填充到 `pDestAddr` 起始、长度 `nDestSize` 的内存区。前提：`nDestSize` 必须是 `xValue.diSize` 的整数倍——否则不填充并返回 0。返回 UDINT = 实际拷贝的字节数。 接入参数：`pDestAddr`, `nDestSize`, `xValue`。每个参数的类型与默认值见 §2 接口定义。 本 FC 是 *无状态* 的纯函数：每次调用独立计算结果，不维护任何内部历史；多任务 / 多线程调用安全；可在 PRG / FB / METHOD / 表达式中任意位置使用。 指针类 FC 跨 x86 / x64 平台自动选用 UDINT / ULINT 做地址算术；调用方仍需保证指针不空、目标内存区可访问，越界访问会触发 PLC Exception。 典型工程场景：把一段 INT 数组全部初始化为 -1（每个 INT 2 字节，重复 N 次填满）。

## 4. 错误码 / 返回值

本 FC 返回类型为 `UDINT`。

本 FC 返回 `UDINT`：通常 0 = 失败 / 无结果，> 0 = 成功 / 实际值。具体语义见 §1 功能简述。

## 5. 使用注意 / 常见坑

- 调用前必须确认 `Tc3_BA2_Common` 库已 reference（版本 ≥ 1.0.2）。
- FC 类无状态，多线程 / 多 task 调用安全；GVL 是常量集合，运行时只读。
- 指针类 FC 内部已处理 x86 / x64 平台差异——但调用方提供的指针仍需保证有效；空指针 / 越界会触发 PLC Exception。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_BA_MemSetEx.TcPOU`](../examples/P_Demo_F_BA_MemSetEx.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：把一段 INT 数组全部初始化为 -1（每个 INT 2 字节，重复 N 次填满）。
- **价值**：比手写 FOR 循环填充更高效（FB 内部调 MEMCPY，可能向量化）；自带尺寸校验。
- **替代方案对比**：`FOR i := 0 TO (nDestSize / SIZEOF(xValue)) - 1 DO MEMCPY(pDestAddr + i * SIZEOF(xValue), ADR(xValue), SIZEOF(xValue)); END_FOR;` 约 3 行（与本 FC/GVL 相比，体现统一化 / 跨平台正确性 / 代码量节省等优势）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.1.2.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785290891.html
- **相关枚举 / 结构**：见 PDF §4.1（DUTs）
