# F_SwapRealEx

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35070091.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_F_SwapRealEx.xml`](../examples/P_Demo_F_SwapRealEx.xml) |

---

## 1. 功能简述

把一个 `REAL`（32 位单精度浮点）变量的高/低 16 位字（Hi-word、Lo-word）对换。用于 PC/CX（x86/x64/Arm）与 BC/BX 总线终端控制器（BC2000/BC3100/BC9000 等）通过 ADS 交换 REAL 数据时的字节序对齐——BC 系列控制器的内存中 REAL 字段以"Hi-word 在前"存放，而 PC/CX 系列是"Lo-word 在前"；如果不交换，两端读到的 REAL 数值会完全不同（甚至变成 NaN / 极端值）。

在线 / 仿真模式由开发环境自动处理这个差异；但通过 ADS-DLL / AdsOcx / VB 客户端 / Scope View 读 BC 端 REAL 时差异暴露，需要手动调本函数。

## 2. 接口定义

### VAR_INPUT

无（数据通过 `VAR_IN_OUT` 原地交换）。

### VAR_IN_OUT

```iecst
VAR_IN_OUT
    fVal : REAL;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `fVal` | `REAL` | 待交换的 REAL 值；原地修改（输入也是输出）。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 交换执行成功；`FALSE` = 执行时发生错误（按 PDF，少见，例如内部异常）。 |

### VAR_OUTPUT

无。

## 3. 行为说明

函数原地修改 `fVal`：把它的 4 字节内存表示拆成两个 16 位 word，再把 Hi-word 与 Lo-word 对换。例如内存 `34 12 CF BE`（小端展示）经函数变为 `CF BE 34 12`，对应的 IEEE 754 解释会变成完全不同的浮点值。

典型用法：
- **从 BC 读 REAL 到 PC**：读取后立即 `F_SwapRealEx(rValueFromBc)`，得到 PC 端正确数值。
- **从 PC 写 REAL 到 BC**：写出前先 `F_SwapRealEx(rValueToBc)`，得到 BC 期望的字节序。
- **TwinCAT Scope View 记录 BC 数据**：在线读取后用本函数转换，否则录到的波形是"乱码"REAL。

注意"双重交换"等于"不交换"：两端各调一次会回到原值；某些链路（如本地仿真）已自动转换，再手动调反而错。判断需不需要调的标准：**只要数据出/入 BC/BX 系列控制器、且不是在线开发模式下，就调；其他情况不调**。

新工程几乎都用 EtherCAT 总线 + IPC/CX 控制器，不再用 BC/BX 系列，所以本函数主要在维护老项目时用到。

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| `TRUE` | 交换成功 |
| `FALSE` | 内部错误（PDF 仅说"Error during function execution"，未列具体场景） |

## 5. 使用注意 / 常见坑

- **只在 BC/BX 系列控制器交换时调用**：IPC ↔ CX 之间字节序一致，调了反而搞错。
- **在线 / 仿真自动处理**：本地仿真不必调；通过外部 ADS 客户端（VB、AdsOcx、Scope）读 BC REAL 才需要。
- **REAL 数组要逐个调**：本函数只处理一个 REAL；数组用 FOR 循环。
- **`LREAL`（64 位）需要 `F_SwapLRealEx`**：本函数是 32 位 REAL 专用；同库另有 LREAL 版（工程经验补充）。
- **InfoSys 未单独收录**：与 PDF 不一致是 Beckhoff 文档维护问题；功能本身在 TC3 运行时支持。
- **新工程几乎用不上**：BC/BX 控制器停产，EtherCAT + IPC 不需要 swap；本函数主要供维护老项目（工程经验补充）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_SwapRealEx.xml`](../examples/P_Demo_F_SwapRealEx.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_SwapRealEx
VAR
    rValueFromBc : REAL := 1.5;
    bOk          : BOOL;
END_VAR

bOk := F_SwapRealEx(fVal := rValueFromBc);
// rValueFromBc 现在是按 PC 字节序解读的结果（与原 1.5 完全不同）
```

## 7. 业务场景与实际价值

- **场景**：老工程改造——把现场 BC9000 控制器的运行数据通过 ADS 上传到中心 CX 控制器做 SCADA 显示；REAL 数据（温度、扭矩）需要在 CX 端 swap 后才能正确解释。
- **价值**：替代手写 `MEMCPY` + WORD 交换的 5 行代码；语义清晰、Beckhoff 验证。
- **替代方案对比**：
  - 手写 WORD 交换：5 行，易在指针类型转换写错
  - 在 BC 端调整数据格式：BC 上不开发，做不到
  - 本函数：单调用、与 LREAL 版（`F_SwapLRealEx`）成套

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.41 节
- **InfoSys topic**：未单独收录函数页（⚠️ not-on-infosys）；BC/BX 互通示例参见 https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35409035.html
- **相关函数**：`F_SwapLRealEx`（64 位 LREAL 版）、`F_SwapWordEx` 等其它字节序工具
