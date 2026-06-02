# F_SplitDpv1WriteResPkg

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION` |
| Category | `Profibus DPV1 (Sinamics)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59170955.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_SplitDpv1WriteResPkg.TcPOU`](../examples/P_Demo_F_SplitDpv1WriteResPkg.TcPOU) |

---

## 1. 功能简述

解析 DPV1 **写参数** 响应报文。与读响应解析类似，但只关心写操作的状态码（成功 / 失败 / 异常码），不返回数据值。返回报文长度。

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
| `stDpv1Parameter` | `ARRAY [1..iMAX_DPV1_PARAMS] OF ST_Dpv1ParamAddrEx` | 与请求时相同的参数清单。 |
| `stDpv1ValueHeaderEx` | `ARRAY [1..iMAX_DPV1_PARAMS] OF ST_Dpv1ValueHeaderEx` | 输出：每条参数的写状态。 |

## 3. 行为说明

`FB_Dpv1Write` 完成后把响应帧指针传给本 FC，FC 解析并把每条参数的写状态填到 `stDpv1ValueHeaderEx[k]`（字段含 success / error code）。业务侧通过 `stDpv1ValueHeaderEx[k].nError` 判断是否写成功；非零值表示驱动器拒绝写入（参数不存在 / 写保护 / 值越界 等）。与读响应一样需要传入相同的 `stDpv1Parameter` 数组让 FC 知道每条记录的结构。本 FC 无状态、同步返回，单个 PLC 周期完成；不需要等待异步信号。驱动器侧把多字节状态码用 Motorola 字节序回复，本 FC 自动翻转为 Intel 字节序填到输出结构。

## 4. 错误码 / 返回值

本函数返回 `USINT` = 响应报文实际长度。

| 返回值 | 含义 |
|---|---|
| > 0 | 解析成功，写状态在 `stDpv1ValueHeaderEx` 中 |
| 0 | 响应帧空 / 格式错 |

## 5. 使用注意 / 常见坑

- Sinamics Profidrive 用 Motorola (big-endian) 字节序，TwinCAT 用 Intel (little-endian)。本系列函数自动做字节翻转。（工程经验补充）
- DPV1 通讯需要 Profibus 主站 FC310x / CX1500-M310 / EL6731 之一；普通 EtherCAT 不行。（工程经验补充）
- 一次最多 39 个参数；DPV1 报文最大 240 字节。超过会被截断。（工程经验补充）
- 参数定义在 `ST_Dpv1ParamAddrEx` 数组里：每条记录含参数号、子索引、字节长度等。（工程经验补充）
- 完整的"读 / 写参数"流程是 3 步：`F_CreateDpv1*ReqPkg` 生成报文 → `FB_Dpv1*` 发报文等响应 → `F_SplitDpv1*ResPkg` 解析响应。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_SplitDpv1WriteResPkg.TcPOU`](../examples/P_Demo_F_SplitDpv1WriteResPkg.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：SINAMICS S120 写参数后解析响应：业务侧拿到每条参数的写状态，决定是否需要重试。
- **价值**：封装写操作响应解析。
- **替代方案对比**：
  - 手解 DPV1
  - **本 FC**：一行解析

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.9.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59170955.html
- **相关 FB / FC**：`F_CreateDpv1WriteReqPkg`, `FB_Dpv1Write`, `F_SplitDpv1ReadResPkg`
