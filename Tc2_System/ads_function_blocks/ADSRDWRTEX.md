# ADSRDWRTEX

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `ADS function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30941323.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_ADSRDWRTEX.xml`](../examples/P_Demo_ADSRDWRTEX.xml) |

---

## 1. 功能简述

ADSRDWRTEX 与 `ADSRDWRT` 功能相同（一次 ADS 调用先写后读），但**额外**输出 `COUNT_R`——本次成功读到的实际字节数。当目标返回长度可变时必须用本 FB；这也是 SymbolByName 类查询的事实标准。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID    : T_AmsNetId;
    PORT     : T_AmsPort;
    IDXGRP   : UDINT;
    IDXOFFS  : UDINT;
    WRITELEN : UDINT;
    READLEN  : UDINT;
    SRCADDR  : PVOID;
    DESTADDR : PVOID;
    WRTRD    : BOOL;
    TMOUT    : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 目标 AMS Net ID；本机空串。 |
| `PORT` | `T_AmsPort` | - | 目标 ADS 端口号。 |
| `IDXGRP` | `UDINT` | - | ADS 索引组号。 |
| `IDXOFFS` | `UDINT` | - | ADS 索引偏移号。 |
| `WRITELEN` | `UDINT` | - | 写入字节数。 |
| `READLEN` | `UDINT` | - | 请求读出的字节数（上限）。 |
| `SRCADDR` | `PVOID` | - | 写源缓冲地址。 |
| `DESTADDR` | `PVOID` | - | 读目标缓冲地址。 |
| `WRTRD` | `BOOL` | - | 上升沿触发命令。 |
| `TMOUT` | `TIME` | `DEFAULT_ADS_TIMEOUT` | 命令超时时长。 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    BUSY    : BOOL;
    ERR     : BOOL;
    ERRID   : UDINT;
    COUNT_R : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `BUSY` | `BOOL` | 命令进行中。期间不接受新 `WRTRD` 上升沿。 |
| `ERR` | `BOOL` | 上次出错；超时 `ERRID = 1861`。 |
| `ERRID` | `UDINT` | ADS 错误码；下次新命令启动时清 0。 |
| `COUNT_R` | `UDINT` | 本次成功读到的实际字节数。可能 < `READLEN`。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**与 ADSRDWRT 的差异**：唯一新增 `COUNT_R` 输出。其余行为完全一致。

**何时必须用本 FB 而非 ADSRDWRT**：(1) 目标返回可变长度数据（不定长 STRING / 变长 ARRAY）；(2) 要做完整性校验：`COUNT_R = READLEN` 判定是否完整；(3) 远程 SymbolByName 之后做循环增量读。

**典型用法**：通过 SymbolByName 查询远端 PLC 全局字符串 `sLastErrorMsg`，请求 256 字节，实际目标只填 28 字节——`COUNT_R = 28`，业务侧据此截断或显示进度。

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
- `COUNT_R` 必须用，否则不知道 `DESTADDR` 缓冲里哪些字节有效；这是与 `ADSRDWRT` 的关键差别。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ADSRDWRTEX.xml`](../examples/P_Demo_ADSRDWRTEX.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：诊断界面用 SymbolByName 查对端 PLC `sLastErrorMsg`（最大 255 字节，但实际内容不固定长）；ADSRDWRTEX 直接给出真实字节数。
- **价值**：替代 ADSRDWRT + 自己 STRLEN 截断；目标返回变长时一并校验完整性。
- **替代方案对比**：定长 SymbolByName 读 ADSRDWRT 够用；变长就上 ADSRDWRTEX。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.2.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30941323.html
- **相关 FB / FC**：`ADSRDWRT`（无 COUNT_R 简化版）、`ADSREADEX`（仅读 + COUNT_R）
