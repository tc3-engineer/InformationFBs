# F_GetClassIdVersioned

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Min Lib Version | `3.3.51.0` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35070091.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetClassIdVersioned.xml`](../examples/P_Demo_F_GetClassIdVersioned.xml) |

---

## 1. 功能简述

把"基本 Class ID（CLSID）+ 库 ID 字符串"组合成"带版本的 Class ID"，用于版本化的 C++ 模块项目（versioned C++ projects）。当同一 C++ 模块在工程里以多个版本共存时（A.A.A.A 与 B.B.B.B），原始 Class ID 不够区分；本函数把 Library ID（厂商|库名|版本）混入 CLSID 哈希得到唯一的版本化 CLSID，供 PLC 端做模块实例化时区分版本。

`sLibraryId` 是规范字符串 `'vendorName|libraryName|libraryVersion'`，比如 `'C++ Module Vendor|IncrementerCpp|0.0.0.1'`，由 C++ 模块的注册信息决定。返回 `BOOL`：`TRUE` 计算成功（`clsIdVersioned` 被填入新 CLSID），`FALSE` 失败（输入格式不对）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    sLibraryId     : STRING(255); // 'vendorName|libraryName|libraryVersion' (e.g. 'C+
+ Module Vendor|IncrementerCpp|0.0.0.1' )
    clsId          : CLSID;
    clsIdVersioned : REFERENCE TO CLSID;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `sLibraryId` | `STRING(255)` | — | 库 ID 字符串，格式 `'厂商\|库名\|版本'`，三段用 `\|` 分隔（例：`'C++ Module Vendor\|IncrementerCpp\|0.0.0.1'`）。 |
| `clsId` | `CLSID` | — | C++ 模块的原始 Class ID（GUID 结构，由模块开发者声明）。 |
| `clsIdVersioned` | `REFERENCE TO CLSID` | — | 输出：本函数计算得到的版本化 Class ID。调用方需提供一个 `CLSID` 变量并通过 `REF=` 引用。 |

### VAR_IN_OUT

无（`clsIdVersioned` 是 `REFERENCE TO`，语义上是出参，PLC 编译器仍按 `VAR_INPUT` 列）。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 计算成功；`FALSE` = `sLibraryId` 格式非法 / `clsIdVersioned` 引用无效。 |

### VAR_OUTPUT

无。

## 3. 行为说明

函数把 `sLibraryId` 与 `clsId` 通过 Beckhoff 内部规则（按 PDF 公开信息：哈希混合 + UUID 派生）组合，生成版本化的新 CLSID 写入 `clsIdVersioned`。同一 `clsId` 配不同 `sLibraryId` 版本得到的 `clsIdVersioned` 不同；同一 `clsId` 配相同 `sLibraryId` 总是得到相同 `clsIdVersioned`（确定性）。

典型上下文：TwinCAT 把多版本 C++ 模块同时部署到 XAR（运行时），PLC 端想引用"v0.0.0.1 的 Incrementer 模块"而不是"v0.0.0.2 的 Incrementer 模块"，就用版本化 CLSID 实例化具体版本。如果工程只有一个版本的 C++ 模块，无需用本函数，直接用基础 CLSID 即可。

`sLibraryId` 格式严格：三段用 ASCII `|`（pipe，0x7C）分隔；任一段为空、缺少分隔符、版本号格式非法 都会让函数返回 `FALSE`。版本号建议遵循 `major.minor.build.revision`（4 段数字）。

PDF 在 InfoSys 上没有专门的 topic 页（已在 `InfoSys-checked` 标 `⚠️ not-on-infosys`），仅 Tc2_Utilities 在 PDF 第 4.37 节有完整描述；版本化 C++ 模块的总体说明在 TE1400 / TwinCAT 3 C++ 文档体系内。

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| `TRUE` | 成功；`clsIdVersioned` 已填入新 CLSID |
| `FALSE` | `sLibraryId` 格式非法 / 引用空 |

## 5. 使用注意 / 常见坑

- **`sLibraryId` 必须严格三段 `\|` 分隔**：缺一段或多一段都返回 `FALSE`。
- **要求库版本 `>= 3.3.51.0`**：早版本无此函数。
- **只在多版本 C++ 模块场景有意义**：工程里 C++ 模块只有一版时，用基础 CLSID 即可，省得引入额外复杂度（工程经验补充）。
- **`clsIdVersioned` 是 `REFERENCE TO`**：调用方提供变量，写法是 `clsIdVersioned := myClsId`（PLC 语法上把引用绑定到变量）。
- **结果是确定性的**：相同 `sLibraryId` + `clsId` 永远得到相同 `clsIdVersioned`；可用于持久化对照表（工程经验补充）。
- **InfoSys 未单独收录**：与 PDF 不同步是 Beckhoff 文档维护的已知问题；功能本身在 TC3 运行时支持（PDF + 版本要求一致）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetClassIdVersioned.xml`](../examples/P_Demo_F_GetClassIdVersioned.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_GetClassIdVersioned
VAR
    sLibId       : STRING(255) := 'C++ Module Vendor|IncrementerCpp|0.0.0.1';
    clsidBase    : CLSID;        // 由 C++ 模块声明，此处假设已初始化
    clsidVerOut  : CLSID;        // 本函数算出的版本化 CLSID
    bSucceeded   : BOOL;
END_VAR

bSucceeded := F_GetClassIdVersioned(
    sLibraryId     := sLibId,
    clsId          := clsidBase,
    clsIdVersioned := clsidVerOut);
```

## 7. 业务场景与实际价值

- **场景**：同一 TwinCAT 工程同时部署多个版本的 C++ 控制算法（v0.0.0.1 用于产线 A、v0.0.0.2 用于产线 B），PLC 端按版本号选择实例化哪个版本的对象。
- **价值**：没有本函数就要给每个版本手动维护一个完整 GUID 对照表；本函数确定性派生，免维护对照。
- **替代方案对比**：
  - 多版本各发一个独立 CLSID：要 vendor 严格规范，易乱
  - 用统一 CLSID + 软件层 IF/CASE 分流：失去 COM 自描述能力
  - 本函数：把"版本"压入 CLSID 派生，Beckhoff 平台层自动区分

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.37 节
- **InfoSys topic**：未单独收录（⚠️ not-on-infosys），参见库根 https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35070091.html
- **相关 / 上下文**：`CLSID`（128 位 GUID 结构）、TwinCAT 3 C++ 模块版本化文档（TE1400）、`I_TcSourceInfo`（源信息接口）
