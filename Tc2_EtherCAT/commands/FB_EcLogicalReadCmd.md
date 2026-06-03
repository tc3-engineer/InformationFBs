# FB_EcLogicalReadCmd

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Commands` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57006859.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcLogicalReadCmd.TcPOU`](../examples/P_Demo_FB_EcLogicalReadCmd.TcPOU) |

---

## 1. 功能简述

EtherCAT 逻辑地址读命令功能块。主站发送 LRD（Logical Read）命令，按"全局逻辑地址"寻址 —— 每个从站本地 DPRAM 区域可在配置时映射到一段全局逻辑地址，本 FB 一次性读所有映射到该地址段的从站数据。常用于直接读取 PDO 映射区（process image）的某一段内容做诊断或离线分析。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId   : T_AmsNetId; 
    logAddr  : UDINT; 
    len      : UDINT;
    pDstBuf  : PVOID;
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站设备的 AMS NetID 字符串。本机主站用空串 `''` |
| `logAddr` | `UDINT` | — | 逻辑地址（global logical address，进程映像中的偏移） |
| `len` | `UDINT` | — | 要读取的字节数 |
| `pDstBuf` | `PVOID` | — | 接收缓冲区首地址（指针）；至少 `len` 字节 |
| `bExecute` | `BOOL` | — | 上升沿触发一次读命令 |
| `tTimeout` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 单次命令允许的最长执行时间 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy  : BOOL;
    bError : BOOL;
    nErrId : UDINT;
    wkc    : UINT; 
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 命令进行中；启动后置 `TRUE`，收到反馈前保持 |
| `bError` | `BOOL` | `bBusy` 落沿后若传输出错则置 `TRUE` |
| `nErrId` | `UDINT` | `bError = TRUE` 时返回 ADS 错误码 |
| `wkc` | `UINT` | 工作计数器；每个成功处理该命令的从站递增 1。若只一个从站映射到该逻辑地址段，正常值为 1 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿启动一次 LRD 命令。电平 `TRUE` 不会重复触发；要再读一次必须先把 `bExecute` 拉回 `FALSE`。

**逻辑地址工作原理**：EtherCAT 主站启动时为每个从站的 PDO 映射区分配一段全局逻辑地址（在 XAE 的 Process Image 中可见），主站的循环帧用 LRD/LWR/LRW 命令按这些地址读写。本 FB 让 PLC 旁路主站循环帧，单独触发一次 LRD：所有 FMMU 配置覆盖该 `logAddr` ~ `logAddr+len` 区间的从站都会把对应数据复制进 EtherCAT 帧。

**完成判定**：`bBusy` 由 `TRUE → FALSE` 之后再读 `bError` / `wkc`：

- `bError = FALSE` 且 `wkc` 等于该地址段实际映射的从站数：所有从站都应答了
- `wkc` 小于预期：某些从站未应答（连接断开、未在 OP 等）
- `bError = TRUE`：ADS 通信错误，看 `nErrId`

**典型用法**：
- 周期低频读 process image 某段做"快照"，与主站循环帧解耦
- 调试 PDO 映射：在主站不运行循环任务时手动触发 LRD 验证映射是否生效

**典型陷阱**：
- `logAddr` 不是 ESC 寄存器地址，而是全局逻辑地址（在 XAE 的 Process Image 视图查）；写错了 wkc 会为 0
- 该 FB 与主站循环帧并发：在主站每 1 ms 都发 LRD 的同时再发本 FB，可能与正常 PDO 数据竞争。日常应在主站周期不太忙时使用
- 本 FB 旁路了 Process Image，读到的是 EtherCAT 帧最新值，而不是 PLC 此周期开始时的 PDO 快照

## 4. 错误码 / 返回值

`nErrId` 是 ADS 错误码。常见取值：

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | ADS 调用成功 | 读 `wkc` 判定是否所有从站都应答 |
| `6` | ADS port not found | 主站未启动 |
| `7` | ADS target not found | `sNetId` 错或路由未建立 |
| `1861` (`0x745`) | 命令超时 | 增大 `tTimeout` |
| `0x70C` / `0x70D` | EtherCAT 命令传输错误 | 链路问题 |

完整 ADS 错误码表对照 Beckhoff『ADS Return Codes』。

## 5. 使用注意 / 常见坑

- **`logAddr` 来源**：必须从 XAE → 主站 → Process Image 视图取出实际映射的全局地址，不能自己猜
- **`wkc` 判定**：日常工程更建议直接读 PLC 端 PDO 变量（在 Process Image 中映射的 IEC 变量），而不是用本 FB 旁路读
- **本 FB 适合的少数场景**：诊断工具、调试链路、与主站循环任务并发的"额外采样"。普通业务用 PDO 链接即可
- **指针生命周期**（工程经验补充）：`pDstBuf` 必须用全局或 FB 成员变量，不能用栈变量

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcLogicalReadCmd.TcPOU`](../examples/P_Demo_FB_EcLogicalReadCmd.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：调试新组的 EtherCAT 网络时发现某 EL3008 模拟量从 PDO 读出全 0；用 LRD 手动读对应 logical address 区段对照，若 wkc = 0 说明 FMMU 映射没生效，若 wkc = 1 但数据全 0 说明硬件输入侧问题
- **价值**：直接验证"主站 PDO 映射是否真正下发到从站"，绕过 PLC 任务的双缓冲机制
- **替代方案对比**：
  - 直接读 PLC 端 PDO 变量：日常业务首选，但读到的是 PLC 任务双缓冲后的值
  - `FB_EcPhysicalReadCmd`：能读任意 ESC 寄存器但需要知道 ESC 内部物理偏移
  - **本 FB**：按主站已建立的逻辑地址映射读，对应"业务意义"明确

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §3.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57006859.html
- **相关 FB / FC**：`FB_EcLogicalWriteCmd`（写）、`FB_EcPhysicalReadCmd`（按 ESC 物理地址读）
