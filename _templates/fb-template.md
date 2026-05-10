# <FB_OR_FC_NAME>

<!--
本模板是强约束。生成文档时必须严格按此格式输出。
缺失字段标 ⚠️ 待人工确认，不要凭空补全。
-->

## 元信息

| 字段 | 值 |
|---|---|
| Library | `Tc2_XXXX` |
| Library Version | `x.y.z` |
| Type | `FUNCTION_BLOCK` / `FUNCTION` |
| Category | `Bistable` / `Counter` / `Timer` / ... |
| Source | `https://infosys.beckhoff.com/.../xxxxx.html` |
| Source PDF | `https://download.beckhoff.com/.../TwinCAT_3_PLC_Lib_Tc2_XXXX_EN.pdf` |
| Verified | `YYYY-MM-DD` ✅ |
| Status | `verified` / `⚠️ verify-failed` / `pending` |
| Example | [`examples/P_Demo_<Name>.xml`](../examples/P_Demo_<Name>.xml) |

---

## 1. 功能简述 (Description)

<!-- 中文一句话说清功能；保留英文术语在括号里。
不许超出 PDF 原文事实。 -->

## 2. 接口定义 (Interface)

### VAR_INPUT

```iecst
VAR_INPUT
    <name> : <type>;
END_VAR
```

| 名称 | 类型 | 说明 | 默认/范围 |
|---|---|---|---|
| `<name>` | `<type>` | <description from PDF> | <default> |

### VAR_OUTPUT

```iecst
VAR_OUTPUT
    <name> : <type>;
END_VAR
```

| 名称 | 类型 | 说明 |
|---|---|---|
| `<name>` | `<type>` | <description from PDF> |

### VAR_IN_OUT

(无 / 见 PDF)

## 3. 行为说明 (Behavior)

<!-- 时序图/状态机/真值表，逐句从 PDF 引用，禁止脑补。
对 PLCopen 运动 FB 必须画状态转移。 -->

## 4. 错误码 / 返回值 (Errors)

| Code | 含义 | 处理建议 |
|---|---|---|
| - | - | - |

<!-- PDF 未列错误码 → 整段写 "PDF 未列出错误码（⚠️ 待人工确认）" -->

## 5. 使用注意 / 常见坑 (Pitfalls)

<!-- 仅写 PDF 中明确提及的注意事项；
工程经验性补充必须标注 "工程经验补充" 与你的依据 -->

- 

## 6. 最小例程 (Minimum Example)

> 配套可导入文件：[`examples/P_Demo_<Name>.xml`](../examples/P_Demo_<Name>.xml)（PLCopenXML，可直接导入 TwinCAT 3 XAE）
>
> 导入步骤：右键 PLC 项目 → Import PLCopenXML → 选该文件 → OK
> 详见 [`examples/README.md`](../examples/README.md)

```iecst
PROGRAM P_Demo_<Name>
VAR
    fb<Name> : <Name>;
    // ...
END_VAR

// 周期调用
fb<Name>(
    // ...
);
```

## 7. 相关 (Related)

- 同类：`<other_FB>`
- 上下游：`<other_FB>`

## 8. 待确认项 (⚠️)

<!-- PDF 上找不到、含糊或矛盾的字段列在这里 -->

- 
