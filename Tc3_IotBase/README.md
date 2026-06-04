# Tc3_IotBase（TF6701 MQTT 基础库）

> Tc3_IotBase 是 TwinCAT 3 **TF6701 IoT Communication (MQTT)** 安装包提供的 PLC 库之一，封装了 MQTT 3.1.1 和 MQTT 5.0 两个协议版本的客户端 FB / DUT / 枚举。运行需要 TF6701 license。

## 元信息

| 字段 | 值 |
|---|---|
| 库名 | `Tc3_IotBase` |
| 版本 | `1.13.0` |
| 安装包 | TwinCAT 3 Function TF6701 IoT Communication (MQTT) |
| PDF | [TF6701_TC3_IoT_Communication_MQTT_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf) §5.1 Tc3_IotBase |
| InfoSys | https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/ |
| TwinCAT 版本要求 | v3.1.4022.0 (MQTT 3)；v3.1.4026.0 (MQTT 5，Tc3_IotBase ≥ 3.4.2.0) |
| 平台 | IPC、CX（x86 / x64 / Arm） |

## ⚠️ 与 Tc3_JsonXml 的关系

**TF6701 PDF 同时收录 Tc3_IotBase（§5.1）和 Tc3_JsonXml（§5.2）两个库**——它们由同一个 TwinCAT Function 安装，但**是两个独立的 PLC 库**：
- 本目录（`Tc3_IotBase/`）只覆盖 **§5.1 Tc3_IotBase**（MQTT 客户端）；
- `Tc3_JsonXml/` 目录单独覆盖 **§5.2 Tc3_JsonXml**（JSON / XML 解析），见仓内现有 337 条文档。

业务上两者常**配合**使用：MQTT 收到的 payload 多数是 JSON，用 `Tc3_JsonXml.FB_JsonDomParser` 解析；要 publish JSON 时用 `FB_JsonSaxWriter` 构造后再调 `FB_IotMqttClient.Publish(...)`。

## 条目索引（21 条）

### MQTT 3.1.1（mqtt3/，5 条）

| 名称 | 类型 | 一行说明 | 例程 |
|---|---|---|---|
| [`FB_IotMqttClient`](mqtt3/FB_IotMqttClient.md) | FB | MQTT 3.1.1 客户端（含 8 个内嵌方法） | [P_Demo](examples/P_Demo_FB_IotMqttClient.TcPOU) |
| [`ST_IotMqttWill`](mqtt3/ST_IotMqttWill.md) | DUT | MQTT 3 遗嘱消息结构 | [P_Demo](examples/P_Demo_ST_IotMqttWill.TcPOU) |
| [`ST_IotMqttTLS`](mqtt3/ST_IotMqttTLS.md) | DUT | MQTT 3 TLS 设置结构 | [P_Demo](examples/P_Demo_ST_IotMqttTLS.TcPOU) |
| [`FB_IotMqttMessageQueue`](mqtt3/FB_IotMqttMessageQueue.md) | FB | MQTT 3 接收 FIFO 队列 | [P_Demo](examples/P_Demo_FB_IotMqttMessageQueue.TcPOU) |
| [`FB_IotMqttMessage`](mqtt3/FB_IotMqttMessage.md) | FB | MQTT 3 消息载体 | [P_Demo](examples/P_Demo_FB_IotMqttMessage.TcPOU) |

### MQTT 5.0 主要 FB（mqtt5/，4 条）

| 名称 | 类型 | 一行说明 | 例程 |
|---|---|---|---|
| [`FB_IotMqtt5Client`](mqtt5/FB_IotMqtt5Client.md) | FB | MQTT 5 客户端（内嵌队列输出 + 9 个方法） | [P_Demo](examples/P_Demo_FB_IotMqtt5Client.TcPOU) |
| [`FB_IotMqtt5ClientBase`](mqtt5/FB_IotMqtt5ClientBase.md) | FB | MQTT 5 客户端基类（重写回调用，12 个方法） | [P_Demo](examples/P_Demo_FB_IotMqtt5ClientBase.TcPOU) |
| [`FB_IotMqtt5MessageQueue`](mqtt5/FB_IotMqtt5MessageQueue.md) | FB | MQTT 5 接收 FIFO 队列（内嵌于 Client） | [P_Demo](examples/P_Demo_FB_IotMqtt5MessageQueue.TcPOU) |
| [`FB_IotMqtt5Message`](mqtt5/FB_IotMqtt5Message.md) | FB | MQTT 5 消息载体（含 properties） | [P_Demo](examples/P_Demo_FB_IotMqtt5Message.TcPOU) |

### MQTT 5.0 DUT 结构体（mqtt5_duts/，4 条）

| 名称 | 类型 | 一行说明 | 例程 |
|---|---|---|---|
| [`ST_IotMqtt5Will`](mqtt5_duts/ST_IotMqtt5Will.md) | DUT | MQTT 5 遗嘱消息（增强版） | [P_Demo](examples/P_Demo_ST_IotMqtt5Will.TcPOU) |
| [`ST_IotMqtt5Tls`](mqtt5_duts/ST_IotMqtt5Tls.md) | DUT | MQTT 5 TLS 设置 | [P_Demo](examples/P_Demo_ST_IotMqtt5Tls.TcPOU) |
| [`ST_IotMqtt5Auth`](mqtt5_duts/ST_IotMqtt5Auth.md) | DUT | MQTT 5 扩展鉴权（OAuth2 / SCRAM / ...） | [P_Demo](examples/P_Demo_ST_IotMqtt5Auth.TcPOU) |
| [`ST_IotMqtt5Connect`](mqtt5_duts/ST_IotMqtt5Connect.md) | DUT | MQTT 5 高级连接参数（session expire / max packet 等） | [P_Demo](examples/P_Demo_ST_IotMqtt5Connect.TcPOU) |

### MQTT 5.0 Properties 容器（mqtt5_properties/，6 条）

| 名称 | 类型 | 一行说明 | 例程 |
|---|---|---|---|
| [`FB_IotMqtt5ConnAckProperties`](mqtt5_properties/FB_IotMqtt5ConnAckProperties.md) | FB | CONNACK 时 broker 返回的 properties | [P_Demo](examples/P_Demo_FB_IotMqtt5ConnAckProperties.TcPOU) |
| [`FB_IotMqtt5DisconnectProperties`](mqtt5_properties/FB_IotMqtt5DisconnectProperties.md) | FB | DISCONNECT 时 broker 返回的 properties | [P_Demo](examples/P_Demo_FB_IotMqtt5DisconnectProperties.TcPOU) |
| [`FB_IotMqtt5PublishProperties`](mqtt5_properties/FB_IotMqtt5PublishProperties.md) | FB | Publish 时附带的 properties 容器 | [P_Demo](examples/P_Demo_FB_IotMqtt5PublishProperties.TcPOU) |
| [`FB_IotMqtt5SubscribeProperties`](mqtt5_properties/FB_IotMqtt5SubscribeProperties.md) | FB | Subscribe 时附带的 properties 容器 | [P_Demo](examples/P_Demo_FB_IotMqtt5SubscribeProperties.TcPOU) |
| [`FB_IotMqtt5UnsubscribeProperties`](mqtt5_properties/FB_IotMqtt5UnsubscribeProperties.md) | FB | Unsubscribe 时附带的 properties 容器 | [P_Demo](examples/P_Demo_FB_IotMqtt5UnsubscribeProperties.TcPOU) |
| [`FB_IotMqtt5UserProperties`](mqtt5_properties/FB_IotMqtt5UserProperties.md) | FB | User Properties 集合（其他 Properties FB 的基类） | [P_Demo](examples/P_Demo_FB_IotMqtt5UserProperties.TcPOU) |

### 枚举（enums/，1 条）

| 名称 | 类型 | 一行说明 | 例程 |
|---|---|---|---|
| [`ETcIotMqttClientState`](enums/ETcIotMqttClientState.md) | ENUM | MQTT 客户端细分连接状态（42 个值） | [P_Demo](examples/P_Demo_ETcIotMqttClientState.TcPOU) |

### GVL 参数表（gvls/，1 条）

| 名称 | 类型 | 一行说明 | 例程 |
|---|---|---|---|
| [`ParameterList`](gvls/ParameterList.md) | GVL | 容量 / 长度上限编译时常量 | [P_Demo](examples/P_Demo_ParameterList.TcPOU) |

## 例程导入说明

每条文档配套一个 TwinCAT 3 原生 `.TcPOU` 例程（在 `examples/` 下）。导入步骤：

1. 在 XAE 里打开 PLC 项目
2. 在 POUs 文件夹上右键 → Add → Existing Item
3. 选择 `examples/P_Demo_<Name>.TcPOU`
4. 编译（Build）+ 登录（Login）+ 运行（Run）
5. 在线 monitor 各 demo 头部注释的"验证步骤"

**所有例程的运行前提**：
- TwinCAT 3 v3.1.4022.0+（MQTT 5 需 v3.1.4026.0+）
- **TF6701 license 已安装**（无 license 时 `bError` 立即置位）
- 本机或网络可达 MQTT broker（mosquitto / EMQX / HiveMQ 都可）
  - MQTT 3 例程：broker 支持 MQTT 3.1.1（绝大多数 broker 默认）
  - MQTT 5 例程：broker 必须支持 MQTT 5（mosquitto ≥ 1.6 / EMQX 4+ / HiveMQ 4+）
- TLS 例程：需要自签或正式签的证书 + 配 hosts（让证书 CN 与 hostname 对上）

## 验证基线

- `verify_doc.py` 21/21 PASS（含 1 篇 `chapter-overview-only` 合规跳过 VAR 自动对比的 GVL）
- `lint_tcpou.py` 21/21 PASS
- `lint_tcpou.py --check-unique` 全仓 GUID 唯一性 PASS

## 关键技术判断（双源对账）

1. **InfoSys slug = `tf6701_tc3_iot_communication_mqtt`**：标准 TF 编号 slug，brief 推测的 slug 是正确的，未做修正。
2. **`ST_IotMqttTLS` 文件名拼写**：PDF 章节标题用 `ST_IotMqttTLS`（大写 TLS），但 TYPE 声明用 `ST_IotMqttTls`（小写 ls）。文件名按 PDF 标题（让 `verify_doc` 能匹配），文档内类型名按 PDF 声明。
3. **`FB_IotMqtt5ClientBase` Syntax 块印刷错误**：PDF §5.1.2.2 Syntax 块声明的类型名是 `FUNCTION_BLOCK FB_IotMqtt5Client`（少了 `Base`）——明显是 PDF 排版错。InfoSys 也保留此 typo。实际类型名以章节标题为准。
4. **`OnMqtt5ConnAck` 方法签名印刷错误**：PDF §5.1.2.2.5 的 Syntax 写成 `METHOD OnMqtt5Disconnected : HRESULT`——是排版错。实际方法名以章节标题 `OnMqtt5ConnAck` 为准。
5. **`ETcIotMqttClientState` 含 `MQTT_ERR_CONN_PENDING := -1` 但 §5.1.3 主定义未列**：在 PDF §7.2 Error Codes 段和 InfoSys "Error Codes" topic 才看到 -1。文档明示双源差异点。
6. **`FB_IotMqtt5ConnAckProperties.nMaxPackateSize` 含字母颠倒**：是 typo（应该是 `nMaxPacketSize`）但 InfoSys 和实际 API 名字就是这个含 typo 的。
7. **`ParameterList` GVL 用 `chapter-overview-only` 状态**：PDF §5.1.4 是参数表不是 `VAR_GLOBAL` 声明，verify_doc 的 VAR 自动对比无法落锚——按合规跳过该自动检查。
8. **DUT 的 `bSetNullTermination` 缓冲 +1 字节**：例程中演示时 `nPayloadSize := SIZEOF(sLastPayload) - 1`——给 `\0` 留位，避免溢出腐蚀下一变量。这是工程经验，PDF 没明说但 InfoSys 隐含。
9. **MQTT 5 properties FB 的 `pXxxProperties` 是 property 不是 method**：访问时不带括号——业务侧容易写错。文档和例程都明示。
10. **不重复做 Tc3_JsonXml**：brief 明确要求只做 §5.1 Tc3_IotBase（21 条），§5.2 Tc3_JsonXml（337 条）是仓里已完成的，跳过。

## 实际工程使用建议

- **新项目首选 MQTT 5**（`FB_IotMqtt5Client`）——broker 支持的话；老 broker 才用 MQTT 3。
- **接收消息默认走队列**（不重写回调）——业务任务异步处理，不拖 driver 周期。
- **生产环境必须 TLS**：跨公网 / 共享网络场景 `bNoServerCertCheck := TRUE` 严禁出现在生产代码。
- **多 PLC 时 ClientId 带机器号**：避免 `MQTT_ERR_CONN_REFUSED` (5) 或 `Session Taken Over` (0x8E)。
- **遥测场景 `bOverwriteOldestEntry := TRUE`**；**命令场景 `FALSE`**——别让命令"静默丢失"。
- **`Execute()` 必须每 PLC 周期调一次**——藏在条件分支里漏调会丢消息。

## 参考资料

- [TF6701 PDF（全文）](https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf)
- [TF6701 InfoSys 主页](https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/)
- [Beckhoff TF6701 产品页](https://www.beckhoff.com/en-us/products/automation/twincat/tfxxxx-twincat-3-functions/tf6xxx-connectivity/tf6701.html)
- [Beckhoff TF6701 示例 GitHub 仓](https://github.com/Beckhoff/TF6701_Samples)
- MQTT 5.0 规范：[OASIS MQTT v5.0 standard](https://docs.oasis-open.org/mqtt/mqtt/v5.0/mqtt-v5.0.html)
- MQTT 3.1.1 规范：[OASIS MQTT v3.1.1 standard](https://docs.oasis-open.org/mqtt/mqtt/v3.1.1/mqtt-v3.1.1.html)
