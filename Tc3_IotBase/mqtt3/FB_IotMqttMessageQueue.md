# FB_IotMqttMessageQueue

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc3_IotBase` |
| Library Version | `1.13.0` |
| Type | `FUNCTION_BLOCK` |
| Category | `MQTT3` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/3392486923.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_IotMqttMessageQueue.TcPOU`](../examples/P_Demo_FB_IotMqttMessageQueue.TcPOU) |

---

## 1. 功能简述

`FB_IotMqttMessageQueue` 是 MQTT 3.1.1 客户端用的**先进先出（FIFO）消息队列**功能块。把它的实例赋给 `FB_IotMqttClient.ipMessageQueue` 后，所有订阅到的消息在 `Execute()` 内被驱动 push 进本队列，业务侧用 `Dequeue()` 出队、用 `nQueuedMessages` 属性查队列深度。

适合不想重写 `OnMqttMessage()` 回调的场景：业务任务只需要每周期出队 N 条消息处理；回调 vs 队列两种范式只能选一种（重写回调后队列不再生效，见 `FB_IotMqttClient.md` §3）。

队列容量受 Tc3_IotBase 库的 GVL 参数 `cMaxEntriesInMqttMessageQueue`（默认 1000 条）和 `cMaxSizeOfMqttMessageQueue`（默认 1 MB）限制；超限时按 `bOverwriteOldestEntry` 决定丢老消息还是新消息。

## 2. 接口定义

本 FB 没有 VAR_INPUT / VAR_OUTPUT / VAR_IN_OUT；状态通过两个 **Property** 暴露，操作通过两个 **Method** 完成。

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

### Property（属性，读写式访问）

| 属性 | 类型 | 访问 | 说明 |
|---|---|---|---|
| `bOverwriteOldestEntry` | `BOOL` | Get / Set | 队列满后行为：`TRUE` 用新消息覆盖最老消息（老消息丢）；`FALSE` 把新消息丢弃保留老消息。默认对应 PDF 未明示，但 InfoSys 默认 `FALSE`——丢新留老 |
| `nQueuedMessages` | `UDINT` | Get | 当前队列里待出队的消息数；用作业务侧轮询 / 限速依据 |

### METHOD Dequeue

从队列头部出队一条消息到调用方提供的 `FB_IotMqttMessage` 实例。

```iecst
METHOD Dequeue : BOOL
VAR_INPUT
    fbMessage : REFERENCE TO FB_IotMqttMessage;
END_VAR
```

| 名称 | 方向 | 类型 | 说明 |
|---|---|---|---|
| `fbMessage` | IN | `REFERENCE TO FB_IotMqttMessage` | 用于接收出队消息的 `FB_IotMqttMessage` 实例引用——通常在调用方声明一个该类型 VAR，调用时按 `Dequeue(fbMessage := fbMsg)` 传入 |

返回值：`BOOL`——`TRUE` 表示成功出队一条（`nQueuedMessages` 减 1）；`FALSE` 表示队列为空。

### METHOD ResetQueue

清空整个队列——所有未出队消息直接丢弃。

```iecst
METHOD ResetQueue : BOOL
```

无参数；返回 `BOOL`——`TRUE` 表示调用成功。

## 3. 行为说明

**注入路径**：在 `FB_IotMqttClient` 实例之外声明一个 `FB_IotMqttMessageQueue` 实例 `fbQueue`，运行前把 `fbMqtt.ipMessageQueue := fbQueue;` 接好。运行时 `Execute()` 内部由 TwinCAT 驱动收到一条订阅消息后就 push 进队列；业务侧用 `WHILE fbQueue.nQueuedMessages > 0 DO ... fbQueue.Dequeue(REF=> fbMsg) ... END_WHILE` 出队处理。

**FIFO 语义**：先进先出。多条消息一周期内进队 → 按到达顺序排队；出队顺序与到达顺序一致。

**`bOverwriteOldestEntry` 抉择**：
- `TRUE`——队列满后老消息会被覆盖。适合实时遥测（最新数据更重要，老数据可丢）；
- `FALSE`（默认）——队列满后新消息丢失。适合命令流（旧命令必须按顺序执行，宁愿丢新也不能错序）。

**容量限制三层**：① 单条消息大小受 `cMaxSizeOfMqttMessage`（默认 100 KB）限制——超限的消息进队时直接丢弃；② 队列总大小受 `cMaxSizeOfMqttMessageQueue`（默认 1 MB）限制；③ 队列条数受 `cMaxEntriesInMqttMessageQueue`（默认 1000 条）限制。任一限制触达即按 `bOverwriteOldestEntry` 决定丢谁。

**出队后的消息生命**：`Dequeue()` 成功后调用方拿到的 `FB_IotMqttMessage` 实例**只在本次出队后短暂有效**；下次 `Dequeue()` 会复用同一引用并被新消息覆盖。业务侧若想保留消息，必须立刻 `GetTopic()` / `GetPayload()` 拷出来。

**回调与队列互斥**：若派生 `FB_IotMqttClient` 并重写了 `OnMqttMessage()`，无论 `ipMessageQueue` 是否赋值，所有订阅消息都走回调——队列收不到任何消息。要用队列就别派生重写回调。

**多订阅共用一个队列**：一个 `FB_IotMqttClient` 实例所有订阅 topic 的消息全混进同一个队列；业务侧用 `fbMsg.GetTopic()` 或 `fbMsg.CompareTopic(REF=> sExpected)` 分发。要 topic 隔离就用回调路径手动分。

**`ResetQueue()` 用法**：用于"业务边界"——例如配方切换、PLC 任务重启时把残留消息全清掉。日常不该周期调，否则等于禁用队列。

## 4. 错误码 / 返回值

各方法以 `BOOL` 返回成功/失败；具体错误反映在父 `FB_IotMqttClient.bError` / `hrErrorCode`：

| 调用 | `TRUE` 含义 | `FALSE` 含义 |
|---|---|---|
| `Dequeue()` | 成功出队一条 | 队列为空 |
| `ResetQueue()` | 队列已清空 | 内部异常（极少出现） |

队列满 / 单条消息超限的丢弃事件不通过本 FB 返回，由 `FB_IotMqttClient` 内部计数；MQTT 5 版本（`FB_IotMqtt5MessageQueue`）提供 `nLostMessages` 显式属性。

## 5. 使用注意 / 常见坑

- **必须放在 `ipMessageQueue` 引脚前实例化**：`fbMqtt.ipMessageQueue := fbQueue;` 这一行的赋值时机决定 broker 之后的所有订阅消息能不能进队；最稳妥的是在 PROGRAM 顶部首次扫描时就赋好。
- **出队后立刻拷贝**：`Dequeue()` 返回的 `FB_IotMqttMessage` 引用不能跨周期保留，下次出队就被覆盖。Topic / payload 必须当周期就 `GetTopic()` / `GetPayload()` 拷到独立缓冲。
- **`WHILE` 轮询限速**：每周期一次性出空整个队列时要小心——一周期处理 1000 条消息会显著拖慢 PLC 任务。建议设上限 `i < cMaxPerCycle` 限速。（工程经验补充）
- **回调路径下队列没用**：若计划重写 `OnMqttMessage()` 就别声明本 FB——徒占内存。
- **队列实例不要跨 FB 共用**：一个 `FB_IotMqttMessageQueue` 实例只能挂到一个 `FB_IotMqttClient` 上；多客户端就多实例化。
- **`bOverwriteOldestEntry` 默认 `FALSE`**：意味着队列满后**新**消息会丢——很多人误以为是丢老消息（直觉）。命令流场景这是对的；遥测场景请显式 `bOverwriteOldestEntry := TRUE`。
- **不能枚举遍历**：本 FB 不提供"看不出队"的窥视方法——要查内容只能 `Dequeue()`，看完再用 `GetTopic()` 决定要不要处理。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_IotMqttMessageQueue.TcPOU`](../examples/P_Demo_FB_IotMqttMessageQueue.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_IotMqttMessageQueue
VAR
    fbMqtt   : FB_IotMqttClient := (sClientId := 'PLC-Q', sHostName := '127.0.0.1');
    fbQueue  : FB_IotMqttMessageQueue;
    fbMsg    : FB_IotMqttMessage;
    nCount   : UDINT;
END_VAR
// 第一周期把队列接上
fbMqtt.ipMessageQueue := fbQueue;
fbQueue.bOverwriteOldestEntry := TRUE;            // 遥测场景：满了丢老消息
fbMqtt.Execute(bConnect := TRUE);
IF fbMqtt.bConnected THEN
    fbMqtt.Subscribe(sTopic := 'plc/+/telemetry', eQoS := TcIotMqttQos.AtMostOnceDelivery);
END_IF
// 限速出队（每周期最多 50 条）
nCount := 0;
WHILE fbQueue.nQueuedMessages > 0 AND nCount < 50 DO
    IF NOT fbQueue.Dequeue(fbMessage := fbMsg) THEN EXIT; END_IF
    // 在此处对 fbMsg 拷贝 topic / payload 做业务处理
    nCount := nCount + 1;
END_WHILE
```

## 7. 业务场景与实际价值

- **场景**：PLC 订阅工厂所有产线的遥测 `plc/+/telemetry`，业务任务把每条消息解出来汇总到 OEE 看板。订阅消息量大、不规则爆发——一个 `Execute()` 内可能收到几十条。
- **价值**：队列模式让业务代码"周期出队"，把 MQTT 接收与业务处理在时间上解耦——不必担心驱动回调拖慢 PLC 周期（回调直接执行业务代码会有此风险）。配 `bOverwriteOldestEntry := TRUE` 适合遥测——最新数据更重要；老数据丢就丢。
- **替代方案对比**：
  - 重写 `OnMqttMessage()` 回调——更省一次拷贝，但回调里的业务代码会直接占用 `Execute()` 调用栈，耗时操作必须自己异步化；
  - 自己用 ARRAY 模拟 FIFO + 互斥——要自己处理内存、扩容、并发，工作量大；
  - **本 FB**：现成 FIFO，安全、内存动态、有溢出策略选项。

## 8. 参考资料

- **PDF**：[`TF6701_TC3_IoT_Communication_MQTT_EN.pdf`](https://download.beckhoff.com/download/document/automation/twincat3/TF6701_TC3_IoT_Communication_MQTT_EN.pdf) §5.1.1.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tf6701_tc3_iot_communication_mqtt/3392486923.html
- **相关 FB / GVL**：`FB_IotMqttClient`（在 `ipMessageQueue` 引脚消费本队列）、`FB_IotMqttMessage`（出队载体）、`ParameterList`（队列容量上限的 GVL 参数）、`FB_IotMqtt5MessageQueue`（MQTT 5 版本，多了 `nLostMessages` / `nMaxSizeOfMessage` 等属性）
