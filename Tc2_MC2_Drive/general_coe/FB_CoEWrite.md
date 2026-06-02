# FB_CoEWrite

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Drive` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `General CoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2297743499.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_CoEWrite.TcPOU`](../examples/P_Demo_FB_CoEWrite.TcPOU) |

---

## 1. 功能简述

通过 **CoE（CANopen over EtherCAT）** 协议向 EtherCAT 从站对象字典写入数据的功能块（Function Block, FB）。与 `FB_CoERead` 对偶：写入走 SDO（Service Data Object）下载，要求从站有 mailbox 并支持 CoE。

用 `Index`（对象索引）+ `SubIndex`（子索引）寻址要写的对象，把 PLC 里源缓冲区（`pSrcBuf` 地址 + `BufLen` 长度）的内容写进去。`CompleteAccess := TRUE` 时可一次性写整个对象（含所有子索引）。

Index/SubIndex 编号需查对应驱动器对象字典文档（AX8000 见 Beckhoff AX8000 对象描述）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NetId          : T_AmsNetID;
    Index          : WORD;
    SubIndex       : BYTE;
    pSrcBuf        : PVOID;
    BufLen         : UDINT;
    Execute        : BOOL;
    Timeout        : TIME := DEFAULT_ADS_TIMEOUT;
    CompleteAccess : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NetId` | `T_AmsNetID` | — | 含 NC 所在 PC 的 AMS NetId 字符串 |
| `Index` | `WORD` | — | 要写的对象索引 |
| `SubIndex` | `BYTE` | — | 要写的对象子索引 |
| `pSrcBuf` | `PVOID` | — | 含要发送数据的缓冲区地址（指针），用 `ADR()` 取 |
| `BufLen` | `UDINT` | — | 要发送的数据字节数，用 `SIZEOF()` 取 |
| `Execute` | `BOOL` | — | 上升沿触发一次写入 |
| `Timeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | FB 执行允许的最大时间 |
| `CompleteAccess` | `BOOL` | — | 置 `TRUE` 时通过 Complete Access 一次性写整个对象 |

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

**触发**：`Execute` 上升沿启动一次 CoE 写入：FB 通过 SDO 下载把 `pSrcBuf` 缓冲区内容写到从站 `Index`/`SubIndex` 指定对象，`Busy := TRUE`，异步执行，**跨多个 PLC 周期**，必须每周期循环调用直到 `Busy` 落回 `FALSE`。

**完成与出错收敛**：本 FB 无 `Done` 输出。成功判据是 **`Busy` 由 TRUE 落回 FALSE 且 `Error = FALSE`**。出错则 `Busy` 复位后 `Error := TRUE`，`AdsErrId`/`CANopenErrId` 给错误码。

**双错误码语义**（同 `FB_CoERead`）：`AdsErrId` 管 ADS 通道；`CANopenErrId` 管 CoE/SDO 服务（对象只读、子索引越界、写值类型不符等）。写对象最常见的 CANopen 错误是"对象只读"或"值超范围"。

**`pSrcBuf`/`BufLen` 一致性**：写入数据类型大小必须与目标对象一致，否则报错或被截断。`CompleteAccess = TRUE` 写整个对象时缓冲区须含完整对象结构。

**与 SoE 区别**：CoE（`Index`/`SubIndex`）≠ SoE（`Idn`/`Element`），对应不同硬件。AX8000/EL72xx 用 CoE。

**复位边沿**：`Busy = FALSE` 后把 `Execute` 拉回 `FALSE` 调一次复位。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` 输出，分 `AdsErrId : UINT`（ADS 错误码）与 `CANopenErrId : UINT`（CANopen 错误码）两路。

| 错误路 | 含义 | 处理建议 |
|---|---|---|
| `AdsErrId` ≠ 0 | ADS 通道错误：超时、从站无 mailbox、NetId 错 | 检查 EtherCAT OP、从站 CoE/mailbox、`NetId` |
| `CANopenErrId` ≠ 0 | CoE/SDO 服务错误：对象只读、子索引越界、写值类型/范围不符 | 核对 `Index`/`SubIndex`、确认对象可写、写值类型大小匹配、范围合法 |

⚠️ PDF 与 InfoSys 未逐条列出具体 ADS / CANopen 错误码数值。见 Beckhoff ADS Return Codes 总表与 CANopen / 驱动器对象字典文档。

**清错**：处理完外部原因后给 `Execute` 新上升沿重试；本 FB 无独立清错入口。

## 5. 使用注意 / 常见坑

- **CoE ≠ SoE**：用 `Index`/`SubIndex` 不是 IDN；AX8000/EL72xx 用 CoE。
- **多数对象写"值"前确认可写**：只读对象写会被 `CANopenErrId` 拒绝。
- **`pSrcBuf`/`BufLen` 类型大小匹配目标对象**：不匹配写失败或截断。
- **两个错误码都要看 + 没有 `Done` + `Busy` 期间持续循环调用**：与 `FB_CoERead` 一致。
- **写对象有持久性后果**：CoE 对象写入改变从站行为，写前确认 Index/SubIndex 和值（工程经验补充）。
- **`CompleteAccess` 写整个对象需缓冲区含完整结构**：部分对象只支持 Complete Access。
- **`AXIS_REF` 必须传引用**：`Axis` 是 VAR_IN_OUT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CoEWrite.TcPOU`](../examples/P_Demo_FB_CoEWrite.TcPOU)

```iecst
// 场景：向 AX8000 对象字典某可写对象 (Index/SubIndex) 写入一个新值
rtCoEWriteTrig(CLK := bCoEWriteReq);
fbCoEWrite(
    NetId    := '',
    Index    := 16#8000,
    SubIndex := 1,
    pSrcBuf  := ADR(nWriteValue),
    BufLen   := SIZEOF(nWriteValue),
    Execute  := rtCoEWriteTrig.Q,
    Timeout  := DEFAULT_ADS_TIMEOUT,
    CompleteAccess := FALSE,
    Axis     := axisServo,
    Busy     => bCoEWriteBusy,
    Error    => bCoEWriteError,
    AdsErrId     => nCoEWriteAdsErr,
    CANopenErrId => nCoEWriteCanErr
);
```

## 7. 业务场景与实际价值

- **场景**：配置 AX8000/EL72xx 等 CoE 驱动器对象字典里的运行参数、改写控制字、设置诊断/滤波对象。
- **价值**：用 Index/SubIndex 通用写任意可写 CoE 对象，无需为每个对象写专用 FB；绑定 NC 轴。
- **替代方案对比**：
  - 用 Tc2_EtherCAT 的 `FB_EcCoeSdoWrite`：通用但需手动管理从站地址，不绑定 NC 轴
  - 在 ESI/DriveManager 手动配：人工、无法运行期动态改
  - **本 FB**：CoE 对象写入且绑定 NC 轴的标准入口

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf) §4.3.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2297743499.html
- **相关 FB**：`FB_CoERead`（读对象）、`FB_CoEExecuteCommand`（执行命令对象）、`FB_SoEWrite`（SoE 协议写）
