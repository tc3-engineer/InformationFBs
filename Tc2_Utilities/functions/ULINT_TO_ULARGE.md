# ULINT_TO_ULARGE

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934159243.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_ULINT_TO_ULARGE.TcPOU`](../examples/P_Demo_ULINT_TO_ULARGE.TcPOU) |

---

## 1. 功能简述

把 TwinCAT 3 原生 `ULINT`（64 位）转换为 TwinCAT 2 旧式 `T_ULARGE_INTEGER`（结构体）；兼容老代码所需。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    in : ULINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `ULINT` | — | TwinCAT 3 原生无符号 64 位整数。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `T_ULARGE_INTEGER` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

函数无状态、立即返回。算法：把 `ULINT`（TwinCAT 3 原生 64 位无符号整数标量类型）拆分为高 32 位 + 低 32 位，分别写入返回的 `T_ULARGE_INTEGER` 结构体的 `HighPart` 与 `LowPart` 字段（这是 TwinCAT 2 时代用 12 字节结构体表示 64 位整数的传统写法）。**值范围相同**——两种表示都覆盖 0..2^64-1；只是底层布局不同。**主要用途**：维护从 TwinCAT 2 移植到 TwinCAT 3 的旧代码——老 API（如某些 ADS 函数、`Tc2_Utilities` 的 `UInt64Add64` 等大整数运算）接受 `T_ULARGE_INTEGER` 参数；新代码用 ULINT 更直观但调用老 API 必须先用本函数桥接。反向函数 `ULARGE_TO_ULINT` 把结构体转回标量。

## 4. 错误码 / 返回值

返回 `T_ULARGE_INTEGER`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **仅用于兼容旧代码**——新代码用 `ULINT` 即可，不需要本函数。
- **值范围相同**（均 0..2^64-1）；只是表示方式不同。
- **反向 `ULARGE_TO_ULINT`** 把 `T_ULARGE_INTEGER` 转回 `ULINT`。
- **`T_ULARGE_INTEGER` 是 8 字节 64 位无符号结构体**（HighPart : DWORD + LowPart : DWORD，各 4 字节，合计 8 字节），与 `ULINT` 同样的 64 位值域，只是表示方式不同（结构体 vs 原生标量）。整个 `Tc2_Utilities` 64 位无符号 API 族（`UInt64Add64` 等）都以这一布局为前提。
- **算术运算请用 `ULINT`**（原生 64 位编译器优化）；`T_ULARGE_INTEGER` 上的 `UInt64Add64` 等是软件模拟，慢。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ULINT_TO_ULARGE.TcPOU`](../examples/P_Demo_ULINT_TO_ULARGE.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：把 TwinCAT 3 的高精度计数器（`ULINT`）传给老 BC2000 接口（接受 `T_ULARGE_INTEGER`）。
- **价值**：替代手写 SHR / AND / 拆位的 5 行代码。
- **替代方案对比**：`ULARGE_TO_ULINT`：反向；直接传 ULINT 给新代码：无需转换。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.71 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934159243.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
