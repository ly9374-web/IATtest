# IAT SwiftUI → Python + Streamlit 迁移规格

## 1. 基线与不可变约束

- 唯一行为基线：项目根目录 `IAT`。
- 基线行数：1506。
- 基线 SHA-256：
  `9feb5ce8d6f8dac1cc589cab6c3f533cce9b53a3846f2c2c3c055ea3e3470b3f`
- 原实现：SwiftUI，入口为 `ContentView`。
- 目标实现：Python + Streamlit，单入口状态路由。
- 硬性约束：页面组件分布、顺序、可见文案和 UI 层级不变。
- 本规格记录的是现有行为，不在迁移时顺手修正疑似缺陷。
- SwiftUI 未显式给出的窗口尺寸、系统字体具体字族、系统色 RGB、
  导航栏高度等，由操作系统决定；Streamlit 端应使用统一 CSS token
  逼近其视觉效果，并以截图对照作为最终依据。

> 文件系统说明：macOS 默认文件系统大小写不敏感，根目录已有文件
> `IAT`，因此 Python 领域包使用 `iat_core/`，避免与源文件冲突。

## 2. 页面与跳转关系

```text
ContentView / NavigationStack
└── HomeView（首页，标题“IAT 测试”）
    ├── CustomSheetView（“自定义”模态弹窗）
    │   ├── 关闭 → HomeView
    │   ├── 确定/保存 → 保存预设并关闭 → HomeView
    │   └── 历史项选择/删除 → 留在弹窗
    └── 开始 → InstructionView（标题“总说明”）
        └── 确定 → TaskView
            ├── 每个 Block 开始 → BlockIntroOverlay
            ├── 关闭遮罩 → 当前 Block 试次
            ├── 当前 Block 完成 → 下一个 Block 的说明遮罩
            ├── 跳过 → 下一个 Block 或报告
            └── Block 7 完成 → ReportView（标题“报告”）
```

目标 Streamlit 路由状态：

```text
home -> instruction -> task -> report
```

`CustomSheetView` 和 `BlockIntroOverlay` 不是独立页面，分别是
`home` 与 `task` 上的模态层。原 `TaskView` 隐藏返回按钮；迁移后答题
期间也不得显示 Streamlit 自动生成的页面导航或返回控件。

## 3. 全局视觉规则

| 项目 | SwiftUI 基线 |
|---|---|
| 全局字体 | `.system(size: 18)` |
| 页面容器 | `NavigationStack` |
| 系统主文字色 | `.primary` |
| 系统次要文字色 | `.secondary` |
| 主按钮 | `.borderedProminent` |
| 次按钮 | `.bordered` |
| 默认操作 | Enter / `.keyboardShortcut(.defaultAction)` |
| 竖向参考线 | 页面宽度 35% 和 65%，1px，次要色 60% 透明，虚线 `[6,6]` |

Streamlit 实现必须隐藏默认侧栏、菜单、页脚、部署工具栏以及会改变原
布局的默认容器留白。系统色应抽象到 `ui/styles.py`，不可散落在页面中。

## 4. 页面 UI 规格

### 4.1 ContentView

- 根组件：`NavigationStack`。
- 初始页：`HomeView`。
- 对所有子页面施加系统字体 18。

### 4.2 HomeView：首页

页面标题：`IAT 测试`

根布局：

- `VStack(spacing: 44)`。
- 整体 `.padding(32)`。
- 内容按以下顺序自上而下排列。

| 顺序 | 组件 | 文案/占位 | 尺寸与样式 |
|---:|---|---|---|
| 1 | 标题文字 | `你要测试态度的概念` | `.title`，semibold |
| 2 | 单行输入框 | `输入测试目标（例如：环保）` | rounded border，最大宽度 380 |
| 3 | 主按钮 | `开始` | 160×48，borderedProminent |
| 4 | 次按钮 | `自定义` | 160×44，bordered |
| 5 | 提示 VStack | 见下 | 行间距 6，18px，secondary |

提示文字按以下三行显示，顺序不可变：

1. `测试会记录反应时与正确率`
2. `请使用键盘按键作答`
3. `建议在安静环境完成`

行为：

- 概念去除首尾空白后为空时，“开始”禁用。
- 页面出现时从本地载入自定义预设。
- “开始”创建精确模式会话：`isPreciseMode = true`。
- “自定义”打开模态弹窗，不离开首页。

### 4.3 CustomSheetView：自定义弹窗

根布局：

- `VStack(spacing: 16)`。
- `.padding(24)`。
- 最小宽度 520。
- 组件顺序如下。

| 顺序 | 组件 | 文案/占位 | 尺寸与样式 |
|---:|---|---|---|
| 1 | 顶部 HStack | 左侧 `xmark` 图标，右侧 Spacer | 图标 16px、semibold |
| 2 | 标题 | `自定义` | `.title2`、semibold |
| 3 | 输入区 VStack | 见下 | 间距 12 |
| 4 | 历史列表 | 仅在展开时显示 | 最大高度 220 |
| 5 | 底部 HStack | `历史`、`确定`、`保存` | 间距 16 |

输入区顺序：

1. 纵向可扩展圆角输入框：`正面词汇（输入正面词汇匹配词）`
2. 纵向可扩展圆角输入框：`负面词汇（输入负面词汇匹配词）`
3. `HStack(spacing: 12)`：
   - `yy（正面词汇更快）`
   - `zz（负面词汇更快）`

底部按钮：

- `历史`：bordered，切换历史列表显示。
- `确定`：borderedProminent，支持 Enter。
- `保存`：bordered。
- 当前 Swift 行为中，“确定”和“保存”都会保存并关闭。

历史列表每一项：

- 左侧：预设显示名按钮。
- 中间：Spacer。
- 右侧：`xmark.circle.fill`，secondary，plain button。
- 显示名规则：`yy/zz`；空值分别回退为字面量 `yy`、`zz`；
  两者均空时显示 `未命名`。

现有行为必须保留：

- 选择历史预设后填充四个字段。
- 选择预设后 `yy` 和 `zz` 禁用。
- 更新已有预设时只更新正面词汇词、负面词汇词和更新时间，不更新 `yy/zz`。
- 删除当前选中预设后解除选中状态。

### 4.4 InstructionView：总说明

页面标题：`总说明`

根布局：

- `VStack(spacing: 24)`。
- `.padding(32)`。
- 页面叠加 35% 与 65% 两条竖向虚线。

组件顺序：

1. 多行说明文字，左对齐，最大宽度 560：

   ```text
   这是一个反应时分类任务。
   屏幕上方左右会显示两个分类标签。
   当刺激属于左侧标签时按 ‘S’，属于右侧标签时按 ‘J’。
   请尽量又快又准。按错会提示错误，需要改正后才能进入下一题。
   ```

2. `确定`按钮：160×48，borderedProminent，支持 Enter。

### 4.5 TaskView：答题页

页面标题：当前 Block 的 `title`。

根布局：

- 主体 `VStack(spacing: 16)`。
- 整体 `.padding(24)`。
- 隐藏导航返回按钮。
- 页面叠加 35% 和 65% 两条竖向虚线。

主体组件顺序：

1. 顶部 `HStack(alignment: top)`，水平 padding 24，整体 20px semibold。
2. Spacer。
3. 当前刺激词或 `准备中…`。
4. 条件性错误文字。
5. Spacer。

顶部区域为等宽三列：

| 位置 | 内容 | 样式 |
|---|---|---|
| 左 | 当前 `leftLabel` | 左对齐，最大可用宽度 |
| 中 | 计时与剩余题数 VStack | 居中，行间距 4，最大可用宽度 |
| 右 | 当前 `rightLabel` | 右对齐，最大可用宽度 |

中央两行：

- `%.0f ms`：18px semibold，红色。
- `本轮剩余关键词：{block.trials.count - trialIndex}`：
  16px，secondary。

刺激区：

- 正常刺激：56px bold，默认 primary。
- 正确反馈期间：刺激变为绿色。
- 刺激垂直 padding 16。
- 无试次时显示 `准备中…`，24px semibold。
- 首次错误后显示 `错误，请改正`，红色。

答题按钮覆盖层：

- 页面中心位置覆盖一个 HStack。
- 左侧按钮 `S`，右侧按钮 `J`，中间 Spacer。
- 按钮样式 bordered，水平 padding 24。
- 支持无修饰键盘快捷键 `s`、`j`。

右下角覆盖层：

- 按钮：`跳过（正式版删除）`。
- bordered。
- 外边距 24。

关键交互：

- Block 说明遮罩显示、或处于 300ms 过渡时，忽略按键。
- 每题出现时开始计时，计时显示约每 16ms 更新。
- 只记录第一次按键和第一次按键对应的 RT/正确性。
- 第一次正确：刺激绿色 300ms，然后进入下一题。
- 第一次错误：显示错误；之后只有正确键能触发绿色 300ms 和前进。
- 跳过会将当前 Block 所有未完成题记为：正确键、正确、800ms。
- Block 完成后进入下一 Block；Block 7 完成后生成报告。

### 4.6 BlockIntroOverlay：每轮说明遮罩

覆盖整个 TaskView：

- 背景：黑色，opacity 0.4，覆盖安全区。
- 中央卡片 `VStack(spacing: 16)`。
- 卡片 padding 24，最大宽度 600。
- 背景：`ultraThickMaterial`。
- 圆角：16，continuous。

卡片组件顺序：

1. 当前 Block 标题：`.title2`、semibold。
2. Block 指令：22px，居中，多行。
3. `本轮题数：{count}`：20px，secondary。
4. `确定`：160×48，borderedProminent，支持 Enter。

### 4.7 ReportView：报告页

页面标题：`报告`

根布局：

- `ScrollView`。
- 内部 `VStack(alignment: leading, spacing: 20)`。
- `.padding(24)`。

#### 结果解释区

内部 `VStack(alignment: leading, spacing: 8)`：

1. `结果解释`：headline。
2. 动态解释文字：title3、bold、绿色。
3. `兼容正式首此眼动错误概率：{值}`：18px、secondary。
4. `不兼容正式首此眼动错误概率：{值}`：18px、secondary。

上述“首此眼动”按原代码保留，不在迁移阶段修正文案。

#### 统计数据区

内部 `VStack(alignment: leading, spacing: 8)`：

1. `统计数据`：headline。
2. `兼容表情变化度` / `待定`
3. `不兼容表情变化度` / `待定`
4. `兼容正确率` / 动态值
5. `不兼容正确率` / 动态值
6. `当 {concept} 与正面词汇词汇配对时你的反应速度/错误率` / 动态值
7. `当 {concept} 与负面词汇词汇配对时你的反应速度/错误率` / 动态值
8. `D 值` / 动态值

每个统计行使用 HStack：标题在左，Spacer，值在右且 semibold。

精确模式 D 值显示：

```text
|D|：{绝对值，2 位小数} ({等级})
```

等级阈值：

- `< 0.15`：`无明显偏好`
- `< 0.35`：`轻微偏好`
- `< 0.65`：`中等偏好`
- 中性词汇：`强偏好`

#### 散点图区

- 标题 `散点图`：headline。
- 图表高度 240。
- 坐标轴：secondary，1px。
- 左轴 x=32；底轴 y=高度-24。
- x 值为反应时秒数，按当前点集 min/max 线性缩放。
- 兼容点：绿色，基线为图高 35%。
- 不兼容点：红色，基线为图高 70%。
- 点直径 6。
- 每个点具有 `[-0.5, 0.5] × 12px` 的垂直随机抖动。

#### 导出区

内部 `VStack(alignment: leading, spacing: 12)`：

1. `导出`：headline。
2. HStack，间距 16：
   - `复制 CSV`
   - `复制 JSON`
3. 复制后显示 `已复制到剪贴板`：footnote、secondary。

## 5. 七个 Block 规格

### 5.1 总览

当前实现始终按 Block 1→7 顺序执行。`orderCondition` 会随机产生并导出，
但当前并未改变 Block 顺序。`positionCondition` 也会产生，但工厂函数中
传入的 `targetLeft` 没有改变现有固定标签映射。迁移时先忠实保留。

| Block | 标题 | 类型 | 题数 | 左标签 / S | 右标签 / J |
|---:|---|---|---:|---|---|
| 1 | `Block 1：目标分类练习` | targetPractice | 8 | `中性词汇` | `{concept}` |
| 2 | `Block 2：属性分类练习` | attributePractice | 8 | `正面词汇` | `负面词汇` |
| 3 | `Block 3：不兼容联合练习` | incompatiblePractice | 10 | `中性词汇 + 正面词汇` | `{concept} + 负面词汇` |
| 4 | `Block 4：不兼容联合正式` | incompatibleFormal | 15 | `中性词汇 + 正面词汇` | `{concept} + 负面词汇` |
| 5 | `Block 5：目标换位练习` | targetSwapPractice | 10 | `{concept}` | `中性词汇` |
| 6 | `Block 6：兼容联合练习` | compatiblePractice | 10 | `{concept} + 正面词汇` | `中性词汇 + 负面词汇` |
| 7 | `Block 7：兼容联合正式` | compatibleFormal | 15 | `{concept} + 正面词汇` | `中性词汇 + 负面词汇` |

总题数：76。

注：原 Swift 源码把 Block 3/4 标为“兼容”、Block 6/7 标为“不兼容”，
但实际配对恰好相反。本迁移保留题目顺序与按键映射，只修正标题和
`BlockType`，使“目标词 + 正面词汇词”作为兼容条件参与报告计算。

### 5.2 各 Block 分类数量和规则

| Block | target | neutral | positive | negative | S 对应分类 | J 对应分类 | 连续同词规避 |
|---:|---:|---:|---:|---:|---|---|---|
| 1 | 4 | 4 | 0 | 0 | neutral | target | 否 |
| 2 | 0 | 0 | 4 | 4 | positive | negative | 否 |
| 3 | 3 | 3 | 2 | 2 | neutral, positive | target, negative | 是 |
| 4 | 4 | 4 | 4 | 3 | neutral, positive | target, negative | 是 |
| 5 | 5 | 5 | 0 | 0 | target | neutral | 否 |
| 6 | 3 | 3 | 2 | 2 | target, positive | neutral, negative | 是 |
| 7 | 4 | 4 | 4 | 3 | target, positive | neutral, negative | 是 |

Block 说明文字：

| Block | 文案 |
|---:|---|
| 1 | `中性词汇按 S，{concept} 按 J` |
| 2 | `正面词汇按 S，负面词汇按 J` |
| 3、4 | `中性词汇和正面词汇按 S，{concept} 和负面词汇按 J` |
| 5 | `{concept} 按 S，中性词汇按 J` |
| 6、7 | `{concept} 和正面词汇按 S，中性词汇和负面词汇按 J` |

### 5.3 刺激词和随机化

- target 刺激始终为用户输入的 `concept`。
- neutral 从固定 31 个中性词中随机抽取。
- positive/negative 优先使用用户自定义词；相应自定义列表为空时回退默认词。
- 自定义词分隔符：英文逗号、中文逗号、分号、换行、空格、英文斜杠、
  中文斜杠。
- 每次抽取允许重复；随后整体洗牌。
- Block 3、4、6、7 最多进行 20 轮洗牌/交换，尝试避免相邻刺激完全相同。
- 会话 seed 为当前 Unix 时间毫秒。
- 随机数状态更新公式：

  ```text
  state = 2862933555777941757 * state + 3037000493
  ```

  按 UInt64 溢出规则计算；seed 为 0 时使用
  `0x1234567890abcdef`。

## 6. Streamlit session_state 规格

后续所有键应由单一初始化函数创建，页面代码不得自行创建同义状态。

### 6.1 路由与全局状态

| 建议键 | 类型 | 初始值 | Swift 来源/用途 |
|---|---|---|---|
| `page` | str | `"home"` | NavigationStack 当前页面 |
| `initialized` | bool | `False` | 防止 rerun 重复初始化 |
| `concept_text` | str | `""` | HomeView.conceptText |
| `is_precise_mode` | bool | `True` | 当前入口固定为 true |

### 6.2 自定义弹窗与预设

| 建议键 | 类型 | 初始值 | Swift 来源/用途 |
|---|---|---|---|
| `custom_dialog_open` | bool | `False` | showCustomSheet |
| `custom_positive_text` | str | `""` | customPositiveText |
| `custom_negative_text` | str | `""` | customNegativeText |
| `custom_yy_text` | str | `""` | customYYText |
| `custom_zz_text` | str | `""` | customZZText |
| `presets` | list | `[]` | presets |
| `preset_history_open` | bool | `False` | showHistory |
| `selected_preset_id` | str/None | `None` | selectedPresetId |

预设对象字段：

- `id`
- `positive_text`
- `negative_text`
- `yy_text`
- `zz_text`
- `updated_at`

### 6.3 会话领域状态

| 建议键 | 类型 | 初始值 | Swift 来源/用途 |
|---|---|---|---|
| `session` | IATSession/None | `None` | 完整 IATSession |
| `subject_id` | session 内字段 | 新 UUID | subjectId |
| `seed` | session 内字段 | 当前毫秒 | seed |
| `order_condition` | session 内字段 | 1 或 2 | orderCondition |
| `position_condition` | session 内字段 | 1 或 2 | positionCondition |
| `link_positive` | session 内字段 | `喜欢` | linkPositive |
| `link_negative` | session 内字段 | `不喜欢` | linkNegative |
| `blocks` | session 内字段 | 7 Blocks | blocks |
| `responses` | session 内字段 | 76 个空响应 | responses |
| `report` | session 内字段 | `None` | report |

### 6.4 答题运行状态

| 建议键 | 类型 | 初始值 | Swift 来源/用途 |
|---|---|---|---|
| `block_index` | int | `0` | blockIndex |
| `trial_index` | int | `0` | trialIndex |
| `show_error` | bool | `False` | showError |
| `trial_start_time` | float/None | `None` | trialStartTime；浏览器端为准 |
| `first_key` | str/None | `None` | firstKey |
| `block_intro_open` | bool | `True` | showBlockIntro |
| `highlight_correct` | bool | `False` | highlightCorrect |
| `is_transitioning` | bool | `False` | isTransitioning |
| `elapsed_ms` | float | `0.0` | elapsedMs 的显示镜像 |
| `last_event_id` | str/None | `None` | 防止组件事件因 rerun 重复处理 |
| `task_instance_id` | str/None | `None` | 隔离不同试次的浏览器组件状态 |

Swift 的 `showReport` 不需要独立布尔值；Streamlit 中应通过
`page == "report"` 表达，避免出现互相矛盾的路由状态。Swift 的
`timerTask` 也不放入 `session_state`，计时循环属于浏览器组件生命周期。

### 6.5 报告 UI 状态

| 建议键 | 类型 | 初始值 | Swift 来源/用途 |
|---|---|---|---|
| `copy_feedback_kind` | str/None | `None` | showCopied 的可区分版本 |
| `scatter_jitter_seed` | int/None | `None` | 保证 rerun 时散点不跳动 |

## 7. Swift 类型到 Python 模块映射

| Swift 类型/职责 | Python 目标 | 说明 |
|---|---|---|
| `ContentView` | `app.py`, `ui/router.py` | 入口与状态路由 |
| `HomeView` | `ui/home.py` | 首页渲染 |
| `InstructionView` | `ui/instruction.py` | 总说明页 |
| `CustomSheetView` | `ui/custom_dialog.py` | 自定义模态层 |
| `TaskView` | `ui/task.py` | 答题页协调与状态推进 |
| `BlockIntroOverlay` | `ui/task.py` | TaskView 私有 UI 单元 |
| `VerticalGuidesView` | `ui/styles.py` | CSS 竖向虚线 |
| `ReportView` | `ui/report.py` | 报告页 |
| `StatRow` | `ui/report.py` | 报告页私有可复用行 |
| `ScatterPlotView` | `ui/charts.py` | 散点图 |
| `ExportView` | `ui/report.py` | 导出区 UI |
| `CustomPreset` | `iat_core/models.py` | dataclass |
| `CustomPresetStore` | `iat_core/preset_store.py` | JSON 本地存储 |
| `CustomWordConfig` | `iat_core/models.py` | dataclass |
| `IATSession` | `iat_core/session.py` | 会话聚合根 |
| `IATBlock` | `iat_core/models.py` | dataclass |
| `BlockType` | `iat_core/models.py` | Enum |
| `IATTrial` | `iat_core/models.py` | dataclass |
| `StimulusCategory` | `iat_core/models.py` | Enum |
| `TrialResponse` | `iat_core/models.py` | dataclass |
| `StimulusBank` | `iat_core/stimuli.py` | 词库与回退规则 |
| `IATBlockFactory` | `iat_core/block_factory.py` | Block/试次生成 |
| `IATReport` | `iat_core/scoring.py` | 报告数据及生成 |
| `ScoredTrial` | `iat_core/models.py` | dataclass |
| `CleanedTrial` | `iat_core/models.py` | dataclass |
| `ConditionType` | `iat_core/models.py` | Enum |
| `ScatterPoint` | `iat_core/models.py` | dataclass |
| `DataCleaner` | `iat_core/scoring.py` | 清洗规则 |
| `CleanedSet` | `iat_core/models.py` | dataclass |
| `BlockStats` | `iat_core/models.py` | dataclass/计算属性 |
| `Stats` | `iat_core/scoring.py` | 纯统计函数 |
| `ExportBuilder` | `iat_core/exporter.py` | CSV/JSON |
| `ExportTrial` | `iat_core/models.py` | 可序列化 dataclass |
| `SeededRandomNumberGenerator` | `iat_core/block_factory.py` | UInt64 兼容 PRNG |
| S/J 键盘与计时 | `components/reaction_task/` | 浏览器端自定义组件 |
| 固定文案/默认词 | `iat_core/constants.py` | 单一事实来源 |
| 全局尺寸/颜色 | `ui/styles.py` | 单一视觉 token 来源 |

依赖方向必须保持：

```text
app.py
  -> ui/*
      -> iat_core/*
      -> components/reaction_task

iat_core/* 不得导入 streamlit 或 ui/*
```

## 8. 已知现状：迁移时不得静默改变

1. `orderCondition` 不改变 Block 顺序。
2. `targetLeft` 参数在工厂函数中未改变标签和分类映射。
3. “首此眼动错误概率”文案疑似笔误，但必须原样保留。
4. CSV 当前通过逗号直接拼接，没有字段转义。
5. 散点抖动在报告创建时随机生成。
6. “确定”和“保存”都保存并关闭弹窗。
7. 已选历史预设的 `yy/zz` 被锁定，更新时也不会更新这两个字段。
8. 默认正面词汇词中存在重复的“幸福”和“美好”，必须保留。
9. `linkPositive/linkNegative` 仅影响最终解释文案，不改变分类规则。

## 9. 后续阶段的验收基线

### 9.1 静态结构

- 页面数量、组件数量、组件顺序和可见文案与本规格一致。
- 页面不得出现 Streamlit 默认侧栏或额外导航。
- `iat_core` 不依赖 Streamlit。
- 原始 `IAT` 哈希保持不变。

### 9.2 实验流程

- 固定 seed 时，Block 和试次可复现。
- 七个 Block 题数依次为 `8, 8, 10, 15, 10, 10, 15`。
- 总试次数为 76。
- 所有分类到 S/J 的映射与第 5 节一致。
- 首次错误、纠错、300ms 正确反馈和跳过逻辑一致。

### 9.3 视觉回归

至少为以下状态建立同尺寸截图对照：

1. 首页空状态。
2. 首页已输入状态。
3. 自定义弹窗默认状态。
4. 自定义弹窗历史展开状态。
5. 总说明页。
6. Block 说明遮罩。
7. 答题正常状态。
8. 答题错误状态。
9. 答题正确绿色反馈状态。
10. 报告页顶部、统计区、散点图和导出区。

优先比较：

- 组件中心线和左右边界；
- 35%/65% 参考线；
- 固定宽高按钮；
- 页面 padding 和组件间距；
- 字体层级、颜色及条件状态。

## 10. 第 1 步完成边界

本阶段允许：

- 建立目录和空模块；
- 声明目标框架依赖；
- 记录迁移规格。

本阶段明确不包含：

- Streamlit 页面实现；
- 领域模型实现；
- Block 生成、计分、持久化或导出实现；
- 浏览器端按键组件；
- 对原始 Swift 行为的修复；
- 对根目录 `IAT` 的任何修改。
