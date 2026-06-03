# Tc2_SerialCom（TF6340 Serial Communication）

> Beckhoff TwinCAT 3 串行通信 PLC 库。
> 提供与串口硬件（PC COM 口、KL60xx / EL60xx 串口端子、USB 虚拟串口）收发数据的功能块、
> 以及 3964R / RK512 协议、ASCII 辅助函数与错误码转事件函数。
> 运行时需要 TF6340 Serial Communication（含 license）。

## 概览

| 字段 | 值 |
|---|---|
| 库版本 | `1.8.1` |
| 来源 PDF | [TF6340_TC3_Serial_Communication_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf) |
| InfoSys 根 | https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/index.html |
| 文档进度 | 24 / 24（FB 17 + FC 6 + GVL 1，DUT 仅作引用） |

## 通信架构

本库分三层，理解这个分层是用对所有功能块的前提：

1. **硬件层（后台通信）**：`SerialLineControl`（物理串口 / 总线端子）或 `SerialLineControlADS`（USB 虚拟串口）。每个 PLC 周期调用一次，在串口硬件过程映像与 PLC 软件缓冲 `ComBuffer` 之间搬运字节。
2. **缓冲层**：`ComBuffer`（接收 `RxBuffer` + 发送 `TxBuffer`），解耦硬件层与应用层；用户不直接读写。
3. **应用层（收 / 发）**：`SendByte` / `SendData` / `SendString` / `SendString255` 往 `TxBuffer` 塞数据；`ReceiveByte` / `ReceiveData` / `ReceiveString` / `ReceiveString255` 从 `RxBuffer` 取数据。

> 关键：应用层收发功能块用的 `TxBuffer` / `RxBuffer` 必须与后台通信功能块**共用同一实例**，否则数据搬不通。

协议层（`3964R` / `RK512`）建立在硬件层之上，处理带握手 / 校验 / 数据块编址的可靠协议。

## 典型部署模板

### 物理串口 / KL6 / EL6 端子
（可选 `KL6Configuration` 配端子参数 → ）每周期调用 `SerialLineControl` → 应用层 `Send*` / `Receive*` 收发

### USB 虚拟串口（COM）
每周期调用 `SerialLineControlADS`（`Connect := TRUE` 打开口，等 `PortOpened`）→ 应用层 `Send*` / `Receive*` 收发

### 3964R / RK512 协议
每周期调用 `SerialLineControl`（硬件层）+ `3964R` 或 `RK512`（协议层，共用 `TxBuffer` / `RxBuffer`）

## Function Blocks（17）

### 发送 + 接收（9）

| 名称 | 用途 | 文档 |
|---|---|---|
| `ReceiveByte` | 从接收缓冲取单字节 | [function_blocks/ReceiveByte.md](function_blocks/ReceiveByte.md) |
| `ReceiveData` | 成帧接收任意二进制（前缀/后缀/超时/长度判帧） | [function_blocks/ReceiveData.md](function_blocks/ReceiveData.md) |
| `ReceiveString` | 接收字符串（80 字符） | [function_blocks/ReceiveString.md](function_blocks/ReceiveString.md) |
| `ReceiveString255` | 接收字符串（255 字符） | [function_blocks/ReceiveString255.md](function_blocks/ReceiveString255.md) |
| `SendByte` | 发送单字节 | [function_blocks/SendByte.md](function_blocks/SendByte.md) |
| `SendData` | 发送任意二进制块 | [function_blocks/SendData.md](function_blocks/SendData.md) |
| `SendString` | 发送字符串（80 字符） | [function_blocks/SendString.md](function_blocks/SendString.md) |
| `SendString255` | 发送字符串（255 字符） | [function_blocks/SendString255.md](function_blocks/SendString255.md) |
| `ClearComBuffer` | 清空 PLC 内部通信缓冲（软件） | [function_blocks/ClearComBuffer.md](function_blocks/ClearComBuffer.md) |

### 配置（4）

| 名称 | 用途 | 文档 |
|---|---|---|
| `ComReset` | 复位串口硬件、清硬件收发缓冲 | [function_blocks/ComReset.md](function_blocks/ComReset.md) |
| `KL6Configuration` | 配置 KL6xxx 端子串口参数 | [function_blocks/KL6Configuration.md](function_blocks/KL6Configuration.md) |
| `KL6ReadRegisters` | 读 KL6xxx 端子寄存器 | [function_blocks/KL6ReadRegisters.md](function_blocks/KL6ReadRegisters.md) |
| `KL6WriteRegisters` | 写 KL6xxx 端子寄存器 | [function_blocks/KL6WriteRegisters.md](function_blocks/KL6WriteRegisters.md) |

### 后台通信（2）

| 名称 | 用途 | 文档 |
|---|---|---|
| `SerialLineControl` | 物理串口 / 端子后台收发 | [function_blocks/SerialLineControl.md](function_blocks/SerialLineControl.md) |
| `SerialLineControlADS` | USB 虚拟串口后台收发（走 ADS 串口服务器） | [function_blocks/SerialLineControlADS.md](function_blocks/SerialLineControlADS.md) |

### 3964R + RK512 协议（2）

| 名称 | 用途 | 文档 |
|---|---|---|
| `3964R` | 3964R 点对点可靠协议（库内类型名 `P3964R`） | [function_blocks/3964R.md](function_blocks/3964R.md) |
| `RK512` | RK512 数据块读写协议（建立在 3964R 之上） | [function_blocks/RK512.md](function_blocks/RK512.md) |

## Functions（6）

### Help（2）

| 名称 | 用途 | 文档 |
|---|---|---|
| `ASC` | 取字符串首字符的 ASCII 码（`BYTE`） | [functions/ASC.md](functions/ASC.md) |
| `CHR` | 把 ASCII 码转为单字符字符串 | [functions/CHR.md](functions/CHR.md) |

### Conversion（4）—— 错误码转 Tc3_EventLogger 事件

| 名称 | 用途 | 文档 |
|---|---|---|
| `ComError_TO_TcEventEntry` | `ComError_t` → `TcEventEntry` | [functions/ComError_TO_TcEventEntry.md](functions/ComError_TO_TcEventEntry.md) |
| `P3964RError_TO_TcEventEntry` | `P3964R_Error_t` → `TcEventEntry` | [functions/P3964RError_TO_TcEventEntry.md](functions/P3964RError_TO_TcEventEntry.md) |
| `RK512Error_TO_TcEventEntry` | `RK512_Error_t` → `TcEventEntry` | [functions/RK512Error_TO_TcEventEntry.md](functions/RK512Error_TO_TcEventEntry.md) |
| `SerialLineControlADSErr_TO_TcEventEntry` | `UDINT` → `TcEventEntry` | [functions/SerialLineControlADSErr_TO_TcEventEntry.md](functions/SerialLineControlADSErr_TO_TcEventEntry.md) |

## Global Constants（1）

| 名称 | 用途 | 文档 |
|---|---|---|
| `stLibVersion_Tc2_SerialCom` | 库版本结构（运行时版本检查用） | [global_constants/stLibVersion_Tc2_SerialCom.md](global_constants/stLibVersion_Tc2_SerialCom.md) |

## DUTs（未单独成文档，在引用它们的 FB / FC 文档中按需说明）

§5.3 出现的数据类型，作为上述 FB / FC 的参数 / 返回类型使用：

### 结构体（Structures）

| 名称 | 用途 |
|---|---|
| `ComBuffer` | 通信缓冲：`Buffer : ARRAY[0..300] OF BYTE` 环形缓冲 + 读写索引 / 计数 / 错误 / 信号量字段；用户不直接读写 |
| `ComRegisterList_t` | `ARRAY[0..63] OF ComRegisterData_t`，KL6 寄存器列表 |
| `ComRegisterData_t` | `Register : BYTE` + `Value : WORD`，单个寄存器项 |
| `ComSerialConfig` | `SerialLineControlADS` 的串口配置：`ComPort` / `Baudrate` / `Parity` / `DataBits` / `StopBits` / `DTR` / `RTS` / `CTS` / `DSR` / `TraceLevel` 等 |
| `KL6inData` / `KL6outData` | KL6xxx 3 字节模式过程映像 |
| `KL6inData5B` / `KL6outData5B` | KL6xxx 5 字节模式过程映像 |
| `KL6inData22B` / `KL6outData22B` | KL6xxx 22 字节模式过程映像 |
| `EL6inData22B` / `EL6outData22B` | EL60xx EtherCAT 端子 22 字节模式过程映像 |
| `PcComInData` / `PcComOutData` | PC 串口过程映像（`SerStatus`/`SerCtrl : WORD` + `D : ARRAY[0..63] OF BYTE`） |
| `P3964buffer` | `3964R` 应用层数据缓冲（`D : ARRAY[0..16#0FFF] OF BYTE`） |

### 枚举（Enumerations）

| 名称 | 取值 |
|---|---|
| `ComDTRCtrl_t` | `DTR_CTRL_DISABLE` / `DTR_CTRL_ENABLE` / `DTR_CTRL_HANDSHAKE` |
| `ComError_t` | 通用错误码（`COMERROR_NOERROR`=0 … `COMERROR_TIMEOUT`=16#1008），见 PDF §7.2 |
| `ComHandshake_t` | `HANDSHAKE_NONE` / `HANDSHAKE_RTSCTS` / `HANDSHAKE_XONXOFF` / `RS485_*` 系列 |
| `ComParity_t` | `PARITY_NONE` / `PARITY_EVEN` / `PARITY_ODD` / `PARITY_MARK` / `PARITY_SPACE`（后两者仅 `SerialLineControlADS`） |
| `ComRTSCtrl_t` | `RTS_CTRL_DISABLE` / `RTS_CTRL_ENABLE` / `RTS_CTRL_HANDSHAKE` / `RTS_CTRL_TOGGLE` |
| `ComSerialLineMode_t` | `SERIALLINEMODE_DEFAULT` / `_KL6_3B_ALTERNATIVE` / `_KL6_5B_STANDARD` / `_KL6_22B_STANDARD` / `_PC_COM_PORT` / `_EL6_22B` / `_IE6_11B` |
| `ComStopBits_t` | `STOPBITS_ONE`=1 / `STOPBITS_TWO`=2 / `STOPBITS_ONE5`=3 |
| `P3964R_Error_t` | 3964R 协议错误码，见 PDF §7.4 |
| `RK512_Error_t` | RK512 协议错误码，见 PDF §7.5 |

## 错误码概览

不同功能块返回不同的错误体系（PDF §7.1）：

| 来源 | 错误类型 | 适用功能块 |
|---|---|---|
| `ComError_t` | 枚举（PDF §7.2） | 多数功能块：`Send*` / `Receive*` / `SerialLineControl` / `ComReset` / `KL6*` |
| SerialLineControlADS 专用 | `UDINT`（PDF §7.3，分 ADS / 服务器 / Win32 / Linux 几段） | `SerialLineControlADS` |
| `P3964R_Error_t` | 枚举（PDF §7.4） | `3964R` |
| `RK512_Error_t` | 枚举（PDF §7.5） | `RK512` |

## 例程导入

每篇文档配套 `examples/P_Demo_<Name>.TcPOU`：

1. 在 TwinCAT 3 XAE 中右键 PLC 项目下 POUs 文件夹 → **Add → Existing Item…**
2. 选择 `P_Demo_<Name>.TcPOU`
3. 引用 `Tc2_SerialCom`（部分错误转换例程还需引用 `Tc3_EventLogger`）；编译 → 登录 → 运行
4. 把示例里的 `arrComIn` / `arrComOut` 链接到实际 COM 口或 KL6/EL6 端子的过程映像
5. 按文档 §6 / §7 中的"验证步骤"在线观察输入输出

## 验证基线

- 全部 24 篇文档已按 PDF（v1.8.1）+ InfoSys 双源核对：变量名 / 类型 / 默认值逐字搬运，错误码表来自 PDF §7。
- `verify_doc.py`：21 / 24 退出 0（PASS）。其余 3 篇为**共享工具 `extract_section.py` 的已知抽取局限**（非内容缺陷），详见下表。
- `lint_tcpou.py`：24 / 24 退出 0。

| 文档 | verify 退出码 | 原因（工具局限，内容已双源核对正确） |
|---|---|---|
| `3964R` | 2 | `extract_section` 要求章节标题以字母开头，而本 FB 标题 `3964R` 以数字开头，导致无法定位章节正文（`_find_section_in_body` 能定位到 §5.1.4.1，但 `extract_section` 抽取失败）。VAR / 错误码已逐字核对 PDF §5.1.4.1 + §7.4 与 InfoSys。 |
| `SerialLineControlADS` | 2 | 同一数字标题问题的连带影响：本 FB 正文（§5.1.3.2）抽取时，因其后续章节 §5.1.4 / §5.1.4.1 标题以数字开头无法识别为边界，抽取越界并入了 `3964R` 的 VAR 区，致使比对出现"3964R 的变量未在本文档"。本文档 VAR / 错误码已逐字核对 PDF §5.1.3.2 + §7.3 与 InfoSys。 |
| `KL6Configuration` | 1（MINOR） | 描述表中 "7 or 8" 一行被 `extract_section` 误判为章节标题"7"，导致正文在 VAR_OUTPUT 之前被截断，比对出现"`Done`/`Busy`/`Error`/`ErrorID` 多于 PDF"。这四个输出确为 PDF §5.1.2.2 所列，本文档已逐字保留。 |

> 以上三项均为 `extract_section.py`（共享工具，本作业禁止修改）对"数字开头的章节标题"和"描述文本中形如『N or M』的行"的解析局限，与文档内容正确性无关。三篇文档的 VAR 区、默认值、错误码均已 PDF + InfoSys 双源逐字核对。

## 参考资料

- **PDF**：[TF6340_TC3_Serial_Communication_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TF6340_TC3_Serial_Communication_EN.pdf)（v1.8.1，2026-03-25）
- **InfoSys 根**：https://infosys.beckhoff.com/content/1033/tf6340_tc3_serial_communication/index.html
- **产品页**：https://www.beckhoff.com/tf6340
