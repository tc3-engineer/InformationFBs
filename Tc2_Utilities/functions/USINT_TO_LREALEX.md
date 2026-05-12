# USINT_TO_LREALEX

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/2213035787.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_USINT_TO_LREALEX.xml`](../examples/P_Demo_USINT_TO_LREALEX.xml) |

---

## 1. 功能简述

无符号整数 → 正 `LREAL` 浮点的**遗留兼容**转换。

TwinCAT 2 在 Arm® 平台上不支持无符号整数到 `LREAL` 的转换，最高位为 1 的无符号数会被当作负数误转。PDF 明确指出：**TwinCAT 3 已默认正确转换 `USINT` → `LREAL` 为正数（隐式与显式都对），所以本函数在 TwinCAT 3 里其实没必要使用**。`USINT_TO_LREALEX` 存在的唯一目的，是为从 TwinCAT 2 项目无修改地编译到 TwinCAT 3 时保留原有源码兼容。

内部实现：对 `USINT` 输入按无符号语义解读后赋给 `LREAL` 输出，结果恒非负，无 Warning 1105。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    in : USINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `USINT` | — | 待转换的 `USINT` 无符号 8 位整数（其值会被当作非负数处理）。 |

### VAR_IN_OUT

无。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `LREAL` | 将 `in` 作为无符号整数解释后得到的非负 `LREAL` 浮点值（范围 0 到 2^8-1）。 |

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

调用即返回，无内部状态。在 TwinCAT 3 上行为等同于直接的 `LREAL_VAR := USINT_VAR`：把 `in` 作为 8 位无符号整数解释，转为对应的非负 `LREAL` 浮点值（如 `USINT := 16#FFFFFFFF` 转 `LREAL` 得到 `+4294967295`）。

在 TwinCAT 2 Arm® 平台上则才有真正的差异：标准转换或赋值会按有符号语义处理最高位、产生 **Warning 1105** 并输出负值，而 `USINT_TO_LREALEX` 不会触发警告并产生正确的正值。这也是 PDF 给出的对照表（`fLreal := ...` 多种写法在 Tc2.x ARM / X86 与 Tc3.x 上结果对比）的核心内容。

## 4. 错误码 / 返回值

返回 `LREAL`，无错误码、无 `bError`、无 `HRESULT`。对任意 `USINT` 输入恒成功并返回对应的非负浮点值。

## 5. 使用注意 / 常见坑

- **TwinCAT 3 不需要它**：PDF 第一段就说「this function can be dispensed with」。新项目应直接写 `lr := i;` 让编译器隐式转换；保留此调用只是出于历史项目可移植性。
- **只服务无符号语义**：输入是 `USINT` 无符号类型；如果业务变量本身是 `INT` / `DINT` 有符号类型，本函数无意义，应改用标准 `INT_TO_LREAL` / `DINT_TO_LREAL`。
- **看 PDF 对照表理解动机**：PDF 第 4 节给出了 Tc2 ARM / Tc2 X86 / Tc3 三平台下 7 种写法的结果对比；要还原「为什么有这函数」必须看这张表。否则会误以为本函数有额外功能。
- **没有 LREALEX 反向函数**：要把 `LREAL` 回 `USINT` 走标准 `LREAL_TO_USINT`；本函数族只覆盖单向 `→ LREAL`。
- **保留它的代价就是一行函数调用开销**（编译后实际多半被 inline）；如果项目已彻底升级到 TwinCAT 3，可批量替换为直接赋值简化代码（工程经验补充）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_USINT_TO_LREALEX.xml`](../examples/P_Demo_USINT_TO_LREALEX.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_USINT_TO_LREALEX
VAR
    nLegacyValue : USINT := 16#FF;   // 最高位为 1，老 Tc2 ARM 易被误判为负
    lrConverted  : LREAL;                  // 期望为正数 2^8-1
END_VAR

// 单行调用：从 Tc2 项目继承的代码，TwinCAT 3 上仍可正确编译并运行
lrConverted := USINT_TO_LREALEX(nLegacyValue);

```

## 7. 业务场景与实际价值

- **场景**：从 TwinCAT 2 Arm®（BCxx / BX9xx 等总线终端控制器）项目移植到 TwinCAT 3 IPC / CX 平台时，原代码中可能含 `lr := USINT_TO_LREALEX(nVal);` 这类调用。本函数让该行**在 TwinCAT 3 上仍可编译通过**且行为正确。
- **价值**：避免移植时把每个 `USINT_TO_LREALEX` 调用都改成直接赋值——保留它即可一键升级，回归测试也更稳。
- **替代方案对比**：
  - 直接赋值 `lr := nVal;`：在 TwinCAT 3 上正确，但要修改源码
  - `USINT_TO_LREAL(nVal)`：与直接赋值等效，仍要修改源码
  - **本函数**：源码零修改完成 Tc2 → Tc3 移植，**仅推荐这一场景使用**

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.72 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/2213035787.html
- **相关函数**：`BYTE_TO_LREALEX` / `WORD_TO_LREALEX` / `DWORD_TO_LREALEX` / `UDINT_TO_LREALEX` / `UINT_TO_LREALEX` / `USINT_TO_LREALEX`
