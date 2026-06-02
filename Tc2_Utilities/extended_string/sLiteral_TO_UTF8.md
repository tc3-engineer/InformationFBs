# sLiteral_TO_UTF8

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/5780471691.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_sLiteral_TO_UTF8.TcPOU`](../examples/P_Demo_sLiteral_TO_UTF8.TcPOU) |

---

## 1. 功能简述

把 `STRING` 字面量编译期编码为 UTF-8；专用于字面量赋值场景（如 `sUtf8 : STRING := sLiteral_TO_UTF8('Hühner legen Eier.')`），配合 `{attribute 'TcEncoding' := 'UTF-8'}` 注解使用。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

无（参见下方 `VAR_IN_OUT CONSTANT`）。

```iecst
VAR_IN_OUT CONSTANT
    sLiteral : STRING;
END_VAR
```

### VAR_IN_OUT (CONSTANT)

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `sLiteral` | `STRING` | 待编码的 STRING 字面量。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `STRING(511)` | 转换后的 UTF-8 字符串（写入 511 字节缓冲）；输入超长时返回空串。 |

## 3. 行为说明

本函数 **VAR_IN_OUT CONSTANT** 参数 `sLiteral : STRING`，意为传入的必须是**编译期常量字面量**，编译器据此生成 UTF-8 编码的字节序列写入返回缓冲。返回类型 `STRING(511)`——如果字面量 UTF-8 编码后超过 511 字节，返回空串；否则返回完整 UTF-8 内容。**典型用途是给带 TcEncoding 注解的 STRING 变量赋初值**：注解告诉编译器变量按 UTF-8 解释，本函数则负责把 STRING 字面量正确转码。

## 4. 错误码 / 返回值

返回 `STRING(511)`：转换后的 UTF-8 字符串（写入 511 字节缓冲）；输入超长时返回空串。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- **只用于字面量**（编译期常量），不是运行时变量。运行时 STRING → UTF-8 请用 `STRING_TO_UTF8`。
- 字面量超 511 字节后**返回空串**——不是截断。需要更长用法请走 `STRING_TO_UTF8`。
- **必须配 `{attribute 'TcEncoding' := 'UTF-8'}`** 才能让上层 API 正确处理。无注解的 STRING 在某些 API（如 OPC UA、ADS Notification）可能被当 ASCII/区域码解读。
- WSTRING 字面量请用 `wsLiteral_TO_UTF8`（取 WSTRING 编码）。
- 纯 ASCII 字面量不需要本函数——直接 `sUtf8 := 'Hello'` 即可。本函数主要为含 Latin-1 高位字符（Ü、€、°）的字面量服务。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_sLiteral_TO_UTF8.TcPOU`](../examples/P_Demo_sLiteral_TO_UTF8.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：OPC UA 服务器发布的字符串变量含德语 Umlaut（Hühner / Größe）；用 `sLiteral_TO_UTF8` 编初值，配 TcEncoding 让 UA 客户端正确显示。
- **价值**：替代手动 UTF-8 字节序列（如 `STRING := '$48$C3$BC...'`）的不可读 hex 转义；可读字面量 + 编译期编码。
- **替代方案对比**：`STRING_TO_UTF8`：运行时；`wsLiteral_TO_UTF8`：WSTRING 字面量；手写 hex 转义：不可维护。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.17 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/5780471691.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
