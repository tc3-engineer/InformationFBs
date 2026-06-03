# F_CONV_3GROUP_TO_2GROUP

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EIB` |
| Library Version | `1.16.1` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187791115.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_CONV_3GROUP_TO_2GROUP.TcPOU`](../examples/P_Demo_F_CONV_3GROUP_TO_2GROUP.TcPOU) |

---

## 1. 功能简述

**把 3 级 EIB 组地址转换为 2 级 EIB 组地址**——`F_CONV_2GROUP_TO_3GROUP` 的反向操作。

**典型场景**：与老 EIB 设备对接时，业务代码内部用 3 级地址处理，下发到老设备前用本 FC 转成 2 级形式。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    IN : EIB_GROUP_ADDR;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `IN` | `EIB_GROUP_ADDR` | — | 3 级 EIB 组地址结构（`MAIN : BYTE` 0..31、`SUB_MAIN : BYTE` 0..7、`NUMBER : BYTE` 0..255） |

### VAR_OUTPUT

无（FC，返回值见 §4）。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用即转换**：纯函数无副作用，每次调用立即返回转换后的 2 级地址。

**3 级到 2 级映射规则**：库内部按 EIB 标准把 3 级的 (SUB_MAIN, NUMBER) 两个 BYTE 合并成 2 级地址的 `SUB_MAIN : WORD`，典型实现 `new_SUB_MAIN := (SUB_MAIN << 8) | NUMBER`。`MAIN` 字段直接复制（注意 3 级 MAIN 范围 0..31 但 2 级 MAIN 范围只有 0..15）。

**MAIN 值丢失风险**：3 级 `MAIN` 是 BYTE 范围 0..31，2 级 `MAIN` 是 BYTE 范围 0..15。如果 3 级 MAIN 值大于 15，截断到 2 级时会**丢失高位**——这是 EIB 协议本身的限制，不是本 FC 的 bug。业务上调用前要先确认 3 级 MAIN ≤ 15。

**何时用 2 级地址**：与早期不支持 3 级地址的老 KNX/EIB 楼宇设备对接时。现代项目几乎都用 3 级；本 FC 主要用于「老设备兼容」或「多代设备共存」场景。

**与 KL6301 无关**：纯算法函数，不需要 EIB_REC、不依赖 KL6301 状态。可在任何 PLC 任务、任何上下文调用。

## 4. 错误码 / 返回值

本 FC 是纯函数，**无错误码 / 无错误输出**。PDF + InfoSys 均未列出错码。极端值（例 `MAIN > 15`）按 EIB 规范截断或回绕（⚠️ 待人工确认）。

## 5. 使用注意 / 常见坑

- **纯函数无副作用**：可在任何上下文调用。
- **MAIN 值丢精度**：3 级 MAIN 范围 0..31，2 级 MAIN 范围 0..15——值 > 15 会丢失高位。这是 EIB 协议本身的限制。
- **与 `F_CONV_2GROUP_TO_3GROUP` 配对**：反向。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_CONV_3GROUP_TO_2GROUP.TcPOU`](../examples/P_Demo_F_CONV_3GROUP_TO_2GROUP.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）

> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_F_CONV_3GROUP_TO_2GROUP
VAR
    st3 : EIB_GROUP_ADDR := (MAIN := 1, SUB_MAIN := 1, NUMBER := 0);
    st2 : EIB_GROUP_ADDR_2GROUP;
END_VAR
st2 := F_CONV_3GROUP_TO_2GROUP(IN := st3);
```

## 7. 业务场景与实际价值

- **场景**：老 EIB 设备兼容 / 多代设备共存
- **价值**：替代手写位运算
- **替代方案对比**：
  - 手写位运算：要懂 EIB 协议
  - 本 FC：标准选择

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EIB_EN.pdf) §4.2.6.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_eib/187791115.html
- **相关**：`F_CONV_2GROUP_TO_3GROUP`（同库 §4.2.6.1，反向）、`EIB_GROUP_ADDR` / `EIB_GROUP_ADDR_2GROUP`（同库 §4.3.2）
