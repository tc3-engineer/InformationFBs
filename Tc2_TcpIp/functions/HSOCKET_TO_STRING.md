# HSOCKET_TO_STRING

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84162827.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_HSOCKET_TO_STRING.TcPOU`](../examples/P_Demo_HSOCKET_TO_STRING.TcPOU) |

---

## 1. 功能简述

把 `T_HSOCKET` 连接句柄结构转换为可读字符串，用于调试输出、日志、HMI 显示。格式固定为：

```
Handle:0xA[BCD] Local:a[aa].b[bb].c[cc].d[dd]:port Remote:a[aa].b[bb].c[cc].d[dd]:port
```

例：`Handle:0x4001 Local:172.16.6.195:28459 Remote:172.16.6.180:2404`。

函数纯计算，无副作用，无异步状态。同一句柄重复调返回相同字符串。要选择性输出（只看本地或只看远端）请用 `HSOCKET_TO_STRINGEX`。

## 2. 接口定义

### Syntax

```iecst
FUNCTION HSOCKET_TO_STRING : STRING
VAR_INPUT
    hSocket : T_HSOCKET;
END_VAR
```

### VAR_INPUT

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `hSocket` | `T_HSOCKET` | — | 要转换的连接句柄 |

### 返回值

| 类型 | 说明 |
|---|---|
| `STRING` | 上述格式的字串。最大约 80 字符；接收变量建议至少 `STRING(80)` |

## 3. 行为说明

**调用即返回**：纯函数；输入合法字符串即合法，输入未初始化句柄会得到 `Handle:0x0 Local:0.0.0.0:0 Remote:0.0.0.0:0` 这种全零结果（**不是错误**，只是表示句柄为空）。

**格式说明**：

- `Handle:0xN` —— `T_HSOCKET.handle` 字段的十六进制表示
- `Local:IP:Port` —— `T_HSOCKET.localAddr.sAddr` + `nPort`
- `Remote:IP:Port` —— `T_HSOCKET.remoteAddr.sAddr` + `nPort`

listener socket 的 `remoteAddr` 是 `0.0.0.0:0`（listener 没有特定 remote）；client socket 两边都有；UDP socket 看具体使用情况而定。

**典型用法**：

```iecst
sLogLine := CONCAT('[', sTimestamp, '] new client: ',
                   HSOCKET_TO_STRING(hClient));
LogMessage(sLogLine);
```

**典型陷阱**：返回 STRING 长度有限——超过 80 字符接收变量会被截断；不要把字符串地址（`ADR()`）传给 `FB_SocketSend` 当成发送 payload，除非真要发这段调试字串。

## 4. 错误码 / 返回值

无错误码——纯函数，永远返回字串（最坏返回全零格式串）。

## 5. 使用注意 / 常见坑

- **接收变量**：`STRING(80)` 比较安全；写 `STRING(40)` 会截掉 Remote 部分。
- **不能反向解析**：输出是固定格式字符串，没有内置"字符串解回 T_HSOCKET"的函数。
- **listener 的 remote 显示 0.0.0.0:0**：正常，不要误以为是 bug。
- **性能**：纯计算，PLC 周期内多次调无明显开销。
- **诊断协议解码**：见 `SOCKETADDR_TO_STRING`（仅地址）和 `HSOCKET_TO_STRINGEX`（带 local/remote 选择）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_HSOCKET_TO_STRING.TcPOU`](../examples/P_Demo_HSOCKET_TO_STRING.TcPOU)

```iecst
// 场景：客户端建连成功后把句柄打成日志，便于追踪每条 TCP 连接。
PROGRAM P_Demo_HSOCKET_TO_STRING
VAR
    hClient    : T_HSOCKET;             // 假设由上游 FB_SocketConnect 提供
    sHandleStr : STRING(80);
END_VAR

sHandleStr := HSOCKET_TO_STRING(hClient);
// 例如 sHandleStr 显示 "Handle:0x4001 Local:172.16.6.195:28459 Remote:172.16.6.180:2404"
```

## 7. 业务场景与实际价值

- **场景**：日志记录每个 TCP 连接信息、HMI 显示当前连接的对端 IP、运行时诊断界面打印句柄列表。
- **价值**：一行调用拿到可读连接信息；省去手工 CONCAT 拼 4 个字段的代码。
- **替代方案对比**：
  - 手动拼：`CONCAT('Handle:0x', ULINT_TO_HEXSTR(...), ' Local:...')`——可行但繁琐
  - 本函数：标准格式，与 Beckhoff 内部日志一致

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.2.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84162827.html
- **相关**：`HSOCKET_TO_STRINGEX`（带 local/remote 开关）、`SOCKETADDR_TO_STRING`（仅地址结构）、`T_HSOCKET`
