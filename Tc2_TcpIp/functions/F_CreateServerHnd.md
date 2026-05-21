# F_CreateServerHnd

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84161291.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_CreateServerHnd.xml`](../examples/P_Demo_F_CreateServerHnd.xml) |

---

## 1. 功能简述

`T_HSERVER` 类型变量初始化函数：把一个未初始化的 `T_HSERVER` 结构体填上"作为 TCP 服务器要监听的本地 IP / 端口 / 模式 / 使能"等内部参数；之后该 `hServer` 被 `FB_ServerClientConnection`（PDF §5.1.20.2 helper FB）作为 `VAR_IN_OUT` 引用，helper FB 自动用其内部信息开 listener / accept / close 三件套。**仅在用 `FB_ServerClientConnection` 时需要**——直接用 `FB_SocketListen` + `FB_SocketAccept` 的人不需要本函数。同一个 `hServer` 可以传给多个 `FB_ServerClientConnection` 实例以支持多并发连接。

## 2. 接口定义

### Syntax

```iecst
FUNCTION F_CreateServerHnd : BOOL
VAR_IN_OUT
    hServer         : T_HSERVER; 
END_VAR
VAR_INPUT
    sSrvNetID       : T_AmsNetID := ''; 
    sLocalHost      : STRING(15) := ''; 
    nLocalPort      : UDINT := 0;
    nMode           : DWORD := LISTEN_MODE_CLOSEALL (* OR CONNECT_MODE_ENABLEDBG*);
    bEnable         : BOOL := TRUE;
END_VAR
```

### VAR_INPUT

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sSrvNetID` | `T_AmsNetID` | `''` | TCP/IP Connection Server AMS NetID。本机用空串 |
| `sLocalHost` | `STRING(15)` | `''` | 本地服务监听 IPv4 字符串（例 `'172.13.15.2'`）。空串走默认网卡 |
| `nLocalPort` | `UDINT` | `0` | 本地服务监听端口 |
| `nMode` | `DWORD` | `LISTEN_MODE_CLOSEALL` | 标志位组合（用 OR 拼接）：`LISTEN_MODE_CLOSEALL` = 启动时先关掉所有遗留 socket；`CONNECT_MODE_ENABLEDBG` = 启用 debug 日志到 TwinCAT System Manager log |
| `bEnable` | `BOOL` | `TRUE` | listener 行为开关。`TRUE` = 保持 listener 开着；`FALSE` = 等所有已 accept 的连接关闭后自动关 listener |

### VAR_IN_OUT

| 名称 | 类型 | 说明 |
|---|---|---|
| `hServer` | `T_HSERVER` | 要初始化的服务器句柄。函数把内部参数写入该结构 |

### 返回值

| 类型 | 说明 |
|---|---|
| `BOOL` | `TRUE` = 全部输入合法、`hServer` 初始化成功；`FALSE` = 某个输入参数非法（如 IP 字符串格式错） |

## 3. 行为说明

**调用时机**：典型放在 PLC 初始化阶段（如 `bInit := TRUE` 块里跑一次），把 `hServer` 准备好后交给 `FB_ServerClientConnection`。`hServer` 是值类型结构，可以被多个 helper FB 实例共享引用。

**`nMode` 标志详解**：
- `LISTEN_MODE_CLOSEALL`（默认）：helper FB 启动时先内部调用 `FB_SocketCloseAll` 清掉本 runtime 遗留 socket。开发期反复 Download 时这个标志很有用
- `CONNECT_MODE_ENABLEDBG`：把 debug 信息写到 TwinCAT System Manager log，便于排查"为什么 accept 不到客户端"。生产可关

**`bEnable` 与 listener 寿命**：`TRUE` 时 listener 一直开着（哪怕 accept 出来的连接全部关掉）；`FALSE` 时一旦最后一个客户端连接关闭，listener 也自动关。**用于"接完一个就下班"的简易服务**。

**返回 `FALSE` 的常见原因**：`sLocalHost` 格式不合法（不是 IPv4 三点分十进制）、`nLocalPort = 0`（虽然函数定义默认 0 是合法的 OS 自动分配，但 PDF 用法语义是显式给端口）、`hServer` 不能写入。

**典型陷阱**：忘了在初始化时跑这个函数，直接把 `hServer` 默认全 0 结构传给 `FB_ServerClientConnection` 会让 helper 行为不定义；在 PLC 周期里反复调本函数没问题（幂等），但每次重置 `hServer` 会让 helper 重新走启动逻辑。

## 4. 错误码 / 返回值

| 返回值 | 含义 | 处理建议 |
|---|---|---|
| `TRUE` | 初始化成功，`hServer` 可用 | 继续传给 `FB_ServerClientConnection` |
| `FALSE` | 某参数非法 | 检查 `sLocalHost` / `nLocalPort` / `nMode`；逐项打印排查 |

本函数无 `bError` / `nErrId` 输出；仅一个 BOOL 返回。

## 5. 使用注意 / 常见坑

- **初始化只跑一次**：放在 `bInit := TRUE` 守卫的 IF 块里；每周期重跑会让上游 helper FB 不必要地重新启动。
- **`sLocalHost := '0.0.0.0'`**：监听所有网卡（推荐生产用法）。
- **`nMode` 标志组合**：`LISTEN_MODE_CLOSEALL OR CONNECT_MODE_ENABLEDBG` 用 `:=` 直接赋值；不要写成两次 OR。
- **`hServer` 结构体的字段不能手改**：PDF §5.3.8 明确"Preserve the default structure elements"——手动改 hServer.xxx 会破坏 helper FB 的内部状态。
- **单 helper 还是多 helper**：一个 `hServer` 可以多个 `FB_ServerClientConnection` 共享以支持并发连接；想完全独立的服务（不同端口）则各自一个 `T_HSERVER`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_CreateServerHnd.xml`](../examples/P_Demo_F_CreateServerHnd.xml)

```iecst
// 场景：PLC 当 TCP 服务器在 200 端口接 HMI；用 FB_ServerClientConnection helper。
PROGRAM P_Demo_F_CreateServerHnd
VAR
    hServer       : T_HSERVER;
    bInit         : BOOL := TRUE;             // 初始化标志，必须 TRUE 初值
    bInitOk       : BOOL;
    sLocalAddr    : STRING(15) := '0.0.0.0';
    nLocalPort    : UDINT := 200;
END_VAR

// 仅在 PLC 启动那一次初始化 hServer
IF bInit THEN
    bInit := FALSE;
    bInitOk := F_CreateServerHnd(
        hServer    := hServer,
        sSrvNetID  := '',
        sLocalHost := sLocalAddr,
        nLocalPort := nLocalPort,
        nMode      := LISTEN_MODE_CLOSEALL,
        bEnable    := TRUE
    );
END_IF
```

## 7. 业务场景与实际价值

- **场景**：所有用 `FB_ServerClientConnection` 提供 TCP 服务的工程。helper FB 把 listen + accept + close 三件套封装；此函数负责为 helper 提供配置入口。
- **价值**：单一函数完成 `T_HSERVER` 配置；后续业务代码只用 helper FB 引用此句柄即可。
- **替代方案对比**：
  - 不用 helper，直接 `FB_SocketListen` + `FB_SocketAccept`：完全不需要本函数；灵活但代码量大
  - 用 helper + 不调本函数：`hServer` 全 0 结构，helper 行为不定义；不要尝试

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.2.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/84161291.html
- **相关**：`FB_ServerClientConnection`（必配 helper FB）、`T_HSERVER`（被初始化的类型）、`LISTEN_MODE_CLOSEALL` / `CONNECT_MODE_ENABLEDBG`（标志常量）
