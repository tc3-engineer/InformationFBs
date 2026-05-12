# FIND

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74414091.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_FIND.xml`](../examples/P_Demo_FIND.xml) |

---

## 1. 功能简述

`FIND` 是 **IEC 61131-3 标准字符串函数**，在主串 `STR1` 中**首次出现**子串 `STR2` 的位置返回字符序号（从 1 开始）。若 `STR2` 在 `STR1` 中**不出现**，则返回 `0`。

返回类型是 `INT`，单值；不返回长度、不返回多个匹配位置。**`0` 是"未找到"的统一约定**——业务侧判断时无须比较具体错误码。

工程上几乎所有解析任务的第一步都是 `FIND`：定位分隔符、定位行结束符、找出标记位以便后续 `LEFT` / `RIGHT` / `DELETE` 切段。它是搭配其他 4 个字符串函数最常用的"指南针"。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION FIND : INT
VAR_INPUT
    STR1 : STRING(255);
    STR2 : STRING(255);
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR1` | `STRING(255)` | 主串（在哪里搜） |
| `STR2` | `STRING(255)` | 待查找的子串（搜什么） |

### 返回值

`INT`：

- **`> 0`**：子串首次出现的字符位置（**从 1 开始**计数）
- **`0`**：子串在主串中不出现

### VAR_OUTPUT / VAR_IN_OUT

无。

## 3. 行为说明

`FIND(STR1, STR2)` 一个 PLC 周期内同步完成。算法等同朴素子串搜索：

1. 从 `STR1` 的第 1 个字符开始，逐位置尝试匹配 `STR2`；
2. 第一次完整匹配时停下，返回该匹配起点在 `STR1` 中的字符位置（1-based）；
3. 若扫到 `STR1` 末尾仍无匹配，返回 `0`。

PDF §4.3 原例：`FIND('SUXYSI', 'XY')` → 在 `SUXYSI` 中 `XY` 出现在第 3 位起，返回 `3`。

**关键语义**：

- **大小写敏感**：`FIND('Hello','HELLO')` → `0`，因为大小写不同；
- **子串为空**：PDF 与 InfoSys 均未明确 `STR2 = ''` 时的行为。⚠️ 工程上不要传入空串，调用前自己 `IF LEN(STR2) > 0 THEN` 拦一道；
- **首次匹配即停**：只返回**第一次**出现的位置，不支持"找第 N 次"或"找最后一次"。需要找下一次须先 `DELETE` 已找到段再 `FIND`；
- **不修改入参**：值传入，仅返回 `INT`。

InfoSys topic 74414091 与 PDF §4.3 文本一致，无额外行为补充。

## 4. 错误码 / 返回值

无错误码。返回 `INT`：

- `0` = 未找到（业务侧统一以此为"miss"分支）
- `1..LEN(STR1)` = 找到，对应起点位置

**0 与位置 1 必须严格区分**：写成 `IF FIND(s,t) THEN ...` 不会按预期工作（IEC 中 INT 非零为真，但 IF 后必须用 `<>` 显式比较）。正确：`IF FIND(s,t) > 0 THEN ...`。

## 5. 使用注意 / 常见坑

- **位置从 1 开始**：返回 `3` 意味着子串起点是 `STR1` 第 3 字符——配合 `MID` / `DELETE` 时该值直接传，**不要 -1**。常见错位坑。
- **大小写敏感**：`FIND` 不做大小写归一。需要不区分大小写就先 `Tc2_Utilities` 里的 `STRING_TO_UPPER` 把两侧都转大写再 `FIND`。
- **子串为空时未定义**：⚠️ PDF + InfoSys 均未说明。工程上一律先 `IF LEN(STR2) > 0 THEN` 校验。
- **多次匹配只返回第一次**：找第二次出现要写循环：先 `FIND` 第 1 次的位置 `n`，再 `MID/DELETE` 删掉前 `n+LEN(STR2)-1` 字节，再 `FIND` 一次。
- **STRING(255) 上限**：主串超 255 字节会被截断处理。需要长文本搜索改用 `Tc2_Utilities` 扩展字符串函数。
- **多字节字符**：`STR1` 中含 UTF-8 中文（每字符 3 字节），返回的 `INT` 是**字节位置**不是字符位置，处理时要小心。Unicode 用 `WFIND`。
- **性能 O(N×M)**：未找到时会扫完整个主串。频繁搜索可考虑预处理（建索引）或换 KMP/Boyer-Moore，但 TwinCAT 标准库不提供，得自己实现或借第三方。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FIND.xml`](../examples/P_Demo_FIND.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）

```iecst
// 场景：从 'IP:192.168.1.10,PORT:502' 这种 KV 串中定位 ',' 的位置，
//       以便后续用 LEFT / RIGHT 拆出 IP 和 PORT 两段
PROGRAM P_Demo_FIND
VAR
    sConfig   : STRING(255) := 'IP:192.168.1.10,PORT:502';
    sDelim    : STRING(255) := ',';
    nDelimPos : INT;                  // ',' 在 sConfig 中的位置
    bSearch   : BOOL;
END_VAR

IF bSearch THEN
    nDelimPos := FIND(sConfig, sDelim);
    bSearch := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：解析 KV 配置串（`IP:xxx,PORT:yyy`）、定位 CR/LF 切多行日志、找特殊标记位以判断协议帧类型、HMI 输入的电邮地址里找 `@` 校验格式。
- **价值**：单次调用拿到子串位置，后续 `LEFT/RIGHT/DELETE` 直接基于该位置切段，三行完成完整解析。
- **替代方案对比**：
  - **手写循环 + 逐字节比较**：约 15 行 ST，边界条件多易踩坑
  - **正则表达式**：TwinCAT 标准库不带正则，需 `Tc3_Common` 或第三方
  - **`Tc2_Utilities.SearchStr` / `SearchSubstr`**：扩展版，支持起点位置、不区分大小写等选项
  - **本 FC**：IEC 标准、零依赖、一行调用即可，**首选**

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §4.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74414091.html
- **相关 FC**：`MID` / `LEFT` / `RIGHT`（基于 FIND 返回位置切段）、`DELETE`（删除已匹配段）、`REPLACE`（找到+替换）、`WFIND`（WSTRING 版本）
