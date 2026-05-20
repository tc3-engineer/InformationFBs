# DATA_TO_HEXSTR

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35077643.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_DATA_TO_HEXSTR.xml`](../examples/P_Demo_DATA_TO_HEXSTR.xml) |

---

## 1. 功能简述

把任意二进制数据（简单类型、结构体）按字节顺序转成空格分隔的十六进制字符串。最大支持 85 字节；若 `cbData > 85`，结果在转完前几十字节后追加一个 `'.'` 并中止后续转换。`pData = 0` 或 `cbData = 0` 时返回空串。

`bLoCase` 控制结果中字母大小写（`FALSE` → `'AB CD'`，`TRUE` → `'ab cd'`）。注意 PLC 在 x86/x64/Arm 上是小端存储，所以 `DWORD := 16#BECF1234` 经本函数得到的字符串是 `'34 12 CF BE'`（最低字节先）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pData   : POINTER TO BYTE;
    cbData  : UDINT(0..85);
    bLoCase : BOOL := FALSE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pData` | `POINTER TO BYTE` | — | 待转换数据起始地址，常用 `ADR()` 取得。 |
| `cbData` | `UDINT(0..85)` | — | 数据长度（字节），上限 85；常用 `SIZEOF()` 取得。 |
| `bLoCase` | `BOOL` | `FALSE` | `TRUE` = 输出小写 `a-f`；`FALSE` = 输出大写 `A-F`。 |

### VAR_IN_OUT

无。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `T_MaxString` | 空格分隔的两位十六进制字符串。如 `'34 12 CF BE'`。超长截断追加 `'.'`，无效参数返回 `''`。 |

### VAR_OUTPUT

无。

## 3. 行为说明

函数从 `pData` 起读取最多 `cbData` 字节，对每个字节生成两位 hex（高位在前），字节之间插一个空格：

- `pData = 0` 或 `cbData = 0` → 返回 `''`
- 1 字节 `16#07` → `'07'`（一字节末尾无空格）
- 4 字节 DWORD `16#BECF1234` → `'34 12 CF BE'`（小端）
- `cbData > 85` → 转换前 N 字节后中止，末尾追加 `'.'` 表示溢出（例如 `'00 00 ... 00.'`）

`bLoCase` 仅影响字母 `A-F` 的大小写，数字 0-9 不变。

边界长度：`cbData <= 85` 时，结果最长 `85 * 3 - 1 = 254` 字符，刚好装入 `T_MaxString`（容量 255）。该上限是 PDF 显式规定，超出即触发"加点中止"逻辑。

与 `HEXSTR_TO_DATA` 是一对反函数：先 `sH := DATA_TO_HEXSTR(ADR(d), SIZEOF(d), FALSE)`，再 `HEXSTR_TO_DATA(sH, ADR(d2), SIZEOF(d2))` 应能恢复原始字节。

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| 非空字符串（无 `.`） | 完整转换 |
| 末尾带 `.` 的字符串 | `cbData > 85`，被截断 |
| `''` | `pData = 0` 或 `cbData = 0` |

## 5. 使用注意 / 常见坑

- **小端字节序**：DWORD `16#BECF1234` → `'34 12 CF BE'`，写日志时容易看反；需要大端展示先 `SWAP()`。
- **85 字节上限**：超出会被截断 + 加 `'.'`；要转长 buffer 用 `DATA_TO_HEXSTR2`（同库 16#FFFFFFFF 长上限）。
- **结构体含填充字节**：编译器对齐填充也会被转，可能看到意料外的 `00`；用 `{attribute 'pack_mode' := '1'}` 或 `MEMSET` 清零。
- **不可直接传 `STRING` 变量**：要 `ADR(s)`，否则传的是值，类型不匹配。
- **数字 0-9 不受 `bLoCase` 影响**：只有 A-F 受控；产线日志统一大写或小写按规范即可。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DATA_TO_HEXSTR.xml`](../examples/P_Demo_DATA_TO_HEXSTR.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_DATA_TO_HEXSTR
VAR
    dwSerial : DWORD := 16#BECF1234;
    sHex     : T_MaxString;
END_VAR

sHex := DATA_TO_HEXSTR(pData := ADR(dwSerial), cbData := SIZEOF(dwSerial), bLoCase := FALSE);
// sHex = '34 12 CF BE'  (小端字节序)
```

## 7. 业务场景与实际价值

- **场景**：把 EtherCAT 主站 ESC 寄存器、CoE SDO 应答、Modbus 寄存器组的原始字节快照写到诊断日志，方便事后比对协议规范。
- **价值**：单调用替代手写 hex 格式化循环；空格分隔可直接和 Wireshark / 协议规范对照。
- **替代方案对比**：
  - 手写 `FOR i := 0 TO N DO sHex := CONCAT(sHex, ...);`：性能差、易写错（漏 0 填充）
  - `F_FormatString` + `%02X`：单字节可，整段不便
  - 本函数：一次转 85 字节，自动空格分隔

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.22 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35077643.html
- **相关函数**：`HEXSTR_TO_DATA`（反向）、`DATA_TO_HEXSTR2`（长度上限更高）、`BYTE_TO_HEXSTR` / `WORD_TO_HEXSTR` 等单值版本
