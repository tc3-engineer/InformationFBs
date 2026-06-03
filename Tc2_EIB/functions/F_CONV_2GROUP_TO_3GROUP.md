# F_CONV_2GROUP_TO_3GROUP

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EIB` |
| Library Version | `1.16.1` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187789579.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_CONV_2GROUP_TO_3GROUP.TcPOU`](../examples/P_Demo_F_CONV_2GROUP_TO_3GROUP.TcPOU) |

---

## 1. 功能简述

**把 2 级 EIB 组地址转换为 3 级 EIB 组地址**。EIB 组地址有两种编址：① 3 级（MAIN/SUB_MAIN/NUMBER，对应新 KNX）；② 2 级（MAIN/SUB_MAIN，对应老 EIB）。本 FC 把 2 级形式转成等价的 3 级形式。

**返回类型**：从 PDF/InfoSys 看本 FC 没有显式列出返回类型——按惯例返回 `EIB_GROUP_ADDR`。在 IEC 代码里用 `stOut := F_CONV_2GROUP_TO_3GROUP(IN := st2)` 形式调用。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    IN : EIB_GROUP_ADDR_2GROUP;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `IN` | `EIB_GROUP_ADDR_2GROUP` | — | 2 级 EIB 组地址结构（`MAIN : BYTE` 0..15、`SUB_MAIN : WORD` 0..2048）。**PDF 描述表把名字标成 `Group_Address`**——以 VAR_INPUT 代码块的 `IN` 为准（实际 IEC 代码用 `IN`） |

### VAR_OUTPUT

无（FC，返回值见 §4）。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用即转换**：纯函数无副作用，每次调用立即返回转换后的 3 级地址。

**2 级到 3 级映射规则**：2 级地址范围比 3 级大（SUB_MAIN 是 WORD 0..2048 vs NUMBER 是 BYTE 0..255），库内部按 EIB 标准把 `SUB_MAIN` 拆成 3 级的 (SUB_MAIN, NUMBER)：典型 `SUB_MAIN >> 8` → 新的 SUB_MAIN，`SUB_MAIN & 0xFF` → NUMBER。PDF 未明确算法，按 EIB/KNX 标准规范。

**何时用 2 级地址**：与早期不支持 3 级的 KNX/EIB 楼宇设备对接时；现代项目几乎都用 3 级。本 FC 主要用于「老项目迁移」或「多代设备共存」场景。

**与 KL6301 无关**：本 FC 是纯算法，不需要 EIB_REC、不依赖 KL6301 状态。可独立调用。

## 4. 错误码 / 返回值

本 FC 是纯函数，**无错误码 / 无错误输出**。传入合法 `EIB_GROUP_ADDR_2GROUP` 总是返回有效的 `EIB_GROUP_ADDR`；极端情况（例 `SUB_MAIN > 2048`）按 EIB 规范截断或回绕。PDF + InfoSys 均未列出错码（⚠️ 待人工确认极端值行为）。

## 5. 使用注意 / 常见坑

- **纯函数无副作用**：每次调用都独立，可在任何上下文调用（不需要 KL6301、不需要 EIB_REC）。
- **PDF 描述表名 `Group_Address` 但 VAR_INPUT 名 `IN`**：以代码块的 `IN` 为准。
- **与 `F_CONV_3GROUP_TO_2GROUP` 配对**：反向转换是另一个 FC（§4.2.6.2）。
- **典型用法是兼容老 EIB 设备**：现代项目多用 3 级；本 FC 是迁移工具。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_CONV_2GROUP_TO_3GROUP.TcPOU`](../examples/P_Demo_F_CONV_2GROUP_TO_3GROUP.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_CONV_2GROUP_TO_3GROUP
VAR
    st2 : EIB_GROUP_ADDR_2GROUP := (MAIN := 1, SUB_MAIN := 256);
    st3 : EIB_GROUP_ADDR;
END_VAR
st3 := F_CONV_2GROUP_TO_3GROUP(IN := st2);
```

## 7. 业务场景与实际价值

- **场景**：老 EIB 设备升级 / 多代设备共存 / 地址格式统一
- **价值**：替代手写位拆分；纯函数调用清晰
- **替代方案对比**：
  - 手写位运算：能做，但要懂 EIB 协议规范
  - 本 FC：迁移工具的**标准**选择

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf) §4.2.6.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187789579.html
- **相关**：`F_CONV_3GROUP_TO_2GROUP`（同库 §4.2.6.2，反向转换）、`EIB_GROUP_ADDR`（同库 §4.3.2.1，3 级地址结构）、`EIB_GROUP_ADDR_2GROUP`（同库 §4.3.2.2，2 级地址结构）
