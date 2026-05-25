# FB_SoERead

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Drive` |
| Library Version | `1.14.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `General SoE` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2306096267.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_SoERead.xml`](../examples/P_Demo_FB_SoERead.xml) |

---

## 1. 功能简述

通过 **SoE（Sercos over EtherCAT）** 协议读取驱动器一个参数的功能块（Function Block, FB）。SoE 用 IDN（Identification Number，标识号）来寻址参数，如 `S-0-0033`、`S-0-0432`。本 FB 把 PLC 里一段缓冲区的地址（`pDstBuf`）和长度（`BufLen`）交给驱动器，驱动器把参数内容回填进去。

参数的不同"组成部分"由 `Element` 指定：值（Value，`16#40`）、名称（Name）、属性（Attribute）、单位（Unit）、最小/最大值、默认值等。默认情况下属性和值是**并行**读取的；若第三方驱动器不支持这种较快的访问方式而报 ADS 错误，可先用 `FB_SoESetDataAccessMode` 切到较慢的**顺序**访问。

IDN 编号需查对应驱动器文档（AX5000 见 Beckhoff AX5000 IDN 描述）。库提供全局常量 `S_0_IDNs`（= `16#0000`）等基地址，写法如 `S_0_IDNs + 33` 表示 `S-0-0033`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NetId    : T_AmsNetID := '';
    Idn      : WORD;
    Element  : BYTE; 
    pDstBuf  : PVOID;
    BufLen   : UDINT;
    Execute  : BOOL;
    Timeout  : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NetId` | `T_AmsNetID` | `''` | 含 NC 所在 PC 的 AMS NetId 字符串（`T_AmsNetId` 类型）；空串表示本机 |
| `Idn` | `WORD` | — | 要访问的参数号，如 `S_0_IDNs + 33` 表示 `S-0-0033` |
| `Element` | `BYTE` | — | 指定访问参数的哪部分。`16#01` = DataState、`16#02` = Name、`16#04` = Attribute、`16#08` = Unit、`16#10` = Min、`16#20` = Max、`16#40` = Value、`16#80` = Default |
| `pDstBuf` | `PVOID` | — | 接收读出值的变量地址，用 `ADR()` 取 |
| `BufLen` | `UDINT` | — | 接收变量的大小，用 `SIZEOF()` 取 |
| `Execute` | `BOOL` | — | 上升沿触发一次读取 |
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
    Busy        : BOOL;
    Error       : BOOL;
    AdsErrId    : UINT;
    SercosErrId : UINT;
    Attribute   : DWORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `Busy` | `BOOL` | FB 激活后置位，直到收到反馈才复位 |
| `Error` | `BOOL` | `Busy` 复位后若命令传输出错则置位 |
| `AdsErrId` | `UINT` | `Error = TRUE` 时返回最后一条命令的 ADS 错误码 |
| `SercosErrId` | `UINT` | `Error = TRUE` 时返回最后一条命令的 Sercos 错误码 |
| `Attribute` | `DWORD` | 返回该 Sercos 参数的属性 |

## 3. 行为说明

**触发**：`Execute` 上升沿启动一次 SoE 读取：FB 向驱动器发出读 IDN 请求，把结果写入 `pDstBuf` 指向的缓冲区，`Busy := TRUE`，异步执行，**跨多个 PLC 周期**，必须每周期循环调用直到 `Busy` 落回 `FALSE`。

**完成与出错收敛**：本 FB 无 `Done` 输出。成功判据是 **`Busy` 由 TRUE 落回 FALSE 且 `Error = FALSE`**，此时 `pDstBuf` 缓冲区里已是读到的参数值，`Attribute` 给出该参数属性。出错则 `Busy` 复位后 `Error := TRUE`，`AdsErrId` 给 ADS 错误码、`SercosErrId` 给 Sercos 错误码。

**两个错误码并存的含义**：`AdsErrId` 反映"PLC ↔ 驱动器"这条 ADS 通道本身是否出错（超时、设备不可达）；`SercosErrId` 反映"驱动器内部 Sercos 服务"是否拒绝（IDN 不存在、Element 不支持、参数只读等）。诊断时两个都要看：ADS 错多半是通信/配置问题，Sercos 错多半是 IDN/Element 用法问题。

**并行 vs 顺序访问**：默认并行读属性+值；若第三方驱动器不支持并行而 `AdsErrId` 报错，先用 `FB_SoESetDataAccessMode` 切顺序访问再重试。某些参数（如读序列号 `S-0-0432`）还需额外的 ActualLength/MaxLength 信息，可在 Drive Manager 参数列表里通过属性判断（右起第 5 位为 4/5/6/7 时需要）。

**复位边沿**：标准用法是 `Busy = FALSE` 后把 `Execute` 拉回 `FALSE` 再调用一次让 FB 复位（见 PDF 示例 `IF NOT fbRead.Busy THEN fbRead(Axis := Axis, Execute := FALSE); END_IF`）。

## 4. 错误码 / 返回值

错误通过 `Error = TRUE` 输出，分两路：`AdsErrId : UINT`（ADS 错误码）与 `SercosErrId : UINT`（Sercos 错误码）。

| 错误路 | 含义 | 处理建议 |
|---|---|---|
| `AdsErrId` ≠ 0 | ADS 通道错误：超时、设备不可达、NetId/AmsPort 错、驱动器不支持并行访问 | 检查 EtherCAT OP、`Axis` Link、`NetId`；并行不支持则用 `FB_SoESetDataAccessMode` 切顺序 |
| `SercosErrId` ≠ 0 | Sercos 服务错误：IDN 不存在、`Element` 不被支持、参数访问被拒 | 核对 IDN 编号（查驱动器手册）、`Element` 取值、`BufLen` 是否与参数实际大小匹配 |

⚠️ PDF 与 InfoSys 未逐条列出具体 ADS / Sercos 错误码数值。ADS 错误码见 Beckhoff ADS Return Codes 总表；Sercos 错误码见对应驱动器（如 AX5000）Sercos 文档。

**清错**：处理完外部原因后给 `Execute` 新上升沿重试；本 FB 无独立清错入口。

## 5. 使用注意 / 常见坑

- **`pDstBuf` / `BufLen` 必须配对且类型匹配**：`pDstBuf := ADR(变量)`、`BufLen := SIZEOF(变量)`，且变量类型大小要与参数实际大小一致，否则 `SercosErrId` 报错或读出脏数据。
- **`Element` 别忘了**：读"值"必须 `Element := 16#40`，漏掉或填错读到的是别的部分（如属性、单位）。
- **两个错误码都要看**：`AdsErrId` 管通信、`SercosErrId` 管 IDN/参数用法，只看一个会误诊。
- **第三方驱动器先试切顺序访问**：并行不支持报 ADS 错时，用 `FB_SoESetDataAccessMode` 切顺序。
- **没有 `Done` 输出 + `Busy` 期间持续循环调用**：异步跨周期，判完成靠 `Busy` 落回 FALSE。
- **IDN 用 `S_0_IDNs + n` 写法**：直观且不易错，比手填 `16#00xx` 可读。
- **`AXIS_REF` 必须传引用**：`Axis` 是 VAR_IN_OUT。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_SoERead.xml`](../examples/P_Demo_FB_SoERead.xml)

```iecst
// 场景：读驱动器某 SoE 参数值（IDN S-0-0033, Element 16#40 = Value）
nReadIdn := S_0_IDNs + 33;
rtReadTrig(CLK := bReadParamReq);
fbSoERead(
    NetId   := '',
    Idn     := nReadIdn,
    Element := 16#40,
    pDstBuf := ADR(nReadValue),
    BufLen  := SIZEOF(nReadValue),
    Execute := rtReadTrig.Q,
    Timeout := DEFAULT_ADS_TIMEOUT,
    Axis    := axisServo,
    Busy    => bReadBusy,
    Error   => bReadError,
    AdsErrId    => nReadAdsErr,
    SercosErrId => nReadSercosErr,
    Attribute   => nReadAttribute
);
```

## 7. 业务场景与实际价值

- **场景**：读取 AX5000/伺服驱动器的电流、温度、序列号、运行参数等 SoE 参数用于监控/诊断/记录；上线前读出参数做配置校验。
- **价值**：直接用 IDN 寻址即可读任意 SoE 参数，无需为每个参数写专用 FB；通过 `AXIS_REF` 关联轴，不必单独管理 NetId/从站地址。
- **替代方案对比**：
  - 用通用 `ADSREAD`：要自己拼 SoE 索引组/偏移，繁琐易错
  - 用型号专用读取 FB（如 `FB_SoEAX5000ReadActMainVoltage`）：只覆盖特定参数，通用性差
  - **本 FB**：IDN + Element 通用读取任意 SoE 参数的标准入口

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf) §4.2.1，全局常量 §6.1 `S_0_IDNs`
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2306096267.html
- **相关 FB**：`FB_SoEWrite`（写参数）、`FB_SoESetDataAccessMode`（切并行/顺序）、`FB_CoERead`（CoE 协议读）
