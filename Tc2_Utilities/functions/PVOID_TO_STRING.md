# PVOID_TO_STRING

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35103755.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_PVOID_TO_STRING.xml`](../examples/P_Demo_PVOID_TO_STRING.xml) |

---

## 1. 功能简述

把 PVOID 指针值转换为 hex 字符串（带 `16#` 前缀）；位宽随平台（32 位系统 8 位 hex / 64 位 16 位 hex）。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    in : PVOID;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `PVOID` | — | 要转换的指针变量。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `T_MaxString` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

函数无状态、立即返回。算法：把 PVOID 的值按平台地址位宽格式化为 hex 字符串，前面加 IEC 风格 `'16#'` 前缀。32 位平台（如老 BC、某些 ARM IPC）输出 `'16#XXXXXXXX'`（共 11 字符）；64 位平台（典型 CX5xxx / CX7xxx / CX9xxx 主流 IPC）输出 `'16#XXXXXXXXXXXXXXXX'`（共 19 字符）。**主要用于诊断 / 日志**——把指针值打印出来便于排查内存布局问题、与 ADS Server 报错信息中的地址对照。空指针（PVOID = 0）返回 `'16#00000000'`（32 位）或 `'16#0000000000000000'`（64 位）——这是合法显示，不是错误。

## 4. 错误码 / 返回值

返回 `T_MaxString`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **位宽随平台**——同一份 PLC 代码在 32 位 / 64 位 CX 上输出长度不同；解析端要兼容。
- **`16#` 前缀**——是 IEC 61131-3 的 hex 字面量风格；解析回时要去前缀。
- **反向 `STRING_TO_PVOID`**：接受 `16#` / `8#` / `2#` / 十进制等多种格式。
- **指针打印用于诊断**——不要用作业务逻辑的 ID（值依赖加载地址，下次启动可能变）。
- 返回类型 `T_MaxString` 充裕；实际只用 11 或 19 字符。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_PVOID_TO_STRING.xml`](../examples/P_Demo_PVOID_TO_STRING.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：排查内存泄漏：把疑似无效指针的值 dump 到日志，对比已知地址区间。
- **价值**：替代手写 hex 格式化 + 平台 if 分支；本函数自动按位宽适应。
- **替代方案对比**：`STRING_TO_PVOID`：反向；`DWORD_TO_HEXSTR`：仅 32 位场景。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.62 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35103755.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
