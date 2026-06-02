# RIGHT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74423307.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_RIGHT.TcPOU`](../examples/P_Demo_RIGHT.TcPOU) |

---

## 1. 功能简述

`RIGHT` 是 **IEC 61131-3 标准字符串函数**，返回字符串 `STR` 最右边的 `SIZE` 个字符组成的新串。PDF §4.9 原话："take the first SIZE characters from the right in the STR string"——从右往左数 `SIZE` 个字符。

返回类型 `STRING(255)`。等价于"截后 N 字符"。`LEFT` / `RIGHT` / `MID` 构成"切段三件套"：左、右、中段；`RIGHT` 专取尾巴。

工程上常用：取文件名扩展名（`RIGHT(s, 3)` 取 `.csv` 之类的后 3 字符）、取协议帧尾部固定字段（如 CRC、ETX 标记位）、HMI 显示中只显示订单号后 4 位、从时间戳 `'2026-05-11 12:34:56'` 取秒位 `RIGHT(s, 2)`。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION RIGHT : STRING(255)
VAR_INPUT
    STR  : STRING(255);
    SIZE : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR` | `STRING(255)` | 源字符串 |
| `SIZE` | `INT` | 要取的字符数（从右边数） |

### 返回值

`STRING(255)`：`STR` 最右边的 `SIZE` 个字符组成的新串。

### VAR_OUTPUT / VAR_IN_OUT

无。

## 3. 行为说明

`RIGHT(STR, SIZE)` 是同步函数，单周期内立即返回。算法等同：先用 `LEN(STR)` 算出源串实际长度 `n`，从第 `n - SIZE + 1` 个字符开始连续取 `SIZE` 个字符复制到结果缓冲，末尾补 `0x00`。当 `SIZE` 超过 `n` 时，按 IEC 标准行为返回整个 `STR`，不补空格也不报错。`SIZE = 0` 时返回空串 `''`；`SIZE < 0` 时 PDF 与 InfoSys 均未明确，⚠️ 工程上禁止传入负数。

PDF §4.9 原例：`RIGHT('SUSI', 3)` → 取最右 3 字符 → `'USI'`。

**关键语义**：

- **从右往左数 `SIZE` 个字符**：注意是"字符数"不是"下标"；
- **`SIZE >= LEN(STR)`**：返回整个 `STR`；
- **`SIZE = 0`**：返回空串；
- **`SIZE < 0`**：⚠️ 行为未规范；
- **不修改入参**。

## 4. 错误码 / 返回值

无错误码。返回值始终 `STRING(255)`。若 `LEN(返回值) < SIZE`，说明源串本身就比 `SIZE` 短。

## 5. 使用注意 / 常见坑

- **`SIZE` 是字符数**：`RIGHT(s, 3)` 取最右 3 字符。常被误以为"从下标 3 到末尾"。
- **超长 SIZE 不报错**：返回整个源串，不补空格。
- **配合 `FIND` 切右半段**：标准模式 `s_right := RIGHT(s, LEN(s) - FIND(s, ':'))`，能完成"提取冒号后部分"的需求。注意 `FIND` 返回 0 时不能减。
- **取文件扩展名**：`RIGHT(sFile, 3)` 取 `.csv` / `.xml` 后 3 字符（含点号），更稳妥的写法是先 `FIND(sFile, '.')` 找点号位置再 `RIGHT`。
- **UTF-8 中文按字节算**：`RIGHT('中文', 3)` 取的是最后 3 字节，正好是一个汉字。Unicode 用 `WRIGHT`。
- **空串安全**：`RIGHT('', 5)` 返回 `''`。
- **返回容器始终 STRING(255)**：即使只取 3 字符，容器仍是 255 字节。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_RIGHT.TcPOU`](../examples/P_Demo_RIGHT.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

```iecst
// 场景：订单号 'ORD2026051100123' 最后 5 位是流水号，HMI 显示时只展示流水号
PROGRAM P_Demo_RIGHT
VAR
    sOrderID  : STRING(255) := 'ORD2026051100123';
    sSerial   : STRING(255);            // 提取出的流水号
    nSerialLen: INT := 5;               // 流水号固定 5 位
    bRun      : BOOL;
END_VAR

IF bRun THEN
    sSerial := RIGHT(sOrderID, nSerialLen);
    bRun := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：取文件扩展名、取订单流水号尾段、取时间戳秒位、取协议帧尾部 CRC 字段、HMI 显示长字符串时只显示后 N 位。
- **价值**：一行调用完成"取后 N 字符"，无需关心源串长度。
- **替代方案对比**：
  - **`MID(s, n, LEN(s)-n+1)`**：能等价但要算两次长度
  - **`DELETE` 从左往右删**：能做但要先算长度
  - **手写循环**：约 8 行 ST
  - **本 FC**：IEC 标准、签名直观（取后 N 字符），尾段提取首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §4.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74423307.html
- **相关 FC**：`LEFT`（取左段）、`MID`（取中段）、`FIND`（先定位再 RIGHT）、`LEN`（先看长度）、`WRIGHT`（WSTRING 版本）
