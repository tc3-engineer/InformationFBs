# F_SplitDpv1ReadResPkgPNET

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION` |
| Category | `Profinet DPV1 (Sinamics)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59176971.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_SplitDpv1ReadResPkgPNET.TcPOU`](../examples/P_Demo_F_SplitDpv1ReadResPkgPNET.TcPOU) |

---

## 1. 功能简述

解析 Profinet 上的 DPV1 读响应。功能与 `F_SplitDpv1ReadResPkg` 对应，但面向 EL6632 Profinet 主站。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pDpv1ResData : POINTER TO ARRAY [1..iMAX_DPV1_SIZE] OF BYTE;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pDpv1ResData` | `POINTER TO ARRAY [1..iMAX_DPV1_SIZE] OF BYTE` | 240 字节响应缓冲指针。 |

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
| `stDpv1Parameter` | `ARRAY [1..iMAX_DPV1_PARAMS] OF ST_Dpv1ParamAddrEx` | 请求时同样的参数清单。 |
| `stDpv1ValueHeaderEx` | `ARRAY [1..iMAX_DPV1_PARAMS] OF ST_Dpv1ValueHeaderEx` | 解析输出。 |

## 3. 行为说明

收到 `FB_Dpv1ReadPNET` 的响应（`bBusy` 落回）后，把响应缓冲指针传给本 FC 解析。本 FC 把响应帧的每条参数值填到 `stDpv1ValueHeaderEx[k]`，并做 Motorola → Intel 字节翻转。业务侧通过 `stDpv1ValueHeaderEx[k].dwValue` 拿到参数值。函数无状态、同步返回，单个 PLC 周期完成；不需要等异步信号。需要传入与请求时一致的 `stDpv1Parameter` 数组，FC 据此判断每条记录的字节长度做拆分。若响应帧含 DPV1 异常码（参数无效 / 写保护等），本 FC 仍可解析但对应字段会标错误。

## 4. 错误码 / 返回值

本函数返回 `USINT` = 响应报文长度。> 0 表示解析成功；0 表示帧空 / 错。

## 5. 使用注意 / 常见坑

- Profinet DPV1 是把 DPV1 协议跑在 Profinet 上的方式。Beckhoff Profinet 主站硬件用 EL6632。（工程经验补充）
- 与 Profibus DPV1 接口几乎一致，差别是用 `iProfinetPort` 代替 `iProfibusSlaveAdr` 寻址 slave。
- Sinamics Profidrive 仍是 Motorola 字节序，本系列函数自动翻转。（工程经验补充）
- 请求 / 响应缓冲长度常量是 `iMAX_DPV1_SIZE_PNET_REQ` / `_PNET_RES`（与 Profibus 版本的 `iMAX_DPV1_SIZE` 不同）。（工程经验补充）
- 完整流程：`F_CreateDpv1*ReqPkgPNET` → `FB_Dpv1*PNET` → `F_SplitDpv1*ResPkgPNET`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_SplitDpv1ReadResPkgPNET.TcPOU`](../examples/P_Demo_F_SplitDpv1ReadResPkgPNET.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：Profinet SINAMICS 读完后解析响应。
- **价值**：封装解析。
- **替代方案对比**：
  - 手解
  - **本 FC**：一行

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.10.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59176971.html
- **相关 FB / FC**：`F_CreateDpv1ReadReqPkgPNET`, `FB_Dpv1ReadPNET`
