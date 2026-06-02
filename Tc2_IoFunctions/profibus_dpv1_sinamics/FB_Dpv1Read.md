# FB_Dpv1Read

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Profibus DPV1 (Sinamics)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59164811.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_Dpv1Read.TcPOU`](../examples/P_Demo_FB_Dpv1Read.TcPOU) |

---

## 1. 功能简述

SINAMICS Profidrive 通过 Profibus DPV1 读 1..39 个参数。完整流程：先用 `F_CreateDpv1ReadReqPkg` 准备报文 → 在 `bExecute` 上升沿前数据缓冲已就绪 → 本 FB 发报文 + 等响应；`bBusy` 下降后用 `F_SplitDpv1ReadResPkg` 解析响应。

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
| `bExecute` | `BOOL` | - | 上升沿触发一次 DPV1 读命令。 |
| `aNetId` | `T_AmsNetId` | - | Profibus 主站设备的 AMS Net ID（System Manager → I/O → Profibus master → ADS tab 中查看）。 |
| `iProfibusSlaveAdr` | `USINT` | - | Profibus slave DP 地址（驱动器在 Profibus 上的站号）。 |
| `iDriveId` | `USINT` | - | drive 对象 ID（1 = CU，2 = drive A，3 = drive B…）。 |
| `pDpv1ReqData` | `POINTER TO ARRAY [1..iMAX_DPV1_SIZE] OF BYTE` | - | 240 字节请求帧缓冲指针（由 `F_CreateDpv1ReadReqPkg` 准备）。 |
| `iDpv1ReqDataLen` | `UDINT` | - | 请求帧缓冲的最大长度（240）。 |
| `pDpv1ResData` | `POINTER TO ARRAY [1..iMAX_DPV1_SIZE] OF BYTE` | - | 240 字节响应帧缓冲指针（应答会写到这里）。 |
| `iDpv1ResDataLen` | `UDINT` | - | 响应帧缓冲的最大长度（240）。 |
| `tTmOut` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 本次 ADS 调用的超时。 |

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

`bExecute` 上升沿触发一次 DPV1 读：`bBusy := TRUE`，FB 把 `pDpv1ReqData` 指向的报文经 ADS 发到 Profibus 主站（`aNetId`），主站把报文发到 slave (`iProfibusSlaveAdr`)，等待应答；应答到来后 FB 把数据填到 `pDpv1ResData`。`bBusy = TRUE` → `FALSE` 的下降沿是业务侧判断"读完成"的关键。完成后 `iRequestRef` 含本次请求的引用号（1..127）；出错时由业务侧观察响应解析结果（本 FB 不输出 bError，由解析 FC 给）。`tTmOut` 控制 ADS 调用超时（默认 5 秒，多参数时建议 10 秒）。⚠️ PDF VAR_OUTPUT 区误写为 `VAR_OUTPUT iRequestRef : USINT;`——实际是 `VAR_OUTPUT`，PDF 中 "Inputs/outputs" 章节标记是排版错误。

## 4. 错误码 / 返回值

本 FB 无具体错误码表；状态由输出参数自行反映。具体错误语义需配合主站 / 现场总线设备手册查询。

## 5. 使用注意 / 常见坑

- Sinamics Profidrive 用 Motorola (big-endian) 字节序，TwinCAT 用 Intel (little-endian)。本系列函数自动做字节翻转。（工程经验补充）
- DPV1 通讯需要 Profibus 主站 FC310x / CX1500-M310 / EL6731 之一；普通 EtherCAT 不行。（工程经验补充）
- 一次最多 39 个参数；DPV1 报文最大 240 字节。超过会被截断。（工程经验补充）
- 参数定义在 `ST_Dpv1ParamAddrEx` 数组里：每条记录含参数号、子索引、字节长度等。（工程经验补充）
- 完整的"读 / 写参数"流程是 3 步：`F_CreateDpv1*ReqPkg` 生成报文 → `FB_Dpv1*` 发报文等响应 → `F_SplitDpv1*ResPkg` 解析响应。
- PDF 把 `iRequestRef` 标在 "Inputs/outputs" 章节但 `VAR_OUTPUT` 关键字明显是 PDF 排版错（应为 VAR_OUTPUT 不是 VAR_IN_OUT）；按 VAR_OUTPUT 处理。（工程经验补充）
- `bBusy` 下降沿后业务侧必须立刻调 `F_SplitDpv1ReadResPkg` 解析响应；否则缓冲会被下次请求覆盖。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_Dpv1Read.TcPOU`](../examples/P_Demo_FB_Dpv1Read.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：SINAMICS S120 双轴：周期 1 秒读 6 个参数（双轴 Speed/Position/Fault）做 SCADA 显示。
- **价值**：封装 DPV1 异步通讯，业务只关心 bExecute + 数据缓冲。
- **替代方案对比**：
  - 手撸 ADSREAD/ADSWRITE 到 Profibus 主站
  - **本 FB**：标准方式

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.9.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59164811.html
- **相关 FB / FC**：`F_CreateDpv1ReadReqPkg`, `F_SplitDpv1ReadResPkg`, `FB_Dpv1Write`
