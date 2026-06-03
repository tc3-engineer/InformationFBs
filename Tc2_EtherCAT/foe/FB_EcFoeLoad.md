# FB_EcFoeLoad

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `FoE interface` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57041803.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcFoeLoad.TcPOU`](../examples/P_Demo_FB_EcFoeLoad.TcPOU) |

---

## 1. 功能简述

通过 FoE（File access over EtherCAT）协议在 PLC 与 EtherCAT 从站之间上传或下载文件。本 FB 是"一站式"接口：自动把目标从站切到 BOOTSTRAP 模式、传输文件、再恢复原状态。是固件升级（`.efw` 文件下载）的标准 FB。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId     : T_AmsNetId ;
    nSlaveAddr : UINT;     
    sPathName  : T_MaxString;
    dwPass     : DWORD := 0;
    eMode      : E_EcFoeMode := eFoeMode_Write;
    bExecute   : BOOL; 
    tTimeout   : TIME := T#200s; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站 AMS NetID |
| `nSlaveAddr` | `UINT` | — | 目标从站固定地址 |
| `sPathName` | `T_MaxString` | — | 本机文件路径（不可用网络路径），如 `'C:\FOE_Test\EL6751\ECATFW__EL6751_C6_V0030.efw'` |
| `dwPass` | `DWORD` | `0` | FoE 密码 |
| `eMode` | `E_EcFoeMode` | `eFoeMode_Write` | 操作模式：写（PLC→从站）/ 读（从站→PLC） |
| `bExecute` | `BOOL` | — | 上升沿触发 |
| `tTimeout` | `TIME` | `T#200s` | 超时（默认 200 s，因固件传输耗时） |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy     : BOOL;
    bError    : BOOL;
    nErrId    : UDINT;
    cbLoad    : UDINT;
    nProgress : UDINT;
    sInfo     : T_MaxString;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中（长时） |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |
| `cbLoad` | `UDINT` | 成功传输字节数 |
| `nProgress` | `UDINT` | 写入进度（0~100%），仅写时有效 |
| `sInfo` | `T_MaxString` | 附加信息（保留） |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 保持 TRUE 数秒到数分钟（视文件大小）。

**自动状态切换**：本 FB 内部自动 `从站 OP → BOOTSTRAP → 传输 → 恢复原状态`。调用方无需手动切换状态。这意味着固件升级期间该从站脱离正常 PDO 数据流，业务侧需感知"该从站暂时不可用"。

**`tTimeout` 默认 200 s**：大固件文件可能数分钟，默认 200 s 应付绝大多数；超大文件可加到 600 s。

**典型用法**：
- 固件升级：sPathName 指向 `.efw` 文件，`eMode = Write`
- 配置文件下载：从站支持的 FoE 配置文件

**典型陷阱**：
- 网络路径不支持：必须是本机绝对路径
- 升级期间从站不可用：业务必须处理"暂时离线"
- 中途断电极危险：可能导致从站固件损坏需返厂

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 升级完成 |
| `1861` (`0x745`) | 超时 | 增大 `tTimeout` |
| FoE 错误码 | 见 InfoSys | 用 `FB_EcGetLastProtErrInfo` |

## 5. 使用注意 / 常见坑

- **断电保护**：升级期间不可断电；HMI 上锁"升级中"按钮
- **密码字段**：部分从站要求 dwPass，不知道默认 0 试
- **批量升级**（工程经验补充）：多从站升级时串行调用，不可并发

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcFoeLoad.TcPOU`](../examples/P_Demo_FB_EcFoeLoad.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：客户现场 100 台 EL6751 模块统一升级固件；维修员把 .efw 拷到 PLC 本机，HMI 点"批量升级"按钮 PLC 串行调本 FB 升每台。免去逐台拆机 USB 烧录
- **价值**：现场固件批量升级 PLC 化，省去 USB 烧录器 + 拆装时间
- **替代方案对比**：XAE 在线 Update Firmware → 单台手动；本 FB → 批量 PLC 自动

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §8.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57041803.html
- **相关 FB / FC**：`FB_EcFoeOpen` / `Close` / `Access`（低级 API）、`FB_EcFoeReadFile` / `WriteFile`（远程文件服务版）
