# CHR

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SerialCom` |
| Library Version | `1.8.1` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85911691.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_CHR.TcPOU`](../examples/P_Demo_CHR.TcPOU) |

---

## 1. 功能简述

把输入变量 `c` 中的 ASCII 码转换为对应字符，以字符串形式返回。串口接收到的字符常以字节形式到达 PLC，而后续处理往往需要字符串形式，`CHR` 就用于把单个字节还原成单字符字符串，便于拼接成可读字符串。

## 2. 接口定义

### Syntax

```iecst
FUNCTION CHR : STRING
VAR_INPUT
   c : BYTE;
END_VAR
```

### VAR_INPUT

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `c` | `BYTE` | — | 要转换的 ASCII 码 |

### 返回值

| 类型 | 说明 |
|---|---|
| `STRING` | 该 ASCII 码对应的单字符字符串 |

## 3. 行为说明

纯函数，调用即返回，无副作用、无异步状态：传入一个字节，返回它对应的单字符字符串。例如 `CHR(16#41)` 返回 `'A'`。同一输入重复调用返回相同结果。它是 `ASC` 的逆操作（`ASC` 把字符串首字符转成字节）。典型用法是把 `ReceiveByte` 收到的字节逐个转成字符，再用 `CONCAT` 拼成完整字符串供后续解析。注意若字节为 16#00，转出的是空字符 `$00`，拼进字符串会成为 IEC 字符串结束符——处理可能含 0 字节的二进制流应避免用字符串方式。

## 4. 错误码 / 返回值

无错误码——纯函数，恒返回一个单字符 `STRING`。

## 5. 使用注意 / 常见坑

- **逆操作是 `ASC`**：字符转字节用 `ASC`。
- **0 字节注意**：`CHR(0)` 返回 `$00`，拼进字符串会被当作结束符截断后续内容；含 0 字节的数据别用字符串拼接（工程经验补充）。
- **逐字节拼串开销**：大量字符逐个 `CHR` + `CONCAT` 效率不高，可考虑直接用 `ReceiveString` 一次收成字符串。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_CHR.TcPOU`](../examples/P_Demo_CHR.TcPOU)

```iecst
// 场景：把收到的字节 16#41 还原为字符 'A'，拼进显示字符串。
PROGRAM P_Demo_CHR
VAR
    byReceived : BYTE := 16#41;
    sChar      : STRING;
END_VAR

sChar := CHR(byReceived);                        // 结果 'A'
```

## 7. 业务场景与实际价值

- **场景**：把 `ReceiveByte` 逐字节收到的数据还原成字符、拼成可读字符串，用于 HMI 显示或文本协议解析。
- **价值**：一行调用把字节转字符，免去查码表；与 `ASC` 配对完成字符 / 字节互转。
- **替代方案对比**：整段文本直接用 `ReceiveString` 一次收成字符串更省事；只在逐字节处理流程里需要把单字节转字符时用 `CHR`。

## 8. 参考资料

- **PDF**：[TF6340_TC3_Serial_Communication_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf) §5.2.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85911691.html
- **相关**：`ASC`（字符转字节，逆操作）、`ReceiveByte`（收字节）、`ReceiveString`（直接收成字符串）
