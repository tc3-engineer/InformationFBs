# F_CheckMemoryArea

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `General functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/4012887435.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_CheckMemoryArea.TcPOU`](../examples/P_Demo_F_CheckMemoryArea.TcPOU) |

---

## 1. 功能简述

F_CheckMemoryArea 返回一个变量所在的内存区域类别（`E_TcMemoryArea` 枚举）：静态区（编译期分配）、动态区（`__NEW` 堆）、未知 / 非法地址等。用于诊断指针来源、检测野指针、判断变量是否仍存活——尤其在动态分配 / 释放复杂的场景下，避免使用已经 `__DELETE` 的变量。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    pData : PVOID;
    nSize : UDINT;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `pData` | `PVOID` | 要检查的变量内存地址，通常 `ADR(myVar)`。 |
| `nSize` | `UDINT` | 变量字节数，通常 `SIZEOF(myVar)`。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**返回值**：`E_TcMemoryArea` 枚举，常见值：

- `eTcMA_Static`：静态分配区（普通 `VAR` / `VAR_GLOBAL`）；
- `eTcMA_Dynamic`：动态分配区（`__NEW` 出来的）；
- `eTcMA_Retain`：retain 持久化区；
- `eTcMA_Unknown` / `eTcMA_Invalid`：地址不属于任何已知区域（如 0 指针或越界）。

具体枚举值见 InfoSys `E_TcMemoryArea` topic。

**典型用法**：在通用接口里收到 `PVOID` 指针时，先 `F_CheckMemoryArea` 确认地址合法再解引用，避免野指针崩 PLC。

**与 `F_GetMappingStatus` 的区别**：本函数判断变量所在的内存类别（静态 / 动态 / 持久化），`F_GetMappingStatus` 判断变量是否被映射到 IO 链。两者关注点不同，常配合使用以诊断变量来源与生命周期。

**调试技巧**：复现野指针崩溃时，在通用接口入口统一加守护，命中 `eTcMA_Unknown` 即记录调用上下文便于定位。

## 4. 错误码 / 返回值

本函数返回 `E_TcMemoryArea`：枚举常量，具体值见 InfoSys 的 `E_TcMemoryArea` 类型 topic。

## 5. 使用注意 / 常见坑

- **不检测对象生命周期**：`__DELETE` 后的内存区域可能仍然『属于动态区』，本函数不能判断对象是否还活着。要管理生命周期需自己加引用计数或 owner 字段。
- **性能开销**：每次调用要扫描内存映射表，循环里频繁调用会拖累实时性。建议只在边界场景（接口入口）调用。（工程经验补充）
- **`nSize` 必须正确**：传入的 `nSize` 错可能误判跨区域；用 `SIZEOF(myVar)` 取最安全。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_CheckMemoryArea.TcPOU`](../examples/P_Demo_F_CheckMemoryArea.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）。
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：动态对象池管理：分发指针前先 `F_CheckMemoryArea` 确认指向动态区且非 0，避免业务侧拿到静态地址用 `__DELETE` 释放（会崩溃）。
- **价值**：替代『假设调用方传对了』的盲信心态；在出 bug 前定位。
- **替代方案对比**：
  - 自己维护 owner 字段 + 引用计数：更准确但要写状态机。
  - 不检查：野指针崩溃风险。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.1.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/4012887435.html
- **相关 FB / FC**：`F_GetMappingStatus`, `F_GetStructMemberAlignment`
