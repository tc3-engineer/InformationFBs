# INSERT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74415627.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_INSERT.TcPOU`](../examples/P_Demo_INSERT.TcPOU) |

---

## 1. 功能简述

`INSERT` 是 **IEC 61131-3 标准字符串函数**，把字符串 `STR2` **插入到 `STR1` 的第 `POS` 个字符之后**。即 PDF §4.4 原话："Insert STR2 into STR1 after position POS"。返回类型 `STRING(255)`。

注意 PDF 文字与 InfoSys 的 example 一致：`INSERT('SUSI','XY',2)` → `'SUXYSI'`。也就是说插入点 `POS` 表示**在 `STR1` 第 `POS` 位之后**开始插入；`POS = 0` 等于"插到最前面"，`POS = LEN(STR1)` 等于"追加到最后"。

工程上典型用途：在配置串中间插入新字段、给日志行加缩进、把转义字符插入到字符串特定位置以便后续协议封包。它与 `DELETE` 互为逆运算。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION INSERT : STRING(255)
VAR_INPUT
    STR1 : STRING(255);
    STR2 : STRING(255);
    POS  : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR1` | `STRING(255)` | 主串，将被插入的目标 |
| `STR2` | `STRING(255)` | 待插入的子串 |
| `POS` | `INT` | 插入点：在 `STR1` 第 `POS` 字符**之后**插入 `STR2`；`POS = 0` 表示插到最前面 |

### 返回值

`STRING(255)`：插入后的新字符串。

### VAR_OUTPUT / VAR_IN_OUT

无。

## 3. 行为说明

`INSERT(STR1, STR2, POS)` 是同步函数，一个 PLC 周期内立即返回插入后的新字符串，不会阻塞任务，也没有完成 / 忙状态输出。算法等同于：先把主串前 `POS` 个字符复制到结果缓冲（保留前缀），然后整段拷入要插入的子串 `STR2`，再把主串第 `POS+1` 字符起的剩余部分追加进去，末尾补 `0x00` 结束符。整个过程不修改任何入参，三段拷贝完成后形成一个新的 `STRING(255)`。

PDF §4.4 原例：`INSERT('SUSI', 'XY', 2)` → 在第 2 字符（`U`）后插入 `XY` → `'SUXYSI'`。

**关键语义**：

- **`POS` 是"之后"不是"位置"**：`POS = 2` 等于"插到第 2 字符后面"。容易和 C 语言的"插入到下标 2"混淆；
- **`POS = 0`**：表示插到字符串**最前面**，等价于 `CONCAT(STR2, STR1)`；
- **`POS >= LEN(STR1)`**：等价于"追加到末尾"，结果等于 `CONCAT(STR1, STR2)`；
- **超 255 字节静默截断**：和 `CONCAT` 一样，结果固定 255 字节容器，超出部分丢失；
- **不修改入参**：值传入。

⚠️ PDF + InfoSys 对负数 `POS` 行为未明确。一律传 ≥0 的值。

## 4. 错误码 / 返回值

无错误码。返回值始终是 `STRING(255)`。检测越界 / 截断需自己写 `IF LEN(STR1)+LEN(STR2) > 255 THEN`。

## 5. 使用注意 / 常见坑

- **`POS` 是"插到第 N 位之后"**：所以 `INSERT('AB','X',0)` = `'XAB'`，`INSERT('AB','X',1)` = `'AXB'`，`INSERT('AB','X',2)` = `'ABX'`。**最容易写错的是 `POS=1` 误以为是"插到最前"**——其实是"插到第 1 字符后"。
- **越界 POS 行为未规范**：负数、超长 `POS` 都未在 PDF 定义，工程上务必先 `IF POS >= 0 AND POS <= LEN(STR1) THEN`。
- **拼接超 255 字节静默截断**：超出尾部直接丢，没任何提示，调试不易；先 `LEN()` 校验。
- **想拼到最前面用 `POS=0`**：`INSERT(s, prefix, 0)` 等价于 `CONCAT(prefix, s)`。两种写法都对，看习惯。
- **多次插入用循环**：插多段不能链式调用，要么连续写多次 `INSERT`，要么一次性算好再 `CONCAT`。
- **UTF-8 中文按字节算**：`POS` 是字节位置，不是字符位置。Unicode 用 `WINSERT`。
- **配合 `FIND` 实现"在某标记后插入"**：常见模式 `s := INSERT(s, ',new', FIND(s, 'old')+LEN('old')-1);`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_INSERT.TcPOU`](../examples/P_Demo_INSERT.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 场景：日志行 'INFO Motor started' 要在 'INFO' 后插入时间戳 '[12:34:56]'
PROGRAM P_Demo_INSERT
VAR
    sLog       : STRING(255) := 'INFO Motor started';
    sTimestamp : STRING(255) := ' [12:34:56]';
    sResult    : STRING(255);
    nInsertPos : INT := 4;           // 'INFO' 4 字符后 = 第 4 字符之后
    bRun       : BOOL;
END_VAR

IF bRun THEN
    sResult := INSERT(sLog, sTimestamp, nInsertPos);
    bRun := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：日志加时间戳、给 CSV 行插入新列、协议帧中间补转义字符、HMI 输入串中间插入分隔符以美化显示、给文件路径插入子目录段。
- **价值**：一行调用完成"按位置插入子串"，比手写 `LEFT + CONCAT + CONCAT + RIGHT` 简洁。
- **替代方案对比**：
  - **`LEFT` + `CONCAT` + `RIGHT`**：等价但 3 行代码、3 个临时变量
  - **`+` 操作符**：只能拼前后，不能从中间插入
  - **`Tc2_Utilities` 扩展**：提供更高阶的字符串构建器，适合频繁拼接的场景
  - **本 FC**：IEC 标准、签名最直观（按位置+插什么），插段首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §4.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74415627.html
- **相关 FC**：`DELETE`（删段，逆操作）、`REPLACE`（覆盖式替换）、`CONCAT`（首尾拼接特例）、`FIND`（先定位再 INSERT）、`WINSERT`（WSTRING 版本）
