# WDELETE

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions (WSTRING)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/2260752907.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_WDELETE.xml`](../examples/P_Demo_WDELETE.xml) |

---

## 1. 功能简述

`WDELETE` 是 **IEC 61131-3 标准字符串函数 `DELETE` 的 WSTRING 版本**，从 WSTRING 字符串 `STR1` 中**自第 `POS` 个字符起删除 `LEN` 个字符**，返回剩余部分组成的新串。PDF §5.2 原话："Delete LEN characters from STR beginning with the POSth character"。

返回类型 `WSTRING(255)`。与 `DELETE` 的关键区别：**按 UCS-2 字符（2 字节单元）计数**，所以一个中文汉字 / 一个 emoji 在 `LEN` 和 `POS` 里都算 **1**，不是 3 字节。这是 WSTRING 系列函数最大的优势——对 Unicode 文本边界正确。

工程上常用于剥离 HMI 输入文本的非法字符段、删除中文日志条目的时间戳前缀、清洗带 emoji 的过程文本。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION WDELETE : WSTRING(255)
VAR_INPUT
    STR1 : WSTRING(255);
    LEN  : INT;
    POS  : INT;
END_VAR
```

注意 PDF 中变量名为 `STR1`（不是 `STR`，与 `DELETE` 略有差异）。

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR1` | `WSTRING(255)` | 待处理的源 WSTRING |
| `LEN` | `INT` | 要删除的**字符数**（按 UCS-2 字符单元计数，不是字节） |
| `POS` | `INT` | 删除起点位置，**从 1 开始**计数 |

### 返回值

`WSTRING(255)`：删除指定段后剩余的字符串。

### VAR_OUTPUT / VAR_IN_OUT

无。

## 3. 行为说明

`WDELETE(STR1, LEN, POS)` 是同步函数，单周期内立即返回。算法等同 `DELETE` 但按 UCS-2 字符（2 字节单元）操作：把 `STR1` 中 `[1, POS-1]` 字符区间复制到结果缓冲（保留前缀），跳过 `[POS, POS+LEN-1]` 这 `LEN` 个字符（被删除部分），把 `[POS+LEN, end]` 区间追加到结果缓冲，末尾补 `0x0000` 结束符。所有索引和长度都是 UCS-2 字符单元，不是字节，所以汉字、emoji 都按 1 个字符算。`LEN = 0` 等价于不删；越界行为未规范。

PDF §5.2 原例：`WDELETE("SUXYSI", 2, 3)` → 从第 3 字符（`X`）起删 2 字符 → `"SUSI"`。

**关键语义**：

- 按 UCS-2 字符计数，**汉字/emoji = 1 个字符**；
- `POS` 从 1 起；
- 越界 `POS`、负数 `LEN`、`POS = 0` 等行为未规范 ⚠️；
- 不修改入参。

## 4. 错误码 / 返回值

无错误码。返回值始终 `WSTRING(255)`。无法判断越界——调用方需自行 `WLEN(STR1)` 校验。

## 5. 使用注意 / 常见坑

- **`POS` 从 1 开始**：第 1 字符 `POS = 1`，不是 0；
- **越界静默**：负值 / 超长不报错，行为不可预期。务必先 `IF POS >= 1 AND POS + LEN - 1 <= WLEN(STR1) THEN`；
- **按字符不按字节**：删 1 个汉字传 `LEN := 1`（不是 3）；
- **不能拼 STRING**：返回 `WSTRING`，要赋给 STRING 必须先 `WSTRING_TO_STRING`；
- **WSTRING 字面量用双引号**：`"abc"` 是 WSTRING，单引号是 STRING；
- **配合 `WFIND` 用得最多**：典型场景"删除某中文标记之前所有内容"：`WDELETE(s, WFIND(s, "标记")-1, 1)`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WDELETE.xml`](../examples/P_Demo_WDELETE.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）

```iecst
// 场景：从中文报警 "[报警] 1号电机过流" 中剔除前缀 "[报警] " 共 5 字符
PROGRAM P_Demo_WDELETE
VAR
    sFullAlarm : WSTRING(255) := "[报警] 1号电机过流";
    sBody      : WSTRING(255);                    // 剔除前缀后的消息体
    nPrefixLen : INT := 5;                        // "[报警] " 共 5 个 UCS-2 字符
    bStrip     : BOOL;
END_VAR

IF bStrip THEN
    sBody := WDELETE(sFullAlarm, nPrefixLen, 1);
    bStrip := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：剥离中文/日文报警前缀、清洗带 emoji 的过程日志、HMI 输入纠错（删除用户多敲的字符段）、协议帧中包含 Unicode 字段的清洗。
- **价值**：UCS-2 安全：删字符就是删字符，不会"拆出半个汉字"。
- **替代方案对比**：
  - **`DELETE` + UTF-8 STRING**：能存中文但要按字节算长度，删 1 个汉字要传 3，容易拆出半个汉字
  - **手写循环按字符删**：约 15 行 ST
  - **本 FC**：IEC 标准、Unicode 安全、签名直观，**Unicode 删段首选**

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §5.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/2260752907.html
- **相关 FC**：`DELETE`（STRING 版本）、`WINSERT`（逆操作）、`WREPLACE`、`WFIND`、`WLEN`
