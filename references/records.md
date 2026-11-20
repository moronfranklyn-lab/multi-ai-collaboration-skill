# 记录规范

字段可映射到现有文档、表格或数据库。UNKNOWN 表示未知，不代表否定、失败或授权。小任务只填会影响交接、核验与恢复的字段。

## 实例能力

| 字段 | 含义 |
|---|---|
| instance | 模型名称、客户端、运行环境及实例别名 |
| platform_identity | 用户、机器人或服务账户及非敏感身份别名 |
| authorization | 测试范围与授权依据 |
| test_target | 获准测试的对象及定位，敏感标识仅放私有记录 |
| capabilities | read/create/append/update/delete/publish 分开记录 |
| evidence_status | 直接测试、他方报告或未知 |
| tested_at / evidence | 实测时间、返回结果或可核验定位 |
| limits / retest_when | 目标范围、限制及需重测条件 |

能力结果可为 passed、failed、not_tested；“他方报告 passed”与“本实例实测 passed”分开表达。失败只说明该身份、对象、时间与操作条件下失败，不能推导整个平台不可用。测试通过也不代表未来永久可用。

## 交接包

最小交接包含目标、输入、交付物、验收；引用已有契约即可，无须重复全文。跨工具或修改共享状态时，按需补充负责人、输入版本、证据状态、可写范围、接收方能力、冲突点和审计入口。使用 [交接模板](../templates/handoff.md)。

“方案完成”“已写入”“已验收”是不同状态。接收者无写权限时，交付待合并稿，标明下一责任人。不得因模板有某字段而反复索取与任务无关的信息。

## 审计事件

通用机器可读模板见 [change-event.json](../templates/change-event.json)。项目可以沿用自己的字段名，保持以下语义即可：

| 字段 | 含义 |
|---|---|
| event_id / task_id | 事件唯一标识与关联任务；一次任务可有多个事件 |
| event_type | capability_check、change、publish、correction、supersede、rollback |
| proposed_by | 提出变更的人或实例 |
| executed_by_instance / platform_identity | 实际执行工具实例与平台身份 |
| recorded_by_instance | 实际补记台账的实例，可与执行者不同 |
| occurred_at / recorded_at | 动作发生与记录时间，建议带时区；不以记录时间冒充发生时间 |
| target / scope | 对象定位、具体修改部分及操作 |
| before_version / after_version | 实际版本或 UNKNOWN，不虚构版本号 |
| diff_or_snapshot | 可核验差异或前后版本定位；敏感快照须受控 |
| authorization_reference | 用户授权或有效规则中的具体范围 |
| evidence | 返回结果、回读、测试或验收的可核验定位 |
| result / limitations | 实际操作结果及未完成部分 |
| audit_status | 可选：pending、recorded、needs_verification；与业务操作结果分开 |
| related_event_ids | 更正、替代、回滚或补记关联的事件 |

结果语义：

- succeeded：所记录范围内的操作已验证完成，不自动等于业务验收。
- partial：只完成部分范围，明确哪些成功、哪些失败。
- failed：目标操作失败，保留可核验原因与任何实际副作用。
- pending_merge：产物已准备，等待有权维护者合并。
- needs_verification：缺少证据，不能确定最终状态。

事件只追加。发现错误时新增 correction 并引用原事件；规则替代新增 supersede，回滚新增 rollback。不得擦除原事件以制造无错历史。

事件编号可按项目、日期和实例生成，或使用平台唯一 ID。编号重复检查再创建只减少意外重复，不能保证并发唯一；需要严格幂等时使用平台唯一约束、幂等键、锁或串行提交。出现重复事件时追加说明其关系，不悄悄删除。

## 证据与版本

“直接观察”“当事人报告”“用户决定”“AI 推断”“待确认”是来源或性质标记，不是单一从低到高的置信度阶梯。用户决定可以确立工作安排，不能凭决定确立外部事实。引用时尽可能带材料版本、章节、页码、录音时间戳或记录定位。

内容哈希只证明所比较字节是否相同，不证明内容真实、授权有效或来源可靠。无法获取平台版本时，可用允许保存的摘要、修改前后片段或快照，说明限制。原始事件日期、最近核实日期和录入日期分别记录。

审计记录失败时，最小待补事件至少含事件编号、实际操作、发生时间、已知结果、证据和补记状态，并明确下一责任人与恢复触发方式。临时文件放在受控位置，恢复后核实是否已有同事件；它不成为另一套长期跨实例台账。用户未安排后续执行时，不承诺自动补记。
