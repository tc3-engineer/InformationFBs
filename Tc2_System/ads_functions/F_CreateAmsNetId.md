# F_CreateAmsNetId

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `ADS functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31035147.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_CreateAmsNetId.xml`](../examples/P_Demo_F_CreateAmsNetId.xml) |

---

## 1. 功能简述

F_CreateAmsNetId 是同步函数：把一个 6 字节的 AMS Net ID 字节数组（`T_AmsNetIdArr`）格式化为字符串形式（`T_AmsNetID`，如 `'127.16.17.3.1.1'`）。字节按网络字节序排列。常用在动态拼接 AMS 路由地址的场景。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nIds : T_AmsNetIdArr;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nIds` | `T_AmsNetIdArr` | - | AMS 网络地址的字节数组（`ARRAY[0..5] OF BYTE`）；每字节对应 NetID 中的一个数字段，按网络字节序排列。 |

### VAR_OUTPUT

```iecst
(* FUNCTION 返回 T_AmsNetId（格式化字符串）*)
FUNCTION F_CreateAmsNetId : T_AmsNetId
```

FUNCTION 返回值类型：`T_AmsNetId`（详见 §4）。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用语义**：FUNCTION 类型，同步即出值。把输入数组 `nIds` 的 6 个字节按 `n0.n1.n2.n3.n4.n5` 格式拼成字符串返回。

**典型用法**（PDF 示例）：
```iecst
ids : T_AmsNetIdArr := 127, 16, 17, 3, 1, 1;
sNetID : T_AmsNetID := '';
sNetID := F_CreateAmsNetId(ids); // 结果 '127.16.17.3.1.1'
```

**与 `F_ScanAmsNetIds` 的关系**：本函数是 array → string 方向；`F_ScanAmsNetIds` 是 string → array 反方向，两者互为反函数。

**何时用**：通过配置文件或上位机读到 6 字节 AMS Net ID（如二进制配置数据），需要传给 `ADSREAD` / `ADSWRITE` 之类要求 `T_AmsNetId` 字符串的 FB；本函数是直通转换。

## 4. 错误码 / 返回值

函数不暴露错误输出；对输入是 6 字节定长数组无歧义；返回字符串始终为合法 AMS Net ID 格式。

## 5. 使用注意 / 常见坑

- 网络字节序——`ids[0]` 是 NetID 字符串里第一个数（最高有效字节）。
- 如果业务侧拿到的是字符串形式（如 HMI 输入），无需调本函数；直接用即可。
- 想反向把 `'127.16.17.3.1.1'` 拆回字节数组用 `F_ScanAmsNetIds`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_CreateAmsNetId.xml`](../examples/P_Demo_F_CreateAmsNetId.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：CX 设备上配置文件里把目标控制器的 AMS Net ID 以 6 字节二进制存储（节省空间）；运行时本函数把字节数组转字符串再交给 `ADSREAD`。
- **价值**：替代手写 `BYTE_TO_STRING(byte) + '.' + ...` 6 次拼接，一行调用。
- **替代方案对比**：`F_ScanAmsNetIds` 反方向（string → array）。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.2.4
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31035147.html
- **相关 FB / FC**：`F_ScanAmsNetIds`（反方向）、`T_AmsNetIdArr`、`T_AmsNetId`
