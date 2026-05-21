# F_SplitDpv1ReadResPkg

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION` |
| Category | `Profibus DPV1 (Sinamics)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59166347.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_SplitDpv1ReadResPkg.xml`](../examples/P_Demo_F_SplitDpv1ReadResPkg.xml) |

---

## 1. 功能简述

解析 DPV1 **读参数** 响应报文。把 240 字节响应帧拆分为各参数值填到 `stDpv1ValueHeaderEx[k]`，同时把字节序翻转回 Intel。返回报文实际长度。

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
| `stDpv1Parameter` | `ARRAY [1..iMAX_DPV1_PARAMS] OF ST_Dpv1ParamAddrEx` | 与请求时相同的参数清单（解析需要它知道每条记录的字节长度）。 |
| `stDpv1ValueHeaderEx` | `ARRAY [1..iMAX_DPV1_PARAMS] OF ST_Dpv1ValueHeaderEx` | 输出：每条参数解析后的值。 |

## 3. 行为说明

`FB_Dpv1Read` 完成（`bBusy` 落回）后，把响应缓冲指针传给本 FC，FC 根据先前发出的 `stDpv1Parameter`（数组依然要传入用以知道每条记录的字节长度）解析每条参数的值，写到 `stDpv1ValueHeaderEx`，并做 Motorola → Intel 字节翻转。业务侧读 `stDpv1ValueHeaderEx[k].dwValue`（或对应类型）即可拿到参数值。本 FC 无状态、同步返回。若响应帧含 DPV1 异常码（参数无效 / 写保护等），本 FC 仍可解析，但 `stDpv1ValueHeaderEx[k]` 内对应字段会标错误。

## 4. 错误码 / 返回值

本函数返回 `USINT` = 响应报文实际长度（字节，≤ 240）。

| 返回值 | 含义 |
|---|---|
| > 0 | 解析成功 |
| 0 | 响应帧空 / 格式错 |

## 5. 使用注意 / 常见坑

- Sinamics Profidrive 用 Motorola (big-endian) 字节序，TwinCAT 用 Intel (little-endian)。本系列函数自动做字节翻转。（工程经验补充）
- DPV1 通讯需要 Profibus 主站 FC310x / CX1500-M310 / EL6731 之一；普通 EtherCAT 不行。（工程经验补充）
- 一次最多 39 个参数；DPV1 报文最大 240 字节。超过会被截断。（工程经验补充）
- 参数定义在 `ST_Dpv1ParamAddrEx` 数组里：每条记录含参数号、子索引、字节长度等。（工程经验补充）
- 完整的"读 / 写参数"流程是 3 步：`F_CreateDpv1*ReqPkg` 生成报文 → `FB_Dpv1*` 发报文等响应 → `F_SplitDpv1*ResPkg` 解析响应。
- 解析必须传入与请求时一致的 `stDpv1Parameter` 数组——FC 据此知道每条参数的字节长度做正确的拆分。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_SplitDpv1ReadResPkg.xml`](../examples/P_Demo_F_SplitDpv1ReadResPkg.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：SINAMICS S120 读 3 个参数：发出读请求 → bBusy 落回 → 调本 FC 解析响应 → 业务侧读 `stDpv1ValueHeaderEx[1..3]` 拿到 3 个参数值。
- **价值**：封装 DPV1 帧拆分 + 字节翻转。
- **替代方案对比**：
  - 手解 DPV1 协议
  - **本 FC**：一行解析

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.9.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59166347.html
- **相关 FB / FC**：`F_CreateDpv1ReadReqPkg`, `FB_Dpv1Read`, `F_SplitDpv1WriteResPkg`
