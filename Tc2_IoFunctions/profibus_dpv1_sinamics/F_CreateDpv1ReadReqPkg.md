# F_CreateDpv1ReadReqPkg

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION` |
| Category | `Profibus DPV1 (Sinamics)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59163275.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_CreateDpv1ReadReqPkg.xml`](../examples/P_Demo_F_CreateDpv1ReadReqPkg.xml) |

---

## 1. 功能简述

生成 DPV1 **读参数** 请求报文。给定参数清单 + drive ID，函数在用户准备的 240 字节缓冲里组装好可发送的 DPV1 帧，自动做大小端字节转换。返回值是组装好的报文实际长度（USINT，≤ 240）。

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
| `pDpv1ReqData` | `POINTER TO ARRAY [1..iMAX_DPV1_SIZE] OF BYTE` | 240 字节缓冲指针（用户准备 `ARRAY[1..240] OF BYTE`，传 `ADR()` 进来）。 |
| `iNumOfParams` | `USINT` | 本次报文要读的参数数（1..39）。 |
| `iDriveId` | `USINT` | drive 对象 ID（1 = ControllerUnit，2 = drive A，3 = drive B…1..16）。 |

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
| `stDpv1Parameter` | `ARRAY [1..iMAX_DPV1_PARAMS] OF ST_Dpv1ParamAddrEx` | 参数清单数组（[1..39]）：每条含参数号、子索引、字节长度。 |

## 3. 行为说明

调用流程：① 用户准备 `pDpv1ReqData : POINTER TO ARRAY[1..240] OF BYTE`（240 字节缓冲）+ `stDpv1Parameter : ARRAY[1..39] OF ST_Dpv1ParamAddrEx`（参数清单）；② 在 stDpv1Parameter 里填好要读的参数号、子索引、字节长度（每条记录）；③ 调本 FC：`nLen := F_CreateDpv1ReadReqPkg(pDpv1ReqData := ADR(buf), iNumOfParams := 3, iDriveId := 2, stDpv1Parameter := arrParams)`；④ FC 把 stDpv1Parameter 编码到 DPV1 帧里、自动把多字节参数翻转大小端，返回报文长度；⑤ 把 `nLen` + `buf` 传给 `FB_Dpv1Read` 实际发出。`iDriveId` 选择驱动器对象：1 = ControllerUnit，2 = drive A，3 = drive B…（最多 16）。本 FC 是无状态、立即返回（不像 FB 有 busy / done 状态），单次 PLC 周期完成。

## 4. 错误码 / 返回值

本函数返回 `USINT` = 生成的 DPV1 读报文实际长度（字节数，≤ 240）。

| 返回值 | 含义 |
|---|---|
| > 0 | 报文生成成功，返回长度供后续 `FB_Dpv1Read` 使用 |
| 0 | 参数错误（iNumOfParams 超出 1..39，或参数列表为空） |

## 5. 使用注意 / 常见坑

- Sinamics Profidrive 用 Motorola (big-endian) 字节序，TwinCAT 用 Intel (little-endian)。本系列函数自动做字节翻转。（工程经验补充）
- DPV1 通讯需要 Profibus 主站 FC310x / CX1500-M310 / EL6731 之一；普通 EtherCAT 不行。（工程经验补充）
- 一次最多 39 个参数；DPV1 报文最大 240 字节。超过会被截断。（工程经验补充）
- 参数定义在 `ST_Dpv1ParamAddrEx` 数组里：每条记录含参数号、子索引、字节长度等。（工程经验补充）
- 完整的"读 / 写参数"流程是 3 步：`F_CreateDpv1*ReqPkg` 生成报文 → `FB_Dpv1*` 发报文等响应 → `F_SplitDpv1*ResPkg` 解析响应。
- 返回值如果是 0，说明参数错；不要把 0 当成有效长度传给 `FB_Dpv1Read`，否则 FB 会发空报文。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_CreateDpv1ReadReqPkg.xml`](../examples/P_Demo_F_CreateDpv1ReadReqPkg.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：SINAMICS S120 双轴驱动器：上电时一次性读两个轴的 Speed Setpoint + Actual Position + Fault Code 共 6 个参数。
- **价值**：把 DPV1 帧编码 + 大小端转换封装为一行函数调用。
- **替代方案对比**：
  - 手撸 DPV1 协议：约 100 行 + 大小端转换
  - 用 SINAMICS Starter 软件读：要工程模式
  - **本 FC**：一行编码

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.9.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59163275.html
- **相关 FB / FC**：`F_SplitDpv1ReadResPkg`, `FB_Dpv1Read`, `F_CreateDpv1WriteReqPkg`
