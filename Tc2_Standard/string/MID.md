# MID

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Standard` |
| Library Version | `1.3.4` |
| Type | `FUNCTION` |
| Category | `String functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74420235.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_MID.xml`](../examples/P_Demo_MID.xml) |

---

## 1. 功能简述

`MID` 是 **IEC 61131-3 标准字符串函数**，返回字符串 `STR` 中**自第 `POS` 个字符起、连续 `LEN` 个字符**组成的新串。PDF §4.7 原话："Retrieve LEN characters from the STR string beginning with the character at position POS"。返回类型 `STRING(255)`。

它是"切段三件套"中的中间段函数：`LEFT` 取左段，`RIGHT` 取右段，`MID` 取**任意位置的中段**。配合 `FIND` 用得最多——先定位两个分隔符位置，再 `MID(s, pos2-pos1-1, pos1+1)` 提取中间的字段。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION MID : STRING(255)
VAR_INPUT
    STR : STRING(255);
    LEN : INT;
    POS : INT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `STR` | `STRING(255)` | 源字符串 |
| `LEN` | `INT` | 要提取的字符数 |
| `POS` | `INT` | 提取起点位置，**从 1 开始**计数（第 1 字符 `POS = 1`） |

### 返回值

`STRING(255)`：自 `STR` 第 `POS` 字符起的连续 `LEN` 个字符组成的子串。

### VAR_OUTPUT / VAR_IN_OUT

无。

## 3. 行为说明

`MID(STR, LEN, POS)` 是同步函数，单周期内立即返回。算法等同：从 `STR` 第 `POS` 个字符开始，连续向右复制 `LEN` 个字符到结果缓冲，末尾补 `0x00`。若 `POS + LEN - 1` 超出 `STR` 实际长度，PDF 与 InfoSys 均未明确，⚠️ 工程上一般观察到返回从 `POS` 起到字符串末尾的所有剩余字符（不补空格也不报错），但**为避免依赖未规范行为，必须自己 `LEN(STR)` 校验后再调用**。

PDF §4.7 原例：`MID('SUSI', 2, 2)` → 从第 2 字符起取 2 字符 → `'US'`。

**关键语义**：

- **入参顺序：先长度后位置**——`MID(STR, LEN, POS)` 容易和 `REPLACE(STR1, STR2, L, P)`、`DELETE(STR, LEN, POS)` 混淆，注意 LEN 在前 POS 在后；
- **`POS = 1`**：从第 1 字符开始取，等价于 `LEFT(STR, LEN)`；
- **`POS + LEN - 1 = LEN(STR)`**：刚好取到末尾；
- **越界**：⚠️ 未规范，禁止依赖；
- **不修改入参**。

## 4. 错误码 / 返回值

无错误码。返回值始终 `STRING(255)`。无法从返回值判断是否发生了越界——调用方必须保证 `POS >= 1`、`LEN >= 0`、`POS + LEN - 1 <= LEN(STR)`。

## 5. 使用注意 / 常见坑

- **入参顺序坑**：`MID(s, LEN, POS)`——LEN 在 POS 前。每年都有工程师把它写成 `MID(s, POS, LEN)` 拿到错误结果。
- **`POS` 从 1 开始**：`MID(s, 3, 0)` 行为未规范。要"从第 1 字符开始取" `POS = 1`。
- **越界静默**：传入越界 `POS` / `LEN` 不会编译错也不会运行时报错，行为随 TwinCAT 版本可能不同——严格自己校验。
- **配合 `FIND` 切中段**：标准模式 `s_mid := MID(s, p2-p1-1, p1+1);` 其中 `p1`、`p2` 是左右分隔符位置。
- **UTF-8 中文按字节算**：`MID('中文', 1, 1)` 返回一个汉字的第一个字节（乱码）。Unicode 用 `WMID`。
- **`LEN = 0`**：返回空串；
- **返回容器始终 STRING(255)**：即使只取 2 字符，容器仍是 255 字节，赋值给短 STRING 变量会再截断。
- **典型工业场景**：从协议帧 `STX|01|02|03|ETX` 中按字段位置提取每个字段——`MID(s, 2, 5)` 取 `'01'`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_MID.xml`](../examples/P_Demo_MID.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）

```iecst
// 场景：从 'IP:192.168.1.10,PORT:502' 中用 FIND + MID 提取中间 IP 段
PROGRAM P_Demo_MID
VAR
    sConfig   : STRING(255) := 'IP:192.168.1.10,PORT:502';
    sIP       : STRING(255);
    nStart    : INT := 4;             // 'IP:' 占 3 字符 → IP 起点是第 4
    nLength   : INT := 12;            // '192.168.1.10' 共 12 字符
    bExtract  : BOOL;
END_VAR

IF bExtract THEN
    sIP := MID(sConfig, nLength, nStart);
    bExtract := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：从协议帧固定位置提取设备 ID / 长度字段 / 校验段、从订单号中间取部门编码、从时间戳串 `'2026-05-11 12:34:56'` 提取小时 `MID(s, 2, 12)`。
- **价值**：单次调用拿到任意位置子段，比 `LEFT` + `RIGHT` 串接简洁。
- **替代方案对比**：
  - **`LEFT(RIGHT(s, total-pos+1), len)`**：能等价但绕弯
  - **`DELETE` 删左右两侧**：能做但要算两次长度
  - **手写循环 + 字节复制**：完全等价但代码长
  - **本 FC**：IEC 标准、签名直观（位置+长度），中段提取首选

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Standard_EN.pdf) §4.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_standard/74420235.html
- **相关 FC**：`LEFT`（取左段）、`RIGHT`（取右段）、`FIND`（先定位再 MID）、`WMID`（WSTRING 版本）
