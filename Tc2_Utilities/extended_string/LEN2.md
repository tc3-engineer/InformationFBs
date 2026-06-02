# LEN2

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483027723.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_LEN2.TcPOU`](../examples/P_Demo_LEN2.TcPOU) |

---

## 1. 功能简述

返回 STRING 的字符长度（任意长度版本），突破 `Tc2_Standard.LEN` 的 255 字符限制。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pSTRING : POINTER TO STRING;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pSTRING` | `POINTER TO STRING` | — | 待测量的 STRING 地址。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `UDINT` | STRING 中的字符数（不含 null 终结符）。 |

## 3. 行为说明

函数无状态。逐字节扫描 `pSTRING` 起始的字节流，遇到 null 字节（0x00）停止，返回扫过的字节数（即字符数）。本质等同 C 的 `strlen`，但内置上限 `Parameterlist.cMaxCharacters` 防止 null 缺失导致的死循环（默认上限约 1M 字符，可在 GVL 调）。**返回值不含 null 终结符自身**——例如 `STRING(10)` 装 `'Hello'` 返回 5，不是 6。本函数针对 `STRING` 类型字节字符——纯 ASCII 时返回值等于字符数；含 UTF-8 多字节字符时返回值是字节数（不是字符数），UTF-8 字符数请用 `UTF8Len`。`Tc2_Standard.LEN` 限定 STRING(255) 上限，本函数无限制，是处理 STRING(1024+) 的标配。

## 4. 错误码 / 返回值

返回 `UDINT`：STRING 中的字符数（不含 null 终结符）。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- **接受指针不接受 STRING 直接传**——`LEN2(ADR(s))` 而不是 `LEN2(s)`。
- **用于 `STRING(1000)` 等长串场景**；255 内的串 `Tc2_Standard.LEN` 即可。
- 返回 0 = 空串；判空用 `IF LEN2(ADR(s)) = 0 THEN`。
- 扫描上限 `cMaxCharacters` 与 CONCAT2 共用——超长 STRING 可能在 null 前停止（罕见）。
- 纯 ASCII 串 == 字节数；UTF-8 串字符数 ≠ 字节数（用 `UTF8Len` 获取字符数）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LEN2.TcPOU`](../examples/P_Demo_LEN2.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：计算变长 logBuffer 当前已写入字符数，作为下次 append 的偏移基准。
- **价值**：`Tc2_Standard.LEN` 限 255——`STRING(1024)` 必须用 `LEN2`。
- **替代方案对比**：`LEN`（Tc2_Standard）：限 255；`UTF8Len`：UTF-8 字符数；手算字节：手动循环易错。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.15 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/3483027723.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
