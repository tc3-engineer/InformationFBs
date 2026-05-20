# ADSRDWRT

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `ADS function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/45035996304574603.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_ADSRDWRT.xml`](../examples/P_Demo_ADSRDWRT.xml) |

---

## 1. 功能简述

ADSRDWRT 在一次 ADS 调用里**先写后读**：把一段数据发给目标设备并立刻接收响应数据。比 `ADSWRITE` 然后 `ADSREAD` 两步少一次往返延迟。典型用例是 ByName 类服务——先写变量名做参数，再读返回值。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID     : T_AmsNetId;
    PORT      : T_AmsPort;
    IDXGRP    : UDINT;
    IDXOFFS   : UDINT;
    WRITELEN  : UDINT;
    READLEN   : UDINT;
    SRCADDR   : PVOID;
    DESTADDR  : PVOID;
    WRTRD     : BOOL;
    TMOUT     : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 目标 AMS Net ID；本机空串。 |
| `PORT` | `T_AmsPort` | - | 目标 ADS 端口号。 |
| `IDXGRP` | `UDINT` | - | ADS 索引组号。 |
| `IDXOFFS` | `UDINT` | - | ADS 索引偏移号。 |
| `WRITELEN` | `UDINT` | - | 本次要写入的字节数。 |
| `READLEN` | `UDINT` | - | 本次要读出的字节数。 |
| `SRCADDR` | `PVOID` | - | 写源缓冲首地址（`ADR()`）。 |
| `DESTADDR` | `PVOID` | - | 读目标缓冲首地址（`ADR()`）。 |
| `WRTRD` | `BOOL` | - | 上升沿触发一次写-读组合命令。 |
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
| `BUSY` | `BOOL` | 命令进行中。期间不接受新的 `WRTRD` 上升沿。 |
| `ERR` | `BOOL` | 上次执行出错。超时 `ERRID = 1861`。 |
| `ERRID` | `UDINT` | ADS 错误码或命令特定错误码；下次新命令启动时清 0。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**调用约束**：必须周期调用让 ADS 状态机推进。`WRTRD` 上升沿启动一次组合命令：`BUSY := TRUE`，先从 `SRCADDR` 取 `WRITELEN` 字节发给目标，目标处理后返回应答，应答数据被写入 `DESTADDR` 指向缓冲（最多 `READLEN` 字节）。

**为什么不用 ADSREAD + ADSWRITE 拼？** 两步法多一次 ADS 往返延迟（在远程网络上能差几毫秒），且需要两个状态机维护；本 FB 一次往返完成。

**典型用法**（PDF 示例改写）：用 SymbolByName 读对端 PLC 的全局变量 `.aLRealVar`——`IDXGRP := 16#0000F004`、`IDXOFFS := 0`、`SRCADDR := ADR(sSymName)` 装 `'.aLRealVar'`（10 字节含开头点号）、`DESTADDR := ADR(rResult)`、`WRITELEN := 10`、`READLEN := 8`（LREAL 长度）。一次往返就拿到值。

**陷阱**：两个缓冲都必须在 `BUSY` 期间保活；`READLEN` 与目标真实返回长度不一致时本 FB 不告知差异，建议用 `ADSRDWRTEX` 拿到 `COUNT_R` 验证。

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
- 如要知道实际读到的字节数，改用 `ADSRDWRTEX`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ADSRDWRT.xml`](../examples/P_Demo_ADSRDWRT.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：跨 PLC 同步——主 PLC 读取分布式从 PLC 中名为 `.fActualPosition` 的全局浮点变量做位置融合；用 ADSRDWRT 一次往返完成 SymbolByName 查询。
- **价值**：替代分两步先 ADSWRITE 拿句柄再 ADSREAD 拿值，单次往返减少延迟。
- **替代方案对比**：固定变量用句柄缓存配合 ADSREAD 更快；动态符号或调试场景用 ADSRDWRT 灵活；要校验长度用 ADSRDWRTEX。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.2.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/45035996304574603.html
- **相关 FB / FC**：`ADSRDWRTEX`（额外返回实际读字节数）、`ADSREAD`、`ADSWRITE`
