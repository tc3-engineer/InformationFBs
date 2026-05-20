# BYTEARR_TO_MAXSTRING

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35073035.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_BYTEARR_TO_MAXSTRING.xml`](../examples/P_Demo_BYTEARR_TO_MAXSTRING.xml) |

---

## 1. 功能简述

把一个含 ASCII 编码的字节数组拼接成 `T_MaxString`（即 `STRING(255)`）字符串。函数遍历 `in` 数组的每个字节，把字节值当作 ASCII 字符（`16#48` → `'H'`，`16#69` → `'i'`），直到遇到 `16#00` 结束符或抵达数组末端为止。

`MAX_STRING_LENGTH` 是 `Tc2_Utilities` 的常量（默认 255），所以数组维度固定为 `[0..255]`，覆盖一个完整的 `STRING(255)`。反向操作由 `MAXSTRING_TO_BYTEARR` 完成。

## 2. 接口定义

### VAR_INPUT

```iecst
FUNCTION BYTEARR_TO_MAXSTRING : T_MaxString
VAR_INPUT
    in : ARRAY[0..MAX_STRING_LENGTH] OF BYTE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `in` | `ARRAY[0..MAX_STRING_LENGTH] OF BYTE` | — | 待转换的字节数组（`MAX_STRING_LENGTH` 默认 255）。数组每个字节解释为一个 ASCII 字符；`16#00` 视为字符串结束。 |

### VAR_IN_OUT

无。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `T_MaxString` | 拼接得到的字符串（`STRING(255)`），不含末尾 `16#00`。 |

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

调用即返回，无状态。函数把 `in` 中的字节序列从 `in[0]` 开始按 ASCII 解释，遇到第一个 `16#00` 字节即停止拼接（不把该字节计入返回串），返回值长度等于截止前的非零字节数。

边界行为：若 `in[0]` 就是 `16#00`，返回空串；若数组前 255 字节全部非零，则返回 255 字符的字符串（`T_MaxString` 的最大容量）。函数本身不做字符校验，控制字符（如 `16#0D`、`16#0A`）原样落到字符串中，调用方在写日志或 CSV 时需自行考虑这些不可打印字节带来的影响。

典型用途：以 ADS 或 EtherCAT 邮箱读到的固定长度字节缓冲（设备序列号、MAC 字符串、ASCII 应答帧）转成 PLC 字符串，便于后续 `FIND` / `MID` / `CONCAT` 处理。

## 4. 错误码 / 返回值

无错误码。返回 `T_MaxString`，最大 255 个 ASCII 字符。无效输入（数组全 0）返回空串。

## 5. 使用注意 / 常见坑

- **找不到 0 结束符就拼满 255 字节**：来源是二进制 buffer（不是 C 字符串）时，结果会被截断到 255；前置务必清零或显式追加 `ar[n] := 16#00`。
- **非可打印字符不会被过滤**：含 `16#0D` / `16#0A` / `16#1B` 的协议帧转成字符串后无法直接打印到日志，按需 `REPLACE` 替换。
- **大小写不变换**：函数只搬字节，不做 ASCII 大小写处理。需要统一大小写时再调 `F_ToUCase` / `F_ToLCase`。
- **入参是值传递的整个数组**：每次调用复制 256 字节，循环里高频调用会占用扫描时间；如能用指针更好。
- **`MAX_STRING_LENGTH` 不能改**：它是 `Tc2_Utilities` 内部常量；自定义长度的字节缓冲先 `MEMCPY` 到 256 字节数组再调本函数（工程经验补充）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_BYTEARR_TO_MAXSTRING.xml`](../examples/P_Demo_BYTEARR_TO_MAXSTRING.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_BYTEARR_TO_MAXSTRING
VAR
    arBuf      : ARRAY[0..MAX_STRING_LENGTH] OF BYTE;   // 来自 EL6022 串口模块的 RX buffer 镜像
    sDeviceTag : T_MaxString;                            // 拼成可打印 PLC 字符串
END_VAR

// 模拟串口 buffer 里收到 "Hi"（0x48 0x69）后被 0x00 结束
arBuf[0] := 16#48;
arBuf[1] := 16#69;
arBuf[2] := 16#00;

sDeviceTag := BYTEARR_TO_MAXSTRING(arBuf);
```

## 7. 业务场景与实际价值

- **场景**：从 EL6022 / EL6001 串口模块或 ADS 读到的固定 256 字节 RX 缓冲，需要解析其中以 0x00 结束的 ASCII 应答（设备 ID、固件版本字符串）。
- **价值**：避免手写 `WHILE` 循环逐字节拼接；一行调用拿到 PLC `STRING` 后立即能 `FIND` / `MID` / 日志输出。
- **替代方案对比**：
  - 手写循环：10~15 行代码，需自己处理 0x00 终止符与数组越界
  - `MEMCPY` 到 `STRING` 变量：要先确定真实长度，多一次 SIZEOF 计算
  - 本函数：单调用、自动处理终止符、返回类型直接是 `T_MaxString`

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.19 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35073035.html
- **相关函数**：`MAXSTRING_TO_BYTEARR`（反向操作）、`HEXSTR_TO_DATA`（带空格的 hex 串 → 字节）、`DATA_TO_HEXSTR`（字节 → hex 串）
