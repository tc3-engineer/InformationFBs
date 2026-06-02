# HSOCKET_TO_STRINGEX

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84164363.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_HSOCKET_TO_STRINGEX.TcPOU`](../examples/P_Demo_HSOCKET_TO_STRINGEX.TcPOU) |

---

## 1. 功能简述

`HSOCKET_TO_STRING` 的扩展版：可选择性输出本地、远端地址。两个 BOOL 输入 `bLocal` / `bRemote` 各自决定是否包含对应字段。默认格式与 `HSOCKET_TO_STRING` 一致，但当 `bLocal := FALSE` 时省略 `Local:...` 段，`bRemote := FALSE` 时省略 `Remote:...` 段；两个都为 `FALSE` 时只剩 `Handle:0xN`。适合 HMI 空间紧张、只关注一边、或要把 local / remote 拆到不同字段显示的场景。

## 2. 接口定义

### Syntax

```iecst
FUNCTION HSOCKET_TO_STRINGEX : STRING
VAR_INPUT
    hSocket : T_HSOCKET;
    bLocal  : BOOL;
    bRemote : BOOL;
END_VAR
```

### VAR_INPUT

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `hSocket` | `T_HSOCKET` | — | 要转换的连接句柄 |
| `bLocal` | `BOOL` | — | `TRUE` = 输出包含 `Local:IP:Port`；`FALSE` = 省略 |
| `bRemote` | `BOOL` | — | `TRUE` = 输出包含 `Remote:IP:Port`；`FALSE` = 省略 |

### 返回值

| 类型 | 说明 |
|---|---|
| `STRING` | 按选项拼出的字串。最大约 80 字符；推荐接收变量 `STRING(80)` |

## 3. 行为说明

**调用即返回**：纯函数，无副作用，同输入永远同输出。两个布尔输入 `bLocal` 和 `bRemote` 独立控制输出中是否包含本地端点和远端端点信息，因此一共四种组合输出。所有组合都保留 `Handle:0xN` 前缀；两个标志都为 `FALSE` 时输出最紧凑（只剩句柄值），常用于 HMI 极窄字段。两个标志都为 `TRUE` 时与 `HSOCKET_TO_STRING` 输出完全一致。

**输出组合表**：

| `bLocal` | `bRemote` | 输出格式 |
|---|---|---|
| `TRUE` | `TRUE` | `Handle:0xN Local:a.b.c.d:p Remote:a.b.c.d:p`（同 `HSOCKET_TO_STRING`） |
| `TRUE` | `FALSE` | `Handle:0xN Local:a.b.c.d:p` |
| `FALSE` | `TRUE` | `Handle:0xN Remote:a.b.c.d:p` |
| `FALSE` | `FALSE` | `Handle:0xN` |

**典型用法**：

- listener socket：`bLocal := TRUE, bRemote := FALSE`（remote 无意义）
- 客户端 socket 监控：`bLocal := FALSE, bRemote := TRUE`（关心连到谁）
- HMI 单字段显示：`bLocal := FALSE, bRemote := FALSE`，再单独显示一个 IP

**与 `HSOCKET_TO_STRING` 的关系**：`HSOCKET_TO_STRING(h)` 等价 `HSOCKET_TO_STRINGEX(h, TRUE, TRUE)`。

## 4. 错误码 / 返回值

无错误码——纯函数。

## 5. 使用注意 / 常见坑

- **接收变量长度**：选 `TRUE, TRUE` 时同 `STRING(80)`；其他组合可以更短。
- **格式末尾空格**：`bRemote := FALSE` 时末尾不带额外空格；safe 拼接。
- **不能反向解析**：无对应的"字符串→句柄"反函数。
- **listener / UDP 句柄**：listener 的 `remoteAddr` 通常 `0.0.0.0:0`；用 `bRemote := FALSE` 跳过避免误导。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_HSOCKET_TO_STRINGEX.TcPOU`](../examples/P_Demo_HSOCKET_TO_STRINGEX.TcPOU)

```iecst
// 场景：HMI 两栏分别显示 local / remote 地址，互不干扰。
PROGRAM P_Demo_HSOCKET_TO_STRINGEX
VAR
    hClient        : T_HSOCKET;
    sLocalOnly     : STRING(80);
    sRemoteOnly    : STRING(80);
END_VAR

sLocalOnly  := HSOCKET_TO_STRINGEX(hSocket := hClient, bLocal := TRUE,  bRemote := FALSE);
sRemoteOnly := HSOCKET_TO_STRINGEX(hSocket := hClient, bLocal := FALSE, bRemote := TRUE);
```

## 7. 业务场景与实际价值

- **场景**：HMI 空间紧、只想显示远端 IP；运维日志拆字段写 CSV；分别推 OPC UA Local / Remote 为独立节点。
- **价值**：一个函数搞定多组合，省去手动 IF/CONCAT 逻辑。
- **替代方案对比**：
  - 拿 `HSOCKET_TO_STRING` 再切：可行但繁琐
  - 直接用 `hSocket.localAddr` / `remoteAddr` 字段手拼：更细粒度但代码量大；本函数适合快速调试

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.2.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84164363.html
- **相关**：`HSOCKET_TO_STRING`（全输出）、`SOCKETADDR_TO_STRING`（仅地址结构）、`T_HSOCKET`
