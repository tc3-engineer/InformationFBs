# HEXSTR_TO_DATA2

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Extended STRING functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/14612506635.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_HEXSTR_TO_DATA2.xml`](../examples/P_Demo_HEXSTR_TO_DATA2.xml) |

---

## 1. 功能简述

把十六进制字符串解析为二进制字节流；只允许空格作为字节分隔符；大小写都接受；遇非法字符立即中止并返回 0。

`Extended STRING functions` 这一组（PDF 4.2.x）是 Beckhoff 在 `Tc2_Standard` 之上扩展的"长字符串友好"版本：`Tc2_Standard` 里的同名函数（`CONCAT` / `FIND` / `INSERT` / `LEN` 等）受 IEC 61131-3 早期 STRING(255) 限制，处理超过 255 字符的串会**静默截断或返回错误结果**；本组的 `*2` 后缀函数全部接受 `POINTER TO STRING` + 显式 `nDstSize`，允许任意长度，并返回 `BOOL` / 字符数明确告知是否完整完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pSrcHexStr : POINTER TO STRING;
    pDstData : POINTER TO BYTE;
    nDstSize : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pSrcHexStr` | `POINTER TO STRING` | — | 源十六进制字符串地址（如 `'AF 34 55 EC'`）。 |
| `pDstData` | `POINTER TO BYTE` | — | 目标缓冲区地址（`ADR(buf)`）。 |
| `nDstSize` | `UDINT` | — | 目标缓冲字节数（`SIZEOF`）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `UDINT` | 成功转换的数据字节数。错误（含非法字符）时返回 0。 |

## 3. 行为说明

函数无状态。逐 2 字符读 `pSrcHexStr`，把每对 hex 字符（`'A0'`、`'1f'` 等）转换为 1 字节写入 `pDstData`。字节之间允许 0 或多个空格作为分隔（也允许无分隔的 `'AF3455EC'`）。遇到任何非 hex / 非空格字符立即中止并**返回 0**（**注意**：不是返回已转字节数）。`nDstSize` 不足时按 `nDstSize` 截断、返回已写入字节数。源串扫到 null 或 `Parameterlist.cMaxCharacters` 字符为止。

## 4. 错误码 / 返回值

返回 `UDINT`：成功转换的数据字节数。错误（含非法字符）时返回 0。

⚠️ 本函数不通过 HRESULT 报错——所有错误均通过返回值的特殊值（`FALSE` / `0`）表达；调用方必须始终判返回值，不能假定调用总成功。

## 5. 使用注意 / 常见坑

- **错误时返 0**，不是 `0xFFFFFFFF` 或部分字节数。这意味着 `'AF 3 55'`（缺一位）整段失败、**不会保留前半部分**。
- **只允许空格作分隔符**——制表符、换行符、逗号、连字符均视为非法字符直接 fail。预处理用 `FindAndReplaceChar` 把其它分隔符替换为空格。
- 大小写都接受（`'af'`、`'AF'`、`'aF'` 都行）；输出无大小写概念（字节）。
- **对称函数 `DATA_TO_HEXSTR2`**：把字节流转回 hex 串。两者打配。
- `pDstData` 必须够大；目标 buffer 不够时只复制能放下的部分但返回值小于源字节数——业务侧用 `result < expected_bytes` 检测截断。
- **结构体反序列化**：可以解析对结构体的 hex 表示，但 padding 字节也会按字节流写入——前提是结构体内存布局已知。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_HEXSTR_TO_DATA2.xml`](../examples/P_Demo_HEXSTR_TO_DATA2.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：从配置文件读出 hex 字符串 `'01 23 AB CD'`，写入 EtherCAT 从站的 PDO 配置字节区。
- **价值**：替代手写 hex 解析循环（每 2 字符调用 `HEXASCNIBBLE_TO_BYTE` 拼字节）；本函数 1 行解决并自带 size 检查。
- **替代方案对比**：`HEXSTR_TO_DATA`：旧版无显式 nDstSize；`HEXASCNIBBLE_TO_BYTE` + 手写循环：可控更细但代码长。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.2.13 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/14612506635.html
- **相关函数**：见同库 `extended_string/` 目录下其他 `*2` 版本扩展函数
