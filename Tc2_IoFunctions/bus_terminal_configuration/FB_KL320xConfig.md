# FB_KL320xConfig

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_IoFunctions` |
| Library Version | `1.5.3` |
| Type | `FUNCTION_BLOCK` |
| Category | `Bus Terminal configuration` |
| Source PDF | https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf |
| Source InfoSys | https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/2084382859.html |
| Verified | 2026-05-21 ✅ |
| InfoSys-checked | ✅ 2026-05-21 |
| Status | `verified` |
| Example | [`examples/P_Demo_FB_KL320xConfig.xml`](../examples/P_Demo_FB_KL320xConfig.xml) |

---

## 1. 功能简述

配置 KL3201 / KL3202 / KL3204（电阻传感器输入端子，RTD / PT100/PT1000 等）的单个通道传感器类型。多通道端子需要为每个通道单独实例化本 FB（混合配置允许）。

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
| `iSetSensorType` | `INT` | 传感器类型编码（PT100 / PT1000 / Ni100 / 直接电阻 等；具体见 PDF KL3201 手册表）。 |
| `tTimeout` | `TIME` | ADS 命令执行允许的最大时长。默认 `DEFAULT_ADS_TIMEOUT`（约 5 秒）。若现场总线设备应答慢需要适当放大。 |

### VAR_OUTPUT

无。

### VAR_IN_OUT

无。

## 3. 行为说明

本 FB 只负责一个通道的配置。多通道端子需要按通道数实例化对应数量的 FB 实例（混合配置允许，例如通道 1 用 PT100、通道 2 用 PT1000）。`bConfigurate` 上升沿启动写配置序列：先读端子通用信息 → 写传感器类型寄存器 → 读回校验 → 输出端子型号 / 特殊版本 / 通道状态等。`bReadConfig` 上升沿启动只读序列：仅读取当前配置而不写入 EEPROM。执行期间 `bBusy := TRUE`，不接受第二个命令。`iSetSensorType` 选择传感器类型（PT100 / PT1000 / Ni100 / 0-3 kΩ 直接电阻 等），具体取值见 PDF KL3201/3202/3204 手册的传感器类型表。`tTimeout` 限制配置时长，默认建议 ≥ 2 秒以适应 K-bus 端子配置握手。完成后 `bBusy` 落回，`bError` / `iErrorId` 反映成功 / 失败。

## 4. 错误码 / 返回值

本 FB 无具体错误码表；状态由输出参数自行反映。具体错误语义需配合主站 / 现场总线设备手册查询。

## 5. 使用注意 / 常见坑

- **写端子寄存器会改 EEPROM**，**不要循环周期调用 `bConfigurate`**——EEPROM 寿命 10 万次写入。上电时配置一次足够。
- `stInData` / `stOutData` 必须 IN_OUT 链到 System Manager 中端子的过程数据区，否则 FB 与端子之间通讯不通。（工程经验补充）
- PDF 指出"本 FB 不遵循 alternative output format"——意思是过程数据在标准 vs alternative 模式下偏移不同，FB 假定**标准模式**；若 System Manager 中端子设为 alternative 会出错。（工程经验补充）
- `tTimeout` 默认未指定时建议给 ≥ 2 秒，K-bus 端子配置握手较慢。（工程经验补充）
- 错误号 `iErrorId` 见 PDF 5.6 节的 KL Config 错误码表（如端子型号不匹配 / 寄存器写失败）；具体表 PDF 在每个 FB 后会列。（工程经验补充）
- 多通道端子须每通道一个 FB 实例；不要把一个 FB 实例切换通道使用。（工程经验补充）
- 传感器类型编码不同端子型号略有差异（KL3201 vs KL3202 vs KL3204），按当前接的端子手册选。（工程经验补充）

## 6. 最小例程

> 配套可导入文件：[`examples/P_Demo_FB_KL320xConfig.xml`](../examples/P_Demo_FB_KL320xConfig.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK

详见 example xml 文件。

## 7. 业务场景与实际价值

- **场景**：炉温监控：KL3204 多通道电阻输入端子，4 个通道接 4 个 PT100，上电时配 4 个 FB 实例把每通道配为 PT100。
- **价值**：端子配置代码化。
- **替代方案对比**：
  - KS2000 工具：要带工具
  - **本 FB**：纯 PLC 程序

## 8. 参考资料

- **PDF**：[TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf](https://download.beckhoff.com/download/document/automation/twincat3/TwinCAT_3_PLC_Lib_Tc2_IoFunctions_EN.pdf) §3.6.3
- **InfoSys topic**：https://infosys.beckhoff.com/content/1033/tcplclib_tc2_iofunctions/2084382859.html
- **相关 FB / FC**：`FB_KL3208Config`, `FB_KL3228Config`, `FB_KL1501Config`
