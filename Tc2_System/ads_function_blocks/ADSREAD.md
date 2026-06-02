# ADSREAD

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `ADS function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30866571.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_ADSREAD.TcPOU`](../examples/P_Demo_ADSREAD.TcPOU) |

---

## 1. 功能简述

ADSREAD 通过 ADS 协议从目标设备异步读取一段数据到本地缓冲区。是 Tc2_System 中最基础的 ADS 读取功能块，所有更复杂的读取（带返回长度、读写组合）都建立在其概念基础上。常用于读 NC 轴状态、IO 模块寄存器、远端 PLC 全局变量等。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID     : T_AmsNetId;
    PORT      : T_AmsPort;
    IDXGRP    : UDINT;
    IDXOFFS   : UDINT;
    LEN       : UDINT;
    DESTADDR  : PVOID;
    READ      : BOOL;
    TMOUT     : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 目标设备 AMS Net ID。本机用空串。 |
| `PORT` | `T_AmsPort` | - | 目标 ADS 设备端口号（如 PLC = 851，NC = 501，IO = 300）。 |
| `IDXGRP` | `UDINT` | - | ADS 索引组号（32-bit 无符号）。从目标设备 ADS 表查得。 |
| `IDXOFFS` | `UDINT` | - | ADS 索引偏移号（32-bit 无符号）。 |
| `LEN` | `UDINT` | - | 要读取的字节数。 |
| `DESTADDR` | `PVOID` | - | 接收缓冲区首地址。由 `ADR()` 取地址；缓冲区必须足以容纳 `LEN` 字节。 |
| `READ` | `BOOL` | - | 上升沿触发一次 ADS 读。 |
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
| `BUSY` | `BOOL` | 命令进行中。`BUSY = TRUE` 期间不接受新的 `READ` 上升沿；监视的是服务被接受的时长，不是服务真正完成的时长。 |
| `ERR` | `BOOL` | 上次执行出错。`BUSY` 落沿后稳定可读；超时时 `ERR = TRUE` 且 `ERRID = 1861`。 |
| `ERRID` | `UDINT` | ADS 错误码；下次新命令启动时清 0。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用约束**：必须每周期调用让 ADS 状态机推进。`READ` 上升沿启动一次读：`BUSY := TRUE`，命令被发送到目标设备；收到目标应答时 `BUSY := FALSE` 并把读到的数据写入 `DESTADDR` 指向的缓冲区。

**陈旧数据警告**（PDF 明确写）：连接断开重连后第一次会输出旧应答数据。**预防**：不要把同一个 ADSREAD 实例复用给多个目标——一个目标一个实例。

**`DESTADDR` 缓冲生命周期**：异步期间（`BUSY = TRUE`）系统会向该地址写入数据；地址指向的内存必须保活到 `BUSY` 落沿，所以不能用栈上 / METHOD 局部变量做缓冲，必须用全局或 FB 实例成员。

**典型用法**：以 NC 轴 6 号的错误码为例——`IDXGRP := 16#00004006`、`IDXOFFS := 1`、`LEN := 4`、`DESTADDR := ADR(dwAxisError)`。读取期间 `BUSY = TRUE`，完成后 `dwAxisError` 装入新值。

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
- `PORT` 常用值速查：PLC `851`，NC `501`，IO `300`，事件 logger `110`，系统服务 `10000`。


## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ADSREAD.TcPOU`](../examples/P_Demo_ADSREAD.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 周期 1 Hz 显示 NC 轴 1 当前位置和错误码；PLC 端用 ADSREAD 从本地 NC 服务读出这两个值再推给 HMI。
- **价值**：替代 PLC 与 NC 之间的 PDO 映射（要在 System Manager 配置链接表），ADSREAD 不用改硬件配置就能动态读 NC 任意服务变量。
- **替代方案对比**：固定数据用 PDO 链接更快；动态采样（每秒一次或诊断用）用 ADSREAD 更灵活。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.2.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30866571.html
- **相关 FB / FC**：`ADSREADEX`（额外返回实际读到字节数）、`ADSWRITE`（写）、`ADSRDWRT`（读写组合）
