# WSTRING_TO_STRING2

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483047691.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_WSTRING_TO_STRING2.xml`](../examples/P_Demo_WSTRING_TO_STRING2.xml) |

---

## 1. 功能简述

`STRING_TO_WSTRING2` 的反向——任意长度 WSTRING 转 STRING。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pDstString : POINTER TO STRING;
    pSrcWString : POINTER TO WSTRING;
    nDstSize : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pDstString` | `POINTER TO STRING` | — | 目标 STRING 地址。 |
| `pSrcWString` | `POINTER TO WSTRING` | — | 源 WSTRING 地址。 |
| `nDstSize` | `UDINT` | — | 目标缓冲字节数。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 完整转换；`FALSE` = 截断。 |

## 3. 行为说明

函数无状态、立即返回。算法：从 `pSrcWSTRING` 起始逐 16 位字符读取（UTF-16 编码），按当前 Codepage 把每个字符压缩为单字节写入 `pDstSTRING`，最后写 8 位 null 终结符。Codepage 内的字符（ASCII + 区域映射的高位字符）正常转换；**Codepage 外字符（如中文 WSTRING 写入西欧 Codepage）行为 ⚠️ PDF/InfoSys 未明确**——可能被替换为占位字符、可能被跳过、可能返回 `FALSE`。生产环境**建议优先使用 `WSTRING_TO_UTF8`**——后者保留 Unicode 完整性，不受 Codepage 限制。本函数主要用于回灌只接受 STRING 的旧 ADS 接口、旧 BACnet 设备等。返回 `FALSE` 时目标内容已截断、null 终结。最多扫描 `Parameterlist.cMaxCharacters` 字符防 null 缺失死循环。`Tc2_Standard.WSTRING_TO_STRING` 限 255 字符，本函数无限制。

## 4. 错误码 / 返回值

返回 `BOOL`：`TRUE` = 完整转换；`FALSE` = 截断。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- **Codepage 外字符丢失**：中文 WSTRING 写入西欧 Codepage 会变乱码或被丢弃。
- 返 `FALSE` 必须当错误处理。
- 更稳妥的反向：`WSTRING_TO_UTF8` 保留 Unicode 完整性。
- `Tc2_Standard.WSTRING_TO_STRING` 限 255——长串用 `WSTRING_TO_STRING2`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WSTRING_TO_STRING2.xml`](../examples/P_Demo_WSTRING_TO_STRING2.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：UI 输入 WSTRING（多语言）→ 写入只支持 STRING 的旧设备。
- **价值**：无限长度；`Tc2_Standard` 限 255。
- **替代方案对比**：`WSTRING_TO_UTF8`：保留 Unicode；`Tc2_Standard.WSTRING_TO_STRING`：限 255。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.28 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483047691.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
