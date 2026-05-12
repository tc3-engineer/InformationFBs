# FILETIME64_TO_DT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Time functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/10501013003.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FILETIME64_TO_DT.xml`](../examples/P_Demo_FILETIME64_TO_DT.xml) |

---

## 1. 功能简述

把 64 位 `T_FILETIME64`（100 纳秒精度，1601 起算）转换为 PLC 的 `DT`（DATE_AND_TIME，秒精度，1970 起算）。`DT` 范围有限（`DT#1970-01-01-00:00:00` ~ `DT#2106-02-06-06:28:15`），超出范围的 `T_FILETIME64` 不能正确表示；毫秒部分被向下取整丢弃。

## 2. 接口定义

### 函数声明

```iecst
FUNCTION FILETIME64_TO_DT : DT
VAR_INPUT
    fileTime : T_FILETIME64;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `fileTime` | `T_FILETIME64` | 待转换的 `T_FILETIME64` 时间 |

### 返回值

`DT` —— 见 §3 行为说明。

### VAR_IN_OUT

无。

## 3. 行为说明

`T_FILETIME64` 基准是 1601-01-01 UTC、单位 100ns；`DT` 基准是 1970-01-01 UTC、单位秒。本函数按这两条规则反向换算：

1. 减去基准偏移 (1970 - 1601 = 369 年 = 11644473600 秒 × 10⁷ = 116444736000000000 个 100ns 单位)
2. 除以 10⁷ 把 100ns 折算成秒
3. 结果赋给 `DT`（向下取整，丢弃毫秒）

`DT` 上限大约 2106-02-06 06:28:15（`UDINT` 表达的秒数 4294967295 上界）。

函数纯计算、无错误码——超界输入会得到截断 / 溢出后的 `DT` 值，调用方需自行确保输入在有效范围。

## 4. 错误码 / 返回值

返回类型 `DT`。函数无错误码 / 无 HRESULT；任意合法类型输入都有定义良好的返回值。详细边界与失败行为见 §5。

## 5. 使用注意 / 常见坑

- **毫秒被丢弃**：`T_FILETIME64` 的 100ns 精度在 `DT` 里完全丢失；需要保留毫秒请用 `FILETIME64_TO_SYSTEMTIME`（结果是 `TIMESTRUCT`，有 wMilliseconds）。
- **2106 年上界**：`DT` 是 32-bit unsigned seconds since 1970，2106-02-06 06:28:15 是绝对上限，之后不能正确表达（与 Unix Y2038 类似的问题）。
- **版本要求 ≥ 3.3.44.0**：旧版 Tc2_Utilities 没有 `_64` 后缀类型，要么升库要么用 legacy `FILETIME_TO_DT`。
- **和 `DT_TO_FILETIME64` 互逆**：先 DT_TO_FILETIME64 再 FILETIME64_TO_DT 应得到相同 `DT`（前提是输入 DT 在有效范围）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FILETIME64_TO_DT.xml`](../examples/P_Demo_FILETIME64_TO_DT.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
timeAsDT := FILETIME64_TO_DT(timeAsFileTime);
```

完整可导入例程见上方链接，里面有 场景 / 价值 / 验证步骤 三件套注释。

## 7. 业务场景与实际价值

- **场景**：Windows 日志 / OPC UA 节点送回的时间戳是 `T_FILETIME64`（或可换算到），PLC 内部业务逻辑用 `DT` 比较 / 显示更方便（直接 `>`、`<`、`-` 算时间差）。
- **价值**：1 行调用完成基准换算 + 单位换算；手写要小心 116444736000000000 这个常量不能算错（19 位整数易笔误）。
- **替代方案对比**：手写常量减法 + 单位除法（易出错）/ 走 `FILETIME64_TO_SYSTEMTIME` + `SYSTEMTIME_TO_DT`（多 1 步）/ 调用本 FC（推荐）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.1.12
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/10501013003.html
- **相关函数**：见 [`Tc2_Utilities README`](../README.md)（同类 time functions）
