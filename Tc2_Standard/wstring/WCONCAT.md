# WCONCAT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions (WSTRING)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/2260750603.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_WCONCAT.xml`](../examples/P_Demo_WCONCAT.xml) |

---

## 1. 功能简述

`WCONCAT` 是 **IEC 61131-3 标准字符串函数的 WSTRING 版本**，实现**两个 WSTRING 的首尾拼接**：返回 `STR1` 后跟 `STR2` 的合并结果。两个入参与返回值均为 `WSTRING(255)`。

它和 `CONCAT` 是镜像函数，区别在于：**`WSTRING` 使用 UCS-2 / UTF-16 编码（每字符 2 字节）**，可以正确处理中文、日文、韩文、emoji 等 Unicode 字符。WSTRING 字面量必须用**双引号**而不是单引号，例如 `"中文"` 而不是 `'中文'`（这是 TwinCAT / IEC 的语法规定）。

工程上凡是 HMI 文本、报警语、操作员可读的诊断信息、需要本地化的字符串都应该用 WSTRING + WCONCAT 系列；只有协议帧、文件名、内部状态码这类纯 ASCII 数据才用 STRING + CONCAT。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION WCONCAT : WSTRING(255)
VAR_INPUT
    STR1 : WSTRING(255); (*Head part of the concatenated result*)
    STR2 : WSTRING(255); (*Tail part of the concatenated result*)
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR1` | `WSTRING(255)` | 拼接结果的**前段**字符串（UCS-2 编码） |
| `STR2` | `WSTRING(255)` | 拼接结果的**后段**字符串。按字面追加到 `STR1` 末尾，不插分隔符 |

### 返回值

`WSTRING(255)`：`STR1` 与 `STR2` 顺序拼接后的新字符串。返回缓冲固定为 255 个字符（512+2 字节含结束符），超过该长度的尾部字符被截断。

### VAR_OUTPUT / VAR_IN_OUT

无。

## 3. 行为说明

`WCONCAT(STR1, STR2)` 是同步函数，单周期内完成。算法等同 `CONCAT` 但按 16 位字符（UCS-2）单元复制：先把 `STR1` 中第一个 `0x0000` 之前的所有字符按 2 字节单元复制进返回缓冲，再把 `STR2` 中的字符追加，末尾补 `0x0000` 结束符。拼接长度超过 255 字符时尾部静默截断，无错误也无告警。`STR1` 与 `STR2` 都是值传入，函数内不会修改它们。

PDF §5.1 原例：`WCONCAT("SUS","WILLI")` → `"SUSWILLI"`（注意 IL 例中 `"SUSI" WCONCAT "WILLI"` → `"SUSIWILLI"`）。

**关键语义**：

- WSTRING 字面量用**双引号** `"..."`，单引号是 STRING 字面量；
- 同步 FC，无 `bBusy` / `bDone` 状态；
- **截断不告警**：超 255 字符尾部丢失，调用方需自己 `WLEN()` 校验；
- **空 WSTRING 合法**：`WCONCAT("", "abc")` → `"abc"`。

## 4. 错误码 / 返回值

无错误码。返回 `WSTRING(255)`。需要识别"是否被截断"必须自己 `IF WLEN(STR1) + WLEN(STR2) > 255 THEN`。

## 5. 使用注意 / 常见坑

- **字面量必须双引号**：`"abc"` 是 WSTRING，`'abc'` 是 STRING。混用会编译报错。
- **入参容器不要小于 255**：声明 `WSTRING(80)` 接 `WCONCAT` 返回值会触发二次截断。
- **每字符 2 字节**：底层存储 UCS-2，所以 `WLEN(s) = 100` 实际占 200 字节内存。
- **不能直接和 STRING 拼**：要拼 STRING 必须先 `STRING_TO_WSTRING` 转换。
- **emoji / 中文一律安全**：每字符 2 字节，没有"半个汉字"问题。Unicode 文本首选 WSTRING 系列。
- **WCONCAT vs `+`**：`+` 操作符对 WSTRING 同样适用，`"a" + "b"` 等价于 `WCONCAT("a","b")`。
- **HMI 联机调试坑**：监视面板里 WSTRING 显示有时是 UCS-2 转字符的结果，乱码多半是文件编码不匹配，不是 WCONCAT 的问题。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WCONCAT.xml`](../examples/P_Demo_WCONCAT.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）

```iecst
// 场景：HMI 报警栏拼"报警前缀（中文）" + "原因（中文）"，结果直接显示
PROGRAM P_Demo_WCONCAT
VAR
    sAlarmPrefix : WSTRING(255) := "报警：";
    sAlarmReason : WSTRING(255) := "1 号电机过流";
    sAlarmText   : WSTRING(255);
    bGenerate    : BOOL;
END_VAR

IF bGenerate THEN
    sAlarmText := WCONCAT(sAlarmPrefix, sAlarmReason);
    bGenerate := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：HMI 中文/日文报警文本拼接、操作员提示语本地化、多语言界面的占位符替换、需要 emoji 显示的过程状态串。
- **价值**：UCS-2 编码保证中文、日文、emoji 不乱码，拼接逻辑与 `CONCAT` 完全一致。
- **替代方案对比**：
  - **`+` 操作符（WSTRING）**：完全等价，更短
  - **`CONCAT` + UTF-8 STRING**：能存中文但按字节算长度，所有切段函数行为不同，且与 HMI 默认 UCS-2 编码不匹配
  - **`Tc2_Utilities` 扩展**：提供更高阶 WSTRING 构建器
  - **本 FC**：IEC 标准、和 HMI 一致编码、Unicode 文本拼接首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §5.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/2260750603.html
- **相关 FC**：`CONCAT`（STRING 版本）、`WINSERT`、`WREPLACE`、`WLEN`（先看长度避免截断）、`STRING_TO_WSTRING`（混合编码转换）
