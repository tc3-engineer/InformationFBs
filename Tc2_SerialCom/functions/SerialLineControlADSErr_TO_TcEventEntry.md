# SerialLineControlADSErr_TO_TcEventEntry

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_SerialCom` |
| Library Version | `1.8.1` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/16281039883.html |
| Verified | 2026-06-02 ✅ |
| InfoSys-checked | ✅ 2026-06-02 |
| Status | `verified` |
| Example | [`examples/P_Demo_SerialLineControlADSErr_TO_TcEventEntry.TcPOU`](../examples/P_Demo_SerialLineControlADSErr_TO_TcEventEntry.TcPOU) |

---

## 1. 功能简述

把 `SerialLineControlADS` 功能块可能产生的错误码转换为事件定义（`TcEventEntry`）。与本库其他三个转换函数不同，它的错误码输入是 `UDINT`（因为 `SerialLineControlADS` 的 `ErrorID` 是 `UDINT`，涵盖 ADS / 服务器 / Win32 / Linux 多段错误码）。转换出的事件定义可配合 Tc3_EventLogger 库创建并发送事件、查询多语言事件文本。

## 2. 接口定义

### Syntax

```iecst
FUNCTION SerialLineControlADSErr_TO_TcEventEntry : BOOL
VAR_INPUT
  nErrorId      : UDINT;
  stEventEntry  : REFERENCE TO TcEventEntry;
END_VAR
```

### VAR_INPUT

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nErrorId` | `UDINT` | — | 要转换的错误码（`SerialLineControlADS` 的 `ErrorID`） |
| `stEventEntry` | `REFERENCE TO TcEventEntry` | — | 转换结果——事件定义（按引用传入，函数写入其中） |

### 返回值

| 类型 | 说明 |
|---|---|
| `BOOL` | 转换成功返回 `TRUE` |

## 3. 行为说明

纯转换函数，调用即返回：传入一个 `UDINT` 错误码和一个 `TcEventEntry` 引用，函数把该错误码对应的事件定义填入引用的 `stEventEntry`，转换成功返回 `TRUE`。它本身不创建 / 不发送事件，只做"错误码 → 事件定义"的映射；拿到 `TcEventEntry` 后交给 Tc3_EventLogger 库登记、发送或查询多语言事件文本。`stEventEntry` 用 `REFERENCE TO` 传入，调用方需先声明一个 `TcEventEntry` 变量。注意它接收的错误码类型是 `UDINT` 而非枚举——因为 `SerialLineControlADS` 的错误码横跨 ADS 系统错误、TcAdsSerialCommServer 错误、Win32 错误、Linux 错误几大段（见 `SerialLineControlADS` 文档 §4），用 `UDINT` 才能覆盖。典型用法：`SerialLineControlADS` 报错（`Error = TRUE`）时把它的 `ErrorID`（`UDINT`）喂给本函数得到事件定义，再推送到事件日志，让 HMI / 诊断界面显示明文（如 COM 口被占用、接收缓冲溢出、USB 设备拔出等），而非裸错误码。`TcEventEntry` 等类型来自 Tc3_EventLogger，使用本函数需引用该库。

## 4. 错误码 / 返回值

返回 `BOOL`：

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 转换成功，`stEventEntry` 已填好 | 可交给 Tc3_EventLogger 发送 |
| `FALSE` | 转换失败 | 检查 `nErrorId` 是否为已知错误码；`stEventEntry` 引用是否有效 |

## 5. 使用注意 / 常见坑

- **错误码是 `UDINT`**：与另外三个转换函数（接枚举）不同，这里接 `UDINT`，直接把 `SerialLineControlADS.ErrorID` 传入即可。
- **需要 Tc3_EventLogger**：`TcEventEntry` 来自 Tc3_EventLogger 库，工程须引用它。
- **只转换不发送**：得到 `TcEventEntry` 后还要用 Tc3_EventLogger 功能块创建 / 发送事件。
- **专用于虚拟串口错误**：只配 `SerialLineControlADS`；物理串口 `SerialLineControl` 的 `ComError_t` 用 `ComError_TO_TcEventEntry`。
- **`stEventEntry` 是引用**：调用方先声明 `TcEventEntry` 变量再传入。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SerialLineControlADSErr_TO_TcEventEntry.TcPOU`](../examples/P_Demo_SerialLineControlADSErr_TO_TcEventEntry.TcPOU)

```iecst
// 场景：把 SerialLineControlADS 报的 UDINT 错误码转成事件定义。
PROGRAM P_Demo_SerialLineControlADSErr_TO_TcEventEntry
VAR
    nErr        : UDINT;
    stEvent     : TcEventEntry;
    bConverted  : BOOL;
END_VAR

bConverted := SerialLineControlADSErr_TO_TcEventEntry(nErrorId := nErr, stEventEntry := stEvent);
// bConverted = TRUE 时 stEvent 已填好，可交给 Tc3_EventLogger 发送
```

## 7. 业务场景与实际价值

- **场景**：用虚拟串口（USB-COM）的工程，把 `SerialLineControlADS` 的 ADS / 服务器 / Win32 错误接入 TwinCAT 事件日志，让运维看到"端口被占用""USB 拔出"等多语言明文。
- **价值**：一行调用把跨多段的 `UDINT` 错误码映射为标准事件定义，免手工维护庞杂的错误码到文本对照。
- **替代方案对比**：自己 `CASE nErrorId OF ...` 拼文本——可行但要覆盖 ADS / 服务器 / Win32 / Linux 几大段、难多语言；本函数产出与 Tc3_EventLogger 配套的标准事件。

## 8. 参考资料

- **PDF**：[TF6340_TC3_Serial_Communication_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf) §5.2.2.4、§7.3（SerialLineControlADS 错误码）
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/16281039883.html
- **相关**：`SerialLineControlADS`（错误来源）、`ComError_TO_TcEventEntry` / `P3964RError_TO_TcEventEntry` / `RK512Error_TO_TcEventEntry`、Tc3_EventLogger 库
