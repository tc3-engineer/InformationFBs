# Tc2_EIB

> Beckhoff KL6301 EIB（European Installation Bus，等同 KNX TP1）总线主端子 PLC 接入库。版本 `1.16.1`。

- [官方 InfoSys](https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/)
- [官方 PDF](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf)
- 适用：TwinCAT 3.1+ + KL6301 端子（K-bus / E-bus 耦合器后挂）

## 索引（48 条 · 全部 ✅ verified）

### 耦合器（Coupler，2）

| Name | 文档 | 例程 |
|---|---|---|
| KL6301 | [✅ verified](coupler/KL6301.md) | [P_Demo_KL6301.TcPOU](examples/P_Demo_KL6301.TcPOU) |
| KL6301_EX | [✅ verified](coupler/KL6301_EX.md) | [P_Demo_KL6301_EX.TcPOU](examples/P_Demo_KL6301_EX.TcPOU) |

### 接收（Read，15）

| Name | DPT | 文档 | 例程 |
|---|---|---|---|
| EIB_BIT_REC | DPT 1.xxx (1-bit 开关) | [✅ verified](read/EIB_BIT_REC.md) | [P_Demo_EIB_BIT_REC.TcPOU](examples/P_Demo_EIB_BIT_REC.TcPOU) |
| EIB_BIT_CONTROL_REC | DPT 2.xxx (2-bit 带优先级) | [✅ verified](read/EIB_BIT_CONTROL_REC.md) | [P_Demo_EIB_BIT_CONTROL_REC.TcPOU](examples/P_Demo_EIB_BIT_CONTROL_REC.TcPOU) |
| EIB_3BIT_CONTROL_REC | DPT 3.xxx (4-bit 调光控制) | [✅ verified](read/EIB_3BIT_CONTROL_REC.md) | [P_Demo_EIB_3BIT_CONTROL_REC.TcPOU](examples/P_Demo_EIB_3BIT_CONTROL_REC.TcPOU) |
| EIB_8BIT_SIGN_REC | DPT 5.001/003/005 (1-byte 缩放) | [✅ verified](read/EIB_8BIT_SIGN_REC.md) | [P_Demo_EIB_8BIT_SIGN_REC.TcPOU](examples/P_Demo_EIB_8BIT_SIGN_REC.TcPOU) |
| EIB_8BIT_UNSIGN_REC | DPT 5.005/010 (1-byte 原始) | [✅ verified](read/EIB_8BIT_UNSIGN_REC.md) | [P_Demo_EIB_8BIT_UNSIGN_REC.TcPOU](examples/P_Demo_EIB_8BIT_UNSIGN_REC.TcPOU) |
| EIB_2OCTET_FLOAT_REC | DPT 9.xxx (2-byte 半精度浮点) | [✅ verified](read/EIB_2OCTET_FLOAT_REC.md) | [P_Demo_EIB_2OCTET_FLOAT_REC.TcPOU](examples/P_Demo_EIB_2OCTET_FLOAT_REC.TcPOU) |
| EIB_2OCTET_SIGN_REC | DPT 8.xxx (2-byte signed) | [✅ verified](read/EIB_2OCTET_SIGN_REC.md) | [P_Demo_EIB_2OCTET_SIGN_REC.TcPOU](examples/P_Demo_EIB_2OCTET_SIGN_REC.TcPOU) |
| EIB_2OCTET_UNSIGN_REC | DPT 7.xxx (2-byte unsigned) | [✅ verified](read/EIB_2OCTET_UNSIGN_REC.md) | [P_Demo_EIB_2OCTET_UNSIGN_REC.TcPOU](examples/P_Demo_EIB_2OCTET_UNSIGN_REC.TcPOU) |
| EIB_4OCTET_FLOAT_REC | DPT 14.xxx (4-byte IEEE 754) | [✅ verified](read/EIB_4OCTET_FLOAT_REC.md) | [P_Demo_EIB_4OCTET_FLOAT_REC.TcPOU](examples/P_Demo_EIB_4OCTET_FLOAT_REC.TcPOU) |
| EIB_4OCTET_SIGN_REC | DPT 13.xxx (4-byte signed) | [✅ verified](read/EIB_4OCTET_SIGN_REC.md) | [P_Demo_EIB_4OCTET_SIGN_REC.TcPOU](examples/P_Demo_EIB_4OCTET_SIGN_REC.TcPOU) |
| EIB_4OCTET_UNSIGN_REC | DPT 12.xxx (4-byte unsigned) | [✅ verified](read/EIB_4OCTET_UNSIGN_REC.md) | [P_Demo_EIB_4OCTET_UNSIGN_REC.TcPOU](examples/P_Demo_EIB_4OCTET_UNSIGN_REC.TcPOU) |
| EIB_DATE_REC | DPT 11.001 (3-byte date) | [✅ verified](read/EIB_DATE_REC.md) | [P_Demo_EIB_DATE_REC.TcPOU](examples/P_Demo_EIB_DATE_REC.TcPOU) |
| EIB_TIME_REC | DPT 10.001 (3-byte time) | [✅ verified](read/EIB_TIME_REC.md) | [P_Demo_EIB_TIME_REC.TcPOU](examples/P_Demo_EIB_TIME_REC.TcPOU) |
| EIB_ALL_DATA_TYPES_REC | 任意类型 + 指定地址 | [✅ verified](read/EIB_ALL_DATA_TYPES_REC.md) | [P_Demo_EIB_ALL_DATA_TYPES_REC.TcPOU](examples/P_Demo_EIB_ALL_DATA_TYPES_REC.TcPOU) |
| EIB_ALL_DATA_TYPES_REC_EX | 任意类型 + 任意地址（嗅探） | [✅ verified](read/EIB_ALL_DATA_TYPES_REC_EX.md) | [P_Demo_EIB_ALL_DATA_TYPES_REC_EX.TcPOU](examples/P_Demo_EIB_ALL_DATA_TYPES_REC_EX.TcPOU) |

### 发送（Send，29）

| Name | 模式 | DPT | 文档 | 例程 |
|---|---|---|---|---|
| EIB_BIT_SEND | 变化触发 | DPT 1.xxx | [✅ verified](send/EIB_BIT_SEND.md) | [P_Demo_EIB_BIT_SEND.TcPOU](examples/P_Demo_EIB_BIT_SEND.TcPOU) |
| EIB_BIT_SEND_EX | 4 模式 + Read | DPT 1.xxx | [✅ verified](send/EIB_BIT_SEND_EX.md) | [P_Demo_EIB_BIT_SEND_EX.TcPOU](examples/P_Demo_EIB_BIT_SEND_EX.TcPOU) |
| EIB_BIT_SEND_MANUAL | 手动触发 | DPT 1.xxx | [✅ verified](send/EIB_BIT_SEND_MANUAL.md) | [P_Demo_EIB_BIT_SEND_MANUAL.TcPOU](examples/P_Demo_EIB_BIT_SEND_MANUAL.TcPOU) |
| EIB_BIT_CONTROL_SEND | 变化触发 | DPT 2.xxx | [✅ verified](send/EIB_BIT_CONTROL_SEND.md) | [P_Demo_EIB_BIT_CONTROL_SEND.TcPOU](examples/P_Demo_EIB_BIT_CONTROL_SEND.TcPOU) |
| EIB_BIT_CONTROL_SEND_EX | 4 模式 + Read | DPT 2.xxx | [✅ verified](send/EIB_BIT_CONTROL_SEND_EX.md) | [P_Demo_EIB_BIT_CONTROL_SEND_EX.TcPOU](examples/P_Demo_EIB_BIT_CONTROL_SEND_EX.TcPOU) |
| EIB_3BIT_CONTROL_SEND | 变化触发 | DPT 3.xxx | [✅ verified](send/EIB_3BIT_CONTROL_SEND.md) | [P_Demo_EIB_3BIT_CONTROL_SEND.TcPOU](examples/P_Demo_EIB_3BIT_CONTROL_SEND.TcPOU) |
| EIB_3BIT_CONTROL_SEND_EX | 4 模式 + Read | DPT 3.xxx | [✅ verified](send/EIB_3BIT_CONTROL_SEND_EX.md) | [P_Demo_EIB_3BIT_CONTROL_SEND_EX.TcPOU](examples/P_Demo_EIB_3BIT_CONTROL_SEND_EX.TcPOU) |
| EIB_8BIT_SIGN_SEND | 变化触发 | DPT 5.001/003/005 | [✅ verified](send/EIB_8BIT_SIGN_SEND.md) | [P_Demo_EIB_8BIT_SIGN_SEND.TcPOU](examples/P_Demo_EIB_8BIT_SIGN_SEND.TcPOU) |
| EIB_8BIT_SIGN_SEND_EX | 4 模式 + Read | DPT 5.001/003/005 | [✅ verified](send/EIB_8BIT_SIGN_SEND_EX.md) | [P_Demo_EIB_8BIT_SIGN_SEND_EX.TcPOU](examples/P_Demo_EIB_8BIT_SIGN_SEND_EX.TcPOU) |
| EIB_8BIT_UNSIGN_SEND | 变化触发 | DPT 5.005/010 | [✅ verified](send/EIB_8BIT_UNSIGN_SEND.md) | [P_Demo_EIB_8BIT_UNSIGN_SEND.TcPOU](examples/P_Demo_EIB_8BIT_UNSIGN_SEND.TcPOU) |
| EIB_8BIT_UNSIGN_SEND_EX | 4 模式 + Read | DPT 5.005/010 | [✅ verified](send/EIB_8BIT_UNSIGN_SEND_EX.md) | [P_Demo_EIB_8BIT_UNSIGN_SEND_EX.TcPOU](examples/P_Demo_EIB_8BIT_UNSIGN_SEND_EX.TcPOU) |
| EIB_2OCTET_FLOAT_SEND | 变化触发 | DPT 9.xxx | [✅ verified](send/EIB_2OCTET_FLOAT_SEND.md) | [P_Demo_EIB_2OCTET_FLOAT_SEND.TcPOU](examples/P_Demo_EIB_2OCTET_FLOAT_SEND.TcPOU) |
| EIB_2OCTET_FLOAT_SEND_EX | 4 模式 + Read | DPT 9.xxx | [✅ verified](send/EIB_2OCTET_FLOAT_SEND_EX.md) | [P_Demo_EIB_2OCTET_FLOAT_SEND_EX.TcPOU](examples/P_Demo_EIB_2OCTET_FLOAT_SEND_EX.TcPOU) |
| EIB_2OCTET_SIGN_SEND | 变化触发 | DPT 8.xxx | [✅ verified](send/EIB_2OCTET_SIGN_SEND.md) | [P_Demo_EIB_2OCTET_SIGN_SEND.TcPOU](examples/P_Demo_EIB_2OCTET_SIGN_SEND.TcPOU) |
| EIB_2OCTET_SIGN_SEND_EX | 4 模式 + Read | DPT 8.xxx | [✅ verified](send/EIB_2OCTET_SIGN_SEND_EX.md) | [P_Demo_EIB_2OCTET_SIGN_SEND_EX.TcPOU](examples/P_Demo_EIB_2OCTET_SIGN_SEND_EX.TcPOU) |
| EIB_2OCTET_UNSIGN_SEND | 变化触发 | DPT 7.xxx | [✅ verified](send/EIB_2OCTET_UNSIGN_SEND.md) | [P_Demo_EIB_2OCTET_UNSIGN_SEND.TcPOU](examples/P_Demo_EIB_2OCTET_UNSIGN_SEND.TcPOU) |
| EIB_2OCTET_UNSIGN_SEND_EX | 4 模式 + Read | DPT 7.xxx | [✅ verified](send/EIB_2OCTET_UNSIGN_SEND_EX.md) | [P_Demo_EIB_2OCTET_UNSIGN_SEND_EX.TcPOU](examples/P_Demo_EIB_2OCTET_UNSIGN_SEND_EX.TcPOU) |
| EIB_4OCTET_FLOAT_SEND | 变化触发 | DPT 14.xxx | [✅ verified](send/EIB_4OCTET_FLOAT_SEND.md) | [P_Demo_EIB_4OCTET_FLOAT_SEND.TcPOU](examples/P_Demo_EIB_4OCTET_FLOAT_SEND.TcPOU) |
| EIB_4OCTET_FLOAT_SEND_EX | 4 模式 + Read | DPT 14.xxx | [✅ verified](send/EIB_4OCTET_FLOAT_SEND_EX.md) | [P_Demo_EIB_4OCTET_FLOAT_SEND_EX.TcPOU](examples/P_Demo_EIB_4OCTET_FLOAT_SEND_EX.TcPOU) |
| EIB_4OCTET_SIGN_SEND | 变化触发 | DPT 13.xxx | [✅ verified](send/EIB_4OCTET_SIGN_SEND.md) | [P_Demo_EIB_4OCTET_SIGN_SEND.TcPOU](examples/P_Demo_EIB_4OCTET_SIGN_SEND.TcPOU) |
| EIB_4OCTET_SIGN_SEND_EX | 4 模式 + Read | DPT 13.xxx | [✅ verified](send/EIB_4OCTET_SIGN_SEND_EX.md) | [P_Demo_EIB_4OCTET_SIGN_SEND_EX.TcPOU](examples/P_Demo_EIB_4OCTET_SIGN_SEND_EX.TcPOU) |
| EIB_4OCTET_UNSIGN_SEND | 变化触发 | DPT 12.xxx | [✅ verified](send/EIB_4OCTET_UNSIGN_SEND.md) | [P_Demo_EIB_4OCTET_UNSIGN_SEND.TcPOU](examples/P_Demo_EIB_4OCTET_UNSIGN_SEND.TcPOU) |
| EIB_4OCTET_UNSIGN_SEND_EX | 4 模式 + Read | DPT 12.xxx | [✅ verified](send/EIB_4OCTET_UNSIGN_SEND_EX.md) | [P_Demo_EIB_4OCTET_UNSIGN_SEND_EX.TcPOU](examples/P_Demo_EIB_4OCTET_UNSIGN_SEND_EX.TcPOU) |
| EIB_DATE_SEND | 5 分钟节拍 | DPT 11.001 | [✅ verified](send/EIB_DATE_SEND.md) | [P_Demo_EIB_DATE_SEND.TcPOU](examples/P_Demo_EIB_DATE_SEND.TcPOU) |
| EIB_DATE_SEND_EX | 4 模式 + Read | DPT 11.001 | [✅ verified](send/EIB_DATE_SEND_EX.md) | [P_Demo_EIB_DATE_SEND_EX.TcPOU](examples/P_Demo_EIB_DATE_SEND_EX.TcPOU) |
| EIB_TIME_SEND | 5 分钟节拍 | DPT 10.001 | [✅ verified](send/EIB_TIME_SEND.md) | [P_Demo_EIB_TIME_SEND.TcPOU](examples/P_Demo_EIB_TIME_SEND.TcPOU) |
| EIB_TIME_SEND_EX | 4 模式 + Read | DPT 10.001（⚠️ PDF 排版错） | [✅ verified](send/EIB_TIME_SEND_EX.md) | [P_Demo_EIB_TIME_SEND_EX.TcPOU](examples/P_Demo_EIB_TIME_SEND_EX.TcPOU) |
| EIB_ALL_DATA_TYPES_SEND | 3 模式 + Read 应答 + 优先级 | 任意 | [✅ verified](send/EIB_ALL_DATA_TYPES_SEND.md) | [P_Demo_EIB_ALL_DATA_TYPES_SEND.TcPOU](examples/P_Demo_EIB_ALL_DATA_TYPES_SEND.TcPOU) |
| EIB_READ_SEND | 主动查询 | — | [✅ verified](send/EIB_READ_SEND.md) | [P_Demo_EIB_READ_SEND.TcPOU](examples/P_Demo_EIB_READ_SEND.TcPOU) |

### 函数（Functions，2）

| Name | 用途 | 文档 | 例程 |
|---|---|---|---|
| F_CONV_2GROUP_TO_3GROUP | 2 级地址 → 3 级地址 | [✅ verified](functions/F_CONV_2GROUP_TO_3GROUP.md) | [P_Demo_F_CONV_2GROUP_TO_3GROUP.TcPOU](examples/P_Demo_F_CONV_2GROUP_TO_3GROUP.TcPOU) |
| F_CONV_3GROUP_TO_2GROUP | 3 级地址 → 2 级地址 | [✅ verified](functions/F_CONV_3GROUP_TO_2GROUP.md) | [P_Demo_F_CONV_3GROUP_TO_2GROUP.TcPOU](examples/P_Demo_F_CONV_3GROUP_TO_2GROUP.TcPOU) |

## 库使用须知

### EIB 是什么

EIB（European Installation Bus）是 1990 年代欧洲制定的楼宇控制总线标准；2002 年与 EHS / BatiBUS 合并升级为 KNX。本库针对的是 KNX 的 TP1（双绞线物理层），通信内容、组地址格式、数据类型与 KNX TP1 兼容——所以面向"新 KNX 设备"也能用本库。

### 三件套：KL6301 + EIB_REC + EIB_*_REC/SEND

任何 PLC 程序使用 Tc2_EIB 都遵循三步骤：

1. **每个 KL6301 端子配置一个 `KL6301` 实例**（用 `idx` 区分），每周期调用一次，至少配 1 个 `EIB_GROUP_FILTER`，`bActivate := TRUE` 启动数据交换。
2. **`KL6301.str_Data_Rec` 是 `EIB_REC` 类型的胶水**——所有 `EIB_*_REC` 和 `EIB_*_SEND` 都要把这个变量传给它们的 `strData_Rec` / `str_Rec` 输入。**串联错位是新手最常见坑**。
3. **所有 EIB 收发 FB 必须与 KL6301 实例在同一 PLC 任务**。跨任务时 `EIB_REC` 状态不同步，收发会静默失败。

### 选择 _EX 还是普通版

| 需求 | 用什么 |
|---|---|
| 仅在数据变化时发 | 普通版（更简洁） |
| 需要周期心跳 / 防 BMS 失同步 | _EX，`iMode = 1` Polling 或 `3` OnChangePolling |
| 需要响应 BMS 发起的 Read_Group_Req | _EX，`bEnableReadReq := TRUE` |
| 需要发送非标 DPT 或带优先级 | `EIB_ALL_DATA_TYPES_SEND` |
| 强制重发同一值（心跳） | `EIB_BIT_SEND_MANUAL`（1-bit）或 _EX Polling |

### KL6301 固件版本影响

| iMode | 含义 | KL6301 固件 |
|---|---|---|
| 0 | 4 过滤器 × 64 条目 | B0+ |
| 1 | 8 过滤器 × 32 条目 | B1+ |
| 2 | 8 过滤器 × 32 条目 反向过滤 | B3+ |
| 100 | 监控模式（接收所有，不 ACK 不发） | B1+ |

固件版本可用 KS2000 软件读出。老 B0 固件用 iMode > 0 会报 `WRONG_EIB_FIRMWARE_B1_NECESSARY` (14) 或 `WRONG_EIB_FIRMWARE_B3_NECESSARY` (15)。

### 关于 _EX 版本（KL6301_EX）

`KL6301_EX` 是 `KL6301` 的 BETA 扩展版，增加 ETS 软件集成（PhysAddr Search + LED Blink）。仅在 PLC + ETS 工程混用时才需要——纯 PLC 项目用 `KL6301` 即可。

### 误用警告

- ⚠️ `EIB_TIME_SEND_EX` 的 PDF VAR_INPUT 与表格描述不一致（`wDay/wMonth/wYear` vs `wHour/wMinute/wSecond`），疑似 PDF 复制粘贴错误。建议优先用 `EIB_TIME_SEND`（节拍固定但定义清晰）或 `EIB_ALL_DATA_TYPES_SEND` 手构 3 byte DPT 10.001 负载，避免本 FB 直到 .library 实际语义确认。详见 [`send/EIB_TIME_SEND_EX.md`](send/EIB_TIME_SEND_EX.md)。

## 验证基线

- `verify_doc` PASS: 48/48
- `lint_tcpou` PASS: 48/48
- 全仓 `lint_tcpou --check-unique` PASS（GUID 不与其它库冲突）
- 所有文档元信息表 `InfoSys-checked` 行均填 `✅ 2026-06-03`（48/48 在 InfoSys 上有具体 topic 页）
