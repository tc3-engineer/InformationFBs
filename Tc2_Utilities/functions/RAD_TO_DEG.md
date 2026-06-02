# RAD_TO_DEG

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_Utilities` |
| Library Version | `2.18.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35148299.html |
| Verified | 2026-05-11 ✅ |
| InfoSys-checked | ✅ 2026-05-11 |
| Status | `verified` |
| Example | [`examples/P_Demo_RAD_TO_DEG.TcPOU`](../examples/P_Demo_RAD_TO_DEG.TcPOU) |

---

## 1. 功能简述

角度单位转换：把以 **弧度 (radian)** 为单位的角度转换为以 **度 (degree)** 为单位。算法直接套用关系 `deg = rad × 180 / π`（数学上等价于乘以常数 57.295780）。

返回 `LREAL` 双精度浮点；对任意有限实数输入恒不溢出（除非乘出 ±Inf）。函数无状态、纯计算，PLC 周期内可任意次调用。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    ANGLE : LREAL;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `ANGLE` | `LREAL` | — | 待转换的角度值，单位 弧度 (radian)。 |

### VAR_IN_OUT

无。

### 返回值

| 类型 | 说明（中文） |
|---|---|
| `LREAL` | 对应的 `度 (degree)` 值（`ANGLE * 57.2957795131`）。 |

### VAR_OUTPUT

无（本符号是 `FUNCTION`，结果通过返回值传出）。

## 3. 行为说明

调用即返回 `ANGLE * 57.2957795131`（约 57.29577951308232）。无内部状态机、无累积、无截断。输入 `0.0` 返回 `0.0`；输入超出常用角度范围（例如 `720°`）也照常乘——不做范围归一化（不会自动 mod 360）。输入 `NaN` 或 `±Inf` 时输出 `NaN` 或 `±Inf`（IEC 浮点 NaN 传染语义）。

工程上注意：从 `弧度 (radian)` 转 `度 (degree)` 再转回 `弧度 (radian)` 会因二进制浮点 π 不能精确表达而产生 `1e-15` 量级尾差，不能用 `=` 直接判等，需用 `ABS(a - b) &lt; eps`。

## 4. 错误码 / 返回值

返回 `LREAL`，无错误码、无 `bError`、无 `HRESULT`。输入 `NaN` 时输出 `NaN`，输入 `±Inf` 时输出 `±Inf`，其他情况下永远返回有效浮点数。

## 5. 使用注意 / 常见坑

- **不做归一化**：传入 `720°` 不会自动 mod 360；如需归一化先 `ANGLE := MOD(ANGLE, 360)`。
- **浮点精度**：π 不能精确表达，往返转换有 `1e-15` 量级尾差，业务侧用 `ABS(...) &lt; 1e-9` 容差比较。
- **单位不要搞反**：所有 IEC 三角函数（`SIN` / `COS` / `TAN`）都以 **度 (degree)** 为输入；HMI / 上位机给的角度通常是 **弧度 (radian)**，先 RAD_TO_DEG 再丢给 `SIN()` 是正确组合。
- **极大角度精度衰减**：当 `ANGLE` 远大于 `2π`（如 `1e8 rad`）时，乘法本身仍精确，但作为三角函数输入会丢失低位信息。建议先取模再三角。
- **负角度**：直接乘负常数，结果亦为负；不会自动转 `0..2π`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_RAD_TO_DEG.TcPOU`](../examples/P_Demo_RAD_TO_DEG.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_RAD_TO_DEG
VAR
    lrInputAngle : LREAL := 1.5707963;   // 在线写值改成 0/45/90/180 测试
    lrOutput     : LREAL;                 // 转换后的角度（在线 monitor）
END_VAR

// 单行调用：单位转换为纯算术
lrOutput := RAD_TO_DEG(lrInputAngle);

```

## 7. 业务场景与实际价值

- **场景**：运动控制 / 机器人 / 凸轮表 / 上位 SCADA 通讯。HMI 一般显示角度为 弧度 (radian)（操作员习惯），但 PLC 内的 `SIN / COS / TAN` 都需要 度 (degree)，在两端之间必须做这一步转换。
- **价值**：避免开发者手敲 `PI / 180` 常量（容易把分子分母写反）；本函数把这个常量封装、写一次永远对。
- **替代方案对比**：
  - 手写 `ANGLE * 3.14159265358979 / 180`：能用但易抄错 π 位数
  - `ANGLE * MATH_PI / 180`（如果常量被定义）：依赖项目里的常量定义
  - **本函数**：一行、无依赖、PDF 双源确认

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_Utilities_EN.pdf) 第 4.63 节
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_utilities/35148299.html
- **相关函数**：`DEG_TO_RAD` / `RAD_TO_DEG`、IEC `SIN` / `COS` / `TAN` / `ATAN`
