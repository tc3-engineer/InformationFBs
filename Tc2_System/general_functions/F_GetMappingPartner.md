# F_GetMappingPartner

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `General functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/2284517003.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetMappingPartner.TcPOU`](../examples/P_Demo_F_GetMappingPartner.TcPOU) |

---

## 1. 功能简述

F_GetMappingPartner 返回 PLC 变量映射伙伴端（mapping partner）的对象 ID（`OTCID` 类型）。若一个 PLC 变量与 IO 链 / NC / 其他 PLC 映射，本函数返回对端对象 ID；用于在运行期诊断映射拓扑。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    p : PVOID;
    n : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `p` | `PVOID` | PLC 变量地址（`ADR(myVar)`）。 |
| `n` | `UDINT` | 变量字节数（`SIZEOF(myVar)`）。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**返回值**：`OTCID` 是 32 位无符号对象 ID，非 0 表示映射伙伴的对象 ID，`0` 表示该变量未映射或映射伙伴不存在。

**典型用法**：在线诊断某 PLC 变量是否真的与硬件 IO 通道挂上，避免『PLC 写值但 IO 不动』的隐蔽错配。

**与 `F_GetMappingStatus` 区别**：本函数返回对端 ID（具体是谁），`F_GetMappingStatus` 返回映射状态（是否映射）。两者常配合使用。

**输入约束**：`p` 用 `ADR(myVar)`，`n` 用 `SIZEOF(myVar)`；尺寸错误可能误判跨变量。

## 4. 错误码 / 返回值

本函数返回 `OTCID`（`UDINT`）：映射伙伴对象 ID；`0` 表示未映射。

## 5. 使用注意 / 常见坑

- **`OTCID = 0`**：未映射 / 映射伙伴不存在；调用方要区分『未配置』与『配置错误』需配合 `F_GetMappingStatus`。
- **实时性影响**：每次调用扫映射表，高频循环里别用。（工程经验补充）
- **`OTCID` 解读**：需要查 TwinCAT 对象表才知道具体是哪个 IO / NC / PLC 对象；本函数只给 ID。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetMappingPartner.TcPOU`](../examples/P_Demo_F_GetMappingPartner.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：启动时检查关键 IO 输入变量是否真的映射到了对应 EtherCAT 终端，未映射立即报告而不是等到执行时出错。
- **价值**：替代靠『手动比对 IO 配置文件』的低效方式。
- **替代方案对比**：
  - 看 TwinCAT IO 配置树：登工程才能看。
  - 不检查：故障难定位。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.1.8
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/2284517003.html
- **相关 FB / FC**：`F_GetMappingStatus`, `F_CheckMemoryArea`
