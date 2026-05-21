# FB_KL27x1Config

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Bus Terminal configuration` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/2084380939.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_KL27x1Config.xml`](../examples/P_Demo_FB_KL27x1Config.xml) |

---

## 1. 功能简述

配置 KL2751 / KL2761（1 通道调光器端子）：斜坡时间 / 调光模式 / 看门狗超时 / 短路后自动恢复 / 50Hz 或 60Hz 等。运行时不需要持续调，**上电配置一次** 即可。

## 2. 接口定义

### VAR_INPUT

```iecst
VAR_INPUT
    bConfigurate : BOOL;
    bReadConfig : BOOL;
    bSetDimRampAbsolute : BOOL;
    iSetRampTime : INT;
    bSetWatchdogDisable : BOOL;
    iSetWatchdogTimeout : UINT;
    iSetTimeoutOnValue : UINT;
    iSetTimeoutOffValue : UINT;
    iSetDimmerMode : INT;
    bSetOnAfterShortCircuit : BOOL;
    bSetLineFrequency60Hz : BOOL;
    tTimeout : TIME;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `bConfigurate` | `BOOL` | 上升沿写配置。 |
| `bReadConfig` | `BOOL` | 上升沿只读配置。 |
| `bSetDimRampAbsolute` | `BOOL` | FALSE = 斜坡时间针对 0..32767 全程；TRUE = 每一步长固定时间。 |
| `iSetRampTime` | `INT` | 斜坡时间设定（具体含义见 PDF 表）。 |
| `bSetWatchdogDisable` | `BOOL` | TRUE = 关闭看门狗。 |
| `iSetWatchdogTimeout` | `UINT` | 看门狗超时（× 10 ms）。 |
| `iSetTimeoutOnValue` | `UINT` | fail-safe 模式下当前过程数据 > 0 时输出的亮度。 |
| `iSetTimeoutOffValue` | `UINT` | fail-safe 模式下当前过程数据 = 0 时输出的亮度。 |
| `iSetDimmerMode` | `INT` | 调光模式（前沿 / 后沿等，见 PDF 表）。 |
| `bSetOnAfterShortCircuit` | `BOOL` | TRUE = 短路恢复后自动开。 |
| `bSetLineFrequency60Hz` | `BOOL` | TRUE = 60Hz, FALSE = 50Hz。 |
| `tTimeout` | `TIME` | 配置超时。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

`bConfigurate` 上升沿写配置；`bReadConfig` 上升沿只读。`iSetRampTime` 与 `bSetDimRampAbsolute` 配合定义斜坡时间：`bSetDimRampAbsolute = FALSE`（相对）→ 斜坡时间是整个数据区 0..32767 全程的时间；`= TRUE`（绝对）→ 每一调光步长都用相同的 ramp 时间。`iSetWatchdogTimeout`（单位 10 ms 倍数）：现场总线丢失通讯后多少 ms 触发 fail-safe。`iSetTimeoutOnValue` / `iSetTimeoutOffValue` 决定 fail-safe 时输出的亮度（取决于当前过程数据是 > 0 还是 = 0）。`bSetWatchdogDisable = TRUE` 关闭看门狗（不推荐生产线用）。`bSetOnAfterShortCircuit = TRUE` 短路恢复后自动点亮；FALSE 短路后保持灭。`bSetLineFrequency60Hz = TRUE` 表示 60 Hz 市电（北美），FALSE 表示 50 Hz（欧 / 亚）。

## 4. 错误码 / 返回值

本 FB 无具体错误码表；状态由输出参数自行反映。具体错误语义需配合主站 / 现场总线设备手册查询。

## 5. 使用注意 / 常见坑

- **写端子寄存器会改 EEPROM**，**不要循环周期调用 `bConfigurate`**——EEPROM 寿命 10 万次写入。上电时配置一次足够。
- `stInData` / `stOutData` 必须 IN_OUT 链到 System Manager 中端子的过程数据区，否则 FB 与端子之间通讯不通。（工程经验补充）
- PDF 指出"本 FB 不遵循 alternative output format"——意思是过程数据在标准 vs alternative 模式下偏移不同，FB 假定**标准模式**；若 System Manager 中端子设为 alternative 会出错。（工程经验补充）
- `tTimeout` 默认未指定时建议给 ≥ 2 秒，K-bus 端子配置握手较慢。（工程经验补充）
- 错误号 `iErrorId` 见 PDF 5.6 节的 KL Config 错误码表（如端子型号不匹配 / 寄存器写失败）；具体表 PDF 在每个 FB 后会列。（工程经验补充）
- 调光模式与负载类型必须匹配（电感 / 电容 / 阻性）；选错会损坏负载或端子。
- 60Hz / 50Hz 设置必须与市电匹配。

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_KL27x1Config.xml`](../examples/P_Demo_FB_KL27x1Config.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：剧院 LED 调光：8 路 KL2751 端子上电时配置成"前沿调光 + 50 Hz + 短路恢复"。
- **价值**：把调光端子配置代码化，便于多台设备工程批量复制。
- **替代方案对比**：
  - KS2000 工具：要带工具
  - **本 FB**：上电一次

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.6.2
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/2084380939.html
- **相关 FB / FC**：`FB_KL320xConfig`, `FB_ReadCouplerRegs (Tc2_Coupler)`
