# FB_TlsSocketSetPsk

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_TcpIp` |
| Library Version | `1.5.2` |
| Type | `FUNCTION_BLOCK` |
| Category | `Function blocks` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/12511163531.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_TlsSocketSetPsk.TcPOU`](../examples/P_Demo_FB_TlsSocketSetPsk.TcPOU) |

---

## 1. 功能简述

把 TLS Pre-Shared Key（预共享密钥）加载到指定 TLS socket。**PSK 模式是证书模式的替代方案**：两端事先离线协商好一对 `(identity, key)`，TLS 握手时不再走证书校验链而是验 PSK，简化部署但对密钥分发提出更高安全要求。适合受控的 IoT 场景（如同型号设备出厂烧录同一 PSK）。客户端和服务端调本 FB 后，**不再需要** `FB_TlsSocketAddCa` / `FB_TlsSocketSetCert` / `FB_TlsSocketAddCrl`——它们是互斥的两套体系。需要 TF6310 v3.3.15.0 或更高版本。**必须在 Connect/Listen 之前调用**。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sSrvNetId : T_AmsNetId:='';
    hSocket   : T_HSOCKET;
    sIdentity : STRING(TCPADS_TLS_PSK_IDENTITY_SIZE):='';
    pskKey    : PVOID:=0;
    pskKeyLen : UDINT(0..TCPADS_TLS_MAX_PSK_KEY_SIZE):=0;
    bExecute  : BOOL;
    tTimeout  : TIME:=T#5s;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sSrvNetId` | `T_AmsNetId` | `''` | TCP/IP Connection Server NetID。本机用空串 |
| `hSocket` | `T_HSOCKET` | — | 由 `FB_TlsSocketCreate` 创建的 socket 句柄 |
| `sIdentity` | `STRING(TCPADS_TLS_PSK_IDENTITY_SIZE)` | `''` | PSK 身份标识字符串（任意 ASCII，最长 `TCPADS_TLS_PSK_IDENTITY_SIZE = 255` 字节）。客户端和服务端必须用同一 identity |
| `pskKey` | `PVOID` | `0` | 指向 PSK 字节数组的指针（`ADR(abPsk)`） |
| `pskKeyLen` | `UDINT(0..TCPADS_TLS_MAX_PSK_KEY_SIZE)` | `0` | PSK 字节数。范围 `0..128`（`TCPADS_TLS_MAX_PSK_KEY_SIZE` = 128） |
| `bExecute` | `BOOL` | — | 上升沿触发一次加载 |
| `tTimeout` | `TIME` | `T#5s` | ADS 超时 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bBusy  : BOOL;
    bError : BOOL;
    nErrId : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bBusy` | `BOOL` | 正在加载 |
| `bError` | `BOOL` | 失败 |
| `nErrId` | `UDINT` | TCP/IP Connection Server 错误号 |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bExecute` 上升沿一次加载。

**单次加载状态机**：上升沿 → `bBusy := TRUE`；Server 拷贝 `(sIdentity, pskKey[0..pskKeyLen-1])` 到 TLS context；完成 → `bBusy := FALSE`、`bError := FALSE`。后续 TLS 握手用 PSK-based cipher suite（如 `TLS_PSK_WITH_AES_128_GCM_SHA256`），双方互验 PSK 一致即建连。

**与证书模式互斥**：调过本 FB 的 socket 不应再调 `AddCa` / `SetCert`（实际行为视底层实现，但 PDF 设计意图是二选一）。

**身份匹配**：客户端在握手时把 `sIdentity` 发给服务端，服务端用此 identity 查找对应 PSK；找到 + 一致 = 握手成功，找不到或不一致 = `TLS_HANDSHAKE_FAIL`。同型号设备组可共用一对 (identity, key)；按设备 ID 区分密钥则每台机器烧一份。

**`pskKey` 缓冲区生命期**：本 FB 在 `bBusy=TRUE` 期间读 `pskKey` 指向的内存，加载完即拷贝完成，之后业务侧可重用或清零该内存。但**强烈建议把 PSK 放进不会被 PLC 重启重置的安全位置**——典型放加密变量或硬件 TPM。

**典型陷阱**：`pskKeyLen > 128` → 范围检查报错（IEC 子类型边界）；`pskKey := 0` 不传指针 → 加载 0 字节 PSK = 等价无 PSK，握手失败；客户端 / 服务端 identity 大小写不同 → `HANDSHAKE_FAIL`；Connect/Listen 后才调 → `TLS_INVALID_STATE`。

## 4. 错误码 / 返回值

| `nErrId` (hex) | 符号 | 含义 |
|---|---|---|
| `0x00008002` | `TCPADSERROR_NOTFOUND` | `hSocket` 无效 |
| `0x00008080` | `TLS_INVALID_STATE` | 已 Connect/Listen 后才调 |
| `0x0000808E` | `TLS_PSK_SETUP_ERROR` | PSK 设置失败（key 长度非法、identity 太长等） |

## 5. 使用注意 / 常见坑

- **PSK ≠ 密码**：PSK 是二进制密钥（典型 16 / 32 字节随机字节），不是 ASCII 字符串密码。要从字符串生成 PSK 务必先用 HKDF 或 KDF 推导。
- **密钥分发**：PSK 安全完全依赖"两端如何共享同一对密钥"。出厂烧录 / 离线 USB / 配对协议各有取舍——分发不安全 = TLS 安全归零。
- **不能用于公网服务**：PSK 适合"少量受控设备"对称场景；想接千万级客户端用证书 PKI 是正确选择。
- **`pskKeyLen` 边界**：IEC 子类型 `UDINT(0..128)` 会在调用时做范围检查；写 200 会编译警告或运行时报错。
- **identity 不加密**：在握手时明文传，**不要**把敏感信息编入 identity；用通用 device ID 或随机 UUID。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_TlsSocketSetPsk.TcPOU`](../examples/P_Demo_FB_TlsSocketSetPsk.TcPOU)

```iecst
// 场景：IoT 客户端用 PSK 接 IoT 网关；不部署证书 PKI 简化运维。
PROGRAM P_Demo_FB_TlsSocketSetPsk
VAR
    fbSetPsk       : FB_TlsSocketSetPsk;
    hSocket        : T_HSOCKET;
    sPskIdentity   : STRING(255) := 'sensor-line-A-station-3';
    abPskBytes     : ARRAY[0..15] OF BYTE := [
        16#A1, 16#B2, 16#C3, 16#D4, 16#E5, 16#F6, 16#07, 16#18,
        16#29, 16#3A, 16#4B, 16#5C, 16#6D, 16#7E, 16#8F, 16#90
    ];   // 16 字节随机 PSK
    bRequestSetPsk : BOOL;
    bSetPskBusy    : BOOL;
    bSetPskError   : BOOL;
    nSetPskErrId   : UDINT;
END_VAR

fbSetPsk(
    sSrvNetId := '',
    hSocket   := hSocket,
    sIdentity := sPskIdentity,
    pskKey    := ADR(abPskBytes),
    pskKeyLen := SIZEOF(abPskBytes),
    bExecute  := bRequestSetPsk,
    tTimeout  := T#5S,
    bBusy     => bSetPskBusy,
    bError    => bSetPskError,
    nErrId    => nSetPskErrId
);
```

## 7. 业务场景与实际价值

- **场景**：同型号设备群组（多台同款扫码枪、多台同款工业相机）出厂烧录同一 PSK，简化 PKI 运维；老旧设备升级时不想引入 CA 链；本地内网受信任设备组。
- **价值**：完全跳过 X.509 / CA / CRL 这套复杂体系，单一密钥即完成认证 + 加密。
- **替代方案对比**：
  - 证书 PKI：分发简单（公网信任）但部署复杂、需要管 CA、续签、CRL/OCSP
  - PSK：分发难（需要安全通道下发）但运行简单、无需 CA
  - 无 TLS：明文，不推荐跨网

## 8. 参考资料

- **PDF**：[TF6310_TC3_TCP_IP_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6310_TC3_TCP_IP_EN.pdf) §5.1.19
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6310_tc3_tcpip/12511163531.html
- **相关**：`FB_TlsSocketCreate`（前置）、`FB_TlsSocketConnect` / `FB_TlsSocketListen`（后续）、`FB_TlsSocketSetCert`（证书模式替代方案）
