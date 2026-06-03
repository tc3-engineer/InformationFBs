# FB_EcSoeRead

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `SoE interface` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57046283.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcSoeRead.TcPOU`](../examples/P_Demo_FB_EcSoeRead.TcPOU) |

---

## 1. 功能简述

通过 SoE（Sercos over EtherCAT）协议读取驱动参数。从站必须支持 SoE 协议（典型 AX5xxx 系列伺服）。用 `nIdn`（identification number）+ `nElement` 定位参数。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId     : T_AmsNetId; 
    nSlaveAddr : UINT; 
    nIdn       : WORD;
    nElement   : BYTE;
    nDriveNo   : BYTE;
    bCommand   : BOOL
    pDstBuf    : PVOID; 
    cbBufLen   : UDINT; 
    bExecute   : BOOL;
    tTimeout   : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站 AMS NetID |
| `nSlaveAddr` | `UINT` | — | 从站固定地址 |
| `nIdn` | `WORD` | — | 参数 IDN（如 S-0-0015 = `WORD` 值 15） |
| `nElement` | `BYTE` | — | Element 位掩码：0x01=Status, 0x02=Name, 0x04=Attribute, 0x08=Unit, 0x10=Min, 0x20=Max, 0x40=Value, 0x80=Default |
| `nDriveNo` | `BYTE` | — | 驱动号（多驱动器从站如 AX5206 时区分） |
| `bCommand` | `BOOL` | — | TRUE = 执行内部命令 |
| `pDstBuf` | `PVOID` | — | 接收缓冲首地址 |
| `cbBufLen` | `UDINT` | — | 缓冲容量 |
| `bExecute` | `BOOL` | — | 上升沿触发 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy  : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    cbRead : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |
| `cbRead` | `UDINT` | 成功读取字节数 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读 `pDstBuf`。

**SoE vs CoE**：SoE 是基于 Sercos 协议的参数访问，CoE 是基于 CANopen 协议；语义不同 —— SoE 参数按 IDN（S-0-xxxx 或 P-0-xxxx），CoE 按 index+sub-index。Beckhoff AX5xxx 系列伺服两者都支持，选哪个取决于工程师习惯与目标参数定义所在的协议。

**`nElement` 位掩码语义**：可以一次读取一个参数的多个 element —— 例如 `nElement = 0x40` 仅读 Value；`nElement = 0x70` 同时读 Min + Max + Value 共三个 element。读到的数据按顺序填入缓冲。

**典型用法**：
- 读 S-0-0015 (Profile Velocity Command)：`nIdn = 15`、`nElement = 0x40`
- 读 P-0-0023 (vendor specific)：`nIdn = 23`、需要先按 `P_0_IDN` 偏移

**典型陷阱**：
- `nDriveNo` 多驱动器从站易错；单驱动器写 0
- `nElement` 位掩码组合时缓冲必须足够大
- IDN 体系下 S-0-xxxx 与 P-0-xxxx 不同区段

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `pDstBuf` |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |
| Sercos 错误 | `FB_EcGetLastProtErrInfo` | 取详细 |

## 5. 使用注意 / 常见坑

- **AX5xxx 系列推荐**：原生支持 SoE
- **CoE 与 SoE 二选一**（工程经验补充）：避免混用同一参数访问
- **位掩码精度**：`nElement = 0x40` 是最常用（仅 Value）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcSoeRead.TcPOU`](../examples/P_Demo_FB_EcSoeRead.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：AX5206 伺服读 S-0-0015（Profile Velocity Command）做轴速度监视
- **价值**：Sercos 标准协议访问，AX5xxx 原生兼容
- **替代方案对比**：`FB_EcCoeSdoRead` CoE 路径 → AX5xxx 也支持但语义不同；本 FB → Sercos 原生

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §9.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57046283.html
- **相关 FB / FC**：`FB_EcSoeWrite`、`FB_SoERead_ByDriveRef`、`FB_EcCoeSdoRead`
