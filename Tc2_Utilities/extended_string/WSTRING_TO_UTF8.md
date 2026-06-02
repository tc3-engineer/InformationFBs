# WSTRING_TO_UTF8

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483049227.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_WSTRING_TO_UTF8.TcPOU`](../examples/P_Demo_WSTRING_TO_UTF8.TcPOU) |

---

## 1. 功能简述

WSTRING（UTF-16）转 UTF-8——保留 Unicode 完整性。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pDstUTF8 : PVOID;
    pSrcWSTRING : POINTER TO WSTRING;
    nDstSize : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pDstUTF8` | `PVOID` | — | 目标 UTF-8 缓冲地址。 |
| `pSrcWSTRING` | `POINTER TO WSTRING` | — | 源 WSTRING 地址。 |
| `nDstSize` | `UDINT` | — | 目标缓冲字节数。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 转换成功；`FALSE` = 缓冲不够。 |

## 3. 行为说明

函数无状态、立即返回。算法：从 `pSrcWSTRING` 起始逐 16 位字符读取（UTF-16 编码），把每个字符转换为 Unicode codepoint（BMP 内字符 codepoint = 字符值；BMP 外字符通过代理对识别——但 TwinCAT 实际行为 ⚠️ PDF/InfoSys 未明确，建议仅传 BMP）；再把 codepoint 按 UTF-8 编码为 1-4 字节序列写入 `pDstUTF8`：ASCII (U+0000 ~ U+007F) 1 字节、U+0080 ~ U+07FF 2 字节、U+0800 ~ U+FFFF 3 字节、U+10000+ 4 字节。最后写 8 位 null 终结符。**`nDstSize ≥ 字符数 × 3 + 1`** 是 BMP 范围最稳妥估值；含中文时基本是 3 倍。目标缓冲不够返回 `FALSE`、按可用空间截断（含 null）。**这是 HMI WSTRING 上云（OPC UA / MQTT）的标准路径**——比先 `WSTRING_TO_STRING2` 再 `STRING_TO_UTF8` 少一次 Codepage 损耗。配套反向 `UTF8_TO_WSTRING`。

## 4. 错误码 / 返回值

返回 `BOOL`：`TRUE` = 转换成功；`FALSE` = 缓冲不够。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- **`nDstSize ≥ 字符数 × 4 + 1`** 保险。
- 返 `FALSE` 时目标内容未定义。
- **最稳妥的 Unicode 输出路径**：HMI WSTRING → UTF-8 → 上云。
- BMP 外字符（emoji）行为 ⚠️ 未明确。
- 配套 `UTF8_TO_WSTRING`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WSTRING_TO_UTF8.TcPOU`](../examples/P_Demo_WSTRING_TO_UTF8.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：HMI WSTRING 数据上 OPC UA 云（UA 强制 UTF-8）。
- **价值**：比 `WSTRING_TO_STRING2` + `STRING_TO_UTF8` 中转少一次转换。
- **替代方案对比**：`STRING_TO_UTF8`：STRING 起点；`WSTRING_TO_STRING2` + `STRING_TO_UTF8`：两步走但有 Codepage 损耗。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.29 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483049227.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
