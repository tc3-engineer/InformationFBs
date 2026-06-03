# FB_EcGetAllSlaveCrcErrors

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Diagnostic` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57012875.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcGetAllSlaveCrcErrors.TcPOU`](../examples/P_Demo_FB_EcGetAllSlaveCrcErrors.TcPOU) |

---

## 1. 功能简述

一次性读取主站所有从站的 CRC 错误计数总和。每个 DWORD 是一台从站所有端口（A、B、C 端口）的 CRC 计数相加。要分端口看，需要分别用 `FB_EcGetSlaveCrcError`（3 端口）或 `FB_EcGetSlaveCrcErrorEx`（4 端口）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId       : T_AmsNetId;
    pCrcErrorBuf : POINTER TO ARRAY[0..EC_MAX_SLAVES] OF DWORD;
    cbBufLen     : UDINT;    
    bExecute     : BOOL; 
    tTimeout     : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站的 AMS NetID |
| `pCrcErrorBuf` | `POINTER TO ARRAY[0..EC_MAX_SLAVES] OF DWORD` | — | 接收 CRC 计数数组首地址 |
| `cbBufLen` | `UDINT` | — | 数组字节容量 |
| `bExecute` | `BOOL` | — | 上升沿触发一次读 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy   : BOOL;
    bError  : BOOL;
    nErrId  : UDINT;
    nSlaves : UINT; 
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码；`1798` 空指针、`1797` 缓冲过小 |
| `nSlaves` | `UINT` | 从站总数 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读数组。

**CRC 计数语义**：每个从站 ESC 内 Counter 寄存器记录该端口收到的 CRC 错误帧数。本 FB 读取并汇总每台从站所有端口的计数为一个 DWORD。计数单调递增（除非主站 reset）。差值法可定位"过去 N 秒内发生了几次 CRC"。

**典型用法**：
- 周期 10 s 调用一次，与上一次差值；某从站差值 > 0 → 该从站对应链路有 CRC（电缆质量、终端接错、信号衰减）
- 配合 `FB_EcGetSlaveCrcError` 当某从站汇总值出现增量后再分端口查到底是 A、B、C 哪个端口

**典型陷阱**：
- "汇总" = 端口相加，无法区分是 A 还是 B 端口的问题；这是设计目的，不是 bug
- 频繁调用（1 ms 周期）显著增加 ADS 负载，建议 ≥ 1 s 周期
- ESC 内的计数寄存器在 16 bit 处饱和，主站固件会处理溢出但极少数情况下可能反复达饱和值

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 数组可读 |
| `1798` (`0x706`) | 空指针 | 检查 `ADR` |
| `1797` (`0x705`) | 缓冲过小 | 扩大数组 |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **当 CRC 持续增长**：网线、屏蔽、接地的物理层问题；不要只看数字，去现场检查走线
- **EK1122 / EP1122 等分支耦合器**：每个分支独立计数；本 FB 给的是该从站全端口汇总，需要分支精度时用 `FB_EcGetSlaveCrcError`
- **缓冲生命周期**（工程经验补充）：用全局或 FB 成员

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcGetAllSlaveCrcErrors.TcPOU`](../examples/P_Demo_FB_EcGetAllSlaveCrcErrors.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：长距离布线的总装线上，月度可靠性 KPI 包含"过去 30 天累计 CRC 错误数"；用本 FB 每小时记录一次，PLC 端做差值汇总
- **价值**：把"全网 CRC 错误总览"封装成一次 ADS 调用；定位"哪台从站在劣化"的速度比手工查 ESC 寄存器快 10 倍
- **替代方案对比**：手工逐台查 ESC 0x0300 ~ 0x030F 寄存器累人；`FB_EcGetSlaveCrcError` 分端口看更精细但调用次数 = 从站数

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §4.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57012875.html
- **相关 FB / FC**：`FB_EcGetSlaveCrcError`（单从站 3 端口）、`FB_EcGetSlaveCrcErrorEx`（单从站 4 端口）
