# FB_EcFoeWriteFile

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `FoE interface` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/16248044683.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcFoeWriteFile.TcPOU`](../examples/P_Demo_FB_EcFoeWriteFile.TcPOU) |

---

## 1. 功能简述

从本机或远端文件服务器读文件，通过 FoE 写到 EtherCAT 从站。是 `FB_EcFoeReadFile` 的写入对等版本。Tc2_EtherCAT ≥ 3.5.1.0。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sFSrvNetId     : T_AmsNetId := '';
    sFSrvPathName  : T_MaxString;
    sEcNetId       : T_AmsNetId;
    nSlaveAddr     : UINT;     
    sFoEPathName   : T_MaxString;
    dwPass         : DWORD := 0;
    bExecute       : BOOL; 
    tTimeout       : TIME := T#200s; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sFSrvNetId` | `T_AmsNetId` | `''` | 源 IPC AMS NetID；空 = 本机 |
| `sFSrvPathName` | `T_MaxString` | — | 源文件路径 |
| `sEcNetId` | `T_AmsNetId` | — | EtherCAT 主站 NetID |
| `nSlaveAddr` | `UINT` | — | 目标从站固定地址 |
| `sFoEPathName` | `T_MaxString` | — | 从站上文件名 |
| `dwPass` | `DWORD` | `0` | FoE 密码 |
| `bExecute` | `BOOL` | — | 上升沿触发 |
| `tTimeout` | `TIME` | `T#200s` | 超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy     : BOOL;
    bError    : BOOL;
    nErrId    : UDINT;
    cbWritten : UDINT;
    nProgress : UDINT;
    sInfo     : T_MaxString;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |
| `cbWritten` | `UDINT` | 成功写入字节数 |
| `nProgress` | `UDINT` | 写入进度（0~100%） |
| `sInfo` | `T_MaxString` | 附加错误信息（保留） |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 保持 TRUE 直到传输完成。

**与 `FB_EcFoeLoad` 区别**：本 FB 支持远程 IPC 作为文件源（`sFSrvNetId`），`FB_EcFoeLoad` 只能本机。同时本 FB 暴露了 `nProgress` 进度，HMI 可显示百分比。配合 `sFSrvNetId` 远程 IPC 路径，本 FB 是分布式 PLC 网络中的固件中心化分发的核心 FB —— 中央服务器统一管固件版本，所有 PLC 直接拉到自己的从站，无需任何中转缓存。

**典型用法**：
- 多 PLC 批量升级：固件从中央服务器拉到每条产线 PLC 再下发，本 FB 一步到位（中央服务器 → 从站）
- 配置文件下发：从中心库写到 EL 模块本地

**典型陷阱**：
- 远程服务器必须可达
- 大文件 timeout 调高
- 升级期间从站不可用

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 写入完成 |
| `1861` (`0x745`) | 超时 | 增大 `tTimeout` |
| FoE 错误 | `FB_EcGetLastProtErrInfo` | 取详细 |

## 5. 使用注意 / 常见坑

- **`nProgress` 用于 HMI 进度条**
- **远程文件服务器**（工程经验补充）：固件中心化管理与版本控制
- **断电保护**：升级中不可断电

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcFoeWriteFile.TcPOU`](../examples/P_Demo_FB_EcFoeWriteFile.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：100 台分布式 PLC，固件统一从中央版本服务器拉。本 FB 直接拉 → 从站，免去 PLC 本地缓存一份
- **价值**：中央化固件管理，分布式部署
- **替代方案对比**：`FB_EcFoeLoad` + 先从中央拉到本机 → 多一步；本 FB → 一步到位

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §8.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/16248044683.html
- **相关 FB / FC**：`FB_EcFoeReadFile`、`FB_EcFoeLoad`
