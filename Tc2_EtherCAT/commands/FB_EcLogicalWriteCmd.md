# FB_EcLogicalWriteCmd

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EtherCAT` |
| Library Version | `1.9.5` |
| Type | `FUNCTION_BLOCK` |
| Category | `EtherCAT Commands` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57008395.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EcLogicalWriteCmd.TcPOU`](../examples/P_Demo_FB_EcLogicalWriteCmd.TcPOU) |

---

## 1. 功能简述

EtherCAT 逻辑地址写命令功能块。主站发送 LWR（Logical Write）命令，按全局逻辑地址寻址 —— 把缓冲区数据一次性写到所有映射到该地址段的从站。常用于诊断或外部工具直接覆盖 PDO 输出区，做硬件测试或离线信号注入。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetId   : T_AmsNetId; 
    logAddr  : UDINT; 
    len      : UDINT;
    pSrcBuf  : PVOID;
    bExecute : BOOL;
    tTimeout : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetId` | `T_AmsNetId` | — | EtherCAT 主站设备的 AMS NetID 字符串。本机主站用空串 `''` |
| `logAddr` | `UDINT` | — | 逻辑地址（global logical address） |
| `len` | `UDINT` | — | 要写入的字节数 |
| `pSrcBuf` | `PVOID` | — | 待写出数据缓冲首地址；至少 `len` 字节 |
| `bExecute` | `BOOL` | — | 上升沿触发一次写命令 |
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
| `bBusy` | `BOOL` | 命令进行中 |
| `bError` | `BOOL` | `bBusy` 落沿后若传输错误则置 `TRUE` |
| `nErrId` | `UDINT` | `bError = TRUE` 时返回 ADS 错误码 |
| `wkc` | `UINT` | 工作计数器；每个成功处理该命令的从站递增 1 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿启动一次 LWR 命令。电平 `TRUE` 不会重复触发。

**写入语义**：LWR 与主站正常循环帧的 LWR 命令是同一种 EtherCAT 命令。本 FB 让 PLC 在主站循环帧之外单独发一次。所有 FMMU 映射覆盖该 `logAddr` ~ `logAddr+len` 区间的从站都会把 EtherCAT 帧里的数据写到对应 DPRAM。

**与主站循环帧的关系**：主站循环帧通常每 1 ms 一次自动 LWR 输出区数据。本 FB 单独触发的 LWR 与之竞争 —— 在两次循环帧之间插入一个额外 LWR 会被覆盖。仅适合主站任务不在跑（调试态）或对该地址段没有循环映射时使用。

**完成判定**：`bBusy` 由 `TRUE → FALSE` 后判定：

- `bError = FALSE` 且 `wkc` 等于该地址段实际映射的从站数：所有从站都应答了
- `wkc` 小于预期：某些从站未应答
- `bError = TRUE`：ADS 通信错误

**典型陷阱**：
- 与主站循环 LWR 并发使用：本 FB 写的值瞬间被下一个循环帧覆盖
- 写到不存在的 logical address：`wkc = 0`，但 `bError = FALSE`
- 写输入侧 logical address（应输入到 PLC 的）：从站会忽略，wkc 仍 = 0

## 4. 错误码 / 返回值

`nErrId` 是 ADS 错误码：

| `nErrId` | 含义 | 处理建议 |
|---|---|---|
| `0` | ADS 调用成功 | 读 `wkc` 判定是否所有从站都应答 |
| `6` | ADS port not found | 主站未启动 |
| `7` | ADS target not found | `sNetId` / 路由问题 |
| `1861` (`0x745`) | 命令超时 | 增大 `tTimeout` |

## 5. 使用注意 / 常见坑

- **基本不用于生产**：日常 PDO 输出写应直接赋值给 PLC 端映射变量。本 FB 适用于硬件验证、协议级测试、离线信号注入
- **与主站循环帧竞争**：在主站任务运行时使用，写入会立即被覆盖；调试时关掉主站循环或选择主站不映射的地址段
- **`logAddr` 来源**：必须从 XAE Process Image 视图查实际映射地址
- **指针生命周期**（工程经验补充）：`pSrcBuf` 必须保活到 `bBusy = FALSE`

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EcLogicalWriteCmd.TcPOU`](../examples/P_Demo_FB_EcLogicalWriteCmd.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：实验室验证一台带 EL2008（8 路数字量输出）的网络，关掉主站循环任务后，用本 FB 直接发 LWR 覆盖输出区，验证某路输出通道硬件接线是否正确
- **价值**：在主站不运行循环帧时做"裸 EtherCAT"硬件验证；或在协议开发期验证 LWR 命令本身被从站识别
- **替代方案对比**：
  - 直接赋值 PDO 输出变量：常规做法，依赖主站循环帧周期下发
  - `FB_EcPhysicalWriteCmd`：能写任意 ESC 寄存器，更底层但需要懂 ESC 地址图
  - **本 FB**：按已有 FMMU 映射写，适合做"已有配置下的旁路注入"

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EtherCAT_EN.pdf) §3.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_ethercat/57008395.html
- **相关 FB / FC**：`FB_EcLogicalReadCmd`（读）、`FB_EcPhysicalWriteCmd`（按 ESC 地址写）
