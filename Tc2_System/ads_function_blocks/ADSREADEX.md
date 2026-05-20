# ADSREADEX

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `ADS function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30939787.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_ADSREADEX.xml`](../examples/P_Demo_ADSREADEX.xml) |

---

## 1. 功能简述

ADSREADEX 与 ADSREAD 功能相同（通过 ADS 异步读取数据），但**额外**输出 `COUNT_R`——本次成功读到的实际字节数。读取可变长度数据（如不定长字符串、可变结构）时必须用本 FB。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    NETID    : T_AmsNetId;
    PORT     : T_AmsPort;
    IDXGRP   : UDINT;
    IDXOFFS  : UDINT;
    LEN      : UDINT;
    DESTADDR : PVOID;
    READ     : BOOL;
    TMOUT    : TIME := DEFAULT_ADS_TIMEOUT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `NETID` | `T_AmsNetId` | - | 目标设备 AMS Net ID。本机用空串。 |
| `PORT` | `T_AmsPort` | - | 目标 ADS 设备端口号。 |
| `IDXGRP` | `UDINT` | - | ADS 索引组号。 |
| `IDXOFFS` | `UDINT` | - | ADS 索引偏移号。 |
| `LEN` | `UDINT` | - | 请求读取的字节数（上限）。 |
| `DESTADDR` | `PVOID` | - | 接收缓冲区首地址，由 `ADR()` 取地址。 |
| `READ` | `BOOL` | - | 上升沿触发一次 ADS 读。 |
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
| `BUSY` | `BOOL` | 命令进行中。`BUSY = TRUE` 期间不接受新的 `READ` 上升沿。 |
| `ERR` | `BOOL` | 上次执行出错。超时 `ERRID = 1861`。 |
| `ERRID` | `UDINT` | ADS 错误码；下次新命令启动时清 0。 |
| `COUNT_R` | `UDINT` | 本次成功读到的实际字节数。可能 < `LEN`，表示目标只返回了一部分数据。 |

### VAR_IN_OUT

无。

## 3. 行为说明

**与 ADSREAD 的差异**：唯一新增 `COUNT_R` 输出。其余行为一致（上升沿启动、`BUSY` 期间不接受新命令、`DESTADDR` 缓冲必须保活到 `BUSY` 落沿）。

**何时必须用本 FB 而非 ADSREAD**：(1) 目标服务返回可变长度（不定长字符串 / 变长 ARRAY），需要知道实际填进缓冲多少字节；(2) 要做循环读分批拉数据；(3) 要做读完整性校验：`COUNT_R = LEN` 否则丢数据。

**典型用法**：从对端 PLC 用 `SYM_VALBYHND` 读一个 `STRING(255)` 类型变量——`LEN := 256` 但变量当前内容只有 5 字节 + 终止符，`COUNT_R := 6` 才是真实长度。

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
- 如果业务只读固定长度（如 4 字节 DINT），`ADSREAD` 已够用且更省一个输出引脚；变长场景才需要本 FB。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ADSREADEX.xml`](../examples/P_Demo_ADSREADEX.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：诊断界面需要读对端 PLC 的全局字符串 `sStatusText`（可变长度，运行时变化），用 SymbolByName + ADSREADEX 拿到真实内容并显示。
- **价值**：替代 ADSREAD 后还要自己 `STRLEN` 截断尾巴，本 FB 直接给出真实字节数省去判断。
- **替代方案对比**：定长固定数据用 ADSREAD；变长 / 不确定数据用 ADSREADEX 才稳。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §3.2.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/30939787.html
- **相关 FB / FC**：`ADSREAD`（无 COUNT_R 简化版）、`ADSRDWRTEX`（读写组合 + 实际读字节数）
