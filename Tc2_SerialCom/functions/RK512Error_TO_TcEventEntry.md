# RK512Error_TO_TcEventEntry

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SerialCom` |
| Library Version | `1.8.1` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/16281038731.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_RK512Error_TO_TcEventEntry.TcPOU`](../examples/P_Demo_RK512Error_TO_TcEventEntry.TcPOU) |

---

## 1. 功能简述

把 `RK512` 功能块可能产生的错误码（`RK512_Error_t`）转换为事件定义（`TcEventEntry`）。转换出的事件定义可配合 Tc3_EventLogger 库创建并发送事件，还能查询事件文本——把 RK512 协议错误码变成多语言明文描述。

## 2. 接口定义

### Syntax

```iecst
FUNCTION RK512Error_TO_TcEventEntry : BOOL
VAR_INPUT
  eErrorId      : RK512_Error_t;
  stEventEntry  : REFERENCE TO TcEventEntry;
END_VAR
```

### VAR_INPUT

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `eErrorId` | `RK512_Error_t` | — | 要转换的 RK512 错误码 |
| `stEventEntry` | `REFERENCE TO TcEventEntry` | — | 转换结果——事件定义（按引用传入，函数写入其中） |

### 返回值

| 类型 | 说明 |
|---|---|
| `BOOL` | 转换成功返回 `TRUE` |

## 3. 行为说明

纯转换函数，调用即返回：传入一个 `RK512_Error_t` 错误码和一个 `TcEventEntry` 引用，函数把该错误码对应的事件定义填入引用的 `stEventEntry`，转换成功返回 `TRUE`。它本身不创建 / 不发送事件，只做"错误码 → 事件定义"的映射；拿到 `TcEventEntry` 后交给 Tc3_EventLogger 库登记、发送或查询多语言事件文本。`stEventEntry` 用 `REFERENCE TO` 传入，调用方需先声明一个 `TcEventEntry` 变量。典型用法：`RK512` 功能块报错时（主动模式 `Error`/`ErrorId` 或被动模式 `ErrorRx`/`ErrorIdRx`），把 `RK512_Error_t` 错误码喂给本函数得到事件定义，再推送到事件日志，让 HMI / 诊断界面显示明文的 RK512 错误（如数据块未登记、报文超时、协议头错误等），而非裸错误码。`TcEventEntry` 等类型来自 Tc3_EventLogger，使用本函数需引用该库。

## 4. 错误码 / 返回值

返回 `BOOL`：

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 转换成功，`stEventEntry` 已填好 | 可交给 Tc3_EventLogger 发送 |
| `FALSE` | 转换失败 | 检查传入的 `eErrorId` 是否为 `RK512_Error_t` 合法值；`stEventEntry` 引用是否有效 |

## 5. 使用注意 / 常见坑

- **需要 Tc3_EventLogger**：`TcEventEntry` 来自 Tc3_EventLogger 库，工程须引用它。
- **只转换不发送**：得到 `TcEventEntry` 后还要用 Tc3_EventLogger 功能块创建 / 发送事件。
- **专用于 RK512 错误**：只接 `RK512_Error_t`；其他错误类型用各自的转换函数。
- **主被动两路错误都可转**：`RK512` 的 `ErrorId`（主动）和 `ErrorIdRx`（被动）都是 `RK512_Error_t`，均可传入。
- **`stEventEntry` 是引用**：调用方先声明 `TcEventEntry` 变量再传入。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_RK512Error_TO_TcEventEntry.TcPOU`](../examples/P_Demo_RK512Error_TO_TcEventEntry.TcPOU)

```iecst
// 场景：把 RK512 功能块报的错误转成事件定义，供事件日志显示明文。
PROGRAM P_Demo_RK512Error_TO_TcEventEntry
VAR
    eErr        : RK512_Error_t;
    stEvent     : TcEventEntry;
    bConverted  : BOOL;
END_VAR

bConverted := RK512Error_TO_TcEventEntry(eErrorId := eErr, stEventEntry := stEvent);
// bConverted = TRUE 时 stEvent 已填好，可交给 Tc3_EventLogger 发送
```

## 7. 业务场景与实际价值

- **场景**：用 RK512 协议做数据块交换的工程，把协议错误（数据块未登记、报文级超时、对端应答含错等）接入 TwinCAT 事件日志，让运维看多语言明文。
- **价值**：一行调用把 RK512 错误码映射为标准事件定义，免手工维护错误文本表，支持多语言。
- **替代方案对比**：自己 `CASE` 拼文本——可行但要手工维护、难多语言；本函数产出与 Tc3_EventLogger 配套的标准事件。

## 8. 参考资料

- **PDF**：[TF6340_TC3_Serial_Communication_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf) §5.2.2.3、§7.5（RK512 错误码）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/16281038731.html
- **相关**：`RK512`（错误来源）、`ComError_TO_TcEventEntry` / `P3964RError_TO_TcEventEntry` / `SerialLineControlADSErr_TO_TcEventEntry`、`RK512_Error_t`、Tc3_EventLogger 库
