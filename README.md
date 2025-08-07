# Claude Code / Open Code Agent Rules

A collection of main orchestrator settings and sub-agent definitions that can be used with Claude Code and Open Code. Operates AI as the main orchestrator, collaborating with specialized sub-agents to streamline development work.

## Features

### 1. Main Orchestrator System
Operates Claude Code as the main orchestrator, **without directly reading or writing code itself**, delegating work to specialized sub-agents.

### 2. Specialized Sub-Agent System
- 8 types of specialized agents handle specific tasks
- Systematic development process following development flow
- Flexible agent selection according to tasks

### 3. Custom Sub-Agent System

#### Overview
A system that operates Claude Code as the main orchestrator and delegates specialized tasks to sub-agents. Sub-agents are defined in Markdown format (.md) and invoked through Claude Code's Task tool.

#### Main Orchestrator Operating Principles
1. **Task Reception**: Receive requests from users
2. **Task Classification**: Determine task nature (new development/modification or other)
3. **Agent Invocation**: Launch sub-agents using Task tool
4. **Parallel Execution**: Invoke multiple sub-agents with Task tool when possible
5. **Result Integration**: Integrate reports from each agent
6. **Final Response**: Return comprehensive results to user

#### Implemented Sub-Agents (8 Types)

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

#### Development Flow Description (defined in workflow_instructions.py)

##### 1. For New Development/Modification
Execute the following development flow in order:

1. **Requirements Understanding & Decomposition** → `/requirement-analyzer`
2. **Development Design** → `/development-designer`
3. **Code Duplication Detection** → `/code-duplication-detector`
4. **Design Docs Creation** → `/design-docs-creator` (User approval required)
5. **Implementation** → `/implementation-agent`
6. **Code Review** → `/code-reviewer`
7. **Code Duplication Re-check** → `/code-duplication-detector`
8. **Testing** → `/test-agent`
9. **UI Operation Verification** → `/playwright-mcp-verifier` (When necessary only)

##### 2. For Other Tasks
**Development flow does not apply**. Respond according to task nature as follows:

- **Implementation Investigation/Code Analysis**: Use `general-purpose` agent
- **Bug Fixes**: Identify problem areas with `/code-reviewer`, fix with `/implementation-agent`
- **Refactoring**: Utilize `/code-duplication-detector` and `/code-reviewer`
- **Testing Only**: Use `/test-agent` directly
- **Other Work**: Use `general-purpose` agent when 8 specialized agents cannot handle

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

### 4. 図表作成ルール

すべてのサブエージェントが図を作成する際は、**必ずMermaid.js**を使用します。フローチャート、シーケンス図、クラス図、ER図など、あらゆる図表はMermaid.js形式で記述されます。

## Open Code対応

このプロジェクトはClaude CodeだけでなくOpen Codeにも対応しています。

### Open Codeでの使用方法

1. **AGENTS.mdの設定**
   - AGENTS.mdはCLAUDE.mdのシンボリックリンクとして既に設定済みです
   - 追加の設定は不要でそのまま使用できます

2. **サブエージェントの配置**
   - Open Codeでサブエージェントを使用する場合は`.opencode/agent/`ディレクトリにコピーしてください：
   ```bash
   mkdir -p .opencode/agent
   cp agents/*.md .opencode/agent/
   ```

3. **設定ファイル（オプション）**
   - 必要に応じて`opencode.json`を作成できます：
   ```json
   {
     "agents": {
       "default": {
         "model": "claude-3-5-sonnet-20241022"
       }
     },
     "instructions": [
       "./AGENTS.md"
     ]
   }
   ```

### Claude CodeとOpen Codeの互換性

- **CLAUDE.md / AGENTS.md**: 完全互換（シンボリックリンクで対応）
- **サブエージェント**: 同じMarkdown形式で互換性あり
- **設定形式**: 両方ともJSON形式で類似の構造

## インストール

### 1. リポジトリのクローン
```bash
git clone https://github.com/your-username/claude-hooks-rules.git
cd claude-hooks-rules
```

### 2. CLAUDE.mdまたはAGENTS.mdを配置

```bash
# Claude Code用
cp CLAUDE.md /path/to/your/project/

# Open Code用（シンボリックリンクとして作成済み）
# AGENTS.md -> CLAUDE.md
```

### 3. 使用開始

Claude CodeまたはOpen Codeを起動すると、自動的に設定が読み込まれます。

## 使い方

Claude CodeまたはOpen Codeを使用すると、以下が自動的に適用されます：

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

3. **バグ修正の場合**
   ```
   ログイン時のエラーを修正して
   ```
   → 必要なエージェントのみが選択的に起動します

## ファイル構成

```
claude-hooks-rules/
├── README.md                         # このファイル
├── CLAUDE.md                         # メインオーケストレーター設定
├── AGENTS.md                         # CLAUDE.mdへのシンボリックリンク（Open Code用）
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

`CLAUDE.md`（またはOpen Codeの場合は`AGENTS.md`）を編集して、開発フローや動作ルールを変更できます。

### 新しいサブエージェントの追加

1. `agents/`ディレクトリに新しい`.md`ファイルを作成
2. YAMLフロントマターでエージェントのメタデータを定義
3. エージェントの責務と動作を記述
4. CLAUDE.mdに必要に応じて呼び出しルールを追加


## トラブルシューティング

### サブエージェントが呼び出されない場合

1. Task toolが正しく使用されているか確認
2. サブエージェント名が正しいか確認（例：`/requirement-analyzer`）
3. Markdown形式のエージェント定義ファイルが存在するか確認

### エラーログの確認

Claude CodeまたはOpen Codeのログを確認してください。


## 貢献

プルリクエストを歓迎します！新しいHookのアイデアやバグ修正など、お気軽にどうぞ。