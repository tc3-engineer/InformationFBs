# F_SplitDpv1WriteResPkgPNET

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION` |
| Category | `Profinet DPV1 (Sinamics)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59181579.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_SplitDpv1WriteResPkgPNET.xml`](../examples/P_Demo_F_SplitDpv1WriteResPkgPNET.xml) |

---

## 1. 功能简述

解析 Profinet 上的 DPV1 写响应。功能与 `F_SplitDpv1WriteResPkg` 对应，面向 EL6632 Profinet 主站。

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
| `stDpv1ValueHeaderEx` | `ARRAY [1..iMAX_DPV1_PARAMS] OF ST_Dpv1ValueHeaderEx` | 解析输出：写状态。 |

## 3. 行为说明

收到 `FB_Dpv1WritePNET` 的响应（`bBusy` 落回）后，把响应缓冲指针传给本 FC 解析。本 FC 把每条参数的写状态填到 `stDpv1ValueHeaderEx[k]`（含 success / error code 字段）。业务侧通过 `stDpv1ValueHeaderEx[k].nError` 判断写成功 / 失败：0 = 成功，非零 = 驱动器拒绝写入（参数不存在 / 写保护 / 值越界 等）。函数无状态、同步返回，单个 PLC 周期完成。需要传入与请求时一致的 `stDpv1Parameter` 数组让 FC 知道结构。驱动器侧把多字节状态码用 Motorola 字节序回复，本 FC 自动翻转为 Intel 字节序。

## 4. 错误码 / 返回值

本函数返回 `USINT` = 响应报文长度。

## 5. 使用注意 / 常见坑

- Profinet DPV1 是把 DPV1 协议跑在 Profinet 上的方式。Beckhoff Profinet 主站硬件用 EL6632。（工程经验补充）
- 与 Profibus DPV1 接口几乎一致，差别是用 `iProfinetPort` 代替 `iProfibusSlaveAdr` 寻址 slave。
- Sinamics Profidrive 仍是 Motorola 字节序，本系列函数自动翻转。（工程经验补充）
- 请求 / 响应缓冲长度常量是 `iMAX_DPV1_SIZE_PNET_REQ` / `_PNET_RES`（与 Profibus 版本的 `iMAX_DPV1_SIZE` 不同）。（工程经验补充）
- 完整流程：`F_CreateDpv1*ReqPkgPNET` → `FB_Dpv1*PNET` → `F_SplitDpv1*ResPkgPNET`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_SplitDpv1WriteResPkgPNET.xml`](../examples/P_Demo_F_SplitDpv1WriteResPkgPNET.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：Profinet SINAMICS 写完后解析响应。
- **价值**：封装解析。
- **替代方案对比**：
  - 手解
  - **本 FC**：一行

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.10.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59181579.html
- **相关 FB / FC**：`F_CreateDpv1WriteReqPkgPNET`, `FB_Dpv1WritePNET`
