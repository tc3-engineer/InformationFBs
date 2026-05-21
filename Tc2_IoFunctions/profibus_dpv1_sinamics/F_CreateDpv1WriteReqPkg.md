# F_CreateDpv1WriteReqPkg

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION` |
| Category | `Profibus DPV1 (Sinamics)` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59167883.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_CreateDpv1WriteReqPkg.xml`](../examples/P_Demo_F_CreateDpv1WriteReqPkg.xml) |

---

## 1. 功能简述

生成 DPV1 **写参数** 请求报文。与读版本类似但多一个 `stDpv1ValueHeaderEx` 数组传递每个参数要写入的值。返回报文实际长度。

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
| `iNumOfParams` | `USINT` | 本次报文要写的参数数（1..39）。 |
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
| `stDpv1Parameter` | `ARRAY [1..iMAX_DPV1_PARAMS] OF ST_Dpv1ParamAddrEx` | 参数清单数组。 |
| `stDpv1ValueHeaderEx` | `ARRAY [1..iMAX_DPV1_PARAMS] OF ST_Dpv1ValueHeaderEx` | 参数值数组，每条对应 `stDpv1Parameter` 同下标的参数要写入的值。 |

## 3. 行为说明

调用流程：① 准备 `pDpv1ReqData`（240 字节缓冲）+ `stDpv1Parameter`（参数清单）+ `stDpv1ValueHeaderEx`（值清单）；② 在 `stDpv1Parameter[k]` 填参数号 / 子索引 / 长度，在 `stDpv1ValueHeaderEx[k]` 填要写入的值；③ 调本 FC 编码生成报文，返回值是组装好的报文长度；④ 用 `FB_Dpv1Write` 发出去。FC 自动把多字节参数值做 Motorola ↔ Intel 字节翻转，保证驱动器收到正确的字节序。本 FC 无状态、同步返回，单个 PLC 周期完成，不会阻塞业务任务。`iDriveId` 选择目标驱动器对象：1 = ControllerUnit，2 = drive A，3 = drive B…（最多 16 个）。

## 4. 错误码 / 返回值

本函数返回 `USINT` = 生成的 DPV1 写报文实际长度。

| 返回值 | 含义 |
|---|---|
| > 0 | 报文生成成功 |
| 0 | 参数错误 |

## 5. 使用注意 / 常见坑

- Sinamics Profidrive 用 Motorola (big-endian) 字节序，TwinCAT 用 Intel (little-endian)。本系列函数自动做字节翻转。（工程经验补充）
- DPV1 通讯需要 Profibus 主站 FC310x / CX1500-M310 / EL6731 之一；普通 EtherCAT 不行。（工程经验补充）
- 一次最多 39 个参数；DPV1 报文最大 240 字节。超过会被截断。（工程经验补充）
- 参数定义在 `ST_Dpv1ParamAddrEx` 数组里：每条记录含参数号、子索引、字节长度等。（工程经验补充）
- 完整的"读 / 写参数"流程是 3 步：`F_CreateDpv1*ReqPkg` 生成报文 → `FB_Dpv1*` 发报文等响应 → `F_SplitDpv1*ResPkg` 解析响应。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_CreateDpv1WriteReqPkg.xml`](../examples/P_Demo_F_CreateDpv1WriteReqPkg.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：SINAMICS S120 上电写参数：把 drive A 的速度限值 + 加速度配置一次性下载。
- **价值**：封装 DPV1 写报文编码 + 字节翻转。
- **替代方案对比**：
  - 手撸 DPV1 协议
  - **本 FC**：一行编码

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.9.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/59167883.html
- **相关 FB / FC**：`F_SplitDpv1WriteResPkg`, `FB_Dpv1Write`, `F_CreateDpv1ReadReqPkg`
