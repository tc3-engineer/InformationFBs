# F_CreateDpv1WriteReqPkgPNET

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION` |
| Category | `Profinet DPV1 (Sinamics)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59178507.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_CreateDpv1WriteReqPkgPNET.xml`](../examples/P_Demo_F_CreateDpv1WriteReqPkgPNET.xml) |

---

## 1. 功能简述

生成 Profinet 上的 DPV1 **写参数** 请求报文。与 `F_CreateDpv1WriteReqPkg` 对应，面向 EL6632 Profinet 主站。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pDpv1ReqData : POINTER TO ARRAY [1..iMAX_DPV1_SIZE] OF BYTE;
    iNumOfParams : USINT;
    iDriveId : USINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pDpv1ReqData` | `POINTER TO ARRAY [1..iMAX_DPV1_SIZE] OF BYTE` | 240 字节缓冲指针。 |
| `iNumOfParams` | `USINT` | 要写的参数数。 |
| `iDriveId` | `USINT` | drive 对象 ID。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stDpv1Parameter : ARRAY [1..iMAX_DPV1_PARAMS] OF ST_Dpv1ParamAddrEx;
    stDpv1ValueHeaderEx : ARRAY [1..iMAX_DPV1_PARAMS] OF ST_Dpv1ValueHeaderEx;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stDpv1Parameter` | `ARRAY [1..iMAX_DPV1_PARAMS] OF ST_Dpv1ParamAddrEx` | 参数清单。 |
| `stDpv1ValueHeaderEx` | `ARRAY [1..iMAX_DPV1_PARAMS] OF ST_Dpv1ValueHeaderEx` | 值清单。 |

## 3. 行为说明

调用流程与 Profibus 写版本相同：① 准备 240 字节缓冲 + 参数清单 + 值清单；② 在参数清单填写每条记录的参数号 / 子索引 / 长度，在值清单填要写入的值；③ 调本 FC 编码生成报文，自动做 Motorola ↔ Intel 字节翻转；④ 拿到返回报文长度，用 `FB_Dpv1WritePNET` 发出去。函数无状态、同步返回，单个 PLC 周期完成；不会阻塞业务任务。返回值 > 0 表示报文成功生成；0 表示参数错（如 iNumOfParams 越界）。

## 4. 错误码 / 返回值

本函数返回 `USINT` = 生成的报文长度。

| 返回值 | 含义 |
|---|---|
| > 0 | 成功 |
| 0 | 错误 |

## 5. 使用注意 / 常见坑

- Profinet DPV1 是把 DPV1 协议跑在 Profinet 上的方式。Beckhoff Profinet 主站硬件用 EL6632。（工程经验补充）
- 与 Profibus DPV1 接口几乎一致，差别是用 `iProfinetPort` 代替 `iProfibusSlaveAdr` 寻址 slave。
- Sinamics Profidrive 仍是 Motorola 字节序，本系列函数自动翻转。（工程经验补充）
- 请求 / 响应缓冲长度常量是 `iMAX_DPV1_SIZE_PNET_REQ` / `_PNET_RES`（与 Profibus 版本的 `iMAX_DPV1_SIZE` 不同）。（工程经验补充）
- 完整流程：`F_CreateDpv1*ReqPkgPNET` → `FB_Dpv1*PNET` → `F_SplitDpv1*ResPkgPNET`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_CreateDpv1WriteReqPkgPNET.xml`](../examples/P_Demo_F_CreateDpv1WriteReqPkgPNET.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：Profinet SINAMICS 上电写参数。
- **价值**：封装 Profinet DPV1 写报文编码。
- **替代方案对比**：
  - 手撸
  - **本 FC**：一行

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.10.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59178507.html
- **相关 FB / FC**：`F_SplitDpv1WriteResPkgPNET`, `FB_Dpv1WritePNET`
