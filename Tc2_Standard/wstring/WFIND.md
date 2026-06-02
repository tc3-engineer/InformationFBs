# WFIND

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions (WSTRING)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/2260754827.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_WFIND.TcPOU`](../examples/P_Demo_WFIND.TcPOU) |

---

## 1. 功能简述

`WFIND` 是 **IEC 61131-3 标准字符串函数 `FIND` 的 WSTRING 版本**，在主串 `STR1` 中查找子串 `STR2` 首次出现的位置；找到返回起点字符序号（**从 1 开始**），未找到返回 `0`。

返回类型 `INT`。与 `FIND` 的关键区别：**按 UCS-2 字符计数**，所以一个汉字在 `STR1` 中算 1 个字符位置，不是 3 字节。这让"找到中文字符 X 的位置"这种需求可以直接得到字符位置而不是字节位置，配合 `WLEFT` / `WRIGHT` / `WMID` 时下标语义统一。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION WFIND : INT
VAR_INPUT
    STR1 : WSTRING(255);
    STR2 : WSTRING(255);
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR1` | `WSTRING(255)` | 主串（在哪里搜） |
| `STR2` | `WSTRING(255)` | 待查找的子串 |

### 返回值

`INT`：

- **`> 0`**：子串首次出现的字符位置（**1-based**）
- **`0`**：子串在主串中不出现

### VAR_OUTPUT / VAR_IN_OUT

无。

## 3. 行为说明

`WFIND(STR1, STR2)` 是同步函数，单周期内立即返回。算法与 `FIND` 一致——朴素子串扫描：从 `STR1` 第 1 字符起逐位置尝试匹配 `STR2`，第一次完整匹配时返回该匹配起点的字符位置；扫到末尾无匹配则返回 `0`。**唯一不同**是计数单位：本函数按 UCS-2 字符（2 字节单元）计数，所以汉字 / emoji 都算 1 个字符，返回的位置可以直接传给 `WMID` / `WLEFT` / `WDELETE` 作为参数，而不必再做字节-字符转换。大小写敏感、空串行为未规范、只返回第一次出现位置等语义都与 `FIND` 完全一致。

PDF §5.3 原例：`WFIND("SUXYSI", "XY")` → `3`。

**关键语义**：

- 大小写敏感；
- `STR2 = ""` 时 ⚠️ 行为未规范，调用前自己 `IF WLEN(STR2) > 0 THEN`；
- 只返回首次匹配位置；
- 按字符计数（Unicode 安全）。

## 4. 错误码 / 返回值

无错误码。返回 `INT`：0 = 未找到，1..WLEN(STR1) = 找到位置。

## 5. 使用注意 / 常见坑

- **大小写敏感**：要不区分大小写就先把两侧统一大写或小写再 `WFIND`。
- **空子串未定义** ⚠️：先 `IF WLEN(STR2) > 0 THEN` 拦一道。
- **配合 WMID/WLEFT/WRIGHT**：`WFIND` 返回字符位置，可直接传给这些函数，不用换算字节。
- **WSTRING 字面量用双引号**：搜索目标必须 `WSTRING`，不能传 `'abc'`（单引号 STRING）。
- **只找第一次**：循环找下一次必须先 `WDELETE` 掉已找到段；
- **找全部用循环**：`WHILE WFIND(s, t) > 0 DO ... END_WHILE`。
- **大文本性能 O(N×M)**：长 WSTRING 频繁搜索要考虑预处理。
- **0 vs 位置 1**：`IF WFIND(s,t) THEN` 不可用；必须 `IF WFIND(s,t) > 0 THEN`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WFIND.TcPOU`](../examples/P_Demo_WFIND.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 场景：中文配置串 "IP：192.168.1.10，端口：502" 用全角逗号分段，先用 WFIND 定位
PROGRAM P_Demo_WFIND
VAR
    sConfig  : WSTRING(255) := "IP：192.168.1.10，端口：502";
    sDelim   : WSTRING(255) := "，";
    nDelimPos: INT;
    bSearch  : BOOL;
END_VAR

IF bSearch THEN
    nDelimPos := WFIND(sConfig, sDelim);
    bSearch := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：中文配置串中定位全角分隔符（`，` / `：`）、找中文报警里的关键词位置以便切段、HMI 输入的中文电邮里找 `@` 校验。
- **价值**：返回字符位置而不是字节位置，下游 `WMID` / `WLEFT` 直接基于该值切段，无须任何换算。
- **替代方案对比**：
  - **`FIND` + UTF-8 STRING**：能存中文但返回字节位置，下游切段要算 3 字节/汉字
  - **`Tc2_Utilities` 扩展**：有支持起点、大小写不敏感的扩展查找
  - **本 FC**：IEC 标准、Unicode 安全、签名直观

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §5.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/2260754827.html
- **相关 FC**：`FIND`（STRING 版本）、`WMID`、`WLEFT`、`WRIGHT`（基于位置切段）、`WDELETE`、`WREPLACE`
