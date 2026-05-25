# F_GetVersionTcMc2Drive

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_MC2_Drive` |
| Library Version | `1.14.2` |
| Type | `FUNCTION` |
| Category | `Functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2305793419.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ⚠️ not-on-infosys |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetVersionTcMc2Drive.xml`](../examples/P_Demo_F_GetVersionTcMc2Drive.xml) |

---

## 1. 功能简述

读取 `Tc2_MC2_Drive` 库自身版本号的函数（Function, FC）。给定一个版本元素编号 `nVersionElement`，返回该编号对应的版本数字。

该函数的典型用途是在工程现场或自动化测试脚本里**确认目标 PLC 上链接的库版本**：库版本决定了哪些 FB 可用（例如 `FB_ParkAxis` 需要 `Tc2_MC2_Drive ≥ V3.3.41.0`），上线前用本函数读出主/次/修订号做一次断言，可避免"代码引用了高版本 FB 但目标机器装的是旧库"的隐性故障。

返回类型为 `UINT`，一次只返回一个版本组成部分；要拼出完整 `主.次.修订` 字符串需对 `nVersionElement = 1/2/3` 各调一次。

## 2. 接口定义

### 函数签名

```iecst
FUNCTION F_GetVersionTcMc2Drive : UINT
VAR_INPUT
    nVersionElement : INT;
END_VAR
```

| 名称 | 类型 | 默认值 | 说明 |
|---|---|---|---|
| `nVersionElement` | `INT` | — | 要读取的版本元素：`1` = 主版本号（major）；`2` = 次版本号（minor）；`3` = 修订号（revision） |

### 返回值

| 名称 | 类型 | 说明 |
|---|---|---|
| （函数返回） | `UINT` | 由 `nVersionElement` 选定的那个版本数字。例如库版本为 `1.14.2` 时，`nVersionElement = 1` 返回 `1`、`= 2` 返回 `14`、`= 3` 返回 `2` |

## 3. 行为说明

本函数是**纯函数**：无内部状态、无边沿、无 Busy/Done 时序，输入 `nVersionElement` 后在同一 PLC 周期内即直接返回结果，可在任意位置同步调用。

`nVersionElement` 的取值语义：

- `nVersionElement = 1`：返回主版本号（major number）
- `nVersionElement = 2`：返回次版本号（minor number）
- `nVersionElement = 3`：返回修订号（revision number）

要得到完整的库版本（如 `1.14.2`），需要分别用 `1`、`2`、`3` 调用三次再自行组合。PDF 仅列出 `1/2/3` 三个合法值；传入其它值时的返回内容 ⚠️ PDF 与 InfoSys 均未说明，不应依赖。本函数读取的是**库版本**而非 TwinCAT 运行时版本，也不是连接驱动器的固件版本——驱动器固件需用 `FB_ReadDriveInfo` 或 SoE/CoE 参数读取。

## 4. 错误码 / 返回值

本函数不返回错误码。返回值即版本数字（见 §2）。`nVersionElement` 传非法值的行为 ⚠️ 待人工确认（PDF + InfoSys 均未列出）。

## 5. 使用注意 / 常见坑

- **一次只返回一个元素**：想打印完整版本字符串必须调用三次（`1`/`2`/`3`），不要期望一次拿到 `1.14.2`。
- **返回的是库版本不是固件版本**：常见误解是用本函数判断驱动器固件是否够新——那要读 SoE/CoE 参数或用 `FB_ReadDriveInfo`，本函数只反映 PLC 工程链接的 `Tc2_MC2_Drive` 库版本。
- **版本断言放上线检查里**：建议在初始化阶段读一次并与"代码所需最低版本"比较，不匹配就报警，避免运行到调用某个新 FB 时才崩。
- **`INT` 入参不要传负数或 0**：合法值是 `1/2/3`，其它值无定义。
- **纯函数无副作用**：可放在任何 POU、任何任务里调用，不占用 ADS 通道，无超时风险（工程经验补充）。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetVersionTcMc2Drive.xml`](../examples/P_Demo_F_GetVersionTcMc2Drive.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）

```iecst
// 场景：上电初始化时校验库版本是否满足代码所需最低版本
nMajor    := F_GetVersionTcMc2Drive(1);
nMinor    := F_GetVersionTcMc2Drive(2);
nRevision := F_GetVersionTcMc2Drive(3);
```

## 7. 业务场景与实际价值

- **场景**：多台设备升级 / 跨工厂部署同一套 PLC 工程时，确认每台目标机的 `Tc2_MC2_Drive` 库版本一致；自动化测试脚本里做版本断言。
- **价值**：把"库版本不符导致引用新 FB 失败"的问题从运行期崩溃前移到初始化期可控报警，提升上线确定性。
- **替代方案对比**：
  - 用全局常量 / 库管理器手工查版本：人工、易漏、无法在运行期程序化判断
  - 读 `ST_DriveInfo`（`FB_ReadDriveInfo`）：得到的是**驱动器硬件/固件**信息，不是 PLC 库版本，用途不同
  - **本函数**：程序化读取 PLC 库版本的唯一标准入口

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_MC2_Drive_EN.pdf) §3.1
- **InfoSys topic**：本函数无独立 topic 页，见库根 https://infosys.beckhoff.com/content/1033/tcplclib_tc2_mc2_drive/2305793419.html（⚠️ not-on-infosys）
- **相关条目**：`FB_ReadDriveInfo`（读驱动器硬件信息）
