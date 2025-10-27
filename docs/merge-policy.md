預設：功能分支→PR→Squash & merge（歷史乾淨、便於 bisect）。

多人跨域/長週期功能：Merge commit（保留脈絡，revert 風險低）。

熱修hotfix/文件變更：Rebase & merge 或 FF（線性歷史、快進）。

禁止：任何人直接 push main。

回滾策略：以 PR 聚合的單點 commit（squash 的那顆）做 revert；跨多 PR 的出錯，優先逐 PR 回滾，避免大範圍 revert。

審核重點：PR 必須綠（CI 全過）、至少 1 人 review 才能合併。
