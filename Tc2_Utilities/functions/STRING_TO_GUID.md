# STRING_TO_GUID

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934149643.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_STRING_TO_GUID.xml`](../examples/P_Demo_STRING_TO_GUID.xml) |

---

## 1. 功能简述

`GUID_TO_STRING` 的反向——把 36 字符无大括号 GUID 串解析为 GUID 结构。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    in : STRING(36);
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `STRING(36)` | — | 无大括号的 GUID 字符串（36 字符）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `GUID` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

函数无状态、立即返回。算法：扫描 `in` 字符串，要求严格 `8hex-4hex-4hex-4hex-12hex` 格式——4 段连字符分隔的 hex 字符，不含大括号；逐字符解码 hex nibble 并组装 16 字节 GUID 结构。第一段按 little-endian、后续段按 big-endian 字节序写入 GUID（Microsoft GUID 历史规范）。**解析失败时返回全零 GUID**——这与 `GUID_TO_STRING('全零 GUID')` 输出对应的解析结果相同，**无法仅凭返回值区分『合法的全零 GUID』和『字符串格式错误』**。业务侧应**先用 `LEN(s) = 36 AND s[9] = '-' AND s[14] = '-' AND s[19] = '-' AND s[24] = '-'` 校验格式**再调用本函数。

## 4. 错误码 / 返回值

返回 `GUID`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **失败返回全零 GUID**——与合法全零输出不可区分；调用方先校验字符串格式。
- **字符串无大括号**；带大括号版本用 `REGSTRING_TO_GUID`。
- **严格 36 字符**——多余空格或字符会导致解析失败。
- **大小写均接受**。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_STRING_TO_GUID.xml`](../examples/P_Demo_STRING_TO_GUID.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：从数据库 `uuid` 列读出 36 字符 GUID 字符串 → 解析为 PLC GUID 结构 → 与本地缓存比对。
- **价值**：替代手写 hex 解析 + 段切分。
- **替代方案对比**：`REGSTRING_TO_GUID`：带大括号版本。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.67 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934149643.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
