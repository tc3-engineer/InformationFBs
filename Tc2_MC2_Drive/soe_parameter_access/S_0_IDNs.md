# S_0_IDNs（SoE Parameter Access 全局常量）

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Drive` |
| Library Version | `1.14.2` |
| Type | `GVL`（VAR_GLOBAL CONSTANT） |
| Category | `SoE Parameter Access` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2305793419.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_S_0_IDNs.xml`](../examples/P_Demo_S_0_IDNs.xml) |

---

## 1. 功能简述

一组用于 **SoE 参数寻址** 的全局常量（VAR_GLOBAL CONSTANT），定义 Sercos IDN 各参数组的**基地址**。Sercos IDN 分若干参数组（S-0、S-1…、P-0…），每组在 `Idn : WORD` 编码里占一段高位；本 GVL 把每组的基地址定义为命名常量，配合 `FB_SoERead` / `FB_SoEWrite` 的 `Idn` 入参使用。

最常用的是 `S_0_IDNs`（= `16#0000`），写法 `S_0_IDNs + 33` 即表示 **S-0-0033**，`S_0_IDNs + 432` 即 **S-0-0432**。相比直接手填 `16#00xx`，用基地址 + 编号的写法更直观、更不易出错，也明确表达了"这是 S-0 组第几号参数"。

## 2. 接口定义

### VAR_GLOBAL CONSTANT（逐字按 PDF §6.1）

```iecst
VAR_GLOBAL CONSTANT
    S_0_IDNs    : WORD := 16#0000;
    S_1_IDNs    : WORD := 16#1000;
    S_2_IDNs    : WORD := 16#2000;
    S_3_IDNs    : WORD := 16#3000;
    S_4_IDNs    : WORD := 16#4000;
    S_5_IDNs    : WORD := 16#5000;
    S_6_IDNs    : WORD := 16#6000;
    S_7_IDNs    : WORD := 16#7000;
    P_0_IDNs    : WORD := 16#8000;
    P_1_IDNs    : WORD := 16#9000;
    P_2_IDNs    : WORD := 16#A000;
    P_3_IDNs    : WORD := 16#B000;
    P_4_IDNs    : WORD := 16#C000;
    P_5_IDNs    : WORD := 16#D000;
    P_6_IDNs    : WORD := 16#E000;
    P_7_IDNs    : WORD := 16#F000;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `S_0_IDNs` | `WORD` | `16#0000` | S-0 标准参数组基地址；`S_0_IDNs + n` 表示 `S-0-nnnn` |
| `S_1_IDNs` | `WORD` | `16#1000` | S-1 参数组基地址 |
| `S_2_IDNs` | `WORD` | `16#2000` | S-2 参数组基地址 |
| `S_3_IDNs` | `WORD` | `16#3000` | S-3 参数组基地址 |
| `S_4_IDNs` | `WORD` | `16#4000` | S-4 参数组基地址 |
| `S_5_IDNs` | `WORD` | `16#5000` | S-5 参数组基地址 |
| `S_6_IDNs` | `WORD` | `16#6000` | S-6 参数组基地址 |
| `S_7_IDNs` | `WORD` | `16#7000` | S-7 参数组基地址 |
| `P_0_IDNs` | `WORD` | `16#8000` | P-0 厂商参数组基地址；`P_0_IDNs + n` 表示 `P-0-nnnn`（如 AX5000 的 P-0-0200） |
| `P_1_IDNs` | `WORD` | `16#9000` | P-1 厂商参数组基地址 |
| `P_2_IDNs` | `WORD` | `16#A000` | P-2 厂商参数组基地址 |
| `P_3_IDNs` | `WORD` | `16#B000` | P-3 厂商参数组基地址 |
| `P_4_IDNs` | `WORD` | `16#C000` | P-4 厂商参数组基地址 |
| `P_5_IDNs` | `WORD` | `16#D000` | P-5 厂商参数组基地址 |
| `P_6_IDNs` | `WORD` | `16#E000` | P-6 厂商参数组基地址 |
| `P_7_IDNs` | `WORD` | `16#F000` | P-7 厂商参数组基地址 |

共 16 个基地址常量：S-0…S-7（标准 Sercos 参数）与 P-0…P-7（厂商专有参数，如 AX5000 的 P-0-xxxx）。

## 3. 行为说明

本 GVL 是**编译期常量**，没有运行时行为、没有时序、没有边沿——它只是给 SoE IDN 寻址提供可读的命名基地址。

**寻址机制**：Sercos IDN 在 `WORD` 里按位编码"参数组 + 组内编号"。`S_0_IDNs = 16#0000` 表示 S-0 组从 0 起，所以 `S_0_IDNs + 33 = 16#0021 = 33` 直接就是 S-0-0033 的编码。`S_1_IDNs = 16#1000` 表示 S-1 组从 `16#1000` 起，`S_1_IDNs + 5` 表示 S-1-0005。

**典型用法**：在调用 `FB_SoERead` / `FB_SoEWrite` 前，先算 `nIdn := S_0_IDNs + 33;`，再把 `nIdn` 传给 FB 的 `Idn` 入参。这正是 PDF 各 SoE FB 示例采用的写法。

**为何用基地址而非裸值**：① 可读性——`S_0_IDNs + 432` 一眼看出是 S-0-0432；② 不易错——避免手算 `16#01B0` 这类十六进制；③ 表达组归属——`S_1_IDNs + n` 明确这是 S-1 组参数，不会和 S-0 组混。

## 4. 错误码 / 返回值

本 GVL 是常量集合，无返回值、无错误码。错误处理在使用它的 `FB_SoERead` / `FB_SoEWrite` 上（见对应文档的 `AdsErrId` / `SercosErrId`）。

⚠️ 若 `Idn` 算错（基地址选错组、编号超出该组范围），会在 SoE FB 上体现为 `SercosErrId ≠ 0`（IDN 不存在/越界），不是本 GVL 报错。

## 5. 使用注意 / 常见坑

- **基地址要选对组**：S-0 参数用 `S_0_IDNs`，S-1 参数用 `S_1_IDNs`；选错组会指向完全不同的参数，SoE FB 报 `SercosErrId`。
- **`+ n` 的 n 是十进制组内编号**：`S_0_IDNs + 33` = S-0-0033，不是 S-0-0021；别把 IDN 文档里的十进制编号当十六进制填。
- **P 组是厂商专有参数**：AX5000 的 `P-0-0200`（电压）等用 `P_0_IDNs + 200` 寻址；P 组参数含义查具体驱动器手册，不同厂商不同。
- **类型是 `WORD`**：与 `FB_SoERead.Idn : WORD` 匹配，运算结果仍是 `WORD`，注意不要溢出组边界。
- **编译期常量无副作用**：可在任意位置引用，不占资源（工程经验补充）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_S_0_IDNs.xml`](../examples/P_Demo_S_0_IDNs.xml)

```iecst
// 场景：用 S_0_IDNs 基地址拼出几个常用 IDN，供 SoE 读写 FB 使用
nIdnS00033 := S_0_IDNs + 33;    // S-0-0033
nIdnS00432 := S_0_IDNs + 432;   // S-0-0432（序列号）
nIdnS10005 := S_1_IDNs + 5;     // S-1-0005
```

## 7. 业务场景与实际价值

- **场景**：任何用 `FB_SoERead` / `FB_SoEWrite` 访问 Sercos 参数的代码，用本 GVL 拼 `Idn`，覆盖伺服参数读写、诊断、配置校验等。
- **价值**：让 IDN 在代码里以"组 + 编号"可读形式出现，降低手算十六进制的出错率，并明确参数组归属。
- **替代方案对比**：
  - 直接手填 `16#00xx`：要手算十六进制，易错、不可读
  - 自定义常量重新定义 IDN 基地址：重复造轮子，且可能与库定义不一致
  - **本 GVL**：库自带的 SoE IDN 寻址标准常量

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf) §6.1 SoE Parameter Access
- **InfoSys topic**：本 GVL 无独立 topic 页，见库根 https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2305793419.html（⚠️ not-on-infosys）
- **相关条目**：`FB_SoERead` / `FB_SoEWrite`（用本 GVL 拼 `Idn`）、`FB_SoEWritePassword`、`FB_SoEReset`
