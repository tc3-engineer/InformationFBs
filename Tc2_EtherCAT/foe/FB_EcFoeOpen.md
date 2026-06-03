# FB_EcFoeOpen

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `FoE interface` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57043339.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcFoeOpen.TcPOU`](../examples/P_Demo_FB_EcFoeOpen.TcPOU) |

---

## 1. 功能简述

打开 FoE 通信端口，返回 handle (`hFoe`) 供后续 `FB_EcFoeAccess` 用。是 FoE 三件套低级 API 的第一步。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId    : T_AmsNetId;
    nPort     : UINT;     
    sPathName : T_MaxString;
    dwPass    : DWORD;
    eMode     : E_EcFoeMode;
    bExecute  : BOOL; 
    tTimeout  : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站 AMS NetID |
| `nPort` | `UINT` | — | 从站固定地址（参数名 nPort 不是 nSlaveAddr） |
| `sPathName` | `T_MaxString` | — | 文件名（含路径），默认仅取文件名部分；3.3.12.0 后可含扩展名 |
| `dwPass` | `DWORD` | — | FoE 密码 |
| `eMode` | `E_EcFoeMode` | — | 读 / 写模式 |
| `bExecute` | `BOOL` | — | 上升沿触发 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy  : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    hFoe   : T_HFoe;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |
| `hFoe` | `T_HFoe` | FoE handle，给 `FB_EcFoeAccess` / `Close` 用 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读 `hFoe`。

**`sPathName` 扩展名处理**：默认情况下本 FB 仅取路径里的文件名部分（不含扩展名）作为 FoE 协议传送的文件名；3.3.12.0 版本起可通过全局变量 `Tc2_EtherCAT.bEcFoeOpenFileNameWithFileExt` 设为 TRUE 让其保留扩展名。这一行为差异是历史原因 —— 早期 FoE 仅用于固件升级（无需扩展名），后扩展为通用文件传输。

**典型用法**：流式 FoE 三件套第一步 —— `Open` 拿 handle → 循环 `Access` → `Close`。

**典型陷阱**：
- 参数名 `nPort` 易与 ADS port 混淆 —— 实际是从站地址
- 路径处理默认丢扩展名，固件升级勿改全局变量

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `hFoe` |
| `1861` (`0x745`) | 超时 | 增大 `tTimeout` |
| FoE 错误 | 见 `FB_EcGetLastProtErrInfo` | 取详细 |

## 5. 使用注意 / 常见坑

- **必须配套 Close**：避免句柄泄漏
- **`bEcFoeOpenFileNameWithFileExt` 全局变量**：影响全部 FB_EcFoeOpen 实例
- **流式三件套基础**（工程经验补充）：日志读取等长流操作首选

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcFoeOpen.TcPOU`](../examples/P_Demo_FB_EcFoeOpen.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：流式读 EL 模块上的"实时日志文件"，先 Open 拿 handle，再循环 Access 读分块，最后 Close
- **价值**：流式 FoE 处理大文件
- **替代方案对比**：`FB_EcFoeReadFile` 全文件一次读 → 简单但内存爆；本 FB 三件套 → 流式

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §8.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57043339.html
- **相关 FB / FC**：`FB_EcFoeAccess`、`FB_EcFoeClose`、`T_HFoe`、`E_EcFoeMode`
