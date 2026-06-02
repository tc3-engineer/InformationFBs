# wsLiteral_TO_UTF8

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/5780535435.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_wsLiteral_TO_UTF8.TcPOU`](../examples/P_Demo_wsLiteral_TO_UTF8.TcPOU) |

---

## 1. 功能简述

`sLiteral_TO_UTF8` 的 WSTRING 版本——把 WSTRING 字面量编译期编码为 UTF-8。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

无（参见下方 `VAR_IN_OUT CONSTANT`）。

```iecst
VAR_IN_OUT CONSTANT
    wsLiteral : WSTRING;
END_VAR
```

### VAR_IN_OUT (CONSTANT)

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `wsLiteral` | `WSTRING` | 待编码的 WSTRING 字面量。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `STRING(511)` | UTF-8 字符串（≤511 字节）；超长返回空串。 |

## 3. 行为说明

语义与 `sLiteral_TO_UTF8` 相同，但参数类型为 `WSTRING` 而不是 `STRING`，因此可以承载 BMP 范围内全部 Unicode 字符——包括中文、日文、韩文等。WSTRING 字面量在 IEC 61131-3 用**双引号**包围（`"中文"`），与 STRING 字面量的单引号（`'ASCII'`）区分。编译器读取 WSTRING 字面量（UTF-16 编码），逐字符转换为 Unicode codepoint，再按 UTF-8 规则编码为 1-4 字节序列：ASCII 1 字节、Latin-1 2 字节、CJK 3 字节、BMP 外 4 字节。输出写入 `STRING(511)` 缓冲，超长则返回空串（不是截断）。运行时该函数实际是编译期常量计算：返回的字节流已经在编译时确定，不消耗 PLC 周期。配合 `{attribute 'TcEncoding' := 'UTF-8'}` 注解让上游 API（OPC UA、MQTT、文件 IO 等）正确处理 UTF-8 内容。

## 4. 错误码 / 返回值

返回 `STRING(511)`：UTF-8 字符串（≤511 字节）；超长返回空串。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- **仅用于 WSTRING 字面量**；运行时变量 WSTRING → UTF-8 请用 `WSTRING_TO_UTF8`。
- 结果超 511 字节返回空串。
- **配 `{attribute 'TcEncoding' := 'UTF-8'}` 注解**让上游 API 正确处理 UTF-8。
- STRING 字面量请用 `sLiteral_TO_UTF8`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_wsLiteral_TO_UTF8.TcPOU`](../examples/P_Demo_wsLiteral_TO_UTF8.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：OPC UA 服务器发布的中文字符串变量初值 `"主泵状态"`；用 `wsLiteral_TO_UTF8` 编码 + TcEncoding 注解。
- **价值**：比手写 UTF-8 字节序列可读 1000 倍。
- **替代方案对比**：`sLiteral_TO_UTF8`：STRING 字面量；`WSTRING_TO_UTF8`：运行时变量。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.27 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/5780535435.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
