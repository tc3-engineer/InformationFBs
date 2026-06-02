# WRIGHT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions (WSTRING)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/2260779147.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_WRIGHT.TcPOU`](../examples/P_Demo_WRIGHT.TcPOU) |

---

## 1. 功能简述

`WRIGHT` 是 **IEC 61131-3 标准字符串函数 `RIGHT` 的 WSTRING 版本**，返回 WSTRING 字符串 `STR` 最右边的 `SIZE` 个字符组成的新串。PDF §5.9 原话："Take the first SIZE characters from the right in WString STR"——从右往左数 `SIZE` 个字符。返回类型 `WSTRING(255)`。

与 `RIGHT` 的关键区别：按 UCS-2 字符（2 字节单元）计数。"取最后 N 个字符"对 Unicode 文本得到符合视觉预期的结果——汉字 / emoji 都算 1 个字符，不会拆出半个。

`WLEFT` / `WRIGHT` / `WMID` 构成 WSTRING 切段三件套：左、右、中段；`WRIGHT` 专取尾巴。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION WRIGHT : WSTRING(255)
VAR_INPUT
    STR   : WSTRING(255);
    SIZE  : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR` | `WSTRING(255)` | 源 WSTRING |
| `SIZE` | `INT` | 要取的**字符数**（从右边数，按 UCS-2 字符算） |

### 返回值

`WSTRING(255)`：`STR` 最右边的 `SIZE` 个字符组成的新串。

### VAR_OUTPUT / VAR_IN_OUT

无。

## 3. 行为说明

`WRIGHT(STR, SIZE)` 是同步函数，单周期内立即返回。算法等同 `RIGHT` 但按 UCS-2 字符单元：先用 `WLEN(STR)` 算出源串字符数 `n`，从第 `n - SIZE + 1` 个字符开始连续取 `SIZE` 个字符复制到结果缓冲，末尾补 `0x0000` 结束符。当 `SIZE` 超过 `n` 时按 IEC 行为返回整个 `STR`，不补空格也不报错。`SIZE = 0` 时返回空串 `""`；`SIZE < 0` 时 ⚠️ PDF + InfoSys 均未明确，禁止传入负数。

PDF §5.9 原例：`WRIGHT("SUSI", 3)` → 取最右 3 字符 → `"USI"`。

**关键语义**：

- 按 UCS-2 字符计数；
- `SIZE >= WLEN(STR)` → 返回整个 `STR`；
- `SIZE = 0` → 返回空串；
- `SIZE < 0` ⚠️ 未规范；
- 不修改入参。

## 4. 错误码 / 返回值

无错误码。返回 `WSTRING(255)`。

## 5. 使用注意 / 常见坑

- **`SIZE` 是字符数不是字节数**：`WRIGHT("中文测试", 2)` = `"测试"`；
- **WSTRING 字面量双引号**；
- **超长 SIZE 不报错**：返回整个源串；
- **配合 `WFIND` 切右半**：`s_right := WRIGHT(s, WLEN(s) - WFIND(s, "："))`；
- **空 WSTRING 安全**：`WRIGHT("", 5)` = `""`；
- **取文件扩展名**：典型模式 `WRIGHT(sFile, 4)` 取 `.csv` 后 4 字符。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WRIGHT.TcPOU`](../examples/P_Demo_WRIGHT.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 场景：从订单号 "客户A订单20260511-00123" 取尾 5 位 "00123" 流水号
PROGRAM P_Demo_WRIGHT
VAR
    sOrderID  : WSTRING(255) := "客户A订单20260511-00123";
    sSerial   : WSTRING(255);
    nSerialLen: INT := 5;
    bRun      : BOOL;
END_VAR

IF bRun THEN
    sSerial := WRIGHT(sOrderID, nSerialLen);
    bRun := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：从中文订单号取尾段流水号、取中文文件名后缀、取时间戳尾段秒位、HMI 显示长字符串末段。
- **价值**：UCS-2 安全，取后 N 字符就是 N 字符。
- **替代方案对比**：
  - **`RIGHT` + UTF-8 STRING**：按字节，可能拆汉字
  - **`WMID(s, n, WLEN(s)-n+1)`**：能等价但绕弯
  - **本 FC**：IEC 标准、Unicode 安全、签名直观

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §5.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/2260779147.html
- **相关 FC**：`RIGHT`（STRING 版本）、`WLEFT`、`WMID`、`WFIND`、`WLEN`
