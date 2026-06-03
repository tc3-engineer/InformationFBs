# ComError_TO_TcEventEntry

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SerialCom` |
| Library Version | `1.8.1` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/16281036427.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_ComError_TO_TcEventEntry.TcPOU`](../examples/P_Demo_ComError_TO_TcEventEntry.TcPOU) |

---

## 1. 功能简述

把 `ComError_t` 类型的错误码转换为事件定义（`TcEventEntry`）。本库多数功能块（`SerialLineControl`、`SendData`、`ReceiveData` 等）通过 `ComError_t` 返回错误，转换出的事件定义可配合 Tc3_EventLogger 库创建并发送事件，还能查询事件文本——从而把错误码变成多语言的明文描述。

## 2. 接口定义

### Syntax

```iecst
FUNCTION ComError_TO_TcEventEntry : BOOL
VAR_INPUT
  eErrorId      : ComError_t;
  stEventEntry  : REFERENCE TO TcEventEntry;
END_VAR
```

### VAR_INPUT

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `eErrorId` | `ComError_t` | — | 要转换的错误码 |
| `stEventEntry` | `REFERENCE TO TcEventEntry` | — | 转换结果——事件定义（按引用传入，函数写入其中） |

### 返回值

| 类型 | 说明 |
|---|---|
| `BOOL` | 转换成功返回 `TRUE` |

## 3. 行为说明

纯转换函数，调用即返回：传入一个 `ComError_t` 错误码和一个 `TcEventEntry` 引用，函数把该错误码对应的事件定义填入引用的 `stEventEntry`，转换成功返回 `TRUE`。它本身不创建 / 不发送事件，只做"错误码 → 事件定义"的映射；拿到 `TcEventEntry` 后，再交给 Tc3_EventLogger 库（如 `FB_TcMessage` 的 `Send` / `SetEventEntry`）去登记、发送或查询多语言事件文本。`stEventEntry` 用 `REFERENCE TO` 传入，调用方需先声明一个 `TcEventEntry` 变量。典型用法：在功能块报错（`Error = TRUE`）时，把它的 `ComError_t` 错误码（或 `ErrorID`）喂给本函数得到事件定义，再推送到事件日志，使 HMI / 诊断界面能显示人类可读的错误描述而非裸错误码。`TcEventEntry` 等类型来自 Tc3_EventLogger，使用本函数需引用该库。

## 4. 错误码 / 返回值

返回 `BOOL`：

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 转换成功，`stEventEntry` 已填好 | 可交给 Tc3_EventLogger 发送 |
| `FALSE` | 转换失败 | 检查传入的 `eErrorId` 是否为本库定义的 `ComError_t` 值；`stEventEntry` 引用是否有效 |

## 5. 使用注意 / 常见坑

- **需要 Tc3_EventLogger**：`TcEventEntry` 来自 Tc3_EventLogger 库，工程须引用它，否则类型未定义。
- **本函数只转换不发送**：得到 `TcEventEntry` 后还要用 Tc3_EventLogger 的功能块去创建 / 发送事件。
- **`stEventEntry` 是引用**：调用方先声明 `TcEventEntry` 变量再传入。
- **配套错误来源**：本函数对应通过 `ComError_t` 报错的功能块（`Send*` / `Receive*` / `SerialLineControl` / `KL6*` 等）；`SerialLineControlADS`、`3964R`、`RK512` 有各自的转换函数。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ComError_TO_TcEventEntry.TcPOU`](../examples/P_Demo_ComError_TO_TcEventEntry.TcPOU)

```iecst
// 场景：把 SendData 报的 ComError_t 错误转成事件定义，供事件日志显示明文。
PROGRAM P_Demo_ComError_TO_TcEventEntry
VAR
    eErr        : ComError_t := ComError_t.COMERROR_TXBUFFOVERRUN;
    stEvent     : TcEventEntry;
    bConverted  : BOOL;
END_VAR

bConverted := ComError_TO_TcEventEntry(eErrorId := eErr, stEventEntry := stEvent);
// bConverted = TRUE 时 stEvent 已填好，可交给 Tc3_EventLogger 发送
```

## 7. 业务场景与实际价值

- **场景**：把串口通信功能块的 `ComError_t` 错误码接入 TwinCAT 事件日志系统，让 HMI / 诊断界面显示多语言明文错误，而不是让运维人员去查错误码表。
- **价值**：一行调用完成"错误码 → 标准事件定义"的映射，免去自己维护错误码到文本的对照表，且文本可多语言。
- **替代方案对比**：自己写 `CASE eErrorId OF ...` 拼错误文本——可行但要手工维护、难多语言；本函数直接产出与 Tc3_EventLogger 配套的标准事件。

## 8. 参考资料

- **PDF**：[TF6340_TC3_Serial_Communication_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf) §5.2.2.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/16281036427.html
- **相关**：`P3964RError_TO_TcEventEntry` / `RK512Error_TO_TcEventEntry` / `SerialLineControlADSErr_TO_TcEventEntry`（其他错误类型的转换）、`ComError_t`、Tc3_EventLogger 库
