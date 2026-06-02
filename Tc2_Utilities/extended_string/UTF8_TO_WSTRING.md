# UTF8_TO_WSTRING

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483038859.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_UTF8_TO_WSTRING.TcPOU`](../examples/P_Demo_UTF8_TO_WSTRING.TcPOU) |

---

## 1. 功能简述

把 UTF-8 字节流转为 WSTRING（UTF-16）——保留 Unicode 完整性，不丢失字符。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pDstWSTRING : POINTER TO WSTRING;
    pSrcUTF8 : PVOID;
    nDstSize : UDINT;
END_VAR

VAR_OUTPUT
    nDstLen : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pDstWSTRING` | `POINTER TO WSTRING` | — | 目标 WSTRING 地址。 |
| `pSrcUTF8` | `PVOID` | — | 源 UTF-8 字节流地址。 |
| `nDstSize` | `UDINT` | — | 目标缓冲字节数（含 null 位置）。 |

### VAR_OUTPUT

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `nDstLen` | `UDINT` | 目标 WSTRING 字符数。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 转换成功；`FALSE` = 转换出错（Codepage 内不能表示）。 |

## 3. 行为说明

函数无状态、立即返回。算法：从 `pSrcUTF8` 起始逐 UTF-8 字符（1-4 字节序列）读取，解码为 Unicode codepoint；再以 UTF-16 编码（WSTRING 即 UTF-16LE 编码）写入 `pDstWSTRING`。BMP 内字符（U+0000 ~ U+FFFF）直接占 1 个 16 位单元；BMP 外字符（U+10000 及以上，含 emoji 等）按 UTF-16 规范需要代理对（2 个 16 位单元）表示——但 TwinCAT 实际处理 ⚠️ PDF/InfoSys 未明确，建议假设仅支持 BMP 范围。写完后写 16 位 null 终结符。`nDstLen` 输出实际字符数。**这是 UTF-8 反向中最稳妥的路径**——WSTRING（Unicode）能容纳所有 BMP 字符，不像 `UTF8_TO_STRING` 受 Codepage 限制。结果不完整时返回 `FALSE`，目标内容已截断、null 终结。

## 4. 错误码 / 返回值

返回 `BOOL`：`TRUE` = 转换成功；`FALSE` = 转换出错（Codepage 内不能表示）。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- **目标 WSTRING 字节数 = 字符数 × 2 + 2**（含 null）；`nDstSize` 用 `SIZEOF`。
- 源 UTF-8 含 BMP 外字符（emoji 等）的行为 ⚠️ PDF 未明确——建议仅传 BMP。
- **`pSrcUTF8` null 终结**保证退出。
- 比 `UTF8_TO_STRING` 更安全——WSTRING 能装下所有 Unicode 字符。
- 配套：`WSTRING_TO_UTF8`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_UTF8_TO_WSTRING.TcPOU`](../examples/P_Demo_UTF8_TO_WSTRING.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：HMI 显示模块用 WSTRING；从 OPC UA Server 收到的 UTF-8 文本需先转 WSTRING 才能送到 HMI。
- **价值**：比 `UTF8_TO_STRING` 保真度高——Unicode 全字符集；适合多语言 HMI。
- **替代方案对比**：`UTF8_TO_STRING`：丢非 Codepage 字符；保留 UTF-8 直传：HMI 需自身支持 UTF-8。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.22 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483038859.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
