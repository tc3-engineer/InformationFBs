# GUID_TO_REGSTRING

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934082955.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_GUID_TO_REGSTRING.TcPOU`](../examples/P_Demo_GUID_TO_REGSTRING.TcPOU) |

---

## 1. 功能简述

把 GUID 结构转为带大括号的注册表格式字符串 `'{xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx}'`（38 字符含大括号）。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    in : GUID;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `GUID` | — | 源 GUID 结构。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `STRING(38)` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `STRING(38)` | 带花括号的 GUID 字符串。全零 GUID 返回 `'{00000000-0000-0000-0000-000000000000}'`。 |

### VAR_OUTPUT

无。

## 3. 行为说明

函数无状态、立即返回。算法：把 16 字节 GUID 按 Windows 注册表标准格式格式化为 `{8-4-4-4-12}` 段式 hex 字符串并在最外层添加大括号。结果共 38 个字符——含 2 个大括号、4 个连字符、32 个 hex 字符。**字节序按 GUID 内部存储**：第一段（Data1）按 little-endian 字节序读出，后续段按 big-endian——这是 Microsoft GUID 规范的历史遗留。初值 GUID（16 字节全 0）→ `'{00000000-0000-0000-0000-000000000000}'`（合法、不报错）。**本函数无错误返回**——任意输入都格式化为 38 字符串；GUID 全 0 输出和未初始化时一样，业务侧无法仅凭返回值区分。生产中通常用 `IsEqualGuid(g, 全零)` 配套检查。

## 4. 错误码 / 返回值

返回 `STRING(38)`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **与 `GUID_TO_STRING` 区别**：本函数有大括号 `{}`；`GUID_TO_STRING` 无大括号。Windows 注册表 / COM API 用带大括号版本。
- **反向函数 `REGSTRING_TO_GUID`**：把 38 字符大括号串解析回 GUID。
- **全零 GUID**（未初始化）也返回合法 38 字符串——业务侧不能用 `LEN > 0` 判 GUID 有效，需检查 `IsEqualGuid(g, 全零)`。
- 返回类型 `STRING(38)` 是为了正好放下 36 字节内容 + 2 字符大括号 + null 终结符；不要按 36 字节估算。
- 字符是 hex 大写（PDF 示例显示）；如果需要小写需要自己再 `F_ToLCase`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_GUID_TO_REGSTRING.TcPOU`](../examples/P_Demo_GUID_TO_REGSTRING.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：把 PLC 内的 OPC UA Application URI（GUID 形式）格式化为日志可读字符串；记入审计表。
- **价值**：替代手写 16 字节 → hex 字符串 + 拼接连字符 + 加大括号的 30 行代码；本函数 1 调用。
- **替代方案对比**：`GUID_TO_STRING`：无大括号版本；`STRING_TO_GUID`/`REGSTRING_TO_GUID`：反向。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.44 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934082955.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
