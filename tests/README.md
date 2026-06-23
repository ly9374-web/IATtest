# 测试目录

测试规划分为：

- 领域模型与固定 seed 测试（已实现）；
- 七个 Block 生成与按键映射测试（已实现）；
- 数据清洗、计分与导出测试（已实现）；
- Streamlit 首页、弹窗和状态测试（已实现）；
- 首页、总说明、task/report 状态路由测试（已实现）；
- 浏览器按键和反应时状态机测试（已实现，使用 Node 内置测试器）；
- TaskView 正确、首次错误、纠错、跳过、Block 切换及最终结束测试
  （已实现）；
- 报告统计值、|D| 分级、散点数量/颜色及 CSV/JSON 复制参数测试
  （已实现）；
- 页面结构及视觉回归测试。

当前测试使用 Python 标准库 `unittest`：

```bash
python3 -m unittest discover -s tests -v
```
