# SendString255

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SerialCom` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/5291300875.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_SendString255.TcPOU`](../examples/P_Demo_SendString255.TcPOU) |

---

## 1. 功能简述

与 `SendString` 完全相同的字符串发送功能块，唯一区别是输入 `SendString` 的长度为 255 字符（`SendString` 为 80）。向 `TxBuffer` 对应的串口发送一个最长 255 字符的字符串。适合发送较长的文本命令或报文。真正的发送由后台功能块 `SerialLineControl` / `SerialLineControlADS` 异步完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  SendString         : STRING(255);
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `SendString` | `STRING(255)` | — | 要发送的字符串（最多 255 字符） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
  TxBuffer         : ComBuffer;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `TxBuffer` | `ComBuffer` | 与所用串口对应的发送数据缓冲区 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  Busy            : BOOL;
  Error           : ComError_t;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | 为 `TRUE` 时发送未完成；`Busy = FALSE` 且 `Error = 0` 表示发送成功。首次调用即发出则 `Busy` 不变 `TRUE`；数据发完 / 出错 / 超时后 `Busy` 变 `FALSE` |
| `Error` | `ComError_t` | 发生故障时返回错误码 |

## 3. 行为说明

行为与 `SendString` 一字不差，仅输入字符串可达 255 字符。调用即把 `SendString` 的内容交给 `TxBuffer`，由后台通信功能块异步发往硬件。功能块按字符串实际字符数（不含结尾 `$00`）发送。发送进度通过 `Busy` 反映：缓冲区放得下时 `Busy` 保持 `FALSE`，较长字符串分批入队时 `Busy` 变 `TRUE`，整串发完回 `FALSE`。判断成功条件为 `Busy = FALSE` 且 `Error = 0`。控制字符用 IEC 字符串转义（`'$R'`=CR、`'$L'`=LF、`'$N'`=换行）。本功能块以电平方式工作，调用方在字符串准备好后调用直到 `Busy = FALSE`。含 `$00`（0 字符）的二进制请改用 `SendData`。

## 4. 错误码 / 返回值

`Error` 为 `ComError_t` 枚举，本功能块相关取值：

| 错误码 | 含义 | 处理建议 |
|---|---|---|
| `COMERROR_NOERROR` (0) | 无错误 | 正常 |
| `COMERROR_TXBUFFOVERRUN` (2) | 字符串超过发送缓冲区容量 | 减小字符串长度，或确保后台通信任务足够快 |

完整 `ComError_t` 列表见 PDF 第 7.2 节。

## 5. 使用注意 / 常见坑

- **与 `SendString` 的唯一差异是长度**：输入可达 255 字符；≤ 80 字符时用 `SendString` 更省内存。
- **控制字符用 IEC 转义**：CR=`'$R'`、LF=`'$L'`、`$` 本身=`'$$'`。
- **不能发含 0 字符的二进制**：含 `$00` 的数据请用 `SendData`。
- **`TxBuffer` 要与后台功能块同实例**。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SendString255.TcPOU`](../examples/P_Demo_SendString255.TcPOU)

```iecst
// 场景：发一条较长的多字段命令（可超 80 字符），以 CR/LF 结尾。
PROGRAM P_Demo_SendString255
VAR
    fbSendString255 : SendString255;
    bufTx           : ComBuffer;
    sLongCommand    : STRING(255) := 'CONFIG:BAUD=9600,PARITY=NONE,STOP=1,FLOW=NONE$R$L';
    bSendNow        : BOOL;
    bBusy           : BOOL;
END_VAR

IF bSendNow THEN
    fbSendString255(
        SendString := sLongCommand,
        TxBuffer   := bufTx,
        Busy       => bBusy
    );
END_IF
```

## 7. 业务场景与实际价值

- **场景**：发送一行较长的文本报文，如带多个参数的配置命令、长 JSON / CSV 行、需要一次发完的长指令串。
- **价值**：在 `SendString` 便利性上把单条字符串上限提到 255 字符，避免长命令触发缓冲溢出或被 80 字符截断。
- **替代方案对比**：≤ 80 字符用 `SendString`；二进制 / 含 0 字符用 `SendData`；单字节用 `SendByte`。

## 8. 参考资料

- **PDF**：[TF6340_TC3_Serial_Communication_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf) §5.1.1.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/5291300875.html
- **相关**：`SendString`（80 字符版）、`ReceiveString255`（收 255 字符）、`SendData`（二进制）、`SerialLineControl`（消费 `TxBuffer`）、`ComError_t`
