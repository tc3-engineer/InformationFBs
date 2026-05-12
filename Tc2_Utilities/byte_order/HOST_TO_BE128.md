# HOST_TO_BE128

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Byte order converting functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35318027.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_HOST_TO_BE128.xml`](../examples/P_Demo_HOST_TO_BE128.xml) |

---

## 1. 功能简述

把一个 128 位"主机字节序"整数转换为"网络字节序"（大端，Big-Endian）。在 TwinCAT 的 x86/x64/ARM 平台（均为小端）上，函数语义等价于将 16 个字节完整反转。

典型使用场景：PLC 作为以太网协议服务端，把要写出去的 128 位字段转成大端后再 `MEMCPY` 进发送缓冲区。返回类型与输入类型相同（`T_UHUGE_INTEGER`），调用方负责按数据语义再做有符号 / 浮点类型转换。

## 2. 接口定义

### 函数声明

```iecst
FUNCTION HOST_TO_BE128 : T_UHUGE_INTEGER
VAR_INPUT
    in : T_UHUGE_INTEGER;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `in` | `T_UHUGE_INTEGER` | 待转换的 128 位整数 |

### 返回值

`T_UHUGE_INTEGER` —— 字节序反转后的同值表示。

### VAR_IN_OUT

无。

## 3. 行为说明

调用 `HOST_TO_BE128(in)` 把 `in` 的 16 字节整体反转后返回。例如：要把数值 V 按大端协议写入帧缓冲区，先调用 `HOST_TO_BE128(V)` 拿到字节顺序已被反转的 `T_UHUGE_INTEGER`，再 `MEMCPY` 出去；大端协议接收方读出的就是 V。

本函数是**纯计算函数**（FUNCTION）：无内部状态、无副作用、可重入、可在任意优先级任务中调用。对同一输入多次调用结果完全一致。

与 `BE128_TO_HOST` 互为逆操作。在小端主机上两者的位运算实现完全相同（都是 16 字节交换），但代码语义不同——`HOST_TO_BE128` 表达"打包方向"。按协议方向选择正确函数有助于代码 review 一眼看懂用途，也便于未来移植到大端平台（在大端平台两个函数都退化为恒等映射）。

## 4. 错误码 / 返回值

返回类型 `T_UHUGE_INTEGER`，无错误码、无 HRESULT。任意 128 位输入都有合法返回结果。

## 5. 使用注意 / 常见坑

- **`T_UHUGE_INTEGER` 是 "legacy" 类型**：TwinCAT 早期没有 64/128 位原生类型时引入的结构体类型，新代码推荐使用 `LWORD` / `T_LARGE_INTEGER` 等原生类型版本（同库的 `HOST_TO_BE128`）。
- **不要写"双重反转"**：错误地连续调用两次本函数会把字节恢复成原样，看起来"什么都没发生"——往往是协议端字节序判断出错的征兆。
- **在协议解码器里只对单条报文调用一次**：函数本身极快但仍占用 PLC 周期，避免放在每周期都执行的逻辑里反复调。
- **128 位浮点 / 有符号转换**：先用本函数做字节级反转，再用 `T_UHUGE_INTEGER_TO_REAL` / `_TO_LREAL` 或位重新解释完成；不要把 `LREAL` / `DINT` 直接传给本 FC（类型不匹配）。
- **协议端的 word/dword 内部顺序**：本函数只处理 byte 内 endian。Modbus 跨 16 位寄存器组成 32/64 位整数时设备厂商对 word 顺序约定不同，先确认 word 顺序再调用本 FC。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_HOST_TO_BE128.xml`](../examples/P_Demo_HOST_TO_BE128.xml)
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_HOST_TO_BE128
VAR
    inValue  : T_UHUGE_INTEGER;   // 待转换数据
    outValue : T_UHUGE_INTEGER;   // 字节序反转结果
    bRun : BOOL;
END_VAR

IF bRun THEN
    outValue := HOST_TO_BE128(inValue);
    bRun := FALSE;
END_IF;
```

## 7. 业务场景与实际价值

- **场景**：PLC 作为以太网协议服务端 / Modbus TCP server / OPC UA Pub-Sub publisher，把内部数据按大端字节序发送出去。所有这些协议都规定大端字节序，但 TwinCAT 主机是小端，直接拷贝会得到字节顺序颠倒的乱码。
- **价值**：1 次调用完成 16 字节反转，比手写多次移位 + 位掩码 + 或运算更短、更可读、避免符号扩展和位运算优先级笔误。代码 review 一眼看出"这里在处理协议字节序"，重构时不会被误删。
- **替代方案对比**：手写位运算（容易出错、可读性差）/ 用 `MEMCPY` 配合反向索引拷贝（多一个临时缓冲区，写起来啰嗦）/ 调用本函数（Beckhoff 官方实现，最简洁）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) §4.3.6
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35318027.html
- **相关函数**：`BE128_TO_HOST`（反向）、`HOST_TO_BE16` / `HOST_TO_BE32` / `HOST_TO_BE64`（其他位宽版本）
