# DATA_TO_HEXSTR

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35077643.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_DATA_TO_HEXSTR.TcPOU`](../examples/P_Demo_DATA_TO_HEXSTR.TcPOU) |

---

## 1. 功能简述

把二进制数据（≤ 85 字节）转为大/小写十六进制字符串；超长加 `.`；参数错误返回空串。`DATA_TO_HEXSTR2` 是无 85 限制的新版。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pData   : POINTER TO BYTE;
    cbData  : UDINT(0..85);
    bLoCase : BOOL := FALSE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `pData` | `POINTER TO BYTE` | — | 源数据起始地址；`ADR(buf)`。 |
| `cbData` | `UDINT(0..85)` | — | 源字节数；**上限 85 字节**（PDF 明确）。超出会截断 + 加 `.`。 |
| `bLoCase` | `BOOL` | FALSE | `TRUE` = 小写 `abcdef`；`FALSE` = 大写 `ABCDEF`。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `T_MaxString` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `T_MaxString` | 空格分隔的两位十六进制字符串。如 `'34 12 CF BE'`。超长截断追加 `'.'`，无效参数返回 `''`。 |

### VAR_OUTPUT

无。

## 3. 行为说明

函数无状态、立即返回。算法：逐字节读 `pData[0..cbData-1]`，按 `bLoCase` 选择字符集格式化为两个 hex 字符，字节间用单空格分隔。**`cbData` 上限 85 字节是函数声明的范围 `UDINT(0..85)` 强制约束**——这是历史限制（输出 STRING 长度限制：每字节 3 字符 × 85 + 容错 = 256+）。超长（cbData > 85）会截断、在结果末尾添 `.` 表示截断。**参数错误**（`pData = 0` 或 `cbData = 0`）返回空串。生产新代码**强烈建议改用 `DATA_TO_HEXSTR2`**：显式 nDstSize、无 85 字节上限。

## 4. 错误码 / 返回值

返回 `T_MaxString`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **上限 85 字节是硬约束**——`UDINT(0..85)` 是声明级范围，超出会编译错或运行时被钳位。
- `pData = 0` 或 `cbData = 0` 返回空串——业务侧靠 `LEN(s) > 0` 判合法。
- **生产新代码用 `DATA_TO_HEXSTR2`**——后者支持任意长度 + 显式 `nDstSize`。
- 默认大写 hex（`bLoCase = FALSE`）；MD5/SHA 习惯小写传 TRUE。
- **反向函数 `HEXSTR_TO_DATA`**（PDF 4.49）。
- 结构体打印：`DATA_TO_HEXSTR(ADR(stRec), SIZEOF(stRec), FALSE)` 含 padding 字节也会被打印。
- 字节分隔是单空格——这与 `DATA_TO_HEXSTR2` 保持一致。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_DATA_TO_HEXSTR.TcPOU`](../examples/P_Demo_DATA_TO_HEXSTR.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：串口 / RS485 协议诊断：把收到的 32 字节命令帧 dump 为 hex 串写入日志。
- **价值**：比手写循环 + `HEXASCNIBBLE_TO_BYTE` 拼接简洁——但 85 字节上限严重——大数据用 `DATA_TO_HEXSTR2`。
- **替代方案对比**：`DATA_TO_HEXSTR2`：无 85 限制 + 显式 `nDstSize`；手写循环：可控但繁琐。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.22 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35077643.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
