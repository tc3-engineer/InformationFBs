# F_GetCpuCoreInfo

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_System` |
| Library Version | `1.17.3` |
| Type | `FUNCTION` |
| Category | `General functions` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/8824297099.html |
| Verified | 2026-05-20 ✅ |
| InfoSys-checked | ✅ 2026-05-20 |
| Status | `verified` |
| Example | [`examples/P_Demo_F_GetCpuCoreInfo.xml`](../examples/P_Demo_F_GetCpuCoreInfo.xml) |

---

## 1. 功能简述

F_GetCpuCoreInfo 读取指定 CPU 核心的详细配置信息（基时 / 核心负载上限等）到一个 `ST_CpuCoreInfo` 结构。返回 `HRESULT`，成功 `S_OK`，无效核心索引返回 `0x9811070B`（参数无效）。用于运行期诊断 CPU 配置是否符合工艺时序要求。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    nCpuCoreIndex : DINT;
    pInfo : POINTER TO ST_CpuCoreInfo;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `nCpuCoreIndex` | `DINT` | 要查询的 CPU 核心索引。 |
| `pInfo` | `POINTER TO ST_CpuCoreInfo` | `POINTER TO ST_CpuCoreInfo` —— 调用方分配的结构体地址。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

**调用方式**：同步函数，立即返回。`pInfo` 指向调用方分配的 `ST_CpuCoreInfo` 实例。

**输入约束**：`nCpuCoreIndex` 必须是 TwinCAT 已分配给 PLC 的核心索引（从 `F_GetCpuCoreIndex` 得来）；超出范围返回 `0x9811070B`。

**输出结构**：`ST_CpuCoreInfo` 包含基时 baseTime（PLC 周期最小单位，单位 100ns）、核心负载上限百分比等字段；具体见 InfoSys `ST_CpuCoreInfo` topic。

**典型用法**：上电后诊断各核基时一致性，避免跨核任务在不同 baseTime 下产生周期错位。

## 4. 错误码 / 返回值

本函数返回 `HRESULT`。`SUCCEEDED(hr)` 为 TRUE 表示成功。

| HRESULT | 含义 |
|---|---|
| `S_OK` (0) | 操作成功 |
| `0x9811070B` | 参数无效（invalid parameter values，PDF 明确列出） |
| 其他 | 见 Beckhoff ADS Return Codes 在线表 |

## 5. 使用注意 / 常见坑

- **`pInfo` 必须指向有效 `ST_CpuCoreInfo`**：传 0 或类型错误会读 / 写错地址。永远 `pInfo := ADR(myInfo)`。
- **`HRESULT` 解读**：`SUCCEEDED(hr)` 才看 `pInfo^`；失败时 `pInfo^` 内容未定义。
- **仅在 TwinCAT v3.1.4024.11 以上可用**（PDF 明确），老版本编译报错。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_F_GetCpuCoreInfo.xml`](../examples/P_Demo_F_GetCpuCoreInfo.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）。
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：MAIN 启动时读取本核 baseTime，与工艺要求的 1 ms 周期比较，不匹配时告警。
- **价值**：替代登工程查 Real-time 面板；PLC 代码自助验证 CPU 配置。
- **替代方案对比**：
  - 看 SYSTEM Real-time 面板：登工程才能看。
  - 凭经验默认 1 ms：不可靠。

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_System_EN.pdf) §4.1.7
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_system/8824297099.html
- **相关 FB / FC**：`F_GetCpuCoreIndex`, `F_GetTaskInfo`
