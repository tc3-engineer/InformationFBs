# F_GetClassIdVersioned

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/11533472139.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetClassIdVersioned.xml`](../examples/P_Demo_F_GetClassIdVersioned.xml) |

---

## 1. 功能简述

为版本化的 TwinCAT C++ 项目计算「带版本号的 Class ID」——`Hash(clsId, sLibraryId) → clsIdVersioned`，使同一 Class 不同版本得到不同 GUID 避免类型冲突。

本函数属于 `Tc2_Utilities` 库的 `Functions` 类别（PDF 第 4 章）——这一类是不带状态的纯函数集合：CRC / 校验和 / 哈希、字符串与字节流互转、GUID 处理、各种基本类型与传输格式之间的桥接。它们是 PLC 通信、日志、配置文件处理的底层零件，多数在 `Tc2_Standard` 之外补充 Beckhoff 工业自动化场景下的常用工具。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sLibraryId : STRING(255);
    clsId : CLSID;
    clsIdVersioned : REFERENCE TO CLSID;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `sLibraryId` | `STRING(255)` | — | 库标识：`'vendor|libName|libVersion'`，如 `'C++ Module Vendor|IncrementerCpp|0.0.0.1'`。 |
| `clsId` | `CLSID` | — | 原始 Class ID（GUID 结构）。 |
| `clsIdVersioned` | `REFERENCE TO CLSID` | — | 输出：版本化后的 Class ID。 |

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | 详见 §3 行为说明。|

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

函数无状态、立即返回。算法：把 `clsId` 与 `sLibraryId` 中的 vendor / lib name / lib version 联合 hash 得到一个新 CLSID，写入 `clsIdVersioned`。这是 **C++ 与 PLC 互操作时的版本管理机制**——同一 C++ Class 在 lib v0.0.0.1 与 v0.0.0.2 之间接口可能改变，如果 PLC 端继续用旧 Class ID 访问会读到字段错位的数据；版本化 Class ID 让 PLC 在加载时立即得知 'lib 升级了我的 ID 也变了，老的代码不能用新 lib'。返回 `TRUE` = 成功生成 versioned ID；`FALSE` = 参数错误（`sLibraryId` 格式不符等）。**仅在使用 TwinCAT 3 C++ Class 时需要**——纯 PLC 项目不用。

## 4. 错误码 / 返回值

返回 `BOOL`——具体语义见 §3。错误约定：
- 多数函数无独立错误码，**通过返回值的特殊值（如 0 / 255 / 空串 / `FALSE`）报错**——调用方必须始终判返回值。
- 涉及输出缓冲的函数在缓冲不够时通常截断、返回 `FALSE` 或特殊标记；调用方应**始终把返回值当主要错误信号**。

## 5. 使用注意 / 常见坑

- **仅 TwinCAT 3 C++ 项目相关**——纯 PLC 项目无需调用。
- **`sLibraryId` 格式严格**：`'vendor|libName|version'` 三段用 `|` 分隔，version 必须是 `a.b.c.d` 四段点分。
- **`clsIdVersioned` 是 `REFERENCE TO CLSID`** —— 调用方必须传入已声明的 CLSID 变量地址；不能传立即量。
- 返回 `FALSE` 时 `clsIdVersioned` 内容未定义。
- **版本号变 → versioned ID 变** —— 这是设计目的，不是 bug。
- **版本要求**：`Tc2_Utilities >= 3.3.51.0`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetClassIdVersioned.xml`](../examples/P_Demo_F_GetClassIdVersioned.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

## 7. 业务场景与实际价值

- **场景**：工业控制器跨版本兼容：CX5020 升级 C++ Class lib 后，PLC 用版本化 ID 加载，新版数据不会被老 PLC 解读错位。
- **价值**：替代手写 GUID 派生算法；标准库提供版本化 ID 计算，确保跨版本兼容性失败时立即报错而不是数据错位。
- **替代方案对比**：**无对照**——这是 TwinCAT 3 C++ 版本机制的一部分；纯 PLC 不涉及。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.37 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/11533472139.html
- **相关函数**：见同库 `functions/` 目录下其他工具函数
