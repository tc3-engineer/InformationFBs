# WLEFT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions (WSTRING)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/2260771467.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_WLEFT.TcPOU`](../examples/P_Demo_WLEFT.TcPOU) |

---

## 1. 功能简述

`WLEFT` 是 **IEC 61131-3 标准字符串函数 `LEFT` 的 WSTRING 版本**，返回 WSTRING 字符串 `STR` 最左边的 `SIZE` 个字符组成的新串。PDF §5.5 原话："Take the first SIZE characters from the left in WString STR"。返回类型 `WSTRING(255)`。

与 `LEFT` 的关键区别：**按 UCS-2 字符（2 字节单元）计数**，汉字 / emoji 都算 1 个字符。这让"取前 N 个字符"对 Unicode 文本得到符合视觉预期的结果——`WLEFT("中文测试", 2)` 拿到的是 `"中文"` 两个完整汉字，不会拆出半个字符。

工程上常用：取中文订单号前缀分流、取中文日志等级标记、HMI 显示中文长字符串前 N 字以截断长名字。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION WLEFT : WSTRING(255)
VAR_INPUT
    STR  : WSTRING(255);
    SIZE : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR` | `WSTRING(255)` | 源 WSTRING |
| `SIZE` | `INT` | 要取的**字符数**（按 UCS-2 字符单元计数） |

### 返回值

`WSTRING(255)`：`STR` 最左边的 `SIZE` 个字符组成的新串。

### VAR_OUTPUT / VAR_IN_OUT

无。

## 3. 行为说明

`WLEFT(STR, SIZE)` 是同步函数，单周期内立即返回。算法等同 `LEFT` 但按 UCS-2 字符单元：从 `STR` 第 1 个 UCS-2 字符开始连续取 `SIZE` 个字符复制到结果缓冲，末尾补 `0x0000` 结束符。当 `SIZE` 超过 `STR` 实际字符数时按 IEC 行为返回**整个 `STR`**（不补空格也不报错）；`SIZE = 0` 时返回空串 `""`；`SIZE < 0` 时 PDF + InfoSys 均未明确，⚠️ 工程上禁止传入负数。

PDF §5.5 原例：`WLEFT("SUSI", 3)` → `"SUS"`。

**关键语义**：

- 按 UCS-2 字符计数，汉字 / emoji = 1 个字符；
- `SIZE >= WLEN(STR)` → 返回整个 `STR`；
- `SIZE = 0` → 返回空串；
- `SIZE < 0` 未规范；
- 不修改入参。

## 4. 错误码 / 返回值

无错误码。返回值始终 `WSTRING(255)`。

## 5. 使用注意 / 常见坑

- **按字符不按字节**：`WLEFT("中文测试", 2)` = `"中文"`，不是"前 2 字节"；
- **WSTRING 字面量双引号**；
- **超长 SIZE 不报错**，返回整个源串；
- **配合 `WFIND` 切左半**：`s_left := WLEFT(s, WFIND(s, "：") - 1)`，先定位再截前；
- **HMI 长名字截断**：常见模式 `s_short := WLEFT(s, 20) + "..."` 显示前 20 字 + 省略号；
- **空 WSTRING 安全**：`WLEFT("", 5)` = `""`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WLEFT.TcPOU`](../examples/P_Demo_WLEFT.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 场景：中文订单号 "客户A订单20260511_00123" 前 4 字 "客户A订" 是部门编码
PROGRAM P_Demo_WLEFT
VAR
    sOrderID  : WSTRING(255) := "客户A订单20260511_00123";
    sDeptCode : WSTRING(255);
    nCodeLen  : INT := 4;
    bRun      : BOOL;
END_VAR

IF bRun THEN
    sDeptCode := WLEFT(sOrderID, nCodeLen);
    bRun := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：取中文订单号前缀分流、取中文日志等级、HMI 长字符串显示截断、提取中文设备名前 N 字。
- **价值**：UCS-2 安全，取前 N 字符就是 N 字符不会拆汉字。
- **替代方案对比**：
  - **`LEFT` + UTF-8 STRING**：能存中文但按字节，取前 4 字节可能拆出 1.x 个汉字
  - **`WMID(s, n, 1)`**：能等价但语义不直观
  - **本 FC**：IEC 标准、Unicode 安全、签名最直观

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §5.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/2260771467.html
- **相关 FC**：`LEFT`（STRING 版本）、`WRIGHT`、`WMID`、`WFIND`、`WLEN`
