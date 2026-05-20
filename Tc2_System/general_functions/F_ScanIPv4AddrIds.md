# F_ScanIPv4AddrIds

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `General functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31010827.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_ScanIPv4AddrIds.xml`](../examples/P_Demo_F_ScanIPv4AddrIds.xml) |

---

## 1. 功能简述

F_ScanIPv4AddrIds 是 `F_CreateIPv4Addr` 的反向操作：把 `'172.16.7.199'` 这样的 IPv4 字符串解析成 4 字节数组（`T_IPv4AddrArr`）。字符串非法时（空串、`'0.0.0.0'`、格式错）返回全零数组——调用方应当通过『非空且非全零』的双重判断检测错误。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sIPv4 : T_IPv4Addr;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `sIPv4` | `T_IPv4Addr` | IPv4 字符串（`T_IPv4Addr`），如 `'172.16.7.199'`。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**解析方式**：从左到右扫描，遇 `.` 或字符串末尾即把当前段写入对应字节，4 段全部填好后返回。

**错误检测**：PDF 明确给出错误条件——若输入既不是空串、也不是 `'0.0.0.0'`，但返回数组所有字节为 0，则说明解析失败（格式不合法）。调用方必须做此双重检查。

**网络字节序**：输出与 `F_CreateIPv4Addr` 一致——`aIds[0]` = 第一段。

## 4. 错误码 / 返回值

本函数返回 `T_IPv4AddrArr`：4 字节数组（网络字节序）。返回全零 + 输入非 `''` / `'0.0.0.0'` 表示解析失败。

## 5. 使用注意 / 常见坑

- **全零返回有歧义**：`'0.0.0.0'` 合法，错串也返回 0；要区分必须比较输入字符串是否为合法格式。
- **只支持 IPv4**：IPv6 字符串解析需要其他库。
- **超长 / 含字母**：超过段值 255 或含字母时本函数返回 0，调用方需做合法性校验。（工程经验补充）
- **前导 / 尾部空格**：未明确，建议预先 `TRIM`。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_ScanIPv4AddrIds.xml`](../examples/P_Demo_F_ScanIPv4AddrIds.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：操作员在 HMI 输入远端 PLC IP 字符串，PLC 解析成 4 字节供 ADS 调用使用。
- **价值**：一行替代手写 split + 字符串转数字 4 次循环。
- **替代方案对比**：
  - 手写按 `.` split + `STRING_TO_USINT` 4 次：约 8-12 行。
  - 调用方自己解析：易错。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.1.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31010827.html
- **相关 FB / FC**：`F_CreateIPv4Addr`
