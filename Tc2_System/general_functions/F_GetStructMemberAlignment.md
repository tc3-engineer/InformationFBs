# F_GetStructMemberAlignment

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `General functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31021579.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetStructMemberAlignment.TcPOU`](../examples/P_Demo_F_GetStructMemberAlignment.TcPOU) |

---

## 1. 功能简述

F_GetStructMemberAlignment 返回当前 TwinCAT runtime 使用的结构体成员对齐字节数（1 / 2 / 4 / 8）。对齐设置直接影响结构体内存布局（padding 字节数）：x86 通常 8，Arm 通常 4。用于跨平台序列化 / 反序列化、与 PC 端 C / C# 程序对接时校验布局一致性。

## 2. 接口定义

### VAR_INPUT

无。

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**返回值**：`BYTE` 类型，值为 1 / 2 / 4 / 8，表示结构体成员的对齐边界。

**对齐影响**：例如 `BYTE + LREAL` 结构体在 8 字节对齐下 SIZEOF = 16（7 字节 padding），在 1 字节对齐下 SIZEOF = 9 无 padding。

**典型用法**：跨平台数据交换时校验 PLC 与 PC 端结构体布局一致；若 PC 端用 `#pragma pack(1)` 而 PLC 是 8 字节对齐，必须用 `MEMCPY` + 手算偏移，不能直接 `MEMCPY` 整个结构。

## 4. 错误码 / 返回值

本函数返回 `BYTE`：对齐字节数（1 / 2 / 4 / 8）。

## 5. 使用注意 / 常见坑

- **编译期常量**：本值由 TwinCAT 版本和目标平台决定，运行期不会变。（工程经验补充）
- **ALIGN pragma 不影响本函数**：变量级的 `{attribute 'pack_mode' := '1'}` 不改全局返回值；要看实际 SIZEOF 才能知道结构体真布局。（工程经验补充）
- **跨平台序列化必须显式打包**：依赖默认对齐做跨平台 IPC 极其脆弱；建议每个字段单独 `MEMCPY` 或用 protobuf / JSON。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetStructMemberAlignment.TcPOU`](../examples/P_Demo_F_GetStructMemberAlignment.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：MAIN 启动时记录当前平台对齐到日志，便于跨平台部署时一眼看出 x86 vs Arm 的差异。
- **价值**：替代凭经验猜对齐；运行期实测最准。
- **替代方案对比**：
  - 凭经验：x86 = 8，Arm = 4——大多数对但偶尔会错。
  - 看 PDF：要找特定版本。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.1.10
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/31021579.html
- **相关 FB / FC**：`MEMCPY`, `F_CheckMemoryArea`
