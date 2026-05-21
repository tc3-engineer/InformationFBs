# F_GetMappingStatus

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `General functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/2284515083.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetMappingStatus.xml`](../examples/P_Demo_F_GetMappingStatus.xml) |

---

## 1. 功能简述

F_GetMappingStatus 返回 PLC 变量的映射状态枚举（`EPlcMappingStatus`）：未映射、已映射、部分映射。用于在线诊断 IO / NC / 跨 PLC 映射的真实状态，比单纯读 IO 配置树更准确。

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

**返回值 `EPlcMappingStatus`**：

- `MS_Unmapped`：变量未参与任何映射；
- `MS_Mapped`：变量整体映射到某个伙伴；
- `MS_Partial`：变量部分字节映射（典型于结构体里只映射了部分字段）。

**与 `F_GetMappingPartner` 区别**：本函数只回三态状态，`F_GetMappingPartner` 进一步告诉对端是谁。两者配合使用：先用本函数过滤出非 `MS_Mapped` 的变量，再用 `F_GetMappingPartner` 看具体对端 ID 定位问题。

**典型用法**：上线前一次性扫描所有重要变量的映射状态，把 `MS_Partial` 或 `MS_Unmapped` 项汇总成报告写入诊断日志。`MS_Partial` 通常是工程配置错误（结构体只挂了部分字段），需要工程师立即修复，运行期再发现就晚了。

**调用开销**：每次调用扫一遍映射表，开销与系统映射条目数成正比，避免在 PLC MAIN 循环里高频调用。

## 4. 错误码 / 返回值

本函数返回 `EPlcMappingStatus`：`MS_Unmapped` / `MS_Mapped` / `MS_Partial`。

## 5. 使用注意 / 常见坑

- **`MS_Partial` 容易忽略**：结构体里只映射几个字段时返回 `MS_Partial`，要不要算『映射完成』取决于业务。
- **实时性影响**：与 `F_GetMappingPartner` 一致，每次调用扫表。（工程经验补充）
- **`nSize` 错误**：传错可能跨越多个变量造成误判。永远 `SIZEOF(myVar)`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetMappingStatus.xml`](../examples/P_Demo_F_GetMappingStatus.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：启动后扫描所有 IO 变量的映射状态，把任何 `MS_Unmapped` / `MS_Partial` 项写入告警日志便于运维定位。
- **价值**：替代手工比对 IO 配置树。
- **替代方案对比**：
  - 看配置树：登工程才能看。
  - `F_GetMappingPartner` 配合：得到更详细的对端 ID。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.1.9
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/2284515083.html
- **相关 FB / FC**：`F_GetMappingPartner`
