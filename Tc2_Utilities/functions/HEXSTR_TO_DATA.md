# HEXSTR_TO_DATA

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35140619.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_HEXSTR_TO_DATA.xml`](../examples/P_Demo_HEXSTR_TO_DATA.xml) |

---

## 1. 功能简述

把 hex 字符串（如 `'AB CD 01 23'`）解析成字节数组，写入 `pData` 指向的目标 buffer。每两个 hex 字符表示一字节，字节之间允许用一个或多个空格作分隔符。返回成功写入的字节数；解析中遇到非法字符（非 hex 非空格）或目标 buffer 容量不足，转换中止并返回 0。

是 `DATA_TO_HEXSTR` 的反向：先把字节 dump 成 hex 文本日志，需要时再用本函数解析回字节。识别大小写 hex（`'ab cd' == 'AB CD'`）。整段一次性解析、单调用，比手写 `HEXASCNIBBLE_TO_BYTE` 循环更高效。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sHex   : T_MaxString;
    pData  : POINTER TO BYTE;
    cbData : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `sHex` | `T_MaxString` | — | 待解析的 hex 字符串（如 `'AB CD EF 01 23'`）。 |
| `pData` | `POINTER TO BYTE` | — | 目标 buffer 起始地址（`ADR()`）。 |
| `cbData` | `UDINT` | — | 目标 buffer 容量（字节，`SIZEOF()`）。 |

### VAR_IN_OUT

无。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `UDINT` | 成功写入字节数；出错返回 0。 |

### VAR_OUTPUT

无。

## 3. 行为说明

函数按以下规则扫描 `sHex` 并写入 `pData`：

1. **跳过分隔空格**：连续多个 `' '`（0x20）被吸收，等同一个分隔
2. **取两个 hex 字符合成一字节**：调用 `HEXASCNIBBLE_TO_BYTE` 把每个字符转 nibble，高 nibble 左移 4 位 OR 低 nibble
3. **写入字节**：写到 `pData^[i]`，`i` 递增
4. **检测容量**：每写一字节前判 `i < cbData`，否则中止
5. **检测错误**：任一 nibble 出错（非 hex、单个 nibble 而非成对）即中止，返回 0
6. **正常结束**：扫完 `sHex` 全部字符返回 `i`（写入字节数）

特性：
- 大小写不敏感
- 只允许空格作分隔；逗号 / 连字符 / `0x` 前缀会触发错误
- 字符必须成对（`'A'` 单独出现报错）
- 目标 buffer 不足时中止；不会越界写

边界：`sHex` 可达 255 字符（`T_MaxString` 上限）即约 85 字节有效数据（含 84 个空格）；要解长 hex 流用 `HEXSTR_TO_DATA2`。

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| `> 0` | 成功写入字节数 |
| `0` | 解析错误（非法字符、奇数 nibble、目标容量不足） |

## 5. 使用注意 / 常见坑

- **只允许空格作分隔**：不接受 `','` `'-'` `':'`；解析协议 hex 串时可能要先 `REPLACE` 转空格。
- **不接受 `'0x'` / `'16#'` 前缀**：`'0xAB 0xCD'` 失败。
- **目标 buffer 容量不足返回 0**：不部分写入；这是好事，避免脏数据。
- **错误时无法区分原因**：都返回 0；调用方按 `LEN(sHex)` 估算预期字节数，比对实际返回值判错（工程经验补充）。
- **`HEXSTR_TO_DATA2` 处理超长字符串**：本函数受 `T_MaxString` 255 字符上限；大段数据用扩展版。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_HEXSTR_TO_DATA.xml`](../examples/P_Demo_HEXSTR_TO_DATA.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_HEXSTR_TO_DATA
VAR
    sHex   : STRING := 'AB CD EF 01 23 45 67 89';
    arData : ARRAY[0..10] OF BYTE;
    nWrote : UDINT;
END_VAR

nWrote := HEXSTR_TO_DATA(sHex := sHex, pData := ADR(arData), cbData := SIZEOF(arData));
```

## 7. 业务场景与实际价值

- **场景**：从日志文件读出昨天保存的 `DATA_TO_HEXSTR` 结果，重新还原成字节数组做事故复盘。
- **价值**：和 `DATA_TO_HEXSTR` 配套；单调用解析整段 hex，识别大小写。
- **替代方案对比**：
  - 手写 `HEXASCNIBBLE_TO_BYTE` 循环：可，但要自己管空格 / 容量
  - `HEXSTR_TO_DATA2`：超长字符串用
  - 本函数：常规场景首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.49 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35140619.html
- **相关函数**：`DATA_TO_HEXSTR`（反向）、`HEXSTR_TO_DATA2`（长字符串版）、`HEXASCNIBBLE_TO_BYTE`（单 nibble 版）
