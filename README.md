# Claude Code Hooks Rules

Claude Codeの動作を改善するためのHookスクリプト集です。TDD（テスト駆動開発）の徹底、曖昧な指示の明確化、コンテキストの保持などを自動化します。

さらに、特定のキーワードで有効化できる特殊モードも提供しています。

## 機能

### 1. ワークフロールールの自動適用
- **TDD厳守**: 実装前に必ずテストを先に書くよう促す
- **曖昧な指示の明確化**: 「できれば」「かな」などの曖昧な表現を検出し、要件を明確化
- **設計の確認**: 実装前に影響範囲や代替案を検討

### 2. コンテキストの保持
- 直近3件のユーザー指示を常に記録
- Compact Summary実行後も作業内容を忘れない
- 長時間の作業でも継続性を維持

### 3. コードレビューの促進
- 機能完成時に俯瞰的な視点でのレビューを促す
- 冗長なコードや改善可能な設計を指摘

### 4. モード管理システム

統一的なモード管理システムで、複数のモードを同時に有効化できます。

#### モードの操作

```
# モードを有効化（既存のモードを置き換え）
mode: explain
mode: explain debug test

# モードを追加（既存のモードに追加）
mode on: explain
mode on: debug test

# モードを無効化（特定のモードのみ）
mode off: explain
mode off: debug test

# すべてのモードを無効化
mode: off
mode clear
mode reset

# 現在のモードを確認
mode list
mode status
```

#### 利用可能なモード

##### 解説モード (explain/explanation)
- コード編集時に初心者向けの解説ドキュメントを自動生成
- `docs/code-explanation/`ディレクトリに保存
- なぜその実装方法を選んだか、設計の意図を記録

## インストール

### 1. リポジトリのクローン
```bash
git clone https://github.com/your-username/claude-hooks-rules.git
cd claude-hooks-rules
```

### 2. スクリプトに実行権限を付与
```bash
chmod +x hooks/*.py
```

### 3. Claude Code設定ファイルの更新

`example.settings.json`の内容を参考に、`~/.claude/settings.json`を編集します：

```bash
# 設定ファイルを開く
open ~/.claude/settings.json

# または、提供されている設定をコピー（パスを自分の環境に合わせて修正）
cp example.settings.json ~/.claude/settings.json
```

**重要**: `example.settings.json`内のパスを自分の環境に合わせて修正してください：
- `/Users/user-name/` → `/Users/あなたのユーザー名/`

### 4. Claude Codeを再起動

設定を反映させるために、Claude Codeを再起動してください。

## 使い方

通常通りClaude Codeを使用するだけで、以下が自動的に適用されます：

### テスト例

1. **曖昧な指示のテスト**
   ```
   認証機能を追加できればいいかなと思った
   ```
   → 要件を明確化する質問が表示されます

2. **TDDルールのテスト**
   ```
   ユーザー登録APIを実装して
   ```
   → テストを先に書くように促されます

3. **Compact後のコンテキスト保持テスト**
   ```
   1. 何か指示を出す
   2. /compact を実行
   3. 「続きをやって」と指示
   ```
   → compact前の指示を覚えています

## ファイル構成

```
claude-hooks-rules/
├── README.md                    # このファイル
├── example.settings.json        # Claude Code設定ファイルのサンプル
└── hooks/
    ├── workflow_instructions.py # ワークフロールールとコンテキスト管理
    ├── preserve_context.py      # Compact時のコンテキスト保存
    ├── review_reminder.py       # コードレビューリマインダー
    ├── code_explainer.py        # 解説モード
    └── mode_manager.py          # 統一モード管理システム
```

## カスタマイズ

### ワークフロールールの変更

`hooks/workflow_instructions.py`の`get_workflow_rules()`関数を編集して、独自のルールを追加できます。

### 保存する指示の件数変更

デフォルトでは直近3件の指示を保存しますが、以下のファイルで変更可能です：
- `workflow_instructions.py`: `save_current_prompt()`関数内の`[:3]`
- `preserve_context.py`: `extract_recent_prompts()`関数の`count`パラメータ


## トラブルシューティング

### Hookが動作しない場合

1. Claude Codeを再起動したか確認
2. スクリプトに実行権限があるか確認：`ls -la hooks/`
3. パスが正しいか確認：設定ファイル内のパスが実際のファイルパスと一致しているか

### エラーログの確認

Hookのエラーは標準エラー出力に出力されます。Claude Codeのログを確認してください。

## ライセンス

MITライセンス

## 貢献

プルリクエストを歓迎します！新しいHookのアイデアやバグ修正など、お気軽にどうぞ。