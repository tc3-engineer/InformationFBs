# SendString

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SerialCom` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85893643.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_SendString.TcPOU`](../examples/P_Demo_SendString.TcPOU) |

---

## 1. 功能简述

向与发送缓冲区 `TxBuffer`（类型 `ComBuffer`）对应的串口发送一个字符串。直接传入 `STRING`（标准长度 80 字符），无需指针。需要发送更长的字符串时改用 `SendString255`（区别仅在 `SendString` 输入长度为 255）。真正的发送由后台功能块 `SerialLineControl` / `SerialLineControlADS` 异步完成。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  SendString         : STRING;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `SendString` | `STRING` | — | 要发送的字符串（最多 80 字符） |

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

调用即把 `SendString` 字符串的内容交给 `TxBuffer`，由后台通信功能块异步发往硬件。字符串以 IEC `STRING` 形式传入，功能块按其实际字符数（不含结尾 `$00`）发送。发送进度通过 `Busy` 反映：缓冲区一次放得下时 `Busy` 保持 `FALSE`；字符串较长需分批入队时 `Busy` 变 `TRUE`，整串发完后回到 `FALSE`。判断成功的条件是 `Busy = FALSE` 且 `Error = 0`。要发送带特殊控制字符（如换行、回车）的协议，用 IEC 字符串转义：`'$R'` 表示 CR、`'$L'` 表示 LF、`'$N'` 表示换行。本功能块以电平方式工作，调用方在字符串准备好后开始调用，直到 `Busy = FALSE`。注意若字符串包含 `$00`（0 字符）会被当作字符串结束符截断，含 0 字节的二进制请改用 `SendData`。

## 4. 错误码 / 返回值

`Error` 为 `ComError_t` 枚举，本功能块相关取值：

| 错误码 | 含义 | 处理建议 |
|---|---|---|
| `COMERROR_NOERROR` (0) | 无错误 | 正常 |
| `COMERROR_TXBUFFOVERRUN` (2) | 字符串超过发送缓冲区容量 | 减小字符串长度，或确保后台通信任务足够快 |

完整 `ComError_t` 列表见 PDF 第 7.2 节。

## 5. 使用注意 / 常见坑

- **控制字符用 IEC 转义**：CR 写 `'$R'`、LF 写 `'$L'`、制表符 `'$T'`、`$` 本身写 `'$$'`。漏掉结束符对端可能无法判断报文边界。
- **80 字符上限**：更长字符串用 `SendString255`。
- **不能发含 0 字符的二进制**：IEC `STRING` 以 `$00` 结尾，二进制请用 `SendData`。
- **`TxBuffer` 要与后台功能块同实例**。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SendString.TcPOU`](../examples/P_Demo_SendString.TcPOU)

```iecst
// 场景：向设备发一条以 CR/LF 结尾的文本命令。
PROGRAM P_Demo_SendString
VAR
    fbSendString : SendString;
    bufTx        : ComBuffer;
    sCommand     : STRING := 'START$R$L';       // "START" + CR + LF
    bSendNow     : BOOL;
    bBusy        : BOOL;
END_VAR

IF bSendNow THEN
    fbSendString(
        SendString := sCommand,
        TxBuffer   := bufTx,
        Busy       => bBusy
    );
END_IF
```

## 7. 业务场景与实际价值

- **场景**：向接收 ASCII 命令的设备发指令，如打印机指令、命令行式仪表（"START\r\n"）、向上位机发文本状态。
- **价值**：直接传 `STRING`，可用字符串拼接（`CONCAT`）动态组报文，无需指针和字节数组。
- **替代方案对比**：二进制 / 含 0 字符用 `SendData`；更长字符串用 `SendString255`；单字节控制码用 `SendByte`。

## 8. 参考资料

- **PDF**：[TF6340_TC3_Serial_Communication_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf) §5.1.1.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85893643.html
- **相关**：`ReceiveString`（收字符串）、`SendString255`（255 字符版）、`SendData`（二进制）、`SerialLineControl`（消费 `TxBuffer`）、`ComBuffer`、`ComError_t`
