# FB_Dpv1ReadPNET

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Profinet DPV1 (Sinamics)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59175435.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_Dpv1ReadPNET.xml`](../examples/P_Demo_FB_Dpv1ReadPNET.xml) |

---

## 1. 功能简述

SINAMICS Profidrive 经 Profinet（EL6632 主站）做 DPV1 读参数。与 `FB_Dpv1Read` 对称，差别是用 `iProfinetPort` 寻址 slave。

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
| `aNetId` | `T_AmsNetId` | Profinet 主站 AMS Net ID（EL6632）。 |
| `iProfinetPort` | `UINT` | Profinet 上 slave 的 port 编号（System Manager 自动分配）。 |
| `iDriveId` | `USINT` | drive 对象 ID（PDF 描述 0..255；按驱动器手册取值）。 |
| `pDpv1ReqData` | `POINTER TO ARRAY [1..iMAX_DPV1_SIZE_PNET_REQ] OF BYTE` | 请求帧缓冲指针。 |
| `iDpv1ReqDataLen` | `UDINT` | 请求缓冲最大长度。 |
| `pDpv1ResData` | `POINTER TO ARRAY [1..iMAX_DPV1_SIZE_PNET_RES] OF BYTE` | 响应帧缓冲指针。 |
| `iDpv1ResDataLen` | `UDINT` | 响应缓冲最大长度。 |
| `tTmOut` | `TIME` | ADS 超时。 |

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
| `iRequestRef` | `USINT` | 请求引用号（PDF 的 VAR_IN_OUT 标记是排版错，实际是 VAR_OUTPUT）。 |
| `bBusy` | `BOOL` | FB 激活到收到反馈期间保持 TRUE。`bBusy = TRUE` 时不接受新的上升沿触发。 |
| `bError` | `BOOL` | 命令传输出错时在 `bBusy` 下降之后置 TRUE。下次成功上升沿触发后自动清零。 |
| `bErrorValues` | `BOOL` | 布尔标志 `bErrorValues`。 |
| `iErrId` | `UDINT` | 无符号整数 `iErrId`。 |
| `iErrorClass` | `BYTE` | 无符号整数 `iErrorClass`。 |
| `iErrorCode` | `BYTE` | 无符号整数 `iErrorCode`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

`bExecute` 上升沿触发：`bBusy := TRUE`，FB 经 ADS 把请求帧发到 Profinet 主站 (`aNetId`)，主站把帧发到 `iProfinetPort` 寻址的 slave 驱动器，等待响应。`bBusy = TRUE` 直到响应到来；下降沿后业务侧立刻调 `F_SplitDpv1ReadResPkgPNET` 解析响应。执行时长取决于参数数量与 Profinet 周期，多参数读取建议 `tTmOut ≥ 10 秒`。PDF 中 `iDriveId` 的描述列写"0..255 possible"，但与 Profibus 版本说的"1..16"冲突，⚠️ 以驱动器手册为准。请求 / 响应缓冲长度常量与 Profibus 版本不同：`iMAX_DPV1_SIZE_PNET_REQ` / `_PNET_RES`。

## 4. 错误码 / 返回值

本 FB 无具体错误码表；状态由输出参数自行反映。具体错误语义需配合主站 / 现场总线设备手册查询。

## 5. 使用注意 / 常见坑

- Profinet DPV1 是把 DPV1 协议跑在 Profinet 上的方式。Beckhoff Profinet 主站硬件用 EL6632。（工程经验补充）
- 与 Profibus DPV1 接口几乎一致，差别是用 `iProfinetPort` 代替 `iProfibusSlaveAdr` 寻址 slave。
- Sinamics Profidrive 仍是 Motorola 字节序，本系列函数自动翻转。（工程经验补充）
- 请求 / 响应缓冲长度常量是 `iMAX_DPV1_SIZE_PNET_REQ` / `_PNET_RES`（与 Profibus 版本的 `iMAX_DPV1_SIZE` 不同）。（工程经验补充）
- 完整流程：`F_CreateDpv1*ReqPkgPNET` → `FB_Dpv1*PNET` → `F_SplitDpv1*ResPkgPNET`。
- `iDriveId` 取值范围 PDF 描述与 Profibus 版本不一致；以驱动器手册为准。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_Dpv1ReadPNET.xml`](../examples/P_Demo_FB_Dpv1ReadPNET.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：Profinet SINAMICS 周期读多个驱动参数。
- **价值**：封装异步 Profinet DPV1。
- **替代方案对比**：
  - 手撸 ADS：繁琐
  - **本 FB**：标准

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.10.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59175435.html
- **相关 FB / FC**：`F_CreateDpv1ReadReqPkgPNET`, `F_SplitDpv1ReadResPkgPNET`, `FB_Dpv1WritePNET`
