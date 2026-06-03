# FB_EcFoeAccess

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `FoE interface` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57038731.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcFoeAccess.TcPOU`](../examples/P_Demo_FB_EcFoeAccess.TcPOU) |

---

## 1. 功能简述

通过已打开的 FoE 通信端口对从站文件进行分块读 / 写。本 FB 是 FoE 协议三件套（`Open`/`Access`/`Close`）中负责数据搬运的中间环节。要求先用 `FB_EcFoeOpen` 拿到 `hFoe` handle。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    hFoe     : T_HFoe;
    pBuffer  : DWORD;    
    cbBuffer : UDINT;
    bExecute : BOOL; 
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT; 
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `hFoe` | `T_HFoe` | — | FoE handle，从 `FB_EcFoeOpen` 输出 |
| `pBuffer` | `DWORD` | — | 数据缓冲首地址（读：接收 buffer；写：源数据） |
| `cbBuffer` | `UDINT` | — | 缓冲字节数 |
| `bExecute` | `BOOL` | — | 上升沿触发一次读/写 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy  : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    cbDone : UDINT;
    bEOF   : BOOL;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | 出错置 `TRUE` |
| `nErrId` | `UDINT` | ADS 错误码 |
| `cbDone` | `UDINT` | 本次成功传输字节数 |
| `bEOF` | `BOOL` | 读时遇到文件末尾置 `TRUE`；写时无意义 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿；`bBusy` 落沿后读 `cbDone` 与 `bEOF`。

**FoE 三件套使用流程**：标准的低级 FoE 流程是 `Open → 循环 Access → Close`。每次 Access 读/写一块数据（典型几 KB），读时 `bEOF = TRUE` 即文件读完。本 FB 用在循环中分块传送整个文件。

**与 `FB_EcFoeLoad` / `FB_EcFoeReadFile` / `FB_EcFoeWriteFile` 关系**：高级 FB 内部就是 `Open` + 循环 `Access` + `Close`。除非需要边读边处理（流式），否则用高级 FB 更方便。

**典型用法**：流式上传大文件 —— `Open` 拿 handle → while NOT bEOF do Access read → 处理本块 → 下一块；最后 `Close`。

**典型陷阱**：
- `hFoe` 必须有效（先 Open）
- `pBuffer` 必须保活到 `bBusy = FALSE`
- 每块大小由 `cbBuffer` 决定；过大会爆 mailbox，过小性能差

## 4. 错误码 / 返回值

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读 `cbDone` / `bEOF` |
| `1861` (`0x745`) | 超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **流式处理大文件**（工程经验补充）：典型用例 —— 上传超大固件分块发
- **`pBuffer` 是 DWORD 不是 PVOID**：用 ADR() 取地址赋给 DWORD
- **配合 Open/Close**：必须配套用

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcFoeAccess.TcPOU`](../examples/P_Demo_FB_EcFoeAccess.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：从 EL 模块上读 1 GB 大日志文件，PLC 内存只有 64 MB；用本 FB 每次读 1 MB 处理（写硬盘），循环直到 bEOF
- **价值**：流式处理超大文件，内存友好
- **替代方案对比**：`FB_EcFoeReadFile` 一次读完 → 内存爆；本 FB → 分块

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §8.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57038731.html
- **相关 FB / FC**：`FB_EcFoeOpen`、`FB_EcFoeClose`、`FB_EcFoeLoad`（一站式高级版）、`T_HFoe`
