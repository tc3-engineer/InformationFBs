# F_ScanAmsNetIds

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `ADS functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31036683.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_ScanAmsNetIds.TcPOU`](../examples/P_Demo_F_ScanAmsNetIds.TcPOU) |

---

## 1. 功能简述

F_ScanAmsNetIds 是同步函数：把 AMS Net ID 字符串（`T_AmsNetID`，如 `'127.16.17.3.1.1'`）解析为 6 字节字节数组（`T_AmsNetIdArr`）。字节按网络字节序排列。是 `F_CreateAmsNetId` 的反函数。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sNetID : T_AmsNetID;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `sNetID` | `T_AmsNetID` | - | TwinCAT AMS 网络地址字符串，形如 `'127.16.17.3.1.1'`。 |

### VAR_OUTPUT

```iecst
(* FUNCTION 返回 T_AmsNetIdArr（6 字节数组）*)
FUNCTION F_ScanAmsNetIds : T_AmsNetIdArr
```

FUNCTION 返回值类型：`T_AmsNetIdArr`（详见 §4）。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用语义**：FUNCTION 类型，同步执行。从左到右把字符串各数字段按点切开转成字节，写到 6 字节返回数组。

**典型用法**（PDF 示例）：
```iecst
sNetID : T_AmsNetID := '127.16.17.3.1.1';
ids := F_ScanAmsNetIds(sNetID);
// ids[0]=127, ids[1]=16, ids[2]=17, ids[3]=3, ids[4]=1, ids[5]=1
```

**错误判定**：PDF 明确——如果输入既不是空串也不是 `'0.0.0.0.0.0'`，但返回数组所有字节都是 0，那一定是字符串格式错误（少点、非数字字符等）；调用方应判断这种情况。

**典型应用**：把 HMI 输入或配置文件里的字符串形式 NetID 转成字节存储，便于序列化或网络传输。

## 4. 错误码 / 返回值

函数本身不抛错误，但返回值中如果数组全为 0 且输入非空且非 `'0.0.0.0.0.0'`，则字符串格式错误。调用方应做这一显式判定（PDF 明确）。

## 5. 使用注意 / 常见坑

- 格式错误时返回全 0 数组而不是抛异常；调用方必须判断。（PDF 明确）
- 输入字符串必须严格 `n.n.n.n.n.n` 形式，6 段；多 / 少都会按错处理。
- 反方向（数组 → 字符串）用 `F_CreateAmsNetId`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_ScanAmsNetIds.TcPOU`](../examples/P_Demo_F_ScanAmsNetIds.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：HMI 上配置远端控制器 AMS Net ID（操作员输入字符串），PLC 把字符串解析为 6 字节存到配置区便于序列化。
- **价值**：替代手写 `STR_TO_BYTE` 循环切割点号；一行函数完成。
- **替代方案对比**：`F_CreateAmsNetId` 是反方向。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.2.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31036683.html
- **相关 FB / FC**：`F_CreateAmsNetId`（反方向）、`T_AmsNetIdArr`、`T_AmsNetId`
