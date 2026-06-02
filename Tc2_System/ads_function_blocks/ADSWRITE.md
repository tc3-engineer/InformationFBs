# ADSWRITE

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `ADS function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30868107.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_ADSWRITE.TcPOU`](../examples/P_Demo_ADSWRITE.TcPOU) |

---

## 1. 功能简述

ADSWRITE 通过 ADS 协议把本地缓冲区的数据异步写到目标设备的指定服务。常用于向 NC 写控制命令、向 IO 模块写配置寄存器、向远端 PLC 写全局变量。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID   : T_AmsNetId;
    PORT    : T_AmsPort;
    IDXGRP  : UDINT;
    IDXOFFS : UDINT;
    LEN     : UDINT;
    SRCADDR : PVOID;
    WRITE   : BOOL;
    TMOUT   : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 目标设备 AMS Net ID。本机用空串。 |
| `PORT` | `T_AmsPort` | - | 目标 ADS 设备端口号。 |
| `IDXGRP` | `UDINT` | - | ADS 索引组号。 |
| `IDXOFFS` | `UDINT` | - | ADS 索引偏移号。 |
| `LEN` | `UDINT` | - | 写入字节数。注释 PDF 写的是 'Number of data to be read in bytes'，按行为含义实际是 'to be written'。 |
| `SRCADDR` | `PVOID` | - | 源缓冲区首地址，由 `ADR()` 取地址。 |
| `WRITE` | `BOOL` | - | 上升沿触发一次 ADS 写。 |
| `TMOUT` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 命令超时时长。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY    : BOOL;
    ERR     : BOOL;
    ERRID   : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | 命令进行中。期间不接受新的 `WRITE` 上升沿。 |
| `ERR` | `BOOL` | 上次执行出错。超时 `ERRID = 1861`。 |
| `ERRID` | `UDINT` | ADS 错误码或命令特定错误码；下次新命令启动时清 0。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用约束**：必须每周期调用让 ADS 状态机推进。`WRITE` 上升沿启动一次写：`BUSY := TRUE`，命令发送到目标设备；收到应答后 `BUSY := FALSE`，根据应答设置 `ERR` / `ERRID`。

**`SRCADDR` 缓冲生命周期**：异步期间（`BUSY = TRUE`）系统会从该地址读取数据写到目标；地址指向的内存必须保活到 `BUSY` 落沿，所以不能用栈上 / METHOD 局部变量做源。

**典型用法**：把 NC 轴 1 去激活——`IDXGRP := 16#00004201`、`IDXOFFS := 16#00000050`、`LEN := 0`、`SRCADDR := 0`。重新激活用 `IDXOFFS := 16#00000051`。某些「无参命令」`LEN`/`SRCADDR` 不重要但仍需明确置 0。

**陷阱**：写命令是状态改变性的，**不要**在 PLC 周期内连续触发（容易写花配置）；`WRITE` 上升沿后等 `BUSY` 落沿再做下一次。`PDF 在 LEN 描述里写的 'to be read in bytes' 是 PDF 笔误，按 ADSWRITE 语义应为 'to be written'`。

## 4. 错误码 / 返回值

`ERRID` 是 ADS 错误码或命令特定错误码。下次新命令在 `bExecute` 上升沿被接受时清 0。常见取值：

| `ERRID` | 含义 | 处理建议 |
|---|---|---|
| `0` | 成功 | 读取 `DESTADDR` 缓冲数据 |
| `6` | ADS port not found | 检查 `PORT` 是否正确 |
| `7` | ADS target not found | 检查 `NETID` 和路由配置 |
| `1808` | Symbol not found | 检查 `IDXGRP`/`IDXOFFS` |
| `1861` (`0x745`) | 调用超时 | 增大 `TMOUT` 或检查链路 |

完整码表请参考 Beckhoff『ADS Return Codes』，⚠️ PDF/InfoSys 在本节未列全。

## 5. 使用注意 / 常见坑

- 异步执行：必须每周期调用使内部状态机推进；不要只在 `bExecute` 上升沿那一帧调用一次。
- 并发同实例：同一 FB 实例不能给多个目标使用，连接断开重连后会输出旧应答（PDF 明确警告，工程上务必每个目标一个实例）。
- 超时错误码：`TMOUT` 到期会把 `ERRID = 1861`（十六进制 `0x745`）标出，请勿把超时当作通讯故障，常见原因是 `TMOUT` 设得过短或目标繁忙。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ADSWRITE.TcPOU`](../examples/P_Demo_ADSWRITE.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 上按下 “复位 NC 轴 1” 按钮，PLC 通过 ADSWRITE 向 NC 写 `IDXGRP=0x4201, IDXOFFS=0x51` 触发轴重新激活。
- **价值**：替代在 System Manager 里建一条 PDO 链接传递控制位，ADSWRITE 不改硬件配置就能发命令。
- **替代方案对比**：高频控制用 PDO；非高频偶发命令（复位、模式切换）用 ADSWRITE 更轻量。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.2.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30868107.html
- **相关 FB / FC**：`ADSREAD`（读）、`ADSRDWRT`/`ADSRDWRTEX`（读写组合）
