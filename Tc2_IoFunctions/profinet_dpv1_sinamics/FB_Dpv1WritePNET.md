# FB_Dpv1WritePNET

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Profinet DPV1 (Sinamics)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59180043.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_Dpv1WritePNET.xml`](../examples/P_Demo_FB_Dpv1WritePNET.xml) |

---

## 1. 功能简述

SINAMICS Profidrive 经 Profinet (EL6632) 做 DPV1 写参数。与 `FB_Dpv1Write` 对称。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bExecute : BOOL;
    aNetId : T_AmsNetId;
    iProfinetPort : UINT;
    iDriveId : USINT;
    pDpv1ReqData : POINTER TO ARRAY [1..iMAX_DPV1_SIZE_PNET_REQ] OF BYTE;
    iDpv1ReqDataLen : UDINT;
    pDpv1ResData : POINTER TO ARRAY [1..iMAX_DPV1_SIZE_PNET_RES] OF BYTE;
    iDpv1ResDataLen : UDINT;
    tTmOut : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bExecute` | `BOOL` | 上升沿触发。 |
| `aNetId` | `T_AmsNetId` | EL6632 主站 NetId。 |
| `iProfinetPort` | `UINT` | SINAMICS Profinet port。 |
| `iDriveId` | `USINT` | drive 对象 ID。 |
| `pDpv1ReqData` | `POINTER TO ARRAY [1..iMAX_DPV1_SIZE_PNET_REQ] OF BYTE` | 请求帧缓冲。 |
| `iDpv1ReqDataLen` | `UDINT` | 请求缓冲长度。 |
| `pDpv1ResData` | `POINTER TO ARRAY [1..iMAX_DPV1_SIZE_PNET_RES] OF BYTE` | 响应帧缓冲。 |
| `iDpv1ResDataLen` | `UDINT` | 响应缓冲长度。 |
| `tTmOut` | `TIME` | 超时。 |

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
| `iRequestRef` | `USINT` | 请求引用号。 |
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bError` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `bErrorValues` | `BOOL` | 布尔标志 `bErrorValues`。 |
| `iErrId` | `UDINT` | 无符号整数 `iErrId`。 |
| `iErrorClass` | `BYTE` | 无符号整数 `iErrorClass`。 |
| `iErrorCode` | `BYTE` | 无符号整数 `iErrorCode`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

`bExecute` 上升沿触发：FB 经 ADS 把写请求帧发到 Profinet 主站 → slave 驱动器，等响应。`bBusy = TRUE` 直到响应到来；下降后业务侧调 `F_SplitDpv1WriteResPkgPNET` 解析写状态。与 `FB_Dpv1Write` 的区别：用 `iProfinetPort` 代替 `iProfibusSlaveAdr` 寻址 slave；请求 / 响应缓冲长度常量是 PNET 系列。`tTmOut` 控制 ADS 超时，多参数时 ≥ 10 秒。PDF 中 `iRequestRef` 在 "Inputs/outputs" 章节实际是 `VAR_OUTPUT`，排版错。

## 4. 错误码 / 返回值

本 FB 无具体错误码表；状态由输出参数自行反映。具体错误语义需配合主站 / 现场总线设备手册查询。

## 5. 使用注意 / 常见坑

- Profinet DPV1 是把 DPV1 协议跑在 Profinet 上的方式。Beckhoff Profinet 主站硬件用 EL6632。（工程经验补充）
- 与 Profibus DPV1 接口几乎一致，差别是用 `iProfinetPort` 代替 `iProfibusSlaveAdr` 寻址 slave。
- Sinamics Profidrive 仍是 Motorola 字节序，本系列函数自动翻转。（工程经验补充）
- 请求 / 响应缓冲长度常量是 `iMAX_DPV1_SIZE_PNET_REQ` / `_PNET_RES`（与 Profibus 版本的 `iMAX_DPV1_SIZE` 不同）。（工程经验补充）
- 完整流程：`F_CreateDpv1*ReqPkgPNET` → `FB_Dpv1*PNET` → `F_SplitDpv1*ResPkgPNET`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_Dpv1WritePNET.xml`](../examples/P_Demo_FB_Dpv1WritePNET.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：Profinet SINAMICS 上电下发参数。
- **价值**：封装异步 Profinet DPV1 写。
- **替代方案对比**：
  - 手撸
  - **本 FB**：标准

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.10.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59180043.html
- **相关 FB / FC**：`F_CreateDpv1WriteReqPkgPNET`, `F_SplitDpv1WriteResPkgPNET`, `FB_Dpv1ReadPNET`
