# F_CreateDpv1ReadReqPkgPNET

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION` |
| Category | `Profinet DPV1 (Sinamics)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59173899.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_CreateDpv1ReadReqPkgPNET.TcPOU`](../examples/P_Demo_F_CreateDpv1ReadReqPkgPNET.TcPOU) |

---

## 1. 功能简述

生成 Profinet 上的 DPV1 **读参数** 请求报文。功能与 `F_CreateDpv1ReadReqPkg` 相同，区别是面向 Profinet 主站 (EL6632) 的封装。

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
| `iNumOfParams` | `USINT` | 本次报文要读的参数数（1..39）。 |
| `iDriveId` | `USINT` | drive 对象 ID。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    stDpv1Parameter : ARRAY [1..iMAX_DPV1_PARAMS] OF ST_Dpv1ParamAddrEx;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `stDpv1Parameter` | `ARRAY [1..iMAX_DPV1_PARAMS] OF ST_Dpv1ParamAddrEx` | 参数清单数组。 |

## 3. 行为说明

调用流程与 Profibus 版本一致：① 准备 240 字节缓冲 + 参数清单（每条含参数号 / 子索引 / 字节长度）；② 调本 FC 编码，函数自动做 Motorola ↔ Intel 字节翻转；③ 拿到返回的报文长度，传给 `FB_Dpv1ReadPNET` 发出去。函数无状态、同步返回，单个 PLC 周期完成。`iDriveId` 选择目标驱动器对象（PDF: 1..16；按驱动器手册取值）。`iNumOfParams` 范围 1..39，且总报文长度 ≤ 240 字节。

## 4. 错误码 / 返回值

本函数返回 `USINT` = 生成的报文长度。

| 返回值 | 含义 |
|---|---|
| > 0 | 成功 |
| 0 | 参数错误 |

## 5. 使用注意 / 常见坑

- Profinet DPV1 是把 DPV1 协议跑在 Profinet 上的方式。Beckhoff Profinet 主站硬件用 EL6632。（工程经验补充）
- 与 Profibus DPV1 接口几乎一致，差别是用 `iProfinetPort` 代替 `iProfibusSlaveAdr` 寻址 slave。
- Sinamics Profidrive 仍是 Motorola 字节序，本系列函数自动翻转。（工程经验补充）
- 请求 / 响应缓冲长度常量是 `iMAX_DPV1_SIZE_PNET_REQ` / `_PNET_RES`（与 Profibus 版本的 `iMAX_DPV1_SIZE` 不同）。（工程经验补充）
- 完整流程：`F_CreateDpv1*ReqPkgPNET` → `FB_Dpv1*PNET` → `F_SplitDpv1*ResPkgPNET`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_CreateDpv1ReadReqPkgPNET.TcPOU`](../examples/P_Demo_F_CreateDpv1ReadReqPkgPNET.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：Profinet + SINAMICS：上电时一次性读多个驱动参数到 PLC。
- **价值**：封装 Profinet DPV1 读报文编码 + 字节翻转。
- **替代方案对比**：
  - 手撸：100 行
  - **本 FC**：一行

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.10.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59173899.html
- **相关 FB / FC**：`F_SplitDpv1ReadResPkgPNET`, `FB_Dpv1ReadPNET`, `F_CreateDpv1WriteReqPkgPNET`
