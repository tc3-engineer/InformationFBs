# ARG_TO_CSVFIELD

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35071499.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_ARG_TO_CSVFIELD.TcPOU`](../examples/P_Demo_ARG_TO_CSVFIELD.TcPOU) |

---

## 1. 功能简述

把任意 PLC 变量（用 `T_Arg` 包装）的值转为 **CSV 数据字段**写入一个 `BYTE` 缓冲区。源串中单引号 `'` 自动转义为双引号 `"`；`bQM = TRUE` 时再在外层包一对双引号。

与 `STRING_TO_CSVFIELD` 的关键差别：本函数接受 `T_Arg` 包装的**任意类型 + 二进制数据**（含 `\x00` 字节），后者只能处理纯 ASCII `STRING`。通常配合 `FB_CSVMemBufferWriter` 在 PLC 内存里拼整张 CSV 表再一次性写文件。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    in       : T_Arg;
    bQM      : BOOL;
    pOutput  : POINTER TO BYTE;
    cbOutput : UDINT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `T_Arg` | — | 待转换的 PLC 源变量；用 `F_BOOL(...)`/`F_DINT(...)`/`F_STRING(...)`/`F_BIGTYPE(...)` 等辅助函数把任意类型包装为 `T_Arg`。 |
| `bQM` | `BOOL` | — | `TRUE` 时给结果字段加外层双引号（QM = Quotation Marks）；`FALSE` 时不加。 |
| `pOutput` | `POINTER TO BYTE` | — | 输出缓冲区起始地址，用 `ADR(field1)` 取得。结果数据写入该缓冲。 |
| `cbOutput` | `UDINT` | — | 输出缓冲区可用字节数，用 `SIZEOF(field1)` 取得。调用方须保证容量足够。 |

### VAR_IN_OUT

无。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `UDINT` | 成功时返回写入缓冲区的字节数；转换出错或数据缺失时返回 `0`。 |

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

调用即返回，无状态。函数读取 `T_Arg` 携带的类型信息和数据指针，把值序列化为 CSV 标准的字段表示：单引号 → 双双引号、可选地加外层 `"`；写入 `pOutput` 指向的字节缓冲，至多写 `cbOutput` 字节。返回实际写入的字节数。

**`bQM` 用法**：CSV 标准里含分隔符（逗号/分号）或换行的字段必须用 `"` 包围；纯字母数字字段可省 `"`。`bQM = TRUE` 适合所有字段统一包围。

**错误返回 0** 的常见原因：缓冲区太小（`cbOutput` 不够）、`T_Arg` 类型无效、`pOutput = 0` 等。

## 4. 错误码 / 返回值

返回 `UDINT`。`> 0` = 写入字节数（成功），`= 0` = 出错或数据缺失。无 `bError` / 错误码 enum。

（注：本函数无 `HRESULT` / 详细错误码——⚠️ 若调用返回 0 而排查不到原因，需用调试器单步进入。）

## 5. 使用注意 / 常见坑

- **不要忘 `T_Arg` 包装**：所有类型必须先用 `F_BOOL(x)` / `F_DINT(x)` / `F_STRING(s)` / `F_BIGTYPE(ADR(buf), SIZEOF(buf))` 等转为 `T_Arg`。直接传裸变量编译报错。
- **缓冲区必须足够大**：经验值字段数据长度 × 2 + 4（双引号转义会膨胀）。CSV 字段含很多 `'` 字符时膨胀更明显。
- **返回 0 是错误**：业务侧必须 `IF nWritten > 0 THEN ...`，不能假设永远成功。
- **优于 STRING_TO_CSVFIELD**：能处理含 `\x00` 二进制字节的源（例：`F_BIGTYPE(ADR(binData), SIZEOF(binData))`）。
- **配套 FB_CSVMemBufferWriter**：本函数只产单字段；整张表组装由 FB 完成。
- **`bQM = TRUE` 推荐**：除非确认字段绝不含分隔符 / 换行，否则统一加引号最稳。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_ARG_TO_CSVFIELD.TcPOU`](../examples/P_Demo_ARG_TO_CSVFIELD.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_ARG_TO_CSVFIELD
VAR
    lrTemperatureC : LREAL := 23.7;          // 一条数据：温度
    abFieldBuf     : ARRAY[0..63] OF BYTE;    // 输出缓冲
    nBytesWritten  : UDINT;                   // 实际写入字节数
END_VAR

// 单行调用：把温度值转为带引号的 CSV 字段
nBytesWritten := ARG_TO_CSVFIELD(
    in       := F_LREAL(lrTemperatureC),
    bQM      := TRUE,
    pOutput  := ADR(abFieldBuf),
    cbOutput := SIZEOF(abFieldBuf)
);

```

## 7. 业务场景与实际价值

- **场景**：PLC 产线数据采集——把过程量（温度 REAL、计数 UDINT、操作员姓名 STRING、配方二进制 buffer）每 5 秒打一条 CSV 记录写本地 SD 卡，MES 后续拉取。
- **价值**：避免业务代码自己处理 CSV 字段的引号转义 / 分隔符 / 二进制传输等繁琐细节；本函数一行搞定一字段。
- **替代方案对比**：
  - 手写 `CONCAT("\"", STR(x), "\"")`：5-10 行，转义易错（`'"'` 出现两次时易少写一次）
  - `STRING_TO_CSVFIELD`：不能处理含 0x00 的二进制
  - **本函数**：双类型（含二进制）+ 标准 CSV 输出 + 缓冲长度返回

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.12 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35071499.html
- **相关函数**：`STRING_TO_CSVFIELD`（纯字符串简化版）、`CSVFIELD_TO_ARG` / `CSVFIELD_TO_STRING`（反向解析）、`FB_CSVMemBufferWriter`（整表组装）、`F_BOOL` / `F_DINT` / `F_STRING` / `F_BIGTYPE`（T_Arg 包装）
