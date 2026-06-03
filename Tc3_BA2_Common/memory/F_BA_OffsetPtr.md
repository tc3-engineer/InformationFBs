# F_BA_OffsetPtr

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_BA2_Common` |
| Library Version | `1.0.2` |
| Type | `FUNCTION` |
| Category | `Functions / Memory` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785292811.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_BA_OffsetPtr.TcPOU`](../examples/P_Demo_F_BA_OffsetPtr.TcPOU) |

---

## 1. 功能简述

把基地址 `pAddr` 加上偏移 `nOffset` 字节，返回新的 PVOID 指针。内部根据运行时平台（x64 或 x86）自动用 ULINT 或 UDINT 做加法，避免 32/64 位平台下的整数截断 bug。⚠️ PDF 函数名印刷为 `F_BA_OffestPtr`（少了 t），实际签名 `F_BA_OffsetPtr`。

## 2. 接口定义

### 完整声明

```iecst
FUNCTION F_BA_OffsetPtr : PVOID
VAR_INPUT
  pAddr      : PVOID;
  nOffset    : DINT;
END_VAR
```

### VAR_INPUT 引脚

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `pAddr` | `PVOID` | - | 基地址。 |
| `nOffset` | `DINT` | - | 偏移字节数。 |

### VAR_IN_OUT

无。


## 3. 行为说明

把基地址 `pAddr` 加上偏移 `nOffset` 字节，返回新的 PVOID 指针。内部根据运行时平台（x64 或 x86）自动用 ULINT 或 UDINT 做加法，避免 32/64 位平台下的整数截断 bug。⚠️ PDF 函数名印刷为 `F_BA_OffestPtr`（少了 t），实际签名 `F_BA_OffsetPtr`。 接入参数：`pAddr`, `nOffset`。每个参数的类型与默认值见 §2 接口定义。 本 FC 是 *无状态* 的纯函数：每次调用独立计算结果，不维护任何内部历史；多任务 / 多线程调用安全；可在 PRG / FB / METHOD / 表达式中任意位置使用。 指针类 FC 跨 x86 / x64 平台自动选用 UDINT / ULINT 做地址算术；调用方仍需保证指针不空、目标内存区可访问，越界访问会触发 PLC Exception。 典型工程场景：操作 RAW 数据缓冲（如总线帧）：拿到帧头指针后 +4 跳过 header 取 payload 指针。

## 4. 错误码 / 返回值

本 FC 返回类型为 `PVOID`。

本 FC 返回 `PVOID`：返回一个内存地址。`0` 表示失败 / 无效。

## 5. 使用注意 / 常见坑

- ⚠️ 本条目 PDF 存在印刷错误，已在 §1 功能简述中标注；编译器实际接受 InfoSys 写法。
- 调用前必须确认 `Tc3_BA2_Common` 库已 reference（版本 ≥ 1.0.2）。
- FC 类无状态，多线程 / 多 task 调用安全；GVL 是常量集合，运行时只读。
- 指针类 FC 内部已处理 x86 / x64 平台差异——但调用方提供的指针仍需保证有效；空指针 / 越界会触发 PLC Exception。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_BA_OffsetPtr.TcPOU`](../examples/P_Demo_F_BA_OffsetPtr.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：操作 RAW 数据缓冲（如总线帧）：拿到帧头指针后 +4 跳过 header 取 payload 指针。
- **价值**：跨 x86/x64 平台自动正确；手写 `pAddr + UDINT(nOffset)` 在 x64 上会把指针截断到 32 位 → 段错误。
- **替代方案对比**：`pNew := pAddr + nOffset;` —— x86 上能用，x64 上指针被截断造成 GPF（与本 FC/GVL 相比，体现统一化 / 跨平台正确性 / 代码量节省等优势）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc3_BA2_Common_EN.pdf) §4.3.1.2.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc3_ba2_common/10785292811.html
- **相关枚举 / 结构**：见 PDF §4.1（DUTs）
