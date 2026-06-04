# ST_IotMqttWill

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_IotBase` |
| Library Version | `1.13.0` |
| Type | `STRUCT` (DUT) |
| Category | `MQTT3` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/3392049675.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_ST_IotMqttWill.TcPOU`](../examples/P_Demo_ST_IotMqttWill.TcPOU) |

---

## 1. 功能简述

`ST_IotMqttWill` 是 MQTT 3.1.1 客户端的**遗嘱消息**（last will and testament，LWT）结构体，赋给 `FB_IotMqttClient.stWill` 后，broker 会在客户端"异常掉线"（TCP 链路断、心跳超时、未主动 DISCONNECT 就消失）时**自动替它**向该结构体配置的 topic 发一条预设消息，让所有订阅该 topic 的对端立刻知道该 PLC 离线了。

工程价值：避免 SCADA / 看板上一个掉线的 PLC 还显示绿色"在线"——通过订阅各 PLC 的 will-topic（典型如 `plc/+/status`），SCADA 在 broker 自动转发 will 后立即把对应 PLC 状态置红。

本结构体只在 `Execute(bConnect := TRUE)` 第一次建立连接时被 broker 读取（will 是 CONNECT 报文的一部分），运行期间改 `stWill` 字段不会生效。

## 2. 接口定义

本条目是结构体类型，不含 VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT；以下为 `STRUCT` 成员（与 PDF 逐字一致）。

### STRUCT 成员

```iecst
TYPE ST_IotMqttWill :
STRUCT
    {attribute 'TcEncoding':='UTF-8'}
    sTopic        : STRING(255); // topic string (UTF-8) (attend that MQTT topics are case sensitive)
    pPayload      : PVOID;
    nPayloadSize  : UDINT;
    eQoS          : TcIotMqttQos := TcIotMqttQos.ExactlyOnceDelivery; // quality of service between the publishing client and the broker
    bRetain       : BOOL; // if TRUE the broker stores the message in order to send it to new subscribers
END_STRUCT
END_TYPE
```

### 成员说明

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sTopic` | `STRING(255)` | — | will 消息的 topic（UTF-8，大小写敏感）。典型命名如 `plc/Line1/status` |
| `pPayload` | `PVOID` | — | will 消息 payload 起始地址。用 `ADR(变量)`；变量必须在 PLC 生命周期内有效 |
| `nPayloadSize` | `UDINT` | — | payload 字节数 |
| `eQoS` | `TcIotMqttQos` | `TcIotMqttQos.ExactlyOnceDelivery` | will 的 QoS。默认 QoS 2（恰好一次）——broker 必须确保订阅者收到，**默认值与 publish 时常用的 QoS 0 不同**，注意按需修改 |
| `bRetain` | `BOOL` | — | `TRUE` 时 broker 把 will 作为 retain 消息——新订阅者订阅该 topic 时立即收到。典型用法：will 设 `bRetain := TRUE`，订阅者就能查到该 PLC 的最后状态 |

## 3. 行为说明

**生命周期**：① PLC 在 `Execute()` 第一次连上 broker 时，本结构体的内容随 MQTT CONNECT 报文一起送到 broker，broker 记住它；② 业务期间正常运行，will 不会被发；③ 客户端**异常掉线**（TCP RST / keepalive 超时 / 突然下电）后 broker 触发 will，向 `sTopic` 替它发一次 `pPayload`；④ 客户端**主动 DISCONNECT**（业务把 `bConnect` 拉 `FALSE` 后再调 `Execute()`）则 will 被取消——broker 不会发 will，这是正常运行的"优雅停机"语义。

**触发判定**：broker 判客户端异常掉线的依据有两条：① TCP 连接断（被动 RST 或对端没回 ACK）；② keepalive 超时（broker 在 `nKeepAlive × 1.5` 秒内没收到任何报文）。任意一条触发都会发 will。

**配置时机**：必须在 `Execute(bConnect := TRUE)` 第一次调用前，把 `fb.stWill := (sTopic := ..., pPayload := ..., ...);` 设好。已连上之后改 `stWill` 不会通知 broker——除非 DISCONNECT 后再 CONNECT 一次（重新进入 §3 第一步）。

**默认 QoS 2 注意**：本结构体的 `eQoS` 默认 `ExactlyOnceDelivery`（QoS 2），表示 broker 必须用四步握手把 will 送给订阅者。这对状态监控场景合适——不允许遗漏离线事件；但若 broker 不支持 QoS 2 或对大量 PLC 配 QoS 2 will 性能不够时可降到 QoS 1。

**retain 用法**：`bRetain := TRUE` 时 broker 把 will 当 retain 消息保存——后续任意时刻有新订阅者订阅该 topic 时立即收到，"最后已知状态"始终可查。配 SCADA 监控建议开 retain。

**payload 内存寿命**：`pPayload` 指向的变量必须在整个 MQTT 连接生命周期内保持有效。用全局变量或 FB 内部 `VAR` 都行；不要用栈变量或函数返回值。

## 4. 错误码 / 返回值

本结构体是数据载体，无返回值。配置错误（如 `nPayloadSize = 0` 或 `sTopic = ''`）会反映在父 FB `FB_IotMqttClient.bError` / `hrErrorCode`：通常 CONNECT 阶段就报错，连接建立不上。

## 5. 使用注意 / 常见坑

- **运行期间改不生效**：will 是 CONNECT 报文的一部分；建链后再改 `stWill` 字段，要么必须先 DISCONNECT 再 CONNECT 一次，要么干脆没用。在线热改 IP / 用户名/密码 一样不生效——MQTT 协议本身限制。
- **PVOID payload 的引用问题**：`pPayload := ADR(localVar)`，若 `localVar` 是某个临时变量、函数返回值或者作用域受限的局部 VAR，broker 真正发 will 时（往往是 PLC 已经掉电的状态）会读到无效内存。**只用全局变量或 FB 持有的 VAR**。
- **默认 QoS 是 2**：大多数 publish 例程用 QoS 0；本结构体特意用 QoS 2 默认，移植代码时要明白这个差异。
- **broker 必须支持 will**：MQTT 规范要求 broker 实现 will；主流 broker 都支持。但部分简化型 broker（嵌入式 broker）可能忽略。
- **payload 不能太大**：受 `cMaxSizeOfMqttMessage`（默认 100 KB）限制；建议 will payload 控制在几十字节（典型 JSON `{"online":false}`）。（工程经验补充）
- **主动停机不发 will 是正常的**：调试时若发现"停 PLC 没看到 will" → 看 PLC 是否走了 `bConnect := FALSE` 路径，那是 DISCONNECT 不是异常掉线。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ST_IotMqttWill.TcPOU`](../examples/P_Demo_ST_IotMqttWill.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
// 演示遗嘱消息：客户端异常掉线时 broker 自动发 'OFFLINE' 到 plc/line1/status
PROGRAM P_Demo_ST_IotMqttWill
VAR
    sStatusTopic     : STRING := 'plc/line1/status';
    sOfflinePayload  : STRING(40) := 'OFFLINE';
    stWill           : ST_IotMqttWill := (
        sTopic       := 'plc/line1/status',
        pPayload     := 0,                              // 等运行时再补
        nPayloadSize := 0,
        eQoS         := TcIotMqttQos.AtLeastOnceDelivery,
        bRetain      := TRUE                            // 让新订阅者立即查到最后状态
    );
    fbMqtt           : FB_IotMqttClient;
    bEnable          : BOOL := TRUE;
END_VAR

// 把全局 payload 地址写回 stWill（避免 FB 实例化时 ADR 还没就绪）
stWill.pPayload     := ADR(sOfflinePayload);
stWill.nPayloadSize := TO_UDINT(LEN(sOfflinePayload));
fbMqtt.stWill := stWill;                                // 必须在 Execute 前完成
fbMqtt.Execute(bConnect := bEnable);
```

## 7. 业务场景与实际价值

- **场景**：工厂 SCADA 监控数十台 PLC 的在线状态；要求"PLC 一断电、SCADA 1 秒内变红"。MES 推命令到某 PLC 时也需要先确认它在线，免得推到死 PLC 上。
- **价值**：用 will 实现"异常掉线自动广播"——免去 SCADA 每秒轮询每台 PLC 的开销，也免去自建心跳超时判定逻辑。配 `bRetain := TRUE` 还能让新加入的订阅端立即查到"该 PLC 当前是不是在线"，跨重启也保留。
- **替代方案对比**：
  - SCADA 每秒轮询每台 PLC——网络流量爆炸，PLC 数过百时不可行；
  - 自建心跳 + 超时检测——SCADA 端要为每个 PLC 维持定时器，断网瞬间也要等几个心跳周期才发现；
  - **本结构体**：broker 直接代发——broker 自己实现的 keepalive 超时判定通常在 1-2 个 keepalive 周期内触发，速度快且统一。

## 8. 参考资料

- **PDF**：[`TF6701_TC3_IoT_Communication_MQTT_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf) §5.1.1.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/3392049675.html
- **相关 DUT / FB**：`FB_IotMqttClient`（在 `stWill` 引脚消费本结构体）、`TcIotMqttQos`（QoS 枚举）、`ST_IotMqtt5Will`（MQTT 5 版本，扩充了 expiry / delay / user-properties 等字段）
