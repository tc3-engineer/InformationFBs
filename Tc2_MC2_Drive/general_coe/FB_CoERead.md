# FB_CoERead

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Drive` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `General CoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2297741579.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_CoERead.xml`](../examples/P_Demo_FB_CoERead.xml) |

---

## 1. 功能简述

通过 **CoE（CANopen over EtherCAT）** 协议从 EtherCAT 从站对象字典读取数据的功能块（Function Block, FB）。读取走 SDO（Service Data Object）访问，要求该从站有 mailbox 并支持 CoE 协议。

CoE 用 `Index`（对象索引，如 `16#1018`）+ `SubIndex`（子索引）寻址对象，这与 SoE 的 IDN 寻址是两套不同体系——AX8000 等用 CoE，AX5000 用 SoE。`CompleteAccess := TRUE` 时可一次性读出整个对象（含所有子索引）。

读出的数据回填进 `pDstBuf` 指向的缓冲区，长度 `BufLen`。Index/SubIndex 编号需查对应驱动器文档（AX8000 见 Beckhoff AX8000 对象描述）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NetId          : T_AmsNetID;
    Index          : WORD;
    SubIndex       : BYTE;
    pDstBuf        : PVOID;
    BufLen         : UDINT;
    Execute        : BOOL;
    Timeout        : TIME := DEFAULT_ADS_TIMEOUT;
    CompleteAccess : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NetId` | `T_AmsNetID` | — | 含 NC 所在 PC 的 AMS NetId 字符串 |
| `Index` | `WORD` | — | 要读的对象索引（如 `16#1018`） |
| `SubIndex` | `BYTE` | — | 要读的对象子索引 |
| `pDstBuf` | `PVOID` | — | 接收缓冲区的地址（指针），用 `ADR()` 取 |
| `BufLen` | `UDINT` | — | 接收缓冲区可用的最大字节数，用 `SIZEOF()` 取 |
| `Execute` | `BOOL` | — | 上升沿触发一次读取 |
| `Timeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | FB 执行允许的最大时间 |
| `CompleteAccess` | `BOOL` | — | 置 `TRUE` 时通过 Complete Access 一次性访问整个对象（含所有子索引） |

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    Axis : AXIS_REF;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Axis` | `AXIS_REF` | 唯一标识系统中一根轴的数据结构，含位置、速度、错误状态等循环数据。**必须传引用**（VAR_IN_OUT 语义） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    Busy         : BOOL;
    Error        : BOOL;
    AdsErrId     : UINT;
    CANopenErrId : UINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | FB 激活后置位，直到收到反馈才复位 |
| `Error` | `BOOL` | `Busy` 复位后若命令传输出错则置位 |
| `AdsErrId` | `UINT` | `Error = TRUE` 时返回 ADS 错误码 |
| `CANopenErrId` | `UINT` | `Error = TRUE` 时返回 CANopen 错误码 |

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次 CoE 读取：FB 通过 SDO 上传从指定 `Index`/`SubIndex` 读对象，把结果写入 `pDstBuf`，`Busy := TRUE`，异步执行，**跨多个 PLC 周期**，必须每周期循环调用直到 `Busy` 落回 `FALSE`。

**完成与出错收敛**：本 FB 无 `Done` 输出。成功判据是 **`Busy` 由 TRUE 落回 FALSE 且 `Error = FALSE`**，此时 `pDstBuf` 缓冲区里是读到的对象数据。出错则 `Busy` 复位后 `Error := TRUE`，`AdsErrId` 给 ADS 错误码、`CANopenErrId` 给 CANopen 错误码。

**双错误码语义**（CoE 版）：`AdsErrId` 反映"PLC ↔ 从站"的 ADS 通道（超时、mailbox 不可用）；`CANopenErrId` 反映从站内部 CoE/SDO 服务（对象不存在、子索引越界、对象不可读等）。诊断时两个都要看。

**`CompleteAccess` 语义**：`FALSE`（默认）时只读 `Index`+`SubIndex` 指定的单个子项；`TRUE` 时把整个 `Index` 对象（所有子索引）一次读出——此时 `pDstBuf` 必须够大装下整个对象结构，且 `SubIndex` 一般填 0。

**与 SoE 的区别**：CoE（`Index`/`SubIndex`）与 SoE（`Idn`/`Element`）是两套寻址体系，对应不同硬件。AX8000/EL72xx 等用 CoE，AX5000 用 SoE。别把 IDN 当 Index 用。

**复位边沿**：`Busy = FALSE` 后把 `Execute` 拉回 `FALSE` 调一次复位 FB 内部状态。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` 输出，分 `AdsErrId : UINT`（ADS 错误码）与 `CANopenErrId : UINT`（CANopen 错误码）两路。

| 错误路 | 含义 | 处理建议 |
|---|---|---|
| `AdsErrId` ≠ 0 | ADS 通道错误：超时、从站无 mailbox、NetId 错 | 检查 EtherCAT OP、从站是否支持 CoE/有 mailbox、`NetId` |
| `CANopenErrId` ≠ 0 | CoE/SDO 服务错误：对象不存在、子索引越界、对象不可读 | 核对 `Index`/`SubIndex`（查驱动器对象字典）、`BufLen` 是否够、`CompleteAccess` 用法 |

⚠️ PDF 与 InfoSys 未逐条列出具体 ADS / CANopen 错误码数值。见 Beckhoff ADS Return Codes 总表与 CANopen / 驱动器对象字典文档。

**清错**：处理完外部原因后给 `Execute` 新上升沿重试；本 FB 无独立清错入口。

## 5. 使用注意 / 常见坑

- **CoE ≠ SoE**：`Index`/`SubIndex` 是 CANopen 体系，别把 SoE 的 IDN 填进来。看硬件用对协议（AX8000/EL72xx → CoE）。
- **`pDstBuf`/`BufLen` 配对且够大**：`CompleteAccess = TRUE` 时缓冲区要装下整个对象，否则报错或截断。
- **从站必须支持 CoE 且有 mailbox**：否则 `AdsErrId` 报错。
- **两个错误码都要看**：`AdsErrId` 管通信、`CANopenErrId` 管对象访问。
- **没有 `Done` 输出 + `Busy` 期间持续循环调用**：异步跨周期。
- **`CompleteAccess` 下 `SubIndex` 通常填 0**：一次读整个对象（工程经验补充）。
- **`AXIS_REF` 必须传引用**：`Axis` 是 VAR_IN_OUT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CoERead.xml`](../examples/P_Demo_FB_CoERead.xml)

```iecst
// 场景：读 AX8000 对象字典里 Identity 对象 (16#1018) 子索引 1 = Vendor ID
rtCoEReadTrig(CLK := bCoEReadReq);
fbCoERead(
    NetId    := '',
    Index    := 16#1018,
    SubIndex := 1,
    pDstBuf  := ADR(nVendorId),
    BufLen   := SIZEOF(nVendorId),
    Execute  := rtCoEReadTrig.Q,
    Timeout  := DEFAULT_ADS_TIMEOUT,
    CompleteAccess := FALSE,
    Axis     := axisServo,
    Busy     => bCoEReadBusy,
    Error    => bCoEReadError,
    AdsErrId     => nCoEReadAdsErr,
    CANopenErrId => nCoEReadCanErr
);
```

## 7. 业务场景与实际价值

- **场景**：读 AX8000/EL72xx 等 CoE 驱动器的对象字典：设备身份（Vendor ID / Product Code）、诊断对象、运行参数、状态字等。
- **价值**：用 Index/SubIndex 通用寻址读任意 CoE 对象，无需为每个对象写专用 FB；通过 `AXIS_REF` 关联轴。
- **替代方案对比**：
  - 用 Tc2_EtherCAT 的 `FB_EcCoeSdoRead`：通用但需手动管理从站地址，不绑定 NC 轴
  - 用通用 `ADSREAD`：要自己拼 CoE 索引组/偏移，繁琐
  - **本 FB**：CoE 对象读取且绑定 NC 轴的标准入口

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf) §4.3.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2297741579.html
- **相关 FB**：`FB_CoEWrite`（写对象）、`FB_CoEExecuteCommand`（执行命令对象）、`FB_SoERead`（SoE 协议读）
