# FB_EcSoeWrite

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `SoE interface` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57047819.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcSoeWrite.TcPOU`](../examples/P_Demo_FB_EcSoeWrite.TcPOU) |

---

## 1. 功能简述

通过 SoE 协议写入驱动参数。是 `FB_EcSoeRead` 的写入对等版本。从站必须支持 SoE。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId     : T_AmsNetId; 
    nSlaveAddr : UINT; 
    nIdn       : WORD; 
    nElement   : BYTE;
    nDriveNo   : BYTE;
    pCommand   : BOOL;
    pSrcBuf    : PVOID; 
    cbBufLen   : UDINT; 
    bExecute   : BOOL;
    tTimeout   : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站 AMS NetID |
| `nSlaveAddr` | `UINT` | — | 从站固定地址 |
| `nIdn` | `WORD` | — | 参数 IDN |
| `nElement` | `BYTE` | — | Element 位掩码（同 Read） |
| `nDriveNo` | `BYTE` | — | 驱动号 |
| `pCommand` | `BOOL` | — | TRUE = 执行内部命令（PDF 此处参数名为 pCommand，与 Read 的 bCommand 不同；PDF 印刷不一致，行为相同） |
| `pSrcBuf` | `PVOID` | — | 数据首地址 |
| `cbBufLen` | `UDINT` | — | 数据字节数 |
| `bExecute` | `BOOL` | — | 上升沿触发 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy  : BOOL;
    bError : BOOL;
    nErrId : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后判结果。

**典型用法**：
- 写 S-0-0016 (Configuration of Telegram)：配置 PDO
- 写 P-0-xxxx：厂商专有参数

**与 CoE Write 区别**：SoE 的 IDN 体系 vs CoE 的 index+sub-index。AX5xxx 系列建议 SoE 优先，标准 CiA402 对象用 CoE。SoE 协议的优势是 Sercos 体系丰富的标准化驱动参数，缺点是仅 Sercos 驱动支持；CoE 是 EtherCAT 设备通用协议，但驱动专用对象覆盖度可能不如 SoE 完整。工程经验是同一驱动同一参数仅用一种协议访问。

**典型陷阱**：
- 部分 SoE 参数只在特定 Sercos phase 才可写
- pCommand 字段名与 Read 的 bCommand 不同 —— PDF 印刷不一致，但功能等价

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 写入完成 |
| `1861` (`0x745`) | 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **PDF 字段名小笔误**：pCommand 实为 bCommand 类用法
- **Sercos phase 限制**（工程经验补充）：某些参数仅在 phase 2 之前可写
- **写完需 reset**：部分参数写完需"激活"才生效

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcSoeWrite.TcPOU`](../examples/P_Demo_FB_EcSoeWrite.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：换工件类型时调整 AX5206 PID 参数，本 FB 写 P-0-xxxx 厂商参数
- **价值**：运行时调驱动参数，无需停机
- **替代方案对比**：XAE Online Drive Manager → 单台手动；本 FB → PLC 自动

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §9.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57047819.html
- **相关 FB / FC**：`FB_EcSoeRead`、`FB_SoEWrite_ByDriveRef`、`FB_EcCoeSdoWrite`
