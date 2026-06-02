# FB_SoEWrite

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Drive` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `General SoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2306123019.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoEWrite.TcPOU`](../examples/P_Demo_FB_SoEWrite.TcPOU) |

---

## 1. 功能简述

通过 **SoE（Sercos over EtherCAT）** 协议写入驱动器一个参数的功能块（Function Block, FB）。与 `FB_SoERead` 对偶：用 IDN（如 `S_0_IDNs + 47` 表示 `S-0-0047`）寻址参数，把 PLC 里一段源缓冲区（`SrcBuf` 地址 + `BufLen` 长度）的内容写进驱动器对应参数。

`Element` 指定写参数的哪部分；通常**只有"值"（Value，`16#40`）可写**，参数的其它组成部分（名称、属性、单位、最小/最大值等）是只读的。`Password` 字段当前未使用——驱动器密码必须用 `FB_SoEWritePassword` 单独写入，本 FB 的 `Password` 留空即可。

IDN 编号需查对应驱动器文档（AX5000 见 Beckhoff AX5000 IDN 描述）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NetId    : T_AmsNetID := '';
    Idn      : WORD;
    Element  : BYTE;
    SrcBuf   : PVOID;
    BufLen   : UDINT;
    Execute  : BOOL;
    Timeout  : TIME := DEFAULT_ADS_TIMEOUT;
    Password : ST_SoE_String;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NetId` | `T_AmsNetID` | `''` | 含 NC 所在 PC 的 AMS NetId 字符串；空串表示本机 |
| `Idn` | `WORD` | — | 要访问的参数号，如 `S_0_IDNs + 47` 表示 `S-0-0047` |
| `Element` | `BYTE` | — | 指定访问参数的哪部分；通常只有值（`16#40` = Value）可写，其它部分只读（`16#01` DataState、`16#02` Name、`16#04` Attribute、`16#08` Unit、`16#10` Min、`16#20` Max、`16#80` Default） |
| `SrcBuf` | `PVOID` | — | 含要写入值的变量地址，用 `ADR()` 取 |
| `BufLen` | `UDINT` | — | 写入数据的字节数，用 `SIZEOF()` 取 |
| `Execute` | `BOOL` | — | 上升沿触发一次写入 |
| `Timeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | FB 执行允许的最大时间 |
| `Password` | `ST_SoE_String` | — | Sercos 字符串密码。当前未使用；密码须用 `FB_SoEWritePassword` 写入 |

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
    Busy        : BOOL;
    Error       : BOOL;
    AdsErrId    : UINT;
    SercosErrId : UINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | FB 激活后置位，直到收到反馈才复位 |
| `Error` | `BOOL` | `Busy` 复位后若命令传输出错则置位 |
| `AdsErrId` | `UINT` | `Error = TRUE` 时返回最后一条命令的 ADS 错误码 |
| `SercosErrId` | `UINT` | `Error = TRUE` 时返回最后一条命令的 Sercos 错误码 |

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次 SoE 写入：FB 把 `SrcBuf` 缓冲区的内容写到驱动器 `Idn` 指定参数的 `Element` 部分，`Busy := TRUE`，异步执行，**跨多个 PLC 周期**，必须每周期循环调用直到 `Busy` 落回 `FALSE`。

**完成与出错收敛**：本 FB 无 `Done` 输出。成功判据是 **`Busy` 由 TRUE 落回 FALSE 且 `Error = FALSE`**。出错则 `Busy` 复位后 `Error := TRUE`，`AdsErrId` 给 ADS 错误码、`SercosErrId` 给 Sercos 错误码。

**双错误码语义**（同 `FB_SoERead`）：`AdsErrId` 管"PLC ↔ 驱动器"的 ADS 通道；`SercosErrId` 管驱动器内部 Sercos 服务（IDN 不存在、参数只读、写值越界等）。写参数最常见的 Sercos 错误是"参数只读"或"写值超出 Min/Max 范围"。

**`SrcBuf`/`BufLen` 一致性**：写入数据类型大小必须与目标参数实际大小一致，否则 `SercosErrId` 报错或写入被截断。写"值"必须 `Element := 16#40`。

**`Password` 字段说明**：本 FB 的 `Password` 形参当前未被使用——不要试图通过它解锁受保护参数。需要密码保护的参数先用 `FB_SoEWritePassword` 把驱动器密码写入，再用本 FB 写参数。

**复位边沿**：同 `FB_SoERead`，`Busy = FALSE` 后把 `Execute` 拉回 `FALSE` 调一次复位。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` 输出，分 `AdsErrId : UINT`（ADS 错误码）与 `SercosErrId : UINT`（Sercos 错误码）两路。

| 错误路 | 含义 | 处理建议 |
|---|---|---|
| `AdsErrId` ≠ 0 | ADS 通道错误：超时、设备不可达、NetId 错 | 检查 EtherCAT OP、`Axis` Link、`NetId` |
| `SercosErrId` ≠ 0 | Sercos 服务错误：IDN 不存在、参数只读、写值越界、需密码保护 | 核对 IDN、确认该参数可写（值用 `16#40`）、写值在 Min/Max 内、必要时先 `FB_SoEWritePassword` |

⚠️ PDF 与 InfoSys 未逐条列出具体 ADS / Sercos 错误码数值。见 Beckhoff ADS Return Codes 总表与驱动器 Sercos 文档。

**清错**：处理完外部原因后给 `Execute` 新上升沿重试；本 FB 无独立清错入口。

## 5. 使用注意 / 常见坑

- **多数参数只有"值"可写**：`Element := 16#40`；试图写名称/属性等只读部分会被 `SercosErrId` 拒绝。
- **写值越界报 Sercos 错**：写之前确认值落在参数 Min/Max 范围内（可先用 `FB_SoERead` 读 Min/Max）。
- **`Password` 形参不起作用**：受保护参数要先用 `FB_SoEWritePassword` 写密码，本 FB 的 `Password` 留空。
- **`SrcBuf`/`BufLen` 类型大小要匹配目标参数**：不匹配会写入失败或截断。
- **双错误码都要看 + 没有 `Done` + `Busy` 期间持续循环调用**：与 `FB_SoERead` 一致。
- **写参数有持久性后果**：SoE 参数写入驱动器是常驻的，写错可能改变伺服行为，写前务必确认 IDN 和值（工程经验补充）。
- **`AXIS_REF` 必须传引用**：`Axis` 是 VAR_IN_OUT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoEWrite.TcPOU`](../examples/P_Demo_FB_SoEWrite.TcPOU)

```iecst
// 场景：把一个 SoE 参数（IDN S-0-0033, Element 16#40 = Value）写成新值
nWriteIdn := S_0_IDNs + 33;
rtWriteTrig(CLK := bWriteParamReq);
fbSoEWrite(
    NetId   := '',
    Idn     := nWriteIdn,
    Element := 16#40,
    SrcBuf  := ADR(nWriteValue),
    BufLen  := SIZEOF(nWriteValue),
    Execute := rtWriteTrig.Q,
    Timeout := DEFAULT_ADS_TIMEOUT,
    Axis    := axisServo,
    Busy    => bWriteBusy,
    Error   => bWriteError,
    AdsErrId    => nWriteAdsErr,
    SercosErrId => nWriteSercosErr
);
```

## 7. 业务场景与实际价值

- **场景**：调试时改伺服参数（增益、限速、滤波等）、产品换型批量改配置、根据工艺动态调整驱动器某参数。
- **价值**：用 IDN 通用寻址写任意可写 SoE 参数，无需为每个参数写专用 FB；参数常驻驱动器侧。
- **替代方案对比**：
  - 用通用 `ADSWRITE`：要自己拼 SoE 索引组/偏移，繁琐易错
  - 在 DriveManager 里手改：人工、无法在程序里自动化
  - **本 FB**：IDN + Element 通用写任意 SoE 参数的标准入口

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf) §4.2.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2306123019.html
- **相关 FB**：`FB_SoERead`（读参数）、`FB_SoEWritePassword`（写驱动器密码）、`FB_CoEWrite`（CoE 协议写）
