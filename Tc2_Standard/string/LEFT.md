# LEFT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74417163.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_LEFT.xml`](../examples/P_Demo_LEFT.xml) |

---

## 1. 功能简述

`LEFT` 是 **IEC 61131-3 标准字符串函数**，返回字符串 `STR` 最左边的 `SIZE` 个字符组成的新串。PDF §4.5 原话："Take the first SIZE character from the left in the string STR"。

返回类型 `STRING(255)`。等价于"截前 N 字符"。最常配合 `FIND` 使用：先用 `FIND` 找到分隔符位置 `n`，再 `LEFT(s, n-1)` 取分隔符之前的子串。也常用于截取协议帧固定长度的头部、生成 HMI 显示的短摘要、把日志等级前缀单独提出来。

`LEFT` 与 `RIGHT`、`MID` 共同构成"切段三件套"。三者都基于 1-based 字符位置。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION LEFT : STRING(255)
VAR_INPUT
    STR  : STRING(255);
    SIZE : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR` | `STRING(255)` | 源字符串 |
| `SIZE` | `INT` | 要取的字符数（从左边数） |

### 返回值

`STRING(255)`：`STR` 最左边的 `SIZE` 个字符组成的新串。

### VAR_OUTPUT / VAR_IN_OUT

无。

## 3. 行为说明

`LEFT(STR, SIZE)` 同步函数，一个 PLC 周期内立即返回。算法是：把 `STR` 从第 1 个字符开始连续取 `SIZE` 个字符复制到结果缓冲，末尾补 `0x00`。如果 `SIZE` 超过 `STR` 实际长度，PDF 与 InfoSys 均按 IEC 行为返回**整个 `STR`**（不补空格也不报错）。`SIZE = 0` 时返回空串 `''`；`SIZE < 0` 时 PDF + InfoSys 均未明确，⚠️ 工程上禁止传入负数。

PDF §4.5 原例：`LEFT('SUSI', 3)` → `'SUS'`。

**关键语义**：

- **`SIZE` 是字符数不是下标**：`LEFT(s, 3)` 取**前 3 个字符**，而不是"到下标 3 为止"；
- **`SIZE >= LEN(STR)`**：返回整个 `STR`，不做填充；
- **`SIZE = 0`**：返回空串 `''`；
- **`SIZE < 0`**：⚠️ 行为未规范，禁止传入；
- **不修改入参**：值传入。

## 4. 错误码 / 返回值

无错误码。返回值始终是 `STRING(255)`。从返回值长度可以反推：若 `LEN(返回值) < SIZE`，说明 `SIZE` 超过了源串长度。

## 5. 使用注意 / 常见坑

- **`SIZE` 是字符计数**：`LEFT(s, 0)` = 空串；`LEFT(s, 5)` = 前 5 字符。常被误以为"下标 5 之前"。
- **超长 SIZE 不报错**：要源串完整长度可用 `LEFT(s, 255)`，但更优雅的是直接传值。
- **配合 `FIND` 切左半段**：标准模式 `s_left := LEFT(s, FIND(s, ':') - 1)`，能完成"提取冒号前部分"的需求。注意 `FIND` 返回 0 时不能减 1，必须先校验。
- **UTF-8 中文按字节算**：`LEFT(中文串, 3)` 拿到的可能是 1 个汉字（每汉字 3 字节）。Unicode 用 `WLEFT`。
- **返回 STRING(255) 不变**：即使只取 3 字符，容器仍是 255 字节。赋值给 `STRING(80)` 会再截断，**但前几位的有效字符不会丢**（因为只取了 3 字符，远小于 80）。
- **空串安全**：`LEFT('', 5)` 返回 `''`，不会崩溃，可放心调用。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_LEFT.xml`](../examples/P_Demo_LEFT.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）

```iecst
// 场景：日志行 'ERROR Motor overcurrent'，需要提取等级前缀 'ERROR' (前 5 字符)
PROGRAM P_Demo_LEFT
VAR
    sLogLine : STRING(255) := 'ERROR Motor overcurrent';
    sLevel   : STRING(255);             // 提取出的等级前缀
    nWidth   : INT := 5;                // 等级标识固定 5 字符（INFO_ / ERROR / WARN_ 对齐）
    bRun     : BOOL;
END_VAR

IF bRun THEN
    sLevel := LEFT(sLogLine, nWidth);
    bRun := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：提取协议帧固定长度的头部（STX + 长度字段）、取日志行等级前缀做分流、从订单号截取前 6 位作为客户编码、生成 HMI 显示的短预览（取前 20 字符 + "..."）。
- **价值**：一行调用完成"取前 N 字符"，无需关心源串实际长度，超长自动返回整串。
- **替代方案对比**：
  - **`MID(s, n, 1)`**：能等价但语义不直观（中段函数干前段活）
  - **`DELETE` 从右往左删**：能等价但要先 `LEN()` 算长度
  - **手写循环 + 字节复制**：能做但 10 行起步
  - **`Tc2_Utilities` 扩展**：提供 `STRING_TO_*` 系列，重在类型转换不是切段
  - **本 FC**：IEC 标准、签名最直观、零依赖，**首选**

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §4.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74417163.html
- **相关 FC**：`RIGHT`（取右段）、`MID`（取中段）、`FIND`（先定位再 LEFT 截取）、`LEN`（先看长度）、`WLEFT`（WSTRING 版本）
