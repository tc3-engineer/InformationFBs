# FB_EnOcean_Search

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_EnOcean` |
| Library Version | `1.7.1` |
| Type | `FUNCTION_BLOCK` |
| Category | `KL6581 / Search` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173290123.html |
| Verified | 2026-06-03 ✅ |
| InfoSys-checked | ✅ 2026-06-03 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_EnOcean_Search.TcPOU`](../examples/P_Demo_FB_EnOcean_Search.TcPOU) |

---

## 1. 功能简述

KL6581 体系下的 **EnOcean 网络设备扫描 FB**。在 `bStart = TRUE` 期间监听所有进入主端子的电报，把每个**收到的不同 EnOcean ID** 收集到 `ar_ID` 数组（容量 256），同时通过 `iDevices` 报告已发现设备总数。可用于工程调试阶段的"网络扫描"——把覆盖区内全部 EnOcean 设备列一遍。

也支持按 KL6583 节点过滤——每个节点单独开一个本 FB 实例可识别"某个设备能被几个 KL6583 节点同时听到"（射频覆盖诊断）。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bStart     : BOOL;
    str_KL6581 : STR_KL6581;
    byNode     : BYTE;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明（中文） |
|---|---|---|---|
| `bStart` | `BOOL` | — | 电平：TRUE 开启扫描，FALSE 关闭 |
| `str_KL6581` | `STR_KL6581` | — | 必接 `fbKL6581.str_KL6581` |
| `byNode` | `BYTE` | — | KL6583 节点过滤：`0` 监听全部，`1..8` 只听对应节点 |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    bReceive : BOOL := TRUE;
    iDevices : INT;
    ar_ID    : ARRAY [0..255] OF DWORD;
END_VAR
```

| 名称 | 类型 | 说明（中文） |
|---|---|---|
| `bReceive` | `BOOL` | **反相脉冲**，新电报到达时 FALSE 一周期 |
| `iDevices` | `INT` | 已发现的不同 EnOcean ID 总数 |
| `ar_ID` | `ARRAY [0..255] OF DWORD` | 已发现的设备 ID 列表（前 `iDevices` 项有效） |

### VAR_IN_OUT

无。

## 3. 行为说明

**触发**：`bStart` 电平。`TRUE` 期间持续监听并收集新 ID。

**去重逻辑**：本 FB 内部判断"已在 `ar_ID[]` 中"——已收过的 ID 不会重复加入。所以 `iDevices` 是"网络中不同设备数量"而不是"已收到电报总数"。

**最大 256 个**：`ar_ID` 容量 256。超过 256 时新设备不再追加（建议工程中实际容量足够，单办公楼很少超过 256）。

**bReceive 反相**：与其它接收块一致，新电报到达时 FALSE 一周期。

**应用做法**：
1. 工程调试时把 `bStart` 置 TRUE 几分钟，等用户操作所有 EnOcean 设备（每个开关按一下，每只门磁开关一次）。
2. 观察 `iDevices` 数值与 `ar_ID[0..iDevices-1]` 列表，与现场设备清单对照检查覆盖率。
3. 完成后 `bStart := FALSE` 清状态。

**复位行为**：`bStart` 由 FALSE 转 TRUE 通常清空列表重新开始扫（PDF 没明说，但典型实现行为）。

**典型陷阱**：① 应用以为 `iDevices` 自动持久化——重启 PLC 后会清零。② 用 `byNode := 0` 收集全部，分不清"哪个 ID 在哪片 KL6583 覆盖"——需要射频覆盖诊断时各 KL6583 节点各开一个本 FB 实例。

## 4. 错误码 / 返回值

本 FB 无显式错误输出，依赖上游 `fbKL6581.iErrorID`。

## 5. 使用注意 / 常见坑

- **`bStart` 电平**：维持 TRUE 持续扫，要停时显式置 FALSE。
- **`bReceive` 反相**：取沿用 `NOT bReceive`。
- **`ar_ID` 256 上限**：通常够用，超大型项目要分区域用多 KL6581。
- **多 KL6583 节点诊断**：要识别"哪个 ID 离哪个 KL6583 近"，每节点各一个 FB_EnOcean_Search 实例，`byNode` 分 1..8 设置。
- **持久化要应用层做**：扫描结果可以拷到 retain VAR_GLOBAL 持久化保存。
- **学习按键 ID 抓取**：本 FB 抓所有 ID（按下按键、开窗、温控发送都会被列入）。若只想抓"按学习按键的设备"，用 `FB_Rec_Teach_In` 或 `FB_Rec_Teach_In_Ex`。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_EnOcean_Search.TcPOU`](../examples/P_Demo_FB_EnOcean_Search.TcPOU)
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

```iecst
PROGRAM P_Demo_FB_EnOcean_Search
VAR
    fbKL6581       : FB_KL6581;
    fbScan         : FB_EnOcean_Search;
    stKL6581Input  AT %I* : KL6581_Input;
    stKL6581Output AT %Q* : KL6581_Output;
    bDoScan        : BOOL := TRUE;
    nDeviceCount   : INT;
    arrIDs         : ARRAY [0..255] OF DWORD;
END_VAR
fbKL6581(bInit := TRUE, nIdx := 1, stKL6581_in := stKL6581Input, stKL6581_out := stKL6581Output);
fbScan(
    bStart     := bDoScan,
    str_KL6581 := fbKL6581.str_KL6581,
    byNode     := 0,
    iDevices   => nDeviceCount,
    ar_ID      => arrIDs
);
```

## 7. 业务场景与实际价值

- **场景**：工程交付前 / 接管现有项目时做"EnOcean 设备清单核对"。现场可能挂十几到上百只 EnOcean 设备，纸面清单与实际不一定一致。打开本 FB 几分钟，让用户操作所有设备，PLC 自动列出实际在线设备列表，跟纸面对照能立刻看出"哪只装上没启用"或"哪只清单上有但实际没装"。
- **价值**：免去现场拿着 EnOcean 嗅探器跑全场；PLC 端就能做网络发现。
- **替代方案对比**：
  - 用 `FB_Rec_Teach_In`：只抓按学习按键的设备，覆盖率不全
  - 用 EnOcean USB 嗅探器（PC 软件）：需要专门工具
  - **本 FB**：在线工程师 / 调试 PLC 时无需额外工具，最方便

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_EnOcean_EN.pdf) §4.1.2.4.1
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_enocean/173290123.html
- **相关**：`FB_KL6581`（上游必备）、`FB_Rec_Teach_In`/`FB_Rec_Teach_In_Ex`（学习按键 ID 抓取版）、`FB_Rec_Generic`（通用接收）
