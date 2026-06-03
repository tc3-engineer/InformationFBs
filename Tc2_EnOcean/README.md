# Tc2_EnOcean

Beckhoff TwinCAT 3 **Tc2_EnOcean** 库的中文技术文档与可导入演示例程。
本库覆盖两条 EnOcean 接入硬件链：**KL6021-0023**（端子自带天线，单天线短距离）和 **KL6581 主端子 + KL6583 远端收发器**（最多 8 节点、覆盖大、楼宇 BMS 标配）。提供按键 / 门窗磁 / 温控房间面板等 EnOcean 设备的接收解码、发送驱动、网络发现与学习按键事件捕获。

| 字段 | 值 |
|---|---|
| Library | `Tc2_EnOcean` |
| Library Version | `1.7.1` |
| PDF | [TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf) |
| InfoSys 入口 | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/index.html |
| 文档总数 | **20 篇（FB 18 + FUNCTION 2）** |
| 例程总数 | **20 个 P_Demo_*.TcPOU** |
| Verify 状态 | 全部 PASS（2026-06-03） |
| Lint 状态 | 全部 PASS（2026-06-03） |
| GUID 全仓唯一性 | PASS（2026-06-03） |

## 库简介

EnOcean® 是一种**自发电无线技术**——按键 / 传感器靠按下时的机械能或环境光 / 温差发电，无电池零维护，覆盖范围 30 m 室内 / 300 m 户外。Beckhoff 在 K-bus 端子系列里提供两类硬件：

- **KL6021-0023**：单端子带 868 MHz 天线，端子直接装控制柜内；适合单房间 / 单工位小覆盖场景。
- **KL6581 + KL6583**：KL6581 是 K-bus 主端子，下挂 1..8 个 KL6583 远端收发器（用专用线引到现场）；适合整楼层 / 多区域覆盖场景。

两条链使用**完全不同的 PLC API**：KL6021-0023 用 `FB_EnOceanReceive` 接收基础 + `FB_EnOceanPTM*` / `FB_EnOceanSTM*` 按设备类型解码；KL6581 用 `FB_KL6581` 作主端子驱动 + `FB_Rec_*` / `FB_Send_*` 各类 send/receive + 学习扫描。新工程一般选 KL6581 体系。

## 分类索引（20 条 · 全部 ✅ verified）

### KL6021-0023 / Receive base（1 个）

KL6021-0023 体系的接收根 FB——所有解析块从这里取数据。

| FB | 用途 |
|---|---|
| [FB_EnOceanReceive](kl6021_receive/FB_EnOceanReceive.md) | KL6021-0023 接收链根 FB，提供 stEnOceanReceivedData 给下游解析块 |

### KL6021-0023 / Read sensor（5 个）

KL6021-0023 体系下按 transmitter 类型解码具体 EnOcean 设备。

| FB | 用途 |
|---|---|
| [FB_EnOceanPTM100](kl6021_sensor/FB_EnOceanPTM100.md) | 8 键单按自发电按键面板（场景模式选择） |
| [FB_EnOceanPTM200](kl6021_sensor/FB_EnOceanPTM200.md) | 4 键双按摇杆面板（按住调光 / 卷帘） |
| [FB_EnOceanSTM100](kl6021_sensor/FB_EnOceanSTM100.md) | ⚠️ 已废弃；STM100 房间温控面板字段硬解码 |
| [FB_EnOceanSTM100Generic](kl6021_sensor/FB_EnOceanSTM100Generic.md) | STM100 通用版（4 byte 原始数据，新工程首选） |
| [FB_EnOceanSTM250](kl6021_sensor/FB_EnOceanSTM250.md) | 门 / 窗磁触点状态 + 学习按键 |

### KL6581 / Master terminal（1 个）

KL6581 体系的主端子驱动——所有 send/receive 块共享其 str_KL6581。

| FB | 用途 |
|---|---|
| [FB_KL6581](kl6581_terminal/FB_KL6581.md) | KL6581 EnOcean 主端子配置 + 通信驱动 |

### KL6581 / Receive（4 个）

KL6581 体系下按 EnOcean 协议类型解码电报。

| FB | 用途 |
|---|---|
| [FB_Rec_Generic](kl6581_receive/FB_Rec_Generic.md) | 通用接收（任意 ORG 类型 + 原始 4 byte） |
| [FB_Rec_1BS](kl6581_receive/FB_Rec_1BS.md) | 1BS 门 / 窗磁（ORG 6） |
| [FB_Rec_RPS_Switch](kl6581_receive/FB_Rec_RPS_Switch.md) | RPS 4 键开关面板（ORG 5） |
| [FB_Rec_RPS_Window_Handle](kl6581_receive/FB_Rec_RPS_Window_Handle.md) | RPS 三态窗把手（ORG 5） |

### KL6581 / Send（4 个）

PLC 模拟 EnOcean 设备发送电报。

| FB | 用途 |
|---|---|
| [FB_Send_Generic](kl6581_send/FB_Send_Generic.md) | 通用发送（任意 ORG 类型 + 4 byte 数据） |
| [FB_Send_4BS](kl6581_send/FB_Send_4BS.md) | 4BS 数据电报（ORG 7 固定，模拟传感器） |
| [FB_Send_RPS_Switch](kl6581_send/FB_Send_RPS_Switch.md) | RPS 开关电报（手动按下 / 释放控制） |
| [FB_Send_RPS_SwitchAuto](kl6581_send/FB_Send_RPS_SwitchAuto.md) | RPS 开关电报（一次触发自动按下 + 释放） |

### KL6581 / Search & Teach-in（3 个）

工程调试期的网络发现 + 学习按键事件捕获。

| FB | 用途 |
|---|---|
| [FB_EnOcean_Search](kl6581_teach_in/FB_EnOcean_Search.md) | 扫描收集所有在线 EnOcean ID（最多 256） |
| [FB_Rec_Teach_In](kl6581_teach_in/FB_Rec_Teach_In.md) | 监听学习按键事件抓 ID |
| [FB_Rec_Teach_In_Ex](kl6581_teach_in/FB_Rec_Teach_In_Ex.md) | 学习事件 + EEP 4-byte 自描述解码（新工程首选） |

### Functions（2 个）

字节转换 helper 函数。

| FC | 用途 |
|---|---|
| [F_Byte_to_Temp](functions/F_Byte_to_Temp.md) | byte → REAL °C 线性温度解码 |
| [F_Byte_to_TurnSwitch](functions/F_Byte_to_TurnSwitch.md) | byte → 5 档旋钮位置布尔结构 |

## 例程导入

所有 20 篇文档配套的 TcPOU 演示程序在 [`examples/`](examples/) 下，文件名 `P_Demo_<Name>.TcPOU`。

导入方式：
1. 右键 TwinCAT 3 PLC 项目 → **Add → Existing Item**
2. 选 `examples/P_Demo_<Name>.TcPOU`
3. 在 References 下添加 `Tc2_EnOcean` 引用
4. 编译 → 登录 → 按文档 §7 与例程头部"验证步骤"注释执行测试

例程包含 KL6021-0023 / KL6581 两条链各类场景：办公室照明 / 调光、会议室一键退房、楼宇门窗磁安防、HVAC 房间温控、新设备入网学习、网络覆盖诊断等真实工业场景。

## 系统选型指南

- **小空间 + 少设备**（单房间 / 单工位 / 50 m² 内）→ KL6021-0023 + 配套 PTM/STM 设备
- **大空间 + 多区域**（整楼层 / 仓库 / 工厂车间）→ KL6581 + 多个 KL6583 远端节点
- **现代 EEP 认证设备**（多数 EnOcean Alliance 设备）→ 用 `FB_Rec_Teach_In_Ex` 自动识别
- **老式 / 厂家定制设备**（如 Eltako 系列变种）→ 用 `FB_Rec_Generic` 或 `FB_EnOceanSTM100Generic` 自己解码

## 已知偏差与待人工确认 ⚠️

1. **`FB_Rec_Teach_In` / `FB_Rec_Teach_In_Ex` 的 `by_Node` 字段描述错误**：PDF（§4.1.2.4.2 / §4.1.2.4.3）描述写为 "Number of EnOcean® devices found"——这是与 `FB_EnOcean_Search` 的 `iDevices` 字段说明混淆。实际语义是"接收到该 LRN 电报的 KL6583 节点编号"。本仓库依协议常识与同类 FB（`FB_Rec_Generic` / `FB_Rec_1BS` 等）的 `by_Node` 语义判定为节点号。InfoSys 同步使用该错误描述。

2. **枚举值 `KL6581_No_KL6853_Found`**：PDF（§4.1.2.6 / §4.2.2.1.2）原文拼写就是 `KL6853`（不是 KL6583）。这是 PDF 印刷错误，本仓库照搬保留。

3. **`bReceive` 反相约定**：KL6581 体系所有 `FB_Rec_*` 块的 `bReceive` 输出**反相**——新电报到达时为 FALSE 一周期，其它时间为 TRUE。这是 PDF 一贯约定，与 KL6021-0023 体系的 `stEnOceanReceivedData.bReceived = TRUE` 语义相反。所有相关文档在 §3 行为说明和 §5 使用注意里均明确标出。

4. **`KL6581_INPUT` / `KL6581_Output` 大小写不一致**：PDF（§4.2.2.2.1 / §4.2.2.2.2）章节标题用 `KL6581_INPUT`（全大写）但 TYPE 声明体内用 `KL6581_Input` 与 `KL6581_Output`（驼峰）。本仓库在 FB_KL6581 文档与 TcPOU 例程内统一用 TYPE 声明里的驼峰拼写（与 PDF 实际代码一致），与 `FB_KL6581` VAR_IN_OUT 区中 PDF 用法一致。

## 文档遵循的硬规则

详见仓库根目录的 [`CLAUDE.md`](../CLAUDE.md)，要点：
- 中文叙述、IEC 关键字与类型名保留英文
- 不出现"详见 PDF"、"见上方"等占位短语
- 每篇含 PDF + InfoSys 双源 URL
- 例程含"场景 / 价值 / 验证步骤"三件套
- 例程注释 ≥ 1/3 代码行，解释 WHY 不复述 WHAT
- 例程是纯 TwinCAT 3 原生 .TcPOU，直接拖入 XAE 即可使用

## 验证基线

- `python3 _meta/tools/verify_doc.py` 全库 20 篇 100% PASS
- `python3 _meta/tools/lint_tcpou.py` 全库 20 个 TcPOU 100% PASS
- `python3 _meta/tools/lint_tcpou.py --check-unique` 全仓 GUID 唯一性 PASS
- 验证日期：2026-06-03
