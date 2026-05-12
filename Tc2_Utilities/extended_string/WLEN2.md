# WLEN2

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483045003.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_WLEN2.xml`](../examples/P_Demo_WLEN2.xml) |

---

## 1. 功能简述

`LEN2` 的 WSTRING 版本——返回 WSTRING 字符数（任意长度）。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pWSTRING : POINTER TO WSTRING;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pWSTRING` | `POINTER TO WSTRING` | — | WSTRING 地址。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `UDINT` | WSTRING 字符数（不含 null 终结符）。 |

## 3. 行为说明

函数无状态、立即返回。算法：从 `pWSTRING` 起始逐 16 位字符读取，遇到 16 位 null（0x0000）停止；返回扫过的字符数（**不含 null 终结符**）。本质等同 C 的 `wcslen`，但内置上限 `Parameterlist.cMaxCharacters` 防止 null 缺失导致的死循环（默认上限约 1M 字符）。返回值是字符数，不是字节数——字节数 = 字符数 × 2（不含 null）或 (字符数 + 1) × 2（含 null）。本函数针对 WSTRING（UTF-16），BMP 外字符（代理对）按 PDF 未明确细节，假设按 2 字符计；建议仅在 BMP 范围内使用。`Tc2_Standard.WLEN` 限 255 字符上限，本函数无限制，是处理 `WSTRING(1024+)` 的标配。

## 4. 错误码 / 返回值

返回 `UDINT`：WSTRING 字符数（不含 null 终结符）。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- **字符数不是字节数**——字节数 = 字符数 × 2。
- **接受指针**：`WLEN2(ADR(ws))`。
- BMP 外字符（代理对）计为 2 个字符（PDF 未明确处理 ⚠️）。
- `Tc2_Standard.WLEN` 限 255 字符——长串必须用 `WLEN2`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WLEN2.xml`](../examples/P_Demo_WLEN2.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：HMI WSTRING 缓冲已写入字符数统计；下一次 `WCONCAT2` 的偏移计算。
- **价值**：`Tc2_Standard.WLEN` 限 255；本函数无限制。
- **替代方案对比**：`LEN2`：STRING 版本；`UTF8Len`：UTF-8 版本。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.26 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483045003.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
