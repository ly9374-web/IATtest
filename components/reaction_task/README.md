# reaction_task 事件协议

`reaction_task` 是 IAT 答题页的最小浏览器组件。它只负责时间敏感
行为、实时毫秒显示和刺激反馈，不生成 Block、不计分、不推进 Python
会话。

## Python → 浏览器

| 字段 | 类型 | 含义 |
|---|---|---|
| `trial_id` | string | 当前试次的稳定唯一标识；变化时重置并重新计时 |
| `stimulus` | string | 当前刺激词 |
| `correct_key` | `"S"` / `"J"` | 正确按键 |
| `left_label` | string | 顶部左侧分类标签 |
| `right_label` | string | 顶部右侧分类标签 |
| `remaining_count` | integer | 当前 Block 剩余题数（包含当前题） |
| `block_title` | string | Block 说明卡片标题 |
| `block_instruction` | string | Block 说明卡片按键规则 |
| `block_count` | integer | 当前 Block 总题数 |
| `enabled` | boolean | 当前组件是否允许作答 |
| `block_intro_open` | boolean | Block 说明遮罩是否打开 |
| `transitioning` | boolean | Python 是否处于题目切换阶段 |

只有 `enabled=true`、`block_intro_open=false` 且
`transitioning=false` 时接受按键。

## 浏览器 → Python

事件结构：

```json
{
  "version": 1,
  "event_id": "实例ID:试次ID:递增序号",
  "type": "trial_complete",
  "trial_id": "0:0",
  "key": "J",
  "correct_key": "J",
  "first_key": "S",
  "is_correct": false,
  "rt_ms": 432.18,
  "reason": "correction",
  "client_time_ms": 12345.67
}
```

事件类型：

- `trial_complete`：正确反馈显示 300ms 后发送一次，携带第一次 S/J
  按键、首次正确性和由 `performance.now()` 得到的首次反应时。首次即
  正确时
  `reason="first_correct"`；首次错误后改正时
  `reason="correction"`。
- `block_start`：关闭 Block 说明遮罩时发送；反应字段均为 `null`。
- `skip_block`：点击跳过时发送；反应字段均为 `null`。

每个事件都有唯一 `event_id`。Python 必须保存最后处理的 ID，并忽略
重复值，避免 Streamlit rerun 重复写入同一反应。

## 浏览器状态机

```text
blocked
  └─ 遮罩关闭/启用 → ready（performance.now 开始）

ready
  ├─ 第一次正确 → correct（绿色）→ 300ms → trial_complete
  └─ 第一次错误 → error（“错误，请改正”）
                         ├─ 错键：保持 error
                         └─ 正确键 → correct（绿色）→ 300ms → trial_complete
```

- `KeyboardEvent.repeat=true` 的长按重复事件被忽略。
- 第一次按键之后不再改写首次按键和反应时。
- 首次按键不会触发 Streamlit rerun，绿色反馈和纠错都在浏览器内完成。
- `trial_id` 改变会清除错误/绿色状态，并重新开始计时。
- Block 遮罩和跳过按钮与任务表面同属一个 iframe，按可视区域自适应
  高度，避免跨坐标系偏移。
- 组件会尝试同时监听 iframe 和父页面键盘事件；卸载时移除监听。
