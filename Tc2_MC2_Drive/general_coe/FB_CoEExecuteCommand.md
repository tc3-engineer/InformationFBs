# FB_CoEExecuteCommand

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Drive` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `General CoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/7607840779.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_CoEExecuteCommand.xml`](../examples/P_Demo_FB_CoEExecuteCommand.xml) |

---

## 1. 功能简述

通过 **CoE（CANopen over EtherCAT）** 执行一条"命令对象"的功能块（Function Block, FB）。CANopen 里有一类特殊对象不是单纯的"读/写数据"，而是"执行某个动作"（command）——例如触发自整定、复位计数、执行校准等；这类对象需要发起命令后**持续轮询其执行状态**直到完成，这正是本 FB 与 `FB_CoEWrite` 的区别。

`Index` 指定命令对象索引；`pSrcBuf`/`SrcBufLen` 给出命令的输入数据，`pDstBuf`/`DstBufLen` 接收命令的输出数据。`Status` 输出反映命令执行的进展状态。

Index 编号需查对应驱动器对象字典文档。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NetId       : T_AmsNetID := '';
    Index       : WORD;
    pSrcBuf     : PVOID;
    SrcBufLen   : UDINT;
    pDstBuf     : PVOID;
    DstBufLen   : UDINT;
    Execute     : BOOL;
    Timeout     : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NetId` | `T_AmsNetID` | `''` | 含 NC 所在 PC 的 AMS NetId 字符串 |
| `Index` | `WORD` | — | 本 FB 引用的 CoE 命令对象索引 |
| `pSrcBuf` | `PVOID` | — | 要发送数据的结构地址，用 `ADR()` 取 |
| `SrcBufLen` | `UDINT` | — | 要发送数据结构的字节大小，用 `SIZEOF()` 取 |
| `pDstBuf` | `PVOID` | — | 接收数据的结构地址，用 `ADR()` 取 |
| `DstBufLen` | `UDINT` | — | 接收数据结构的字节大小，用 `SIZEOF()` 取 |
| `Execute` | `BOOL` | — | 上升沿触发一次命令执行 |
| `Timeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | FB 执行允许的最大时间 |

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
    Busy    : BOOL;
    Error   : BOOL;
    ErrorId : UDINT;
    Status  : _E_CoECommandStatus;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | FB 激活后置位，直到收到反馈才复位 |
| `Error` | `BOOL` | `Busy` 复位后若命令传输出错则置位 |
| `ErrorId` | `UDINT` | `Error = TRUE` 时返回 ADS 错误码 |
| `Status` | `_E_CoECommandStatus` | 命令执行的状态。⚠️ PDF 与 InfoSys 未列出 `_E_CoECommandStatus` 的具体枚举成员（这是内部状态类型），含义请参见对应驱动器命令对象文档 |

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次命令执行：FB 把 `pSrcBuf` 的输入数据随命令对象 `Index` 发给从站，发起命令后**持续轮询命令执行状态**，结果写入 `pDstBuf`，`Busy := TRUE`，异步执行，**跨多个 PLC 周期**，必须每周期循环调用直到 `Busy` 落回 `FALSE`。

**完成与出错收敛**：本 FB 无 `Done` 输出。成功判据是 **`Busy` 由 TRUE 落回 FALSE 且 `Error = FALSE`**，此时 `pDstBuf` 是命令的输出数据，`Status` 反映最终执行状态。出错则 `Busy` 复位后 `Error := TRUE`、`ErrorId` 给 ADS 错误码。

**`Status` 的作用**：命令型对象与普通读写不同——发起后驱动器需要时间执行，期间命令处于"进行中"，完成后转"成功/失败"。`Status` 输出（`_E_CoECommandStatus`）就是反映这个进展的状态字。⚠️ 其具体枚举成员 PDF/InfoSys 未列出，使用时应结合具体命令对象文档判断，或在线观察 `Status` 值变化推断含义。

**与 `FB_CoEWrite` 的区别**：`FB_CoEWrite` 写完一个值即结束；命令对象要"发起 + 等执行完"，本 FB 内部承担轮询，调用方只需循环调用并看 `Busy`/`Status`。命令型对象需双向数据：输入参数（`pSrcBuf`）和输出结果（`pDstBuf`）。

**复位边沿**：`Busy = FALSE` 后把 `Execute` 拉回 `FALSE` 调一次复位 FB 内部状态。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` + `ErrorId : UDINT` 输出。`ErrorId` 为 **ADS 错误码**（不是 NC 错误号、也不是 HRESULT）。命令执行的状态另由 `Status : _E_CoECommandStatus` 输出。

| 输出 | 含义 | 处理建议 |
|---|---|---|
| `ErrorId` ≠ 0 | ADS 通道错误：超时、从站无 mailbox、对象不存在 | 检查 EtherCAT OP、从站 CoE/mailbox、`Index`、`NetId` |
| `Status` | 命令执行状态字（成功 / 进行中 / 失败等）| ⚠️ 具体枚举值 PDF/InfoSys 未列出，参见驱动器命令对象文档 |

⚠️ PDF 与 InfoSys 未逐条列出具体 ADS 错误码数值，也未列出 `_E_CoECommandStatus` 枚举成员。ADS 错误码见 Beckhoff ADS Return Codes 总表；命令状态含义见对应命令对象文档。

**清错**：处理完外部原因后给 `Execute` 新上升沿重试；本 FB 无独立清错入口。

## 5. 使用注意 / 常见坑

- **命令对象 ≠ 普通读写对象**：用本 FB 而非 `FB_CoEWrite`——命令需"发起 + 等执行完"，本 FB 才会轮询状态。
- **要同时给输入和输出缓冲区**：`pSrcBuf`/`SrcBufLen`（命令参数）与 `pDstBuf`/`DstBufLen`（命令结果）都要正确配对。
- **`Status` 枚举含义不脑补**：⚠️ PDF/InfoSys 未列出 `_E_CoECommandStatus` 成员，结合命令对象文档或在线观察判断，不要凭名字猜。
- **没有 `Done` 输出 + `Busy` 期间持续循环调用**：异步且可能耗时（命令执行），判完成靠 `Busy` 落回 FALSE。
- **错误输出叫 `ErrorId` 不是 `AdsErrId`**：与 `FB_CoERead`/`FB_CoEWrite` 的输出名不同，写代码别照搬。
- **某些命令执行期间不要打断**（如自整定、校准）：中途中止可能让驱动器停在中间状态（工程经验补充）。
- **`AXIS_REF` 必须传引用**：`Axis` 是 VAR_IN_OUT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_CoEExecuteCommand.xml`](../examples/P_Demo_FB_CoEExecuteCommand.xml)

```iecst
// 场景：触发 AX8000 一个 CoE 命令对象（如校准/自整定），等其执行完
rtCmdTrig(CLK := bExecCmdReq);
fbCoECmd(
    NetId     := '',
    Index     := 16#FB00,
    pSrcBuf   := ADR(stCmdInput),
    SrcBufLen := SIZEOF(stCmdInput),
    pDstBuf   := ADR(stCmdOutput),
    DstBufLen := SIZEOF(stCmdOutput),
    Execute   := rtCmdTrig.Q,
    Timeout   := DEFAULT_ADS_TIMEOUT,
    Axis      := axisServo,
    Busy      => bCmdBusy,
    Error     => bCmdError,
    ErrorId   => nCmdErrorId,
    Status    => eCmdStatus
);
```

## 7. 业务场景与实际价值

- **场景**：触发 AX8000 等 CoE 驱动器的命令型功能：参数自整定、编码器校准、计数器复位、出厂复位等需要"发起后等执行完"的动作。
- **价值**：本 FB 内部承担命令轮询，调用方不必自己写"发起→反复读状态→判完成"的状态机，一次调用搞定。
- **替代方案对比**：
  - 用 `FB_CoEWrite` 写命令对象：只写不轮询，无法知道命令何时真正执行完
  - 自己用 `FB_CoERead` 反复读状态：要手写轮询状态机，繁琐易错
  - **本 FB**：命令型对象执行 + 自动轮询的标准入口

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf) §4.3.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/7607840779.html
- **相关 FB**：`FB_CoERead`（读对象）、`FB_CoEWrite`（写对象）
