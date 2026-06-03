# FB_EcCoeSdoRead

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `CoE interface` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/56996235.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcCoeSdoRead.TcPOU`](../examples/P_Demo_FB_EcCoeSdoRead.TcPOU) |

---

## 1. 功能简述

通过 CoE（CANopen over EtherCAT）协议从指定从站的对象目录中读取一个单一 SDO 对象的值。`nIndex` + `nSubIndex` 定位对象。要读取完整对象（含所有 sub elements）须用 `FB_EcCoeSdoReadEx` 的 `bCompleteAccess`。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId     : T_AmsNetId; 
    nSlaveAddr : UINT; 
    nSubIndex  : BYTE; 
    nIndex     : WORD;
    pDstBuf    : PVOID; 
    cbBufLen   : UDINT; 
    bExecute   : BOOL;
    tTimeout   : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站 AMS NetID |
| `nSlaveAddr` | `UINT` | — | 目标从站固定地址 |
| `nSubIndex` | `BYTE` | — | 要读对象的 sub-index |
| `nIndex` | `WORD` | — | 要读对象的 index（如 `16#1018` = Identity Object） |
| `pDstBuf` | `PVOID` | — | 接收缓冲首地址 |
| `cbBufLen` | `UDINT` | — | 缓冲容量字节数 |
| `bExecute` | `BOOL` | — | 上升沿触发一次 SDO Upload |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | ADS 调用超时 |

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
| `cbRead` | `UDINT` | 成功读取的字节数 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读 `pDstBuf` 数据。

**CoE SDO 概念**：CANopen over EtherCAT 协议通过从站邮箱进行参数化读写。对象字典（Object Dictionary）按 `index : sub-index` 结构组织，标准对象如 `0x1018` 是 Identity（vendor / product / revision / serial），`0x6000+` 是输入对象，`0x7000+` 是输出对象，`0x8000+` 是配置参数。

**前置条件**：从站必须有邮箱（mailbox），且支持 CoE 协议。绝大多数 Beckhoff EL 模块都支持，部分简单从站（如 EK1100 总线耦合器）不支持。

**典型用法**：
- 读 `0x1018:1` 获取 Vendor ID 做厂商校验
- 读 `0x8000:01` 等配置对象监控配置项
- 读 `0x6020:11` 等运行时对象做高级诊断

**典型陷阱**：
- 从站必须 PREOP / SAFEOP / OP 状态；INIT 邮箱不可用
- `cbBufLen` < 对象实际大小：bError 报错
- 数据格式按对象字典定义：UDINT/STRING/UINT 等，调用方必须正确解析
- 想读对象的"完整结构"（含所有 sub elements）必须用 `FB_EcCoeSdoReadEx` + `bCompleteAccess = TRUE`

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `pDstBuf` 数据 |
| `1861` (`0x745`) | ADS 超时 | 增大 `tTimeout` |
| CoE Abort Code | 见 `FB_EcCoESdoAbortCode` | 用 `FB_EcGetLastProtErrInfo` 取详细描述 |

## 5. 使用注意 / 常见坑

- **缓冲必须保活**：`pDstBuf` 在 `bBusy = TRUE` 期间不能释放；用全局或 FB 成员
- **对象字典文档**：每个从站都有 ESI（EtherCAT Slave Information）文件，列出全部对象；在 XAE 中右键从站 → Online → CoE-Online 查看
- **CompleteAccess 的差别**（工程经验补充）：本 FB 只读单子项；要一次拿整个对象用 Ex 版

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcCoeSdoRead.TcPOU`](../examples/P_Demo_FB_EcCoeSdoRead.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 显示一个 EL3008 模块的硬件 vendor ID 做防伪校验。每分钟调一次本 FB 读 `0x1018:1`，与期望值 `16#00000002`（Beckhoff）比对
- **价值**：把 CoE 标准对象访问封装成一行；业务侧免学 CoE 协议细节
- **替代方案对比**：手写 ADS 命令 → 长且易错；本 FB → 简洁

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §7.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/56996235.html
- **相关 FB / FC**：`FB_EcCoeSdoReadEx`（带 CompleteAccess）、`FB_EcCoeSdoWrite`（写）、`FB_EcCoESdoAbortCode`（错误码解析）
