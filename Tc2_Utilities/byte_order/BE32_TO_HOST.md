# BE32_TO_HOST

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Byte order converting functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35321099.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_BE32_TO_HOST.xml`](../examples/P_Demo_BE32_TO_HOST.xml) |

---

## 1. 功能简述

把一个 32 位"网络字节序"（大端，Big-Endian）整数转换为"主机字节序"。TwinCAT 运行的 x86 / x64 / ARM 平台主机字节序均为小端（Little-Endian），因此函数语义等价于把 4 字节按 `[B0 B1 B2 B3]` 反转成 `[B3 B2 B1 B0]`。

典型使用场景：以太网协议帧解码（Modbus TCP 多寄存器组合、EtherNet/IP、Profinet IO 大端 32 位整数 / 浮点）、解析由 C/C++ 上位机按 `htonl()` 打包的二进制结构。返回类型与输入类型相同（`DWORD`），是否再做有符号 / `REAL` 类型转换由调用方决定。

## 2. 接口定义

### 函数声明

```iecst
FUNCTION BE32_TO_HOST : DWORD
VAR_INPUT
    in : DWORD;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `DWORD` | 待转换的 32 位整数（按大端字节序解读） |

### 返回值

`DWORD` —— 在主机字节序下解读时表示的同一数值。

### VAR_IN_OUT

无。

## 3. 行为说明

把输入双字的 4 个字节完整反转：`16#B3B2B1B0`（主机端原始字节）变为 `16#B0B1B2B3`（按大端协议端应有的数值表示）。对应 C 语言常见的 `ntohl()`。

举例：网络上收到字节流 `0x12 0x34 0x56 0x78`，按大端解读代表 `0x12345678`；这 4 字节直接复制到 `DWORD` 后在小端 PLC 里被读作 `0x78563412`。调用 `BE32_TO_HOST(16#78563412) = 16#12345678` 即可恢复协议端打包前的原始数值。

本函数是**纯计算函数**（FUNCTION）：无内部状态、无副作用、可重入、可在中断 / 任意优先级任务中调用。对同一输入多次调用结果完全一致。

与 `HOST_TO_BE32` 互为逆操作。在小端主机上两个函数的位运算实现完全相同（都是 4 字节交换），但代码语义不同——`BE32_TO_HOST` 用于"读入大端"，`HOST_TO_BE32` 用于"写出大端"。在协议层代码中按方向选择正确函数有助于可读性，也便于将来移植到大端平台（在大端平台两个函数都退化为恒等映射）。

## 4. 错误码 / 返回值

返回类型 `DWORD`，无错误码、无 HRESULT。任意 32 位输入都有合法返回结果。

## 5. 使用注意 / 常见坑

- **Modbus 32 位寄存器组合顺序**：Modbus 协议本身只定义 16 位寄存器单位，跨寄存器组成 32 位整数时设备厂商可能用 "high-word-first"（最常见）或 "low-word-first"（少数厂商）。本函数处理的是 byte 内 endian，**word 内 endian** 需要先用 `WORD` 数组组合时自行选好顺序。（工程经验补充）
- **从 `REAL` 类型转换**：`REAL` 与 `DWORD` 位宽相同，可通过指针重新解释（`pDword^ := pReal^`）后再调用本函数完成大端浮点转换；不能直接传 `REAL` 给本 FC。
- **避免对累计计数器频繁调用**：函数本身极快（数条机器指令），但放在每周期都跑的逻辑里仍是 PLC 周期负担；在协议解码器里仅对刚收到的报文调用一次。
- **签名扩展坑**：`DWORD_TO_DINT` 是位级再解释、不会做符号扩展；要把转换后的大端 32 位有符号数恢复为 `DINT` 直接 `DWORD_TO_DINT` 即可。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_BE32_TO_HOST.xml`](../examples/P_Demo_BE32_TO_HOST.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_BE32_TO_HOST
VAR
    dwModbusValue : DWORD := 16#78563412;  // 大端协议帧拷贝到 DWORD 后的小端解读
    dwHostValue   : DWORD;                  // 期望 16#12345678
    bRun          : BOOL;
END_VAR

IF bRun THEN
    dwHostValue := BE32_TO_HOST(dwModbusValue);
    bRun := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：PLC 作为 Modbus TCP / EtherNet/IP / 自定义 TCP 协议客户端，从 IT 系统读取 32 位整数或 IEEE 754 浮点数据。这些协议都规定大端字节序，但 TwinCAT 主机是小端，直接拷贝会得到字节顺序颠倒的乱码。
- **价值**：1 行调用完成 4 字节反转，比手写 `(d SHL 24) OR (d SHR 24) OR ((d AND 16#0000FF00) SHL 8) OR ((d AND 16#00FF0000) SHR 8)` 更短、更可读、不会出符号扩展和位掩码笔误。代码 review 一眼看出"这里在做字节序处理"。
- **替代方案对比**：手写位运算（容易写错、可读性差）/ 用 `MEMCPY` + 反向索引拷贝（多 1 个临时缓冲区）/ 直接调用 `BE32_TO_HOST`（Beckhoff 官方实现，最简洁）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.3.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35321099.html
- **相关函数**：`HOST_TO_BE32`（反向）、`BE16_TO_HOST` / `BE64_TO_HOST` / `BE128_TO_HOST`（其他位宽）
