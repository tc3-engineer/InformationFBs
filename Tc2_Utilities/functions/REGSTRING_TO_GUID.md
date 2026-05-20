# REGSTRING_TO_GUID

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934147723.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_REGSTRING_TO_GUID.xml`](../examples/P_Demo_REGSTRING_TO_GUID.xml) |

---

## 1. 功能简述

`GUID_TO_REGSTRING` 的反向——把带大括号的 38 字符 GUID 串解析为 GUID 结构。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    in : STRING(38);
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `STRING(38)` | — | 注册表格式的 GUID 字符串（带大括号 38 字符）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `GUID` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

函数无状态、立即返回。算法：扫描 `in` 字符串，要求格式严格 `{8hex-4hex-4hex-4hex-12hex}`——大括号 + 4 段连字符分隔的 hex 字符；逐字符解码 hex nibble 并组装 16 字节 GUID 结构。第一段按 little-endian、后续段按 big-endian 写入 GUID（与 `GUID_TO_REGSTRING` 对称）。**解析失败时返回全零 GUID**——这与 `GUID_TO_REGSTRING` 输出的 `'{0...0}'` 字符串对应的解析结果相同，**无法仅凭返回值区分『成功但 GUID 本就是全零』和『格式错误』**。业务侧应**先用 `LEN(s) = 38 AND s[1] = '{' AND s[37] = '}'` 校验格式**再调用本函数。

## 4. 错误码 / 返回值

返回 `GUID`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **失败返回全零 GUID** —— 与合法的 `'{0-0-0-0-0}'` 输出不可区分。需调用方先检查 `in` 是否符合大括号 + 连字符格式。
- **字符串必须带大括号**；无大括号版本用 `STRING_TO_GUID`。
- **严格 38 字符**——字符串末尾空格 / 多余字符会导致解析失败。
- **大小写均接受**。
- **对应 `GUID_TO_REGSTRING`** 是无损往返。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_REGSTRING_TO_GUID.xml`](../examples/P_Demo_REGSTRING_TO_GUID.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：从 Windows 注册表读出 `'{CLSID-string}'` → 解析为 PLC GUID 结构 → 用于 COM API 调用。
- **价值**：替代手写 hex 解析 + 段切分代码。
- **替代方案对比**：`STRING_TO_GUID`：无大括号版本。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.64 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934147723.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
