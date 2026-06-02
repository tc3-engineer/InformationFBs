# F_SwapRealEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35119115.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_SwapRealEx.TcPOU`](../examples/P_Demo_F_SwapRealEx.TcPOU) |

---

## 1. 功能简述

把 REAL 的 Hi-Lo word 交换字节序——用于 BC2000/BC3100/BC9000 等总线终端控制器（基于 ARM 大端）与 IPC / 嵌入式 PC（x86/x64 小端）之间通信时的浮点数转换。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_IN_OUT
    fVal : REAL;
END_VAR
```


### VAR_IN_OUT

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `fVal` | `REAL` | 要交换字节序的 REAL 变量（修改实参）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出，部分参数同时被 VAR_IN_OUT 修改）。

## 3. 行为说明

函数立即返回，**直接修改 `fVal` 实参的内存表示**（VAR_IN_OUT 语义）。算法：把 REAL（4 字节）的高 2 字节与低 2 字节交换（不是单字节翻转）——`[B0 B1 B2 B3]` 变为 `[B2 B3 B0 B1]`。这是因为 Beckhoff 老总线终端 BC2000/BC3100/BC9000 内部用 16 位字为单位存储 REAL，高低字顺序与 x86 IPC 相反。**调用前后业务必须知道当前数据来源是哪种格式**——只在跨平台 ADS 通信场景使用；同平台数据不要调用，否则会破坏 REAL 值。返回 `TRUE` 表示成功；`FALSE` 表示函数执行错误（PDF 未明示触发条件）。

## 4. 错误码 / 返回值

返回 `BOOL`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **同平台数据不要调用**——会破坏 REAL 值。仅在 BC/BX <-> PC/CX 通信时使用。
- **修改实参**——VAR_IN_OUT 直接改 `fVal`；不要在不影响业务的中间变量上用。
- **Hi-Lo word 交换不是字节翻转**——`[B0 B1 B2 B3]` → `[B2 B3 B0 B1]`，不是 `[B3 B2 B1 B0]`。
- **目标平台已用 little-endian 的 REAL** 标准格式时：BX 控制器是 big-endian / hi-lo-word 倒置；IPC 是 little-endian / 标准；本函数仅处理这两者的差异。
- **只针对 REAL（32 位）**；LREAL（64 位）需要不同处理，本函数不支持。
- **`F_SwapReal`（旧版无 Ex 后缀）也存在**，参数语义稍异，参考 PDF 区分。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_SwapRealEx.TcPOU`](../examples/P_Demo_F_SwapRealEx.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：老产线 CX5020 IPC 通过 ADS 从 BC9000 总线终端读取 REAL 类型的温度变量；从网络收到的字节流必须经 `F_SwapRealEx` 才能正确解读。
- **价值**：替代手写 `MEMCPY` + 字节位运算交换；本函数对调用方透明。
- **替代方案对比**：新设备直接用 EtherCAT / EAP（兼容字节序）；旧 BC/BX 必须调本函数。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.41 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35119115.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
