# BE16_TO_HOST

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Byte order converting functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35319563.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_BE16_TO_HOST.xml`](../examples/P_Demo_BE16_TO_HOST.xml) |

---

## 1. 功能简述

把一个 16 位"网络字节序"（大端，Big-Endian）整数转换为"主机字节序"（Host Byte Order）。在 TwinCAT 运行的 x86/x64/ARM 平台上主机字节序均为小端（Little-Endian），因此本函数在这些平台上等价于把高低字节交换。

典型使用场景：从 Modbus TCP / Profinet IO / EtherNet/IP 等以太网协议帧里读取 16 位寄存器值，或者解析任何由非 PLC 端按大端约定打包的二进制结构。返回类型与输入类型相同（`WORD`），调用方负责按数据语义再做有符号 / 无符号转换。

## 2. 接口定义

### 函数声明

```iecst
FUNCTION BE16_TO_HOST : WORD
VAR_INPUT
    in : WORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `WORD` | 待转换的 16 位整数，**输入按大端字节序解读** |

### 返回值

`WORD` —— 在主机字节序（小端）下解读时表示的同一数值。

### VAR_IN_OUT

无。

## 3. 行为说明

函数把输入字的高低字节进行交换：低 8 位与高 8 位互换位置。形式化地，对输入 `in = 16#HHLL`（H 表高字节、L 表低字节），返回值是 `16#LLHH`。

举例：网络字节流里收到字节序列 `0x12 0x34`，按大端解读代表数值 `0x1234`；这两个字节直接复制到 `WORD` 后在小端 PLC 里被读成 `0x3412`。要恢复"协议端写入的值 0x1234"，需调用 `BE16_TO_HOST(16#3412) = 16#1234`。

本函数是**纯计算函数**（FUNCTION），调用即返回，无内部状态、无副作用、可重入、可在任意任务上下文调用。对同一输入多次调用结果完全一致。

`BE16_TO_HOST` 与 `HOST_TO_BE16` 互为逆操作；在小端主机上两者的位操作完全相同（都是字节交换），但语义不同：前者用于"读入大端数据"，后者用于"写出大端数据"。代码中按语义选择正确的方向有助于可读性。

## 4. 错误码 / 返回值

返回类型 `WORD`，无错误码、无 HRESULT。任何 16 位输入都有合法返回结果。

## 5. 使用注意 / 常见坑

- **不要用 `BE16_TO_HOST` 转有符号数后再赋值给 `INT`**：先做 `WORD ↔ WORD` 字节交换，再 `WORD_TO_INT` 才不会丢符号位语义。
- **输入直接来自 `MEMCPY` 或指针访问时**：源缓冲区里的字节必须按大端顺序排好；如果上游已经是小端，本函数会反而把字节弄错。（工程经验补充）
- **WORD 与 UINT 在 IEC 61131-3 中位宽相同但语义不同**：本函数声明的是 `WORD`（位串）而非 `UINT`（无符号整数），调用前后可用 `WORD_TO_UINT` 显式转换避免编译器告警。
- **不要做"双重交换"**：错误地对同一数据连续调用两次 `BE16_TO_HOST` 会把字节恢复成原样，看起来"什么都没发生"，实际上是协议端字节序判断出了问题。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_BE16_TO_HOST.xml`](../examples/P_Demo_BE16_TO_HOST.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_BE16_TO_HOST
VAR
    wModbusHoldingReg : WORD := 16#3412;   // 从 Modbus TCP 帧里抓到的大端 16 位值
    wHostReg          : WORD;              // 转换后小端解读结果
    bRun              : BOOL;
END_VAR

IF bRun THEN
    wHostReg := BE16_TO_HOST(wModbusHoldingReg);  // 期望 16#1234
    bRun := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：PLC 作为 Modbus TCP 客户端从远端 RTU 设备读取一组 holding register。Modbus 协议明确规定寄存器值按大端打包，但 TwinCAT 在 x86/x64/ARM 上都是小端运行。直接把以太网帧里的 2 字节拷贝进 `WORD` 会得到字节顺序颠倒的"垃圾数值"。
- **价值**：1 行调用把字节交换语义抽出来，代码可读、可复用、易测试。比起手写 `(in SHL 8) OR (in SHR 8) AND 16#00FF`，避免移位运算符号扩展坑（`WORD` 没问题，`INT` 移位时会带符号），也更容易让 code review 一眼看出"这里在处理字节序"。
- **替代方案对比**：手写位运算（容易出错、可读性差）/ 用 `ROL`/`ROR` 循环移位（取决于编译器是否生成等价代码）/ 调用本函数（语义明确、Beckhoff 官方实现）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.3.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35319563.html
- **相关函数**：`HOST_TO_BE16`（反向）、`BE32_TO_HOST` / `BE64_TO_HOST` / `BE128_TO_HOST`（32/64/128 位版本）
