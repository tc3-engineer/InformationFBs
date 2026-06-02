# SOCKETADDR_TO_STRING

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84165899.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_SOCKETADDR_TO_STRING.TcPOU`](../examples/P_Demo_SOCKETADDR_TO_STRING.TcPOU) |

---

## 1. 功能简述

把 `ST_SockAddr` 地址结构转换为字符串，格式 `IP:Port`。例：`'172.16.6.195:80'`。`ST_SockAddr` 是 `T_HSOCKET` 中 `localAddr` / `remoteAddr` 字段的类型，单独存放一对 IP + 端口；本函数只对地址结构做字串化，不带 `Handle:` 前缀（与 `HSOCKET_TO_STRING` 区分）。适合只想显示对端地址或 listener 监听地址等单端点场景。

## 2. 接口定义

### Syntax

```iecst
FUNCTION SOCKETADDR_TO_STRING : STRING
VAR_INPUT
    stSockAddr : ST_SockAddr;
END_VAR
```

### VAR_INPUT

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `stSockAddr` | `ST_SockAddr` | — | 要转换的地址结构（`nPort : UDINT` + `sAddr : STRING(15)`） |

### 返回值

| 类型 | 说明 |
|---|---|
| `STRING` | 上述 `IP:Port` 格式字串。最长约 22 字符；接收变量 `STRING(22)` 即可 |

## 3. 行为说明

**调用即返回**：纯函数，无副作用。`stSockAddr.sAddr` 为空串时输出 `:Port`（前面没 IP），`nPort = 0` 时输出 `IP:0`。空结构（全零）输出 `0.0.0.0:0`——常见 listener 的 remoteAddr 或未初始化 socket。

**和 `HSOCKET_TO_STRING` / `EX` 的差别**：本函数处理 `ST_SockAddr`，前两者处理 `T_HSOCKET`。要把 `T_HSOCKET` 拆开后单独输出本地或远端字串，可以这样写：

```iecst
sLocalStr  := SOCKETADDR_TO_STRING(hSock.localAddr);
sRemoteStr := SOCKETADDR_TO_STRING(hSock.remoteAddr);
```

也可以从 `FB_SocketUdpReceiveFrom` 的 `sRemoteHost`、`nRemotePort` 输出手动构造 `ST_SockAddr` 后调用——但更直接的是 `CONCAT(sRemoteHost, ':', UDINT_TO_STRING(nRemotePort))`，无需本函数。

**典型用法**：把 listener 实际绑定的网卡 IP 显示出来（多网卡机器很有用）：

```iecst
sListenAddr := SOCKETADDR_TO_STRING(hListener.localAddr);
// 输出 "172.16.6.195:200" 等，验证 listener 实际绑在哪个网卡
```

## 4. 错误码 / 返回值

无错误码——纯函数。

## 5. 使用注意 / 常见坑

- **接收变量长度**：`STRING(22)` 足以容纳 `255.255.255.255:65535`（21 字符）+ `$00`。
- **不能反向解析**：无对应"字符串→ST_SockAddr"反函数；要解析自己拆字符串。
- **空结构语义**：全零 `ST_SockAddr` 输出 `0.0.0.0:0`，业务侧应自行判断空。
- **listener 的 remoteAddr**：listener socket 没有特定 remote，调本函数会得 `0.0.0.0:0`——这是预期。
- **IPv6**：本库及本函数只支持 IPv4。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_SOCKETADDR_TO_STRING.TcPOU`](../examples/P_Demo_SOCKETADDR_TO_STRING.TcPOU)

```iecst
// 场景：把 hSocket 的 local 和 remote 各自拆出来分别显示。
PROGRAM P_Demo_SOCKETADDR_TO_STRING
VAR
    hClient        : T_HSOCKET;
    sLocalAddr     : STRING(22);
    sRemoteAddr    : STRING(22);
END_VAR

sLocalAddr  := SOCKETADDR_TO_STRING(stSockAddr := hClient.localAddr);
sRemoteAddr := SOCKETADDR_TO_STRING(stSockAddr := hClient.remoteAddr);
```

## 7. 业务场景与实际价值

- **场景**：listener 实际绑定网卡确认（多网卡机器）、HMI 紧凑显示单一 IP、日志拆字段写 CSV。
- **价值**：单字段化提取地址结构。
- **替代方案对比**：
  - 自己拼 `CONCAT(stAddr.sAddr, ':', UDINT_TO_STRING(stAddr.nPort))`：可行但繁琐
  - 用 `HSOCKET_TO_STRINGEX`：处理整个 `T_HSOCKET` 句柄，前缀带 `Handle:`，不适合单地址场景

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.2.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84165899.html
- **相关**：`HSOCKET_TO_STRING` / `HSOCKET_TO_STRINGEX`（处理整个句柄）、`ST_SockAddr`（被转换的类型）、`T_HSOCKET`
