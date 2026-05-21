# FB_Dpv1Write

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Profibus DPV1 (Sinamics)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59169419.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_Dpv1Write.xml`](../examples/P_Demo_FB_Dpv1Write.xml) |

---

## 1. 功能简述

SINAMICS Profidrive 通过 Profibus DPV1 写 1..39 个参数。与 `FB_Dpv1Read` 用法对称：先 `F_CreateDpv1WriteReqPkg` 准备帧 → 本 FB 发 → `bBusy` 下降后 `F_SplitDpv1WriteResPkg` 解析响应。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute : BOOL;
    aNetId : T_AmsNetId;
    iProfibusSlaveAdr : USINT;
    iDriveId : USINT;
    pDpv1ReqData : POINTER TO ARRAY [1..iMAX_DPV1_SIZE] OF BYTE;
    iDpv1ReqDataLen : UDINT;
    pDpv1ResData : POINTER TO ARRAY [1..iMAX_DPV1_SIZE] OF BYTE;
    iDpv1ResDataLen : UDINT;
    tTmOut : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `bExecute` | `BOOL` | - | 上升沿触发一次 DPV1 写。 |
| `aNetId` | `T_AmsNetId` | - | Profibus 主站 AMS Net ID。 |
| `iProfibusSlaveAdr` | `USINT` | - | SINAMICS 在 Profibus 上的 DP 地址。 |
| `iDriveId` | `USINT` | - | drive 对象 ID（1=CU, 2=drive A, ...）。 |
| `pDpv1ReqData` | `POINTER TO ARRAY [1..iMAX_DPV1_SIZE] OF BYTE` | - | 240 字节请求帧缓冲指针。 |
| `iDpv1ReqDataLen` | `UDINT` | - | 请求缓冲最大长度。 |
| `pDpv1ResData` | `POINTER TO ARRAY [1..iMAX_DPV1_SIZE] OF BYTE` | - | 240 字节响应缓冲指针。 |
| `iDpv1ResDataLen` | `UDINT` | - | 响应缓冲最大长度。 |
| `tTmOut` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 超时。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    iRequestRef : USINT;
    bBusy : BOOL;
    bError : BOOL;
    bErrorValues : BOOL;
    iErrId : UDINT;
    iErrorClass : BYTE;
    iErrorCode : BYTE;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `iRequestRef` | `USINT` | 请求引用号（1..127；0 保留）。 |
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bError` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `bErrorValues` | `BOOL` | 布尔标志 `bErrorValues`。 |
| `iErrId` | `UDINT` | 无符号整数 `iErrId`。 |
| `iErrorClass` | `BYTE` | 无符号整数 `iErrorClass`。 |
| `iErrorCode` | `BYTE` | 无符号整数 `iErrorCode`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

`bExecute` 上升沿触发一次 DPV1 写：`bBusy := TRUE`，FB 经 ADS 把写请求发到 Profibus 主站（`aNetId`），主站把报文转给 slave 驱动器；等待 slave 应答。应答到来后 `bBusy := FALSE`，业务侧调 `F_SplitDpv1WriteResPkg` 解析每条参数的写状态。`tTmOut` 控制超时；写多参数时建议 ≥ 10 秒。`iRequestRef` 是请求引用号；多并发请求时可用来匹配。与读 FB 一样，PDF 中 `VAR_IN_OUT iRequestRef` 是排版错误，实际是 `VAR_OUTPUT`。

## 4. 错误码 / 返回值

本 FB 无具体错误码表；状态由输出参数自行反映。具体错误语义需配合主站 / 现场总线设备手册查询。

## 5. 使用注意 / 常见坑

- Sinamics Profidrive 用 Motorola (big-endian) 字节序，TwinCAT 用 Intel (little-endian)。本系列函数自动做字节翻转。（工程经验补充）
- DPV1 通讯需要 Profibus 主站 FC310x / CX1500-M310 / EL6731 之一；普通 EtherCAT 不行。（工程经验补充）
- 一次最多 39 个参数；DPV1 报文最大 240 字节。超过会被截断。（工程经验补充）
- 参数定义在 `ST_Dpv1ParamAddrEx` 数组里：每条记录含参数号、子索引、字节长度等。（工程经验补充）
- 完整的"读 / 写参数"流程是 3 步：`F_CreateDpv1*ReqPkg` 生成报文 → `FB_Dpv1*` 发报文等响应 → `F_SplitDpv1*ResPkg` 解析响应。
- 写参数会改变驱动器实际行为，写之前务必把驱动器停下或在安全状态。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_Dpv1Write.xml`](../examples/P_Demo_FB_Dpv1Write.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：SINAMICS S120 上电下发驱动参数：速度限值 + 加速度 + 急停减速度 一次性写入。
- **价值**：封装 DPV1 写报文 + 异步发送。
- **替代方案对比**：
  - 用 Starter 软件：要工程模式
  - **本 FB**：纯 PLC 程序

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.9.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59169419.html
- **相关 FB / FC**：`F_CreateDpv1WriteReqPkg`, `F_SplitDpv1WriteResPkg`, `FB_Dpv1Read`
