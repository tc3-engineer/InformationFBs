# GuidsEqualByVal

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/11500193035.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_GuidsEqualByVal.xml`](../examples/P_Demo_GuidsEqualByVal.xml) |

---

## 1. 功能简述

按值比较两个 GUID 是否相等；`TRUE` = 相等，`FALSE` = 不等。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    guidA : GUID;
    guidB : GUID;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `guidA` | `GUID` | — | 第一个 GUID。 |
| `guidB` | `GUID` | — | 第二个 GUID。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 完全相同；`FALSE` = 任一字段不同。 |

### VAR_OUTPUT

无。

## 3. 行为说明

函数无状态、立即返回。算法：逐字节比较 `guidA` 与 `guidB` 的 16 字节内存内容。全 16 字节相同 → `TRUE`；任一字节不同 → 立即返回 `FALSE`（短路求值）。**关键提示**：直接 `guidA = guidB` 在 IEC 61131-3 中**不能比较结构体**——必须用本函数（这是 IEC / TwinCAT 的强制限制）。`stA = stB` 编译错误；`GuidsEqualByVal(stA, stB)` 才合法。**值语义比较，不按引用**——即使两个 GUID 变量在不同内存地址，只要值相同也判等。无错误处理：始终返回 `TRUE` / `FALSE`，没有第三种结果。

## 4. 错误码 / 返回值

返回 `BOOL`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **IEC 61131-3 不能直接比较结构体**（含 GUID）—— 必须用 `GuidsEqualByVal`，写 `g1 = g2` 是编译错。
- 按内存逐字节比较——`UUID v4` 等任何变种都按字节相等判定。
- 未初始化的 GUID（全 0）之间相等：`GuidsEqualByVal(全0, 全0) = TRUE`。业务侧检查 GUID 有效性需用此函数对照全零 GUID 常量。
- 无错误处理：始终返回 `TRUE` / `FALSE`。
- **性能**：16 字节比较是 O(1)；高频比较场景无忧。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_GuidsEqualByVal.xml`](../examples/P_Demo_GuidsEqualByVal.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：OPC UA Session ID 验证：每次客户端请求带 GUID Session ID，PLC 服务端比对预先生成的 Session ID 决定是否拒绝。
- **价值**：**IEC 强制要求**——不能用 `=` 比较结构体；本函数是 GUID 比较的唯一标准方式。
- **替代方案对比**：**无替代**——`MEMCMP` 可以但不推荐（破坏类型安全）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.46 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/11500193035.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
