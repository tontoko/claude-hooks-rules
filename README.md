# Claude Code Hooks Rules

Claude Codeの動作を改善するためのHookスクリプト集です。メインオーケストレーターとしてClaude Codeを拡張し、専門的なサブエージェントと連携して開発作業を効率化します。

## 機能

### 1. メインオーケストレーターシステム
Claude Codeをメインオーケストレーターとして動作させ、**自身はコードを直接読み書きせず**、専門的なサブエージェントに作業を委譲します。

### 2. コンテキストの保持
- 直近3件のユーザー指示を常に記録
- /compact実行後はコンテキストを自動的に復元
- Compact Summary実行後も作業内容を忘れない
- セッション別にコンテキストを管理

### 3. コードレビューの促進
- 機能完成時に俯瞰的な視点でのレビューを促す
- 冗長なコードや改善可能な設計を指摘

### 4. カスタムサブエージェントシステム

#### 概要
Claude Codeをメインオーケストレーターとして動作させ、専門的なタスクはサブエージェントに委譲するシステムです。サブエージェントはMarkdown形式（.md）で定義され、Claude CodeのTask toolを通じて呼び出されます。

#### メインオーケストレーターの動作原則
1. **タスク受信**: ユーザーからのリクエストを受け取る
2. **タスク分類**: タスクの性質を判断（新規開発・改修 or その他）
3. **エージェント呼び出し**: Task toolを使用してサブエージェントを起動
4. **並列実行**: 可能な場合はTask toolで複数のサブエージェントを呼び出す
5. **結果統合**: 各エージェントからの報告を統合
6. **最終レスポンス**: ユーザーに総合的な結果を返す

#### 実装されているサブエージェント（8種類）

##### 1. 要件分析エージェント (/requirement-analyzer)
- **責務**: ユーザー要件の分析と明確化
- **機能**:
  - 曖昧な要件の洗い出し
  - 機能要件・非機能要件の整理
  - 制約事項の確認
  - ユースケースの定義

##### 2. 開発設計エージェント (/development-designer)
- **責務**: システム設計とアーキテクチャ決定
- **機能**:
  - アーキテクチャパターンの提案
  - モジュール構成の設計
  - データモデル設計
  - インターフェース定義

##### 3. 重複コード検出エージェント (/code-duplication-detector)
- **責務**: 既存コードの重複を検出
- **機能**:
  - 類似コードパターンの検出
  - リファクタリング候補の提案
  - DRY原則の遵守支援

##### 4. 設計ドキュメント作成エージェント (/design-docs-creator)
- **責務**: 実装前の設計ドキュメント作成
- **機能**:
  - 詳細設計書の作成
  - API仕様の定義
  - データフロー図の作成（Mermaid.js使用）
  - ユーザー承認が必須

##### 5. 実装エージェント (/implementation-agent)
- **責務**: TDDに基づくコード実装
- **機能**:
  - **テストファーストの徹底**
  - design docsに基づく実装
  - エラーハンドリング実装
  - コーディング規約の遵守

##### 6. コードレビューエージェント (/code-reviewer)
- **責務**: コード品質の評価と改善提案
- **機能**:
  - コードレビュー実施
  - リファクタリング提案
  - 可読性・保守性の評価
  - ベストプラクティス準拠チェック

##### 7. テストエージェント (/test-agent)
- **責務**: テスト戦略とテストコード作成
- **機能**:
  - テストケース設計
  - 単体テスト作成
  - 統合テスト作成
  - テストカバレッジ分析

##### 8. Playwright MCP検証エージェント (/playwright-mcp-verifier)
- **責務**: UI動作確認（必要時のみ）
- **機能**:
  - ブラウザ自動テスト
  - UI操作の検証
  - スクリーンショット取得

#### 開発フローの説明（workflow_instructions.pyで定義）

##### 1. 新規開発・改修の場合
以下の開発フローを順番に実行します：

1. **要件理解・分解** → `/requirement-analyzer`
2. **開発設計** → `/development-designer`
3. **重複コード発見** → `/code-duplication-detector`
4. **design docs作成** → `/design-docs-creator` （ユーザー承認必須）
5. **実装** → `/implementation-agent`
6. **コードレビュー** → `/code-reviewer`
7. **重複コード再確認** → `/code-duplication-detector`
8. **テスト** → `/test-agent`
9. **UI動作確認** → `/playwright-mcp-verifier` （必要時のみ）

##### 2. その他のタスクの場合
**開発フローは適用されません**。タスクの性質に応じて、以下のように対応します：

- **実装調査・コード解析**: `general-purpose`エージェントを使用
- **バグ修正**: `/code-reviewer` で問題箇所を特定し、`/implementation-agent` で修正
- **リファクタリング**: `/code-duplication-detector` と `/code-reviewer` を活用
- **テストのみ**: `/test-agent` を直接使用
- **その他の作業**: 8つの専門エージェントで対応できない場合は、`general-purpose`エージェントを使用

**重要**: その他のタスクでも、可能な限り作業はサブエージェントに委譲し、自分でコードを読み書きすることは避けてください。

#### サブエージェント呼び出し形式

```
Task(
    description="[エージェント名]による[タスク内容]",
    prompt="/[エージェント名] [具体的な指示]",
    subagent_type="general-purpose"
)
```

#### 実行ルール
- **Task toolの使用必須**: 各エージェントの呼び出しはTask toolを使用
- **1ステップずつ実行**: 前のステップの結果を確認してから次へ
- **エラー時は適切なステップに戻る**: ユーザー指示または問題発見時
- **自分でコードは触らない**: 全てのコード操作はサブエージェントに委任
- **タスクに応じた判断**: 新規開発・改修以外では開発フローに縛られず、柔軟に対応
- **並列実行の活用**: 可能な場合はTask toolで複数のサブエージェントを呼び出す

#### 設定方法

サブエージェントは通常のClaude Code機能として実装されており、特別な設定は不要です。メインオーケストレーターがTask toolを通じて自動的に呼び出します。

##### 使用例

###### 新機能の開発
```
ユーザー認証機能を実装してください
```
→ 開発フローに従って各エージェントが順番に起動

###### バグ修正
```
ログイン時のエラーを修正してください
```
→ 必要なエージェントのみが選択的に起動

### 5. モード管理システム

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

### 6. 図表作成ルール

すべてのサブエージェントが図を作成する際は、**必ずMermaid.js**を使用します。フローチャート、シーケンス図、クラス図、ER図など、あらゆる図表はMermaid.js形式で記述されます。

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

### オーケストレーターの動作例

1. **新規開発の場合**
   ```
   ユーザー認証機能を実装して
   ```
   → メインオーケストレーターが開発フローに従って各サブエージェントを順番に呼び出します

2. **調査・分析の場合**
   ```
   現在のコードベースの認証実装を調査して
   ```
   → 開発フローは適用されず、general-purposeエージェントまたは適切な専門エージェントを使用します

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
├── README.md                         # このファイル
├── example.settings.json             # Claude Code設定ファイルのサンプル
├── hooks/
│   ├── workflow_instructions.py      # メインオーケストレーターのルール定義とコンテキスト管理
│   ├── preserve_context.py           # PreCompact時のコンテキスト保存
│   ├── review_reminder.py            # コードレビューリマインダー
│   ├── code_explainer.py             # 解説モード
│   └── mode_manager.py               # 統一モード管理システム
└── agents/                           # サブエージェント定義（Markdown形式）
    ├── requirement-analyzer.md       # 要件分析エージェント
    ├── development-designer.md       # 開発設計エージェント
    ├── code-duplication-detector.md  # 重複コード検出エージェント
    ├── design-docs-creator.md        # 設計ドキュメント作成エージェント
    ├── implementation-agent.md       # 実装エージェント
    ├── code-reviewer.md              # コードレビューエージェント
    ├── test-agent.md                 # テストエージェント
    └── playwright-mcp-verifier.md    # Playwright MCP検証エージェント
```

## カスタマイズ

### ワークフロールールの変更

`hooks/workflow_instructions.py`の`get_workflow_rules()`関数を編集して、開発フローや動作ルールを変更できます。

### 新しいサブエージェントの追加

1. `agents/`ディレクトリに新しい`.md`ファイルを作成
2. YAMLフロントマターでエージェントのメタデータを定義
3. エージェントの責務と動作を記述
4. workflow_instructions.pyに必要に応じて呼び出しルールを追加

### 保存する指示の件数変更

デフォルトでは直近3件の指示を保存しますが、以下のファイルで変更可能です：
- `workflow_instructions.py`: `save_current_prompt()`関数内の`[:3]`
- `preserve_context.py`: `extract_recent_prompts()`関数の`count`パラメータ


## トラブルシューティング

### Hookが動作しない場合

1. Claude Codeを再起動したか確認
2. スクリプトに実行権限があるか確認：
   ```bash
   ls -la hooks/
   ```
3. パスが正しいか確認：設定ファイル内のパスが実際のファイルパスと一致しているか

### サブエージェントが呼び出されない場合

1. Task toolが正しく使用されているか確認
2. サブエージェント名が正しいか確認（例：`/requirement-analyzer`）
3. Markdown形式のエージェント定義ファイルが存在するか確認

### コンテキストが保持されない場合

1. `~/.claude/hook_contexts.json`ファイルが作成されているか確認
2. セッションIDが正しく取得されているか確認
3. ファイルの書き込み権限があるか確認

### エラーログの確認

Hookのエラーは標準エラー出力に出力されます。Claude Codeのログを確認してください。


## 貢献

プルリクエストを歓迎します！新しいHookのアイデアやバグ修正など、お気軽にどうぞ。