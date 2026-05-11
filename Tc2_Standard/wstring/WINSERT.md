# WINSERT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions (WSTRING)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/2260756747.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_WINSERT.xml`](../examples/P_Demo_WINSERT.xml) |

---

## 1. 功能简述

`WINSERT` 是 **IEC 61131-3 标准字符串函数 `INSERT` 的 WSTRING 版本**，把 WSTRING 字符串 `STR2` **插入到 `STR1` 的第 `POS` 个字符之后**。PDF §5.4 原话："Add STR2 in STR1 after the POSth position"。返回类型 `WSTRING(255)`。

与 `INSERT` 的关键区别：所有位置和长度按 UCS-2 字符（2 字节单元）计数，汉字 / emoji = 1 个字符。`POS` 同样表示"插到第 `POS` 字符之后"，`POS = 0` 表示插到最前面，`POS >= WLEN(STR1)` 表示追加到末尾。

工程上典型用途：在中文配置串中间插入新字段、给中文日志加 emoji 等级标记、HMI 显示前对中文字段补充括号注释。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION WINSERT : WSTRING(255)
VAR_INPUT
    STR1 : WSTRING(255);
    STR2 : WSTRING(255);
    POS  : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR1` | `WSTRING(255)` | 主串 |
| `STR2` | `WSTRING(255)` | 待插入的子串 |
| `POS` | `INT` | 插入点：第 `POS` 字符**之后**；`POS = 0` 表示插到最前面 |

### 返回值

`WSTRING(255)`：插入后的新字符串。

### VAR_OUTPUT / VAR_IN_OUT

无。

## 3. 行为说明

`WINSERT(STR1, STR2, POS)` 是同步函数，单周期内立即返回。算法等同 `INSERT` 但按 UCS-2 字符（2 字节单元）操作：把 `STR1` 中 `[1, POS]` 字符区间复制到结果缓冲（保留前缀），整段拷入 `STR2`，再把 `STR1` 的 `[POS+1, end]` 区间追加到结果缓冲，末尾补 `0x0000` 结束符。索引和长度都是 UCS-2 字符单元，汉字 / emoji 都算 1 个字符。`POS = 0` 等价于 `WCONCAT(STR2, STR1)`，插到最前面；`POS >= WLEN(STR1)` 等价于追加到末尾；超 255 字符静默截断。

PDF §5.4 原例：`WINSERT("SUSI", "XY", 2)` → 在第 2 字符后插入 `XY` → `"SUXYSI"`（PDF 例中 IL 注释写成 `"UXYSI"` 是 PDF 印刷笔误，正确结果是 `"SUXYSI"`，与 InfoSys 一致）。

**关键语义**：

- `POS` 是"之后"，`POS = 1` 表示插到第 1 字符后；
- `POS = 0` → 插到最前面；
- 超 255 字符静默截断；
- 不修改入参。

## 4. 错误码 / 返回值

无错误码。返回值始终 `WSTRING(255)`。

## 5. 使用注意 / 常见坑

- **`POS` 是"插到第 N 位之后"**：`WINSERT("AB","X",0)` = `"XAB"`，`WINSERT("AB","X",1)` = `"AXB"`，`WINSERT("AB","X",2)` = `"ABX"`。
- **WSTRING 字面量双引号**：插入子串必须 `"..."`；`'...'` 是 STRING。
- **越界 POS 未规范**：必须先 `IF POS >= 0 AND POS <= WLEN(STR1) THEN`。
- **截断不告警**：超 255 字符尾部丢，先 `WLEN()` 校验。
- **多次插入用循环**：插多段不能链式调用。
- **配合 `WFIND` 实现"标记后插入"**：`s := WINSERT(s, "新字段", WFIND(s, "旧标记") + WLEN("旧标记") - 1);`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WINSERT.xml`](../examples/P_Demo_WINSERT.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）

```iecst
// 场景：中文日志 "信息 电机启动" 要在 "信息" 后插入时间戳 " [12:34:56]"
PROGRAM P_Demo_WINSERT
VAR
    sLog        : WSTRING(255) := "信息 电机启动";
    sTimestamp  : WSTRING(255) := " [12:34:56]";
    sResult     : WSTRING(255);
    nInsertPos  : INT := 2;           // 插到第 2 字符（"息"）之后
    bRun        : BOOL;
END_VAR

IF bRun THEN
    sResult := WINSERT(sLog, sTimestamp, nInsertPos);
    bRun := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：给中文日志加时间戳、给中文报警插入设备编号、给 HMI 输入串中间补全 emoji 标识、协议中插入 Unicode 字段。
- **价值**：UCS-2 安全。插入点 `POS` 按字符算，不必计算汉字字节数。
- **替代方案对比**：
  - **`INSERT` + UTF-8 STRING**：能存中文但要按字节算 `POS`
  - **`WLEFT + WCONCAT + WRIGHT`**：能等价但 4 步
  - **本 FC**：IEC 标准、Unicode 安全、签名直观

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §5.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/2260756747.html
- **相关 FC**：`INSERT`（STRING 版本）、`WDELETE`（逆操作）、`WREPLACE`（覆盖式替换）、`WCONCAT`（首尾拼接特例）
