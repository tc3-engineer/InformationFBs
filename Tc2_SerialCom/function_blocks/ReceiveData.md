# ReceiveData

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SerialCom` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85887499.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_ReceiveData.TcPOU`](../examples/P_Demo_ReceiveData.TcPOU) |

---

## 1. 功能简述

从与接收缓冲区 `RxBuffer` 对应的串口接收任意类型的成帧数据，并写入 `pReceiveData` 指向的变量。数据帧的起止通过四种可组合的机制识别：前缀（Prefix）、后缀（Suffix）、块长度（达到 `SizeReceiveData`）和字符间超时（Timeout）。当输出 `DataReceived = TRUE` 时，`pReceiveData` 指向的内存里就是收齐的一帧，长度由 `LenReceiveData` 给出。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
  pPrefix         : POINTER TO BYTE;
  LenPrefix       : BYTE;
  pSuffix         : POINTER TO BYTE;
  LenSuffix       : BYTE;
  pReceiveData    : POINTER TO BYTE;
  SizeReceiveData : DINT;
  Timeout         : TIME;
  Reset           : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `pPrefix` | `POINTER TO BYTE` | — | 前缀数据的地址，用 `ADR(变量)` 取；空（null）表示从第一个收到的字符开始 |
| `LenPrefix` | `BYTE` | — | 前缀的字节数 |
| `pSuffix` | `POINTER TO BYTE` | — | 后缀数据的地址，用 `ADR(变量)` 取 |
| `LenSuffix` | `BYTE` | — | 后缀的字节数 |
| `pReceiveData` | `POINTER TO BYTE` | — | 接收数据存放地址，用 `ADR(接收变量)` 取 |
| `SizeReceiveData` | `DINT` | — | 接收数据最大长度，用 `SIZEOF(接收变量)` 取（⚠️ 见 §9：PDF 描述表误写为 UDINT，声明为 DINT） |
| `Timeout` | `TIME` | — | 两个接收字符之间的最大间隔；从收到第一个字符后开始计时。为 0 时不做时间监控，一直收到 `SizeReceiveData` |
| `Reset` | `BOOL` | — | 置位将功能块从接收态复位到初始态；仅在例外情况（如期望数据未到、功能块卡在 busy）需要 |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
  RXBuffer         : ComBuffer;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `RxBuffer` | `ComBuffer` | 与所用串口对应的接收缓冲区 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
  DataReceived    : BOOL;
  busy            : BOOL;
  Error           : ComError_t;
  RxTimeout       : BOOL;
  LenReceiveData  : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `DataReceived` | `BOOL` | 收齐数据时变 `TRUE`，且只保持一个周期，必须立即取走数据 |
| `busy` | `BOOL` | 收到第一个字符后变 `TRUE`，收齐 / 出错 / 超时后变 `FALSE` |
| `Error` | `ComError_t` | 发生故障时返回错误码 |
| `RxTimeout` | `BOOL` | 字符间隔超过最大值导致接收中止时变 `TRUE`；无后缀时这是正常结束，有后缀时表示后缀未收到 |
| `LenReceiveData` | `UDINT` | 实际收到的字节数（含前缀、后缀），≤ `SizeReceiveData` |

## 3. 行为说明

调用即执行、内部带 `busy` 状态机：收到第一个字符后 `busy = TRUE`，按设定的判帧规则继续收，直到收齐、出错或超时，`busy` 回到 `FALSE` 并把 `DataReceived` 拉高一个周期。判帧规则可组合——给了 `pPrefix`，收到的头部必须与前缀一致，否则前面的字符被丢弃；给了 `pSuffix`，一直收到帧尾与后缀匹配为止，若中途达到 `SizeReceiveData` 则报 `COMERROR_DATASIZEOVERRUN`；不给后缀时收满 `SizeReceiveData` 为止；给了 `Timeout` 则按字符间隔超时断帧。后缀与超时可同时给：满足后缀匹配、达到最大长度、或字符间隔超时三者之一即结束。关键时序陷阱是 `DataReceived` 只保持一个 PLC 周期，必须在同一周期内把 `pReceiveData` 的数据取走。要只接受"完整且无误"的帧，除了判 `DataReceived = TRUE`，还应同时判 `RxTimeout = FALSE` 且 `Error = COMERROR_NOERROR`（无后缀场景例外，此时超时即正常结束）。

## 4. 错误码 / 返回值

`Error` 为 `ComError_t` 枚举，本功能块相关取值：

| 错误码 | 含义 | 处理建议 |
|---|---|---|
| `COMERROR_NOERROR` (0) | 无错误 | 正常 |
| `COMERROR_PARAMETERCHANGED` (1) | 接收过程中输入参数被改变 | 接收期间不要改 `pPrefix` / `pSuffix` 等输入 |
| `COMERROR_INVALIDRXPOINTER` (21) | `pReceiveData` 指针无效 | 确认用 `ADR()` 正确赋值 |
| `COMERROR_INVALIDRXLENGTH` (22) | 接收长度无效（如为 0） | 确认 `SizeReceiveData` 用 `SIZEOF()` 赋值且 > 0 |
| `COMERROR_DATASIZEOVERRUN` (23) | 收到的数据超过接收块上限 | 加大接收变量 / 检查后缀是否正确 |

完整 `ComError_t` 列表见 PDF 第 7.2 节。

## 5. 使用注意 / 常见坑

- **`DataReceived` 只亮一个周期**：必须当周期取走数据，否则错过这一帧。
- **完整帧判定**：用后缀时务必同时检查 `RxTimeout = FALSE` 和 `Error = COMERROR_NOERROR`，否则会把"超时截断的半帧"当成完整帧处理。
- **`Timeout` 不能用来判断报文是否到达**：超时监控从收到第一个字符后才生效，整帧没来时它不报超时，必须由外部逻辑监控。
- **指针生命周期**：`pReceiveData` 指向的接收变量、`pPrefix` / `pSuffix` 指向的前后缀变量，在接收期间都要保持有效。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ReceiveData.TcPOU`](../examples/P_Demo_ReceiveData.TcPOU)

```iecst
// 场景：收以 CR/LF 结尾的定长称重报文，用后缀判帧。
PROGRAM P_Demo_ReceiveData
VAR
    fbReceiveData : ReceiveData;
    bufRx         : ComBuffer;
    abyFrame      : ARRAY[0..63] OF BYTE;      // 接收落点
    asSuffix      : ARRAY[0..1] OF BYTE := [16#0D, 16#0A];  // CR LF
    bGotFrame     : BOOL;
    nFrameLen     : UDINT;
END_VAR

fbReceiveData(
    pPrefix         := 0,
    LenPrefix       := 0,
    pSuffix         := ADR(asSuffix),
    LenSuffix       := SIZEOF(asSuffix),
    pReceiveData    := ADR(abyFrame),
    SizeReceiveData := SIZEOF(abyFrame),
    Timeout         := T#200MS,
    Reset           := FALSE,
    RXBuffer        := bufRx,
    DataReceived    => bGotFrame,
    LenReceiveData  => nFrameLen
);
```

## 7. 业务场景与实际价值

- **场景**：接收带固定结束符或固定长度的二进制 / 文本报文，如称重仪表（CR/LF 结尾）、自定义协议帧（前缀 STX + 后缀 ETX）、定长状态包。
- **价值**：把前缀过滤、后缀匹配、超时断帧、长度上限四种判帧逻辑封装进一次调用，免去自己维护接收状态机和环形缓冲。
- **替代方案对比**：纯文本且只按结束符断帧用 `ReceiveString` 更直接；逐字节自处理用 `ReceiveByte`，但需要自己写判帧；`ReceiveData` 是处理任意结构化二进制帧的首选。

## 8. 参考资料

- **PDF**：[TF6340_TC3_Serial_Communication_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf) §5.1.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85887499.html
- **相关**：`SendData`（成帧发送）、`ReceiveString`（字符串接收）、`SerialLineControl`（填充 `RxBuffer`）、`ComBuffer`、`ComError_t`

## 9. 待确认项 (⚠️)

- `SizeReceiveData` 的类型：PDF / InfoSys 的 VAR_INPUT 声明块均为 `DINT`，但同页描述表的类型列写作 `UDINT`。本文档以**声明块**为准取 `DINT`（逐字搬运规则）。实际工程用 `SIZEOF()` 赋值时两者数值一致，不影响使用。
