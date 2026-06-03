# FB_EcFoeReadFile

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `FoE interface` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/9859439755.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcFoeReadFile.TcPOU`](../examples/P_Demo_FB_EcFoeReadFile.TcPOU) |

---

## 1. 功能简述

从 EtherCAT 从站下载文件到本机或远端文件服务器。是 `FB_EcFoeLoad` 的扩展版 —— 多出"文件存哪台机"选项，可写到本机也可写到远端 TwinCAT IPC（通过 `sFSrvNetId`）。

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
| `sFSrvNetId` | `T_AmsNetId` | `''` | 文件目标 IPC AMS NetID；空 = 本机 |
| `sFSrvPathName` | `T_MaxString` | — | 目标文件路径（如 `'C:\Data\LogData.csv'`） |
| `sEcNetId` | `T_AmsNetId` | — | EtherCAT 主站 AMS NetID |
| `nSlaveAddr` | `UINT` | — | 源从站固定地址 |
| `sFoEPathName` | `T_MaxString` | — | 从站上的文件名（FoE 路径） |
| `dwPass` | `DWORD` | `0` | FoE 密码 |
| `bExecute` | `BOOL` | — | 上升沿触发 |
| `tTimeout` | `TIME` | `T#200s` | 超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy     : BOOL;
    bError    : BOOL;
    nErrId    : UDINT;
    cbRead    : UDINT;
    sInfo     : T_MaxString;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中（长时） |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |
| `cbRead` | `UDINT` | 成功读取字节数 |
| `sInfo` | `T_MaxString` | 附加 FoE 错误信息（保留） |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 保持 TRUE 直到文件传输完成。

**远程文件服务器特性**：本 FB 比 `FB_EcFoeLoad` 多了 `sFSrvNetId` —— 可以指定"文件存哪台 TwinCAT IPC"。例如 PLC 在 CX2030（A），文件服务器在另一台 IPC（B），本 FB 可以让 EtherCAT 从站文件直接传到 B 而不经过 A 的本地硬盘。

**Tc2_EtherCAT >= 3.3.14 才有本 FB**。

**典型用法**：
- 日志归档：把生产线 EL 模块的运行日志直接写到中央文件服务器
- 多 PLC 共享配置：从中心库读模板写到 PLC 本地

**典型陷阱**：
- 远程 IPC 必须有 ADS 路由
- 大文件超时调大 `tTimeout`
- 网络路径不支持（必须本机或 ADS 远程，不可 SMB）

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `cbRead` |
| `1861` (`0x745`) | 超时 | 增大 `tTimeout` |
| FoE 错误 | 用 `FB_EcGetLastProtErrInfo` | 取详细 |

## 5. 使用注意 / 常见坑

- **`sFSrvNetId` 空串 = 本机**：与 `FB_EcFoeLoad` 等效
- **路径必须 ADS 可达**（工程经验补充）：远端 IPC 必须有 ADS 路由
- **TwinCAT 版本要求**：≥ 3.3.14

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcFoeReadFile.TcPOU`](../examples/P_Demo_FB_EcFoeReadFile.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：5 条产线各有一台 PLC，但日志统一存到中央文件服务器（独立 IPC）。每条产线 PLC 用本 FB 把 EL 日志直接写到中央服务器，免去经过自己本地硬盘转一次
- **价值**：分布式 IPC 间 FoE 转储，省去中转硬盘空间
- **替代方案对比**：`FB_EcFoeLoad` → 仅本机；本 FB → 远程 IPC

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §8.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/9859439755.html
- **相关 FB / FC**：`FB_EcFoeWriteFile`、`FB_EcFoeLoad`（本机版）
