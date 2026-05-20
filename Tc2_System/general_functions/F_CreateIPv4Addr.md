# F_CreateIPv4Addr

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `General functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31009291.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_CreateIPv4Addr.xml`](../examples/P_Demo_F_CreateIPv4Addr.xml) |

---

## 1. 功能简述

F_CreateIPv4Addr 把 IPv4 地址的 4 个字节数组（`T_IPv4AddrArr`，4 字节）格式化为字符串（如 `'172.16.7.199'`）。字节顺序是网络字节序（高字节在前）。适用于把数字形式的 IP 转成 HMI 显示字符串、日志记录、或拼接 URL 等场景。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nIds : T_IPv4AddrArr;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nIds` | `T_IPv4AddrArr` | IPv4 地址的 4 字节数组（`T_IPv4AddrArr`），网络字节序。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**输入字节顺序**：`nIds[0]` = IP 第一段，`nIds[3]` = IP 最后一段；与点分十进制阅读顺序一致。

**返回值**：`T_IPv4Addr` 字符串，固定格式 `D.D.D.D`，每段 0–255，无前导零。

**典型用法**：从 ADS / DHCP 接口拿到 4 字节 IP 后转字符串显示，或把工程配置中的 4 字节数组转字符串写入配置文件。

**反向操作**：`F_ScanIPv4AddrIds` 是本函数的反向——字符串→字节数组。

## 4. 错误码 / 返回值

本函数返回 `T_IPv4Addr`（字符串）：格式 `'D.D.D.D'`，每段 0–255。

## 5. 使用注意 / 常见坑

- **只支持 IPv4**：要 IPv6 字符串拼接需要自己实现或用 `F_FormatStringArray`（其他库）。
- **字节序**：传入数组应是网络字节序而不是主机字节序；x86 是小端，如果直接强转 `DWORD` 会颠倒。
- **返回值是固定 `T_IPv4Addr` 类型**（约 16 字节字符串），不要赋给 `STRING(7)` 等过短类型。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_CreateIPv4Addr.xml`](../examples/P_Demo_F_CreateIPv4Addr.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 显示远端 PLC IP：从 ADS 读到 4 字节 IP 数组后用本函数转成 `'192.168.1.10'` 显示。
- **价值**：替代手写 `CONCAT(USINT_TO_STRING(...))` 4 次 + 3 个点号；一行代码搞定。
- **替代方案对比**：
  - 手拼字符串：约 4-6 行。
  - `F_FormatStringArray`：通用但更复杂。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.1.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31009291.html
- **相关 FB / FC**：`F_ScanIPv4AddrIds`, `F_CreateMacAddr`
