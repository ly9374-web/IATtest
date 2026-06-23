# IAT Streamlit 迁移工程

本目录用于把根目录中的 SwiftUI 单文件应用 `IAT` 迁移为模块化的
Python + Streamlit 应用。

当前已完成迁移第 1 至第 8 步：

- 固定原始 SwiftUI 行为基线；
- 建立 Python 工程骨架；
- 记录页面、实验流程、状态和模块映射；
- 实现与 UI 无关的数据模型、词库、Swift 兼容随机数生成器；
- 实现七个 Block、试次生成、会话创建与反应记录；
- 实现正式 Block 数据清洗、统计、D 值和报告生成；
- 实现与 Swift 字段一致的 CSV、JSON 导出；
- 实现 Streamlit 首页、自定义预设弹窗和 JSON 本地持久化；
- 使用 `session_state` 管理首页、弹窗、输入和历史选择状态；
- 实现 `home / instruction / task / report` 单入口状态路由；
- 实现总说明页、返回导航、35%/65% 竖向虚线和 Enter 确认；
- 在进入 task 前原子化创建会话，并修复不完整路由状态；
- 实现独立浏览器反应组件：S/J、`performance.now()`、首次按键、
  错误纠正、300ms 绿色反馈及唯一事件 ID；
- 实现 Python 事件协议校验和 Streamlit rerun 去重；
- 实现完整 TaskView：实时计时、左右标签、剩余题数、S/J、错误反馈、
  竖向虚线、Block 说明遮罩、跳过和七段推进；
- 使用独立 `TaskProgress` 领域控制器记录反应、切换 Block 并完成报告；
- 实现报告页、精确模式 |D| 分级、双行红绿散点图及 CSV/JSON 复制；
- 为领域逻辑建立标准库 `unittest` 回归测试；
- 页面和主要业务链路已完整迁移；下一步为整体视觉与行为回归验收。

原始 `IAT` 文件是迁移期间唯一的行为基线，不应被修改。
完整规格见 [docs/migration_spec.md](docs/migration_spec.md)。
