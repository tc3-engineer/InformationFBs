# FB_EcCoESdoAbortCode

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `CoE interface` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1031/tcplclib_tc2_ethercat/19126799883.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcCoESdoAbortCode.TcPOU`](../examples/P_Demo_FB_EcCoESdoAbortCode.TcPOU) |

---

## 1. 功能简述

读取指定从站最近一次 CoE SDO 失败的 abort code。返回 `ST_EcAbortCode` 结构包含详细错误信息。当 `FB_EcCoeSdoRead`/`Write` 报错后立即调本 FB 取详细原因，比通用 ADS 错误码精确得多。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId          : T_AmsNetId; 
    nSlaveAddr      : UINT;  
    bExecute        : BOOL;  
    tTimeout        : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站 AMS NetID |
| `nSlaveAddr` | `UINT` | — | 报错从站固定地址 |
| `bExecute` | `BOOL` | — | 上升沿触发 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy  : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    stAbortCode : ST_EcAbortCode;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |
| `stAbortCode` | `ST_EcAbortCode` | CoE Abort Code 结构（含错误码与描述） |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读 `stAbortCode`。

**最近错误生命周期**：与 `FB_EcGetLastProtErrInfo`（多协议通用版）的概念相同 —— 主站对每个从站每种协议维护一份"最近 abort"，任何成功的同种协议调用会覆盖。所以必须在 CoE 错误发生后立即调本 FB。

**与 `FB_EcGetLastProtErrInfo` 的区别**：
- 本 FB：专门读 CoE Abort，返回结构更紧凑直接
- `FB_EcGetLastProtErrInfo`：通用，支持 CoE / FoE / SoE 等

**常见 CoE Abort Code**：
- `0x06010002`：对象只读，写入被拒
- `0x06020000`：对象不存在
- `0x06070010`：数据长度不匹配
- `0x06090030`：数值超出范围
- `0x08000020`：数据不能传送或保存

**典型陷阱**：
- 必须立即调用，事后任何成功 CoE 命令会清掉
- 从站不在 OP / 邮箱不通时本 FB 也失败

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `stAbortCode` |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **立刻调**：失败后第一时间，不要先做别的 SDO 读
- **抽象层封装**（工程经验补充）：写"SDO 读写"通用 helper FB 时本 FB 作为错误诊断分支
- **CoE Abort 表**：ETG.1000.4 规范定义全部 Abort code，工程中常做枚举翻译为可读字符串

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcCoESdoAbortCode.TcPOU`](../examples/P_Demo_FB_EcCoESdoAbortCode.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：现场某 EL3008 配置参数写不进去，HMI 仅显示"SDO Write Failed"。维修员按"查看详情"按钮调本 FB，HMI 显示具体 Abort `0x06010002` (Object is read-only) — 立即知道是对象类型错了
- **价值**：把 CoE 错误的真实原因暴露给现场维修
- **替代方案对比**：Wireshark 抓 EtherCAT 包解析 → 慢；本 FB → PLC 直读

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §7.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1031/tcplclib_tc2_ethercat/19126799883.html
- **相关 FB / FC**：`FB_EcGetLastProtErrInfo`（多协议版）、`ST_EcAbortCode`、`FB_EcCoeSdoRead`、`FB_EcCoeSdoWrite`
