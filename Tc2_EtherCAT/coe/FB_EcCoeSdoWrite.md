# FB_EcCoeSdoWrite

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `CoE interface` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/56999307.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcCoeSdoWrite.TcPOU`](../examples/P_Demo_FB_EcCoeSdoWrite.TcPOU) |

---

## 1. 功能简述

通过 CoE 协议向从站对象目录写入一个单一 SDO 对象值。`nIndex` + `nSubIndex` 定位对象。要批量写整对象用 `FB_EcCoeSdoWriteEx` 的 `bCompleteAccess`。是参数化从站（量程、采样率、滤波器系数等）的标准方式。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId     : T_AmsNetId; 
    nSlaveAddr : UINT; 
    nSubIndex  : BYTE; 
    nIndex     : WORD;
    pSrcBuf    : PVOID; 
    cbBufLen   : UDINT; 
    bExecute   : BOOL;
    tTimeout   : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站 AMS NetID |
| `nSlaveAddr` | `UINT` | — | 目标从站固定地址 |
| `nSubIndex` | `BYTE` | — | 要写的 sub-index |
| `nIndex` | `WORD` | — | 要写的对象 index |
| `pSrcBuf` | `PVOID` | — | 待写数据首地址 |
| `cbBufLen` | `UDINT` | — | 写入字节数 |
| `bExecute` | `BOOL` | — | 上升沿触发 SDO Download |
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

**触发**：`bExecute` 上升沿；`bBusy` 落沿后判 `bError` 决定成功失败。

**SDO Download 语义**：本 FB 把 `pSrcBuf` 中 `cbBufLen` 字节写入从站对象字典指定 sub-element。从站会按对象定义检查数据格式 / 范围，违规返回 CoE Abort Code。写入是同步的（在 ADS 调用粒度内）—— 从站接到 Download 后立即处理，主站在完成时回 ACK，本 FB 看到 ACK 后落 `bBusy`。所以 `bBusy = FALSE` + `bError = FALSE` 即可视为参数已写入。

**典型用法**：
- 参数化 EL3008：写 `0x8000:01`（Channel Settings）设量程
- 配置 EL7411：写 `0x8010:11`（PWM 频率）

**前置条件**：
- 从站邮箱可用（PREOP / SAFEOP / OP）
- 写"启动参数"对象通常要求 PREOP；运行时对象支持 OP

**典型陷阱**：
- 部分对象只读，写入返回 CoE Abort `0x06010002` (read-only)
- 写参数后需要 SAFEOP→OP 重转才生效；某些从站需要更深的 reset
- `cbBufLen` 必须匹配对象大小，多字节 / 少字节都报错

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 写入完成 |
| CoE Abort `0x06010002` | 对象只读 | 检查 ESI 文档 |
| CoE Abort `0x06070010` | 数据长度不匹配 | 调整 `cbBufLen` |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **写后未生效**：某些对象写入后需切 SAFEOP→OP；查 ESI 文档"Startup parameter"标识
- **`pSrcBuf` 类型匹配**：传 UINT 不能传 UDINT 长度
- **错误后用 `FB_EcGetLastProtErrInfo`**（工程经验补充）：取 CoE Abort 详细原因

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcCoeSdoWrite.TcPOU`](../examples/P_Demo_FB_EcCoeSdoWrite.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：换线时切换 EL3008 量程从 ±10V 改为 0~20mA。PLC 启动期调本 FB 写 `0x8000:01` 配置量程，无需手动 XAE 改 ESI
- **价值**：把"参数化配置"自动化，免去工程师每次换线下载工程
- **替代方案对比**：XAE 改 ESI 重下工程 → 慢；本 FB → PLC 自动调

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §7.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/56999307.html
- **相关 FB / FC**：`FB_EcCoeSdoWriteEx`、`FB_EcCoeSdoRead`、`FB_EcCoESdoAbortCode`
