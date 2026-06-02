# FB_KL3228Config

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Bus Terminal configuration` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/2084386699.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_KL3228Config.TcPOU`](../examples/P_Demo_FB_KL3228Config.TcPOU) |

---

## 1. 功能简述

配置 KL3228（8 通道电阻传感器输入端子）单个通道的传感器类型。与 KL3208 类似但端子型号是 KL3228。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bConfigurate : BOOL;
    bReadConfig : BOOL;
    iSetSensorType : INT;
    tTimeout : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bConfigurate` | `BOOL` | 布尔标志 `bConfigurate`。 |
| `bReadConfig` | `BOOL` | 布尔标志 `bReadConfig`。 |
| `iSetSensorType` | `INT` | 传感器类型编码（按 KL3228 手册表）。 |
| `tTimeout` | `TIME` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

与 `FB_KL3208Config` 用法相同，本 FB 只负责一个通道的配置，8 通道端子需要 8 个 FB 实例。`bConfigurate` 上升沿启动写配置序列（读通用信息 → 写传感器类型寄存器 → 读回校验）。`bReadConfig` 上升沿启动只读序列（不写 EEPROM）。`iSetSensorType` 选传感器类型，编码按 KL3228 手册表（与 KL3208 可能略有差异，按当前接的端子手册选）。执行期间 `bBusy := TRUE`，结束后通过 `bError` / `iErrorId` 反映成功 / 失败。`tTimeout` 限制配置时长，默认建议 ≥ 2 秒以适应 K-bus 握手延迟。

## 4. 错误码 / 返回值

本 FB 无具体错误码表；状态由输出参数自行反映。具体错误语义需配合主站 / 现场总线设备手册查询。

## 5. 使用注意 / 常见坑

- **写端子寄存器会改 EEPROM**，**不要循环周期调用 `bConfigurate`**——EEPROM 寿命 10 万次写入。上电时配置一次足够。
- `stInData` / `stOutData` 必须 IN_OUT 链到 System Manager 中端子的过程数据区，否则 FB 与端子之间通讯不通。（工程经验补充）
- PDF 指出"本 FB 不遵循 alternative output format"——意思是过程数据在标准 vs alternative 模式下偏移不同，FB 假定**标准模式**；若 System Manager 中端子设为 alternative 会出错。（工程经验补充）
- `tTimeout` 默认未指定时建议给 ≥ 2 秒，K-bus 端子配置握手较慢。（工程经验补充）
- 错误号 `iErrorId` 见 PDF 5.6 节的 KL Config 错误码表（如端子型号不匹配 / 寄存器写失败）；具体表 PDF 在每个 FB 后会列。（工程经验补充）
- KL3228 与 KL3208 编码可能不同，按 KL3228 手册选。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_KL3228Config.TcPOU`](../examples/P_Demo_FB_KL3228Config.TcPOU)（TwinCAT 3 原生 .TcPOU，可直接拖入 XAE 的 PLC POUs 文件夹）
>
> 导入步骤：右键 PLC 项目下 POUs 文件夹 → Add → Existing Item → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：KL3228 8 通道温度采集，上电配置每个通道为对应传感器类型。
- **价值**：代码化批量配置。
- **替代方案对比**：
  - KS2000 工具
  - **本 FB**：上电完成

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.6.5
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/2084386699.html
- **相关 FB / FC**：`FB_KL3208Config`, `FB_KL320xConfig`
