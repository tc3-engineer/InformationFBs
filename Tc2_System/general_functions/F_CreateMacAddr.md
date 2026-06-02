# F_CreateMacAddr

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `General functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/20034182027.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_CreateMacAddr.TcPOU`](../examples/P_Demo_F_CreateMacAddr.TcPOU) |

---

## 1. 功能简述

F_CreateMacAddr 把 6 字节 MAC 地址数组（`T_MacAddrArr`）格式化为字符串（如 `'01-02-03-04-05-06'`）。可选分隔符 `sSeparator`（默认 `'-'`，常见也用 `':'`）和大小写控制 `bLoCase`（FALSE = 大写 `ABCDEF`，TRUE = 小写 `abcdef`）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    aMacAddr : T_MacAddrArr;
    sSeparator : STRING(1) := '-';
    bLoCase : BOOL := FALSE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `aMacAddr` | `T_MacAddrArr` | - | 6 字节 MAC 地址数组（`T_MacAddrArr`）。 |
| `sSeparator` | `STRING(1)` | `'-'` | 字节之间的分隔符（1 字符），默认 `'-'`，常用也填 `':'`。 |
| `bLoCase` | `BOOL` | `FALSE` | TRUE 用小写 `abcdef`，FALSE 用大写 `ABCDEF`。默认 FALSE。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**输入**：`aMacAddr` 是 6 字节数组，按硬件 OUI 顺序排列（如 `[0x1C, 0x2C, 0x3C, 0x4C, 0x5C, 0x6C]`）。

**格式化规则**：每字节转 2 位 16 进制，用 `sSeparator` 拼接。`sSeparator` 长度限 1 字符，超出未定义。

**返回值**：`T_MacAddr` 字符串，17 字符（6×2 + 5 分隔符），固定长度。

**典型应用场景**：HMI 网络信息页显示本机 / 远端网卡 MAC、把 MAC 写入工艺日志、生成设备唯一标识用于绑定 license。

**与 `F_CreateIPv4Addr` 的关系**：风格一致——字节数组 → 字符串；不同点是 MAC 字节没有网络字节序与主机字节序之分（按硬件 OUI 顺序）。

## 4. 错误码 / 返回值

本函数返回 `T_MacAddr`（字符串，17 字符）：如 `'01-02-03-04-05-06'`。

## 5. 使用注意 / 常见坑

- **`sSeparator` 限 1 字符**：传 `'::'` 等行为未定义。
- **字节序**：按硬件顺序传入；与 IP 不同，MAC 没有『网络字节序』反转。
- **大小写不一致**：业务侧切换 `bLoCase` 后 HMI 显示可能与日志记录不一致；建议全工程统一。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_CreateMacAddr.TcPOU`](../examples/P_Demo_F_CreateMacAddr.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 显示本机网卡 MAC：从 ADS 读取本机 MAC 6 字节，转成 `'1C-2C-3C-4C-5C-6C'` 显示在『网络信息』页面。
- **价值**：替代手写 6 次 BYTE_TO_HEX + 5 次拼接；一行调用。
- **替代方案对比**：
  - 手拼字符串：约 8-10 行。
  - `F_FormatStringArray`：通用但更复杂。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.1.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/20034182027.html
- **相关 FB / FC**：`F_CreateIPv4Addr`
