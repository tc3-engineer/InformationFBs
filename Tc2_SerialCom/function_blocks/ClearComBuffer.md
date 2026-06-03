# ClearComBuffer

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SerialCom` |
| Library Version | `1.8.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85896587.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_ClearComBuffer.TcPOU`](../examples/P_Demo_ClearComBuffer.TcPOU) |

---

## 1. 功能简述

清空 PLC 内部的通信缓冲区 `Buffer`（类型 `ComBuffer`）。该功能块只复位 PLC 侧的软件环形缓冲（读写索引、计数清零），不触碰串口硬件的收发缓冲——清硬件缓冲要用 `ComReset`。常用于初始化阶段，或在切换协议、重启通信前把残留数据丢弃，避免上一轮通信的旧字节混进新数据。

## 2. 接口定义

### VAR_IN_OUT

```iecst
VAR_IN_OUT
  Buffer         : ComBuffer;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Buffer` | `ComBuffer` | 要清空的 PLC 内部通信缓冲区（可以是接收缓冲或发送缓冲） |

### VAR_INPUT

无。

### VAR_OUTPUT

无。

## 3. 行为说明

调用即执行、无状态、无返回：每次调用就把传入的 `Buffer`（一个 `ComBuffer` 实例）清空——把环形缓冲的读索引、写索引、字节计数复位，相当于丢弃缓冲区里当前所有未处理的字节。没有 Execute 上升沿，也没有 Busy / Done / Error 输出，因此通常配合一个上升沿触发条件（如初始化标志、协议切换信号）单次调用，而不是每周期无脑清。它清的是 PLC 软件缓冲：对接收缓冲调用就丢掉所有还没被 `ReceiveByte` / `ReceiveData` 读走的字节；对发送缓冲调用就丢掉所有还没被后台发出的待发字节。要同时清空串口硬件内部的收发缓冲（如刚上电、波特率刚改），应另外调用 `ComReset`——两者职责互补：`ClearComBuffer` 清 PLC 软件缓冲，`ComReset` 清硬件缓冲。

## 4. 错误码 / 返回值

无错误码 / 无返回值——本功能块没有 `Error` 或返回值输出。调用即清空，不会失败。

## 5. 使用注意 / 常见坑

- **只清软件缓冲，不清硬件**：硬件收发缓冲要用 `ComReset` 清。初始化时通常两者都调。
- **用边沿触发**：每周期都清会把正在到达的数据也丢掉。应在初始化标志 / 协议切换的上升沿单次调用。
- **接收和发送是不同实例**：清接收缓冲传 `RxBuffer`，清发送缓冲传 `TxBuffer`，按需分别清。
- **清缓冲不影响硬件链路状态**：它不会重连串口，只是丢弃 PLC 侧缓存的字节。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ClearComBuffer.TcPOU`](../examples/P_Demo_ClearComBuffer.TcPOU)

```iecst
// 场景：开始新一轮通信前，丢弃接收缓冲里上一轮的残留字节。
PROGRAM P_Demo_ClearComBuffer
VAR
    fbClearComBuffer : ClearComBuffer;
    bufRx            : ComBuffer;
    bStartNewSession : BOOL;
    rtrigClear       : R_TRIG;
END_VAR

// 在“开始新会话”的上升沿清一次接收缓冲
rtrigClear(CLK := bStartNewSession);
IF rtrigClear.Q THEN
    fbClearComBuffer(Buffer := bufRx);
END_IF
```

## 7. 业务场景与实际价值

- **场景**：通信初始化、协议 / 波特率切换、错误恢复后重新开始收发时，需要丢弃缓冲区里的陈旧字节，避免它们污染下一轮数据帧。
- **价值**：一次调用复位 PLC 通信缓冲，免去自己操作 `ComBuffer` 内部的读写索引和计数字段。
- **替代方案对比**：要清硬件收发缓冲（不止 PLC 软件缓冲）用 `ComReset`；只需丢 PLC 侧残留字节用本功能块更轻量、不影响硬件链路。

## 8. 参考资料

- **PDF**：[TF6340_TC3_Serial_Communication_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf) §5.1.1.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/85896587.html
- **相关**：`ComReset`（清硬件收发缓冲）、`ReceiveByte` / `ReceiveData`（从缓冲读数据）、`ComBuffer`（缓冲区结构）
