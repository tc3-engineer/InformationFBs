# LEN

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74418699.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_LEN.xml`](../examples/P_Demo_LEN.xml) |

---

## 1. 功能简述

`LEN` 是 **IEC 61131-3 标准字符串函数**，返回字符串 `STR` 的**有效字符长度**（不含结束符 `0x00`）。PDF §4.5 原话："returns the length of a string"。返回类型 `INT`。

注意：`LEN` 返回的是**当前有效字符数**，而不是 `STRING(N)` 声明里的容器大小 `N`。声明 `s : STRING(255) := 'abc'` 时 `LEN(s) = 3`，不是 255。这是工程上最容易混淆的点。

`LEN` 是字符串处理的"探针"：在调用 `LEFT` / `RIGHT` / `MID` / `INSERT` / `DELETE` 前，几乎都需要先 `LEN()` 校验长度避免越界或截断。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION LEN : INT
VAR_INPUT
    STR : STRING(255);
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR` | `STRING(255)` | 待测量的字符串 |

### 返回值

`INT`：`STR` 的有效字符数（自第 1 字符起到第一个 `0x00` 结束符之前的字符数量）。

### VAR_OUTPUT / VAR_IN_OUT

无。

## 3. 行为说明

`LEN(STR)` 同步函数，一个 PLC 周期内立即返回。底层算法等同 C 的 `strlen`：从 `STR` 第 1 字节开始逐字节扫描，遇到第一个 `0x00` 字节停下，返回**已扫过的字节数**。这意味着字符串中间不能有提前出现的 `0x00`，否则截断点就是 `LEN` 的返回值，而不是声明的容器大小。空串 `''` 返回 `0`；255 字节全填且尾部仍有 `0x00` 时返回 `255`，再长就需要更大的容器才能正确测量。

PDF §4.6 原例：`LEN('SUSI')` → `4`。

**关键语义**：

- **返回有效字符数，不是容器大小**：`STRING(255) := 'abc'` 的 `LEN` 是 3，不是 255；
- **空串返回 0**：`LEN('')` = `0`；
- **UTF-8 中文按字节**：每汉字 3 字节，`LEN('中文')` = 6，不是 2。需要"字符数"应改用 `WLEN`；
- **中间 `0x00` 提前截断**：若程序中误把中间字节写成 `0x00`，`LEN` 只数到该字节为止——这是排查"字符串看起来短"问题的最常见原因。

## 4. 错误码 / 返回值

无错误码。返回 `INT`，永远 ≥ 0。0 表示空串。**INT 是 16 位有符号**，理论上限 32767，但本函数源串容器最大 `STRING(255)`，所以实际取值范围 0..255。

## 5. 使用注意 / 常见坑

- **返回字符数不是字节大小**：对纯 ASCII 两者相等，但 UTF-8 中文字符 `LEN` 返回字节数（一汉字 3 字节）。要"用户视觉字符数"必须 `WLEN`。
- **不要混淆"容器大小"**：`SIZEOF(s)` 才返回容器字节大小；`LEN(s)` 是有效内容长度。
- **拼接前校验长度**：`IF LEN(s1) + LEN(s2) > 255 THEN` 是 `CONCAT` 调用前的标准防截断模式。
- **结束符位置异常**：若用 `MEMCPY` 直接写入 STRING 缓冲但忘记补 `0x00`，`LEN` 返回值会比预期大（一直扫到下个偶然出现的 0 字节）。（工程经验补充）
- **空串安全**：`LEN('')` 不会崩溃，可放心调用。
- **频繁调用无副作用**：纯函数无内部状态，循环里反复调用安全（除了 O(N) 扫描成本，长串频繁 LEN 会拖性能）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LEN.xml`](../examples/P_Demo_LEN.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）

```iecst
// 场景：HMI 输入框限制最多 50 字符，PLC 收到后先用 LEN 校验，超长则拒收
PROGRAM P_Demo_LEN
VAR
    sUserInput : STRING(255);          // HMI 写入
    nInputLen  : INT;                  // 输入长度
    bAccept    : BOOL;                 // 通过校验
    nMaxLen    : INT := 50;            // 业务限定上限
END_VAR

nInputLen := LEN(sUserInput);
bAccept := (nInputLen > 0) AND (nInputLen <= nMaxLen);
```

## 7. 业务场景与实际价值

- **场景**：HMI 输入长度校验、拼接前防截断检查、协议帧分包时判断剩余空间、空串保护（`IF LEN(s) > 0 THEN ...`）。
- **价值**：一行调用拿到长度，所有后续字符串运算都依赖它。
- **替代方案对比**：
  - **`SIZEOF`**：返回声明容器字节数，**不是**有效字符数，不能替代
  - **手写循环找 `0x00`**：完全等价但浪费代码
  - **`Tc2_Utilities.LEN2`**：扩展版本，对超大字符串（>255）和带类型推导的字符串更友好
  - **本 FC**：IEC 标准、零依赖、所有字符串运算的前置探针，**必备**

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §4.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74418699.html
- **相关 FC**：`SIZEOF`（容器字节大小）、`WLEN`（WSTRING 版，按字符计数）、`Tc2_Utilities.LEN2`（扩展）
