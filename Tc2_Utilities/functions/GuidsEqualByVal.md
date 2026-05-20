# GuidsEqualByVal

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934084875.html |
| Verified | 2026-05-12 ✅ |
| InfoSys-checked | ✅ 2026-05-12 |
| Status | `verified` |
| Example | [`examples/P_Demo_GuidsEqualByVal.xml`](../examples/P_Demo_GuidsEqualByVal.xml) |

---

## 1. 功能简述

按值比较两个 GUID 结构是否相等。`TRUE` = 完全相同（128 位全等），`FALSE` = 任一位不同。

虽然结构体也能用 `=` 语法比较（PLC 编译器对结构体重载了等于运算符），但 `GUID` 内部有数组字段 `Data4[0..7]`，部分老编译器对含数组的结构体 `=` 行为不一致；本函数保证按字节逐位比较，跨编译器版本结果一致。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    guidA : GUID;
    guidB : GUID;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `guidA` | `GUID` | — | 第一个 GUID。 |
| `guidB` | `GUID` | — | 第二个 GUID。 |

### VAR_IN_OUT

无。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `BOOL` | `TRUE` = 完全相同；`FALSE` = 任一字段不同。 |

### VAR_OUTPUT

无。

## 3. 行为说明

函数对 `guidA.Data1`、`guidA.Data2`、`guidA.Data3` 与 `guidB` 对应字段做整数相等比较，并对 `guidA.Data4[0..7]` 与 `guidB.Data4[0..7]` 8 字节做逐字节比较，全部相等才返回 `TRUE`。整个比较过程是按值进行，16 字节固定开销，与具体 GUID 内容无关。

典型用途：一是空 GUID 检测，建一个常量 `cZeroGuid : GUID;`（默认全零）后用 `GuidsEqualByVal(gMaybeUnset, cZeroGuid)` 判断 GUID 是否已被分配；二是会话或实例标识比较，确定收到的消息是否属于当前会话；三是 C++ 模块版本对照，与 `F_GetClassIdVersioned` 算出的 CLSID 列表逐个比对来选版本。性能上 `GUID` 仅 16 字节，整体比较是 O(1) 常数时间，可放在主循环里高频调用而无明显开销，也不涉及共享状态，跨任务调用安全。

## 4. 错误码 / 返回值

| 返回值 | 含义 |
|---|---|
| `TRUE` | 两 GUID 完全相同 |
| `FALSE` | 至少一字段不同 |

## 5. 使用注意 / 常见坑

- **不用 `gA = gB`**：编译器对含数组结构体的 `=` 行为不一定可靠（按版本），用本函数最稳。
- **结构体顺序无关**：因为按值比较，不论字段在内存中的字节序，只要逻辑值相等即等。
- **常量比较**：可建 `cZeroGuid` / `cExpectedGuid` 等 `VAR CONSTANT GUID` 常量做对比，HMI 直接展示常量名（工程经验补充）。
- **大小写无关**：本函数不涉及字符串，纯数值比较；`GUID_TO_STRING` 后用 `EQ` 字符串比较则需注意大小写（工程经验补充）。
- **跨任务安全**：纯值比较，不涉及共享状态，跨任务调用安全。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_GuidsEqualByVal.xml`](../examples/P_Demo_GuidsEqualByVal.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_GuidsEqualByVal
VAR
    gIncomingMessageId : GUID;
    gExpectedMessageId : GUID;
    bMatch             : BOOL;
END_VAR

bMatch := GuidsEqualByVal(guidA := gIncomingMessageId, guidB := gExpectedMessageId);
```

## 7. 业务场景与实际价值

- **场景**：MES 下发的指令消息含 `MessageId : GUID`，PLC 端把已处理消息 ID 缓存到环形 buffer；新消息到达时用本函数遍历 buffer 检测是否已处理（去重），防止 MES 重发导致一个动作执行两次。
- **价值**：可靠的 GUID 等值比较；跨编译器版本结果一致。
- **替代方案对比**：
  - `gA = gB`：依赖编译器对含数组结构体的 `=` 实现，老版本可能不行
  - `MEMCMP(ADR(gA), ADR(gB), SIZEOF(GUID)) = 0`：可行，但要包指针；语义不如本函数清晰
  - 本函数：语义清晰、跨版本稳定

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.46 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/934084875.html
- **相关函数 / 类型**：`GUID_TO_STRING`、`GUID_TO_REGSTRING`、`STRING_TO_GUID`、`REGSTRING_TO_GUID`、`GUID`（128 位结构）
