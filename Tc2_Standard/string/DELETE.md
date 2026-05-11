# DELETE

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74412555.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_DELETE.xml`](../examples/P_Demo_DELETE.xml) |

---

## 1. 功能简述

`DELETE` 是 **IEC 61131-3 标准字符串函数**，从字符串 `STR` 中**自第 `POS` 个字符起删除 `LEN` 个字符**，返回剩余部分组成的新字符串。即 PDF §4.2 原话："Delete LEN characters from STR beginning with the character in the POS"。

返回类型固定为 `STRING(255)`。该函数最常用在：清洗 PLC 收到的协议帧（剔除头部前导字节或尾部 CRC 字节）、去掉日志条目中的时间戳前缀、把 HMI 输入框中用户多敲的非法字符段挖掉。

字符位置 `POS` 是**从 1 开始**计数（IEC 字符串惯例），不是 C 风格的 0 起始。这是工程上最容易踩的坑。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION DELETE : STRING(255)
VAR_INPUT
    STR  : STRING(255);
    LEN  : INT;
    POS  : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR` | `STRING(255)` | 待处理的源字符串 |
| `LEN` | `INT` | 要删除的字符数（从 `POS` 处开始向后数 `LEN` 个字符删掉） |
| `POS` | `INT` | 删除起点位置，**从 1 开始**计数（第 1 个字符 `POS = 1`） |

### 返回值

`STRING(255)`：删除指定段后剩余的字符串。

### VAR_OUTPUT / VAR_IN_OUT

无。

## 3. 行为说明

`DELETE(STR, LEN, POS)` 一个 PLC 周期内同步完成。算法等同：

1. 复制 `STR` 中 `[1, POS-1]` 区间的字符到结果缓冲（即 `POS` 之前的所有字符保留）；
2. 跳过 `[POS, POS+LEN-1]` 这 `LEN` 个字符（要删掉的部分）；
3. 把剩余字符 `[POS+LEN, end]` 追加到结果缓冲；
4. 在结果末尾补 `0x00`。

PDF §4.2 原例：`DELETE('SUXYSI', 2, 3)` → 从第 3 个字符开始删 2 个字符（即删掉 `XY`），返回 `'SUSI'`。

**关键语义**：

- **`POS = 1` 表示从最前面删**：`DELETE('HELLO', 2, 1)` → 删除前 2 个字符 → `'LLO'`；
- **`LEN = 0`**：等于不删，返回与 `STR` 相同的字符串；
- **`POS` 超出字符串长度**：PDF 与 InfoSys 均未明确，工程上一般返回原字符串不变，但**为了可移植性应在调用前自己用 `LEN(STR)` 校验**；
- **`POS + LEN - 1` 超出字符串长度**：删除从 `POS` 起到末尾的所有字符，相当于截断；
- **不修改入参**：值传入，返回新字符串。

⚠️ PDF + InfoSys 对越界 `POS`、负数 `LEN`、`POS = 0` 的行为均未给出明确规范。工程上必须自己校验或避免传入这些值。

## 4. 错误码 / 返回值

无错误码。返回值始终是 `STRING(255)`。无法从返回值判断是否发生了非预期删除（如 `POS` 越界）——调用方必须保证入参合法。

## 5. 使用注意 / 常见坑

- **`POS` 从 1 开始数**：C/C++/Python 用习惯了的工程师极容易写 `DELETE(s, 3, 0)` 想"从开头删 3 个"，实际结果未定义；正确写法 `DELETE(s, 3, 1)`。
- **`LEN`、`POS` 是 INT 不是 UINT**：负数不会编译报错。传负值后行为未定义，必须自己拦截。（工程经验补充）
- **越界静默返回**：PDF 没规定越界怎么处理，不同 TwinCAT 版本可能行为不同——一律先 `IF POS >= 1 AND POS <= LEN(STR) THEN`。
- **删完后变量类型不变**：返回仍是 `STRING(255)`，删 254 个字符也是 255 字节容器，只是内容前几位有效。
- **配合 `FIND` 用得最多**：典型场景"删除某个标记之前的所有字符"，写法 `DELETE(s, FIND(s, 'tag')-1, 1)`。
- **批量清洗用循环**：删多段不能链式调用，要在 ST 里写循环或多次赋值。
- **多字节字符要警惕**：`STRING` 是 ANSI 单字节，UTF-8 中文每字符占 3 字节，`LEN := 1` 实际只删了 1/3 个汉字。Unicode 必须改用 `WDELETE`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DELETE.xml`](../examples/P_Demo_DELETE.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

```iecst
// 场景：通讯帧 'STX|01|DATA|ETX' 收到后要剔除头部 'STX|' 4 字节再交给业务层
PROGRAM P_Demo_DELETE
VAR
    sRawFrame  : STRING(255) := 'STX|01|DATA|ETX';  // 收到的原始帧
    sPayload   : STRING(255);                        // 剔除头部后的有效载荷
    nHeaderLen : INT := 4;                           // 头部 'STX|' 4 字节
    bStrip     : BOOL;                               // 触发一次清洗
END_VAR

IF bStrip THEN
    sPayload := DELETE(sRawFrame, nHeaderLen, 1);   // 从第 1 字节起删 4 字节
    bStrip := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：剥离协议帧头部（STX / 长度字段 / 设备 ID）、删除日志条目的时间戳前缀以便后续解析、把 HMI 用户输入的非法连续空格段挖掉、从订单号中删除分隔符。
- **价值**：一次调用完成"按位置 + 长度删一段"，比手写 `MEMCPY` + 起止指针 + 长度计算简单得多。
- **替代方案对比**：
  - **`FIND` + `LEFT` + `RIGHT` 组合**：能做但代码长 3-4 倍，且每次都要计算长度
  - **`REPLACE` 替换为空串**：在多数实现里等价，但行为不如 `DELETE` 直观
  - **`Tc2_Utilities` 扩展**：提供 `TrimLeft` / `TrimRight` 等专用函数，去空白比 DELETE 更适合
  - **本 FC**：IEC 标准、签名最直观（按位置+长度），删段首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §4.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74412555.html
- **相关 FC**：`INSERT`（插入子串，DELETE 的逆操作）、`REPLACE`（替换段）、`MID`（取中间段）、`WDELETE`（WSTRING 版本）
