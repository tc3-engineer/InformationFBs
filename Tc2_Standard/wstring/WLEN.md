# WLEN

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions (WSTRING)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/2260773387.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_WLEN.xml`](../examples/P_Demo_WLEN.xml) |

---

## 1. 功能简述

`WLEN` 是 **IEC 61131-3 标准字符串函数 `LEN` 的 WSTRING 版本**，返回 WSTRING 字符串 `STR` 的**有效字符数**（不含结束符 `0x0000`）。PDF §5.6 原话："outputs the length of a WSTRING"。返回类型 `INT`。

与 `LEN` 的关键区别：**按 UCS-2 字符（2 字节单元）计数**，所以 `WLEN("中文测试") = 4`（4 个汉字）。需要"用户视觉字符数"时必须用 `WLEN`，不能用 `LEN` 或 `SIZEOF` 替代。

它是所有 WSTRING 切段函数的前置探针：调用 `WLEFT` / `WRIGHT` / `WMID` / `WINSERT` / `WDELETE` 前先 `WLEN()` 校验长度，避免越界。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION WLEN : INT
VAR_INPUT
    STR : WSTRING(255);
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR` | `WSTRING(255)` | 待测量的 WSTRING |

### 返回值

`INT`：`STR` 的有效字符数（自第 1 字符起到第一个 `0x0000` 结束符之前的 UCS-2 字符数）。

### VAR_OUTPUT / VAR_IN_OUT

无。

## 3. 行为说明

`WLEN(STR)` 是同步函数，单周期内立即返回。底层算法是逐 UCS-2 字符（2 字节）单元扫描，遇到第一个 `0x0000` 字符停下，返回已扫过的字符数。空 WSTRING 返回 0；255 字符全填且尾部仍有 `0x0000` 时返回 255，再长就需要更大的容器。`WSTRING(255)` 容器声明里的 255 是字符数（容器占 512 字节，含尾部 2 字节结束符），不是字节数；`WLEN` 返回的是有效字符数而不是容器大小。

PDF §5.6 原例：`WLEN("SUSI")` → `4`。

**关键语义**：

- 返回有效字符数，**汉字 / emoji = 1 个字符**；
- 空 WSTRING → 0；
- 中间 `0x0000` 会提前截断扫描，返回截断点之前的字符数；
- 不修改入参。

## 4. 错误码 / 返回值

无错误码。返回 `INT`，永远 ≥ 0，取值范围 0..255。

## 5. 使用注意 / 常见坑

- **返回字符数不是字节数**：`WLEN("中") = 1`；要算字节用 `SIZEOF` 或 `WLEN(s) * SIZEOF(WCHAR)`；
- **WSTRING(255) 容器的 255 是字符**：声明 `WSTRING(255)` 实际占 512 字节，但 `WLEN(s) <= 255`；
- **拼接防截断**：`IF WLEN(s1) + WLEN(s2) > 255 THEN` 是 `WCONCAT` 前的标准守卫；
- **空串安全**：`WLEN("")` = 0，可放心调用；
- **不要用 SIZEOF 误以为是字符数**：`SIZEOF(s)` 是容器字节数，不是有效字符数；
- **频繁调用 O(N)**：长 WSTRING 在循环里频繁 WLEN 会拖性能。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WLEN.xml`](../examples/P_Demo_WLEN.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）

```iecst
// 场景：HMI 中文输入框限制最多 50 字（汉字算 1 字），用 WLEN 校验
PROGRAM P_Demo_WLEN
VAR
    sUserInput : WSTRING(255);
    nCharCount : INT;
    nMaxChars  : INT := 50;
    bAccept    : BOOL;
END_VAR

nCharCount := WLEN(sUserInput);
bAccept := (nCharCount > 0) AND (nCharCount <= nMaxChars);
```

## 7. 业务场景与实际价值

- **场景**：HMI 中文输入长度校验、拼接前防截断、空 WSTRING 保护、协议帧 Unicode 字段长度检查。
- **价值**：直接返回视觉字符数，与 HMI 端 / MES 端的"字符数"语义统一。
- **替代方案对比**：
  - **`LEN`**：处理 STRING，按字节数算长度，对中文返回字节数不是字符数
  - **`SIZEOF`**：返回容器字节数，不是有效字符数
  - **手写循环找 0x0000**：完全等价但浪费代码
  - **本 FC**：IEC 标准、Unicode 安全，**WSTRING 长度查询必备**

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §5.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/2260773387.html
- **相关 FC**：`LEN`（STRING 版本）、`SIZEOF`（容器字节大小）
