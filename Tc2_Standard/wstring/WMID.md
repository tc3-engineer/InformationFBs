# WMID

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions (WSTRING)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/2260775307.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_WMID.TcPOU`](../examples/P_Demo_WMID.TcPOU) |

---

## 1. 功能简述

`WMID` 是 **IEC 61131-3 标准字符串函数 `MID` 的 WSTRING 版本**，返回 WSTRING 字符串 `STR` 中**自第 `POS` 个字符起、连续 `LEN` 个字符**组成的新串。PDF §5.7 原话："Fetch LEN characters from WSTRING STR beginning with the character at position POS"。返回类型 `WSTRING(255)`。

与 `MID` 的关键区别：所有位置和长度按 UCS-2 字符（2 字节单元）计数，汉字 / emoji 都算 1 个字符。这让"取中间 N 个字符"对 Unicode 文本得到符合视觉预期的结果，不会拆出半个汉字。

它是 WSTRING 切段三件套的中段函数：`WLEFT` / `WRIGHT` / `WMID`，三者都基于 1-based 字符位置。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION WMID : WSTRING(255)
VAR_INPUT
    STR : WSTRING(255);
    LEN : INT;
    POS : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR` | `WSTRING(255)` | 源 WSTRING |
| `LEN` | `INT` | 要提取的**字符数**（按 UCS-2 字符算） |
| `POS` | `INT` | 提取起点位置，**从 1 开始**计数 |

### 返回值

`WSTRING(255)`：自 `STR` 第 `POS` 字符起的连续 `LEN` 个字符组成的子串。

### VAR_OUTPUT / VAR_IN_OUT

无。

## 3. 行为说明

`WMID(STR, LEN, POS)` 是同步函数，单周期内立即返回。算法等同 `MID` 但按 UCS-2 字符单元：从 `STR` 第 `POS` 个 UCS-2 字符开始连续向右复制 `LEN` 个字符到结果缓冲，末尾补 `0x0000`。若 `POS + LEN - 1` 超出 `STR` 实际字符数，PDF 与 InfoSys 均未明确具体行为，⚠️ 工程上一般观察到返回从 `POS` 起到末尾的所有剩余字符。`LEN = 0` 返回空串；`POS = 1` 时等价于 `WLEFT(STR, LEN)`；`POS + LEN - 1 = WLEN(STR)` 刚好取到末尾。**入参顺序是 (STR, LEN, POS)——LEN 在 POS 前**，和 `MID` 一致但与 C / Python 习惯不同。

PDF §5.7 原例：`WMID("SUSI", 2, 2)` → 从第 2 字符起取 2 字符 → `"US"`。

**关键语义**：

- 入参顺序：**LEN 在 POS 前**；
- `POS` 从 1 起；
- `LEN` 与 `POS` 按 UCS-2 字符计数；
- 越界 ⚠️ 未规范；
- 不修改入参。

## 4. 错误码 / 返回值

无错误码。返回值始终 `WSTRING(255)`。

## 5. 使用注意 / 常见坑

- **入参顺序坑**：`WMID(s, LEN, POS)`——LEN 在前 POS 在后。每年都有工程师写成 `WMID(s, POS, LEN)`。
- **`POS` 从 1 开始**：要"从第 1 字符开始取" `POS = 1`。
- **越界静默**：传入越界 `POS` / `LEN` 不会编译错也不报错，⚠️ 行为不可预期；
- **配合 `WFIND` 切中段**：`s_mid := WMID(s, p2-p1-1, p1+1);` 其中 `p1` `p2` 是左右分隔符字符位置。
- **按字符不按字节**：取 1 个汉字传 `LEN := 1`；
- **WSTRING 字面量双引号**；
- **`LEN = 0`** → 返回空串。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_WMID.TcPOU`](../examples/P_Demo_WMID.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 场景：从 "IP：192.168.1.10，端口：502" 中提取中间 IP 段 "192.168.1.10"
PROGRAM P_Demo_WMID
VAR
    sConfig  : WSTRING(255) := "IP：192.168.1.10，端口：502";
    sIP      : WSTRING(255);
    nStart   : INT := 4;            // "IP：" 占 3 字符 → IP 起点 = 第 4 字符
    nLength  : INT := 12;           // "192.168.1.10" 共 12 字符
    bExtract : BOOL;
END_VAR

IF bExtract THEN
    sIP := WMID(sConfig, nLength, nStart);
    bExtract := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：从中文配置串提取中间 IP / 端口字段、从带中文前缀的订单号取中段流水段、从时间戳串 "2026年05月11日 12:34:56" 提取 "12:34" 段。
- **价值**：UCS-2 安全，按字符算位置和长度，结果符合视觉预期。
- **替代方案对比**：
  - **`MID` + UTF-8 STRING**：能存中文但按字节算位置和长度，每次都要换算
  - **`WLEFT(WRIGHT(s, total-POS+1), LEN)`**：能等价但绕弯
  - **本 FC**：IEC 标准、Unicode 安全、签名直观

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §5.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/2260775307.html
- **相关 FC**：`MID`（STRING 版本）、`WLEFT`、`WRIGHT`、`WFIND`（先定位再 WMID）、`WLEN`
