# FB_EcCoeSdoWriteEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `CoE interface` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57000843.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcCoeSdoWriteEx.TcPOU`](../examples/P_Demo_FB_EcCoeSdoWriteEx.TcPOU) |

---

## 1. 功能简述

带 `bCompleteAccess` 选项的 CoE SDO 写入版。`bCompleteAccess = TRUE` 时把整个对象（所有 sub-element）一次性 download，是写"PDO 映射表"等复合对象的标准方式。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId          : T_AmsNetId;
    nSlaveAddr      : UINT;
    nSubIndex       : BYTE;
    nIndex          : WORD;
    pSrcBuf         : PVOID;
    cbBufLen        : UDINT;
    bExecute        : BOOL;
    tTimeout        : TIME := DEFAULT_ADS_TIMEOUT;
    bCompleteAccess : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站 AMS NetID |
| `nSlaveAddr` | `UINT` | — | 目标从站地址 |
| `nSubIndex` | `BYTE` | — | sub-index（CompleteAccess 时通常 0） |
| `nIndex` | `WORD` | — | 对象 index |
| `pSrcBuf` | `PVOID` | — | 数据首地址 |
| `cbBufLen` | `UDINT` | — | 数据字节数 |
| `bExecute` | `BOOL` | — | 上升沿触发 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 超时 |
| `bCompleteAccess` | `BOOL` | — | TRUE = 写整对象；FALSE = 写单子项 |

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

**`bCompleteAccess` 模式区别**：当 `TRUE` 时把 `pSrcBuf` 整个内容按对象 DUT 顺序写入，覆盖整对象。当 `FALSE` 时只写 `nSubIndex` 单子项，等价于 `FB_EcCoeSdoWrite`。CompleteAccess 是原子写入 —— 中间任何子项失败整笔回滚，避免出现"部分写完部分没写"的中间态，对 PDO 映射这类必须原子的对象至关重要。

**写 PDO 映射对象**：是典型的 CompleteAccess 用例 —— PDO 映射对象（0x1A00 等）含 sub 0（数量）+ sub 1..N（各 PDO entry），必须一次原子写入避免中间态。

**典型用法**：
- 运行时动态切 PDO 映射（多产品兼容机型）
- 写"安全参数组"对象做完整配置

**典型陷阱**：
- 从站不支持 CompleteAccess 时报 Abort `0x06010000`
- 写 PDO 映射前必须先把对应 SyncManager 失能（0x1C12 / 0x1C13 sub 0 写 0），否则报错
- `cbBufLen` 必须精确等于对象总大小

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 写入完成 |
| CoE Abort `0x06010000` | 不支持 CompleteAccess | fallback 用单子项循环 |
| CoE Abort `0x06070010` | 数据长度不匹配 | 调整 `cbBufLen` |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **PDO 映射改动流程**（工程经验补充）：禁用 SM → 清 0x1A00:0 → 写各 entry → 写 0x1A00:0 = count → 恢复 SM → 切 OP
- **DUT 结构必须匹配 ESI**：字段顺序、大小都按 ESI 定义；错位会写入垃圾
- **`bCompleteAccess` 默认 FALSE**：忘记设 TRUE 会退化为单子项写

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcCoeSdoWriteEx.TcPOU`](../examples/P_Demo_FB_EcCoeSdoWriteEx.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：一条产线兼容 3 种产品，每种产品要求不同的 EL3068 PDO 映射。换型时 PLC 用本 FB 动态切 PDO 映射，免去为每种产品单独工程
- **价值**：单工程多产品兼容；切换无需 XAE 介入
- **替代方案对比**：每种产品独立工程 → 维护成本 3 倍；本 FB → 1 工程

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §7.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57000843.html
- **相关 FB / FC**：`FB_EcCoeSdoWrite`（单子项）、`FB_EcCoeSdoReadEx`、`FB_EcCoESdoAbortCode`
