# FB_EcCoeSdoReadEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `CoE interface` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/56997771.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcCoeSdoReadEx.TcPOU`](../examples/P_Demo_FB_EcCoeSdoReadEx.TcPOU) |

---

## 1. 功能简述

带 `bCompleteAccess` 选项的 CoE SDO 读取版本。当 `bCompleteAccess = TRUE` 时，把整个对象（含所有 sub-element）一次性 upload 进缓冲，而不是只取一个 sub-index。是读取"整体记录型"对象（如 PDO 映射、TSCs）的标准方式。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId          : T_AmsNetId;
    nSlaveAddr      : UINT;
    nSubIndex       : BYTE;
    nIndex          : WORD;
    pDstBuf         : PVOID;
    cbBufLen        : UDINT;
    bExecute        : BOOL;
    tTimeout        : TIME := DEFAULT_ADS_TIMEOUT;
    bCompleteAccess : BOOL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站 AMS NetID |
| `nSlaveAddr` | `UINT` | — | 目标从站固定地址 |
| `nSubIndex` | `BYTE` | — | sub-index（CompleteAccess = TRUE 时通常 0） |
| `nIndex` | `WORD` | — | 对象 index |
| `pDstBuf` | `PVOID` | — | 接收缓冲首地址；CompleteAccess 时需大于对象整体大小 |
| `cbBufLen` | `UDINT` | — | 缓冲容量字节数 |
| `bExecute` | `BOOL` | — | 上升沿触发 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 超时 |
| `bCompleteAccess` | `BOOL` | — | TRUE = 读整对象；FALSE = 仅读 `nSubIndex` 单子项 |

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
| `cbRead` | `UDINT` | 实际读取字节数 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读 `pDstBuf`。

**`bCompleteAccess` 模式区别**：当 `TRUE` 时本 FB 把对象的所有 sub-element 按 DUT 字段顺序填入 `pDstBuf`。例如 0x1018 Identity 含 4 个 UDINT，可一次读出 16 字节。当 `FALSE` 时仅读 `nSubIndex` 指定的单个 sub-element，与 `FB_EcCoeSdoRead` 等价。同一 FB 通过开关切换两种模式，工程实际中常按"读完整配置 vs 读特定项"两种用例分别实例化两个不同名的 FB 实例。

**典型用法**：
- `bCompleteAccess = TRUE`、`nIndex = 0x1018`：一次读出全部 Identity 信息
- `bCompleteAccess = TRUE`、PDO 映射对象：批量读取映射配置做诊断

**前置条件 / 限制**：
- 从站必须支持 CoE CompleteAccess（多数 Beckhoff 模块都支持，部分简陋第三方不支持）
- `pDstBuf` 必须按目标对象 DUT 结构定义匹配，否则字段位置错乱
- `cbBufLen` 必须 ≥ 对象总大小

**典型陷阱**：
- 对象长度未知时无法预估 buffer；先用 `bCompleteAccess = FALSE` 读 sub 0（typical 含数量字段）
- DUT 字段必须按 EEPROM ESI 定义顺序，否则读到的数据偏移错

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `pDstBuf` |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |
| CoE Abort | 见 `FB_EcCoESdoAbortCode` | 用 `FB_EcGetLastProtErrInfo` |

## 5. 使用注意 / 常见坑

- **DUT 必须配 ESI**：本 FB 给原始字节，业务侧必须用对应 DUT 解析
- **从站不支持 CompleteAccess**：可能 nErrId = CoE Abort 0x06010000；fallback 用单子项循环读
- **完整 PDO 配置读取**（工程经验补充）：`bCompleteAccess` 是读 PDO 映射对象（0x1A00 等）的标准做法

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcCoeSdoReadEx.TcPOU`](../examples/P_Demo_FB_EcCoeSdoReadEx.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：诊断工具一次读出某 EL7411 完整 Identity Object（vendor/product/revision/serial 4 个 UDINT 共 16 字节）。比起单子项 `FB_EcCoeSdoRead` 调 4 次更快
- **价值**：一次邮箱往返拿整对象，减 75% ADS 负载
- **替代方案对比**：单子项 4 次调用 → 4 次邮箱往返；本 FB CompleteAccess → 1 次

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §7.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/56997771.html
- **相关 FB / FC**：`FB_EcCoeSdoRead`（单子项）、`FB_EcCoeSdoWriteEx`、`FB_EcCoESdoAbortCode`
