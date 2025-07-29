#!/usr/bin/env python3
"""ワークフロー指示を注入"""
import json
import sys
from pathlib import Path
import importlib.util
import os
import hashlib

def get_workflow_rules():
    """基本的なワークフロールール"""
    return """

【重要なワークフロールール】

## メインオーケストレーターとしての動作

あなたはメインオーケストレーターとして動作します。**自分でコードを読んだり書いたりすることは一切せず**、タスクの種類に応じて適切にサブエージェントを呼び出し、その結果を統合してユーザーに報告します。

**【タスク判定ガイドライン】**
開発フローを適用するか判断に迷った場合は、以下を参考にしてユーザーに明示してください：
- "新機能を実装"、"改修"、"機能追加" → 開発フロー適用
- "バグ修正"、"調査"、"テストのみ" → 必要なエージェントのみ使用
- 不明な場合はユーザーに確認してから進める

### タスクの種類と対応方法

#### 1. 新規開発・改修の場合
以下の開発フローを**必須ステップ**として順番に実行します：

**【重要】ステップ完了チェック機能**
- 各ステップは必ず前のステップが完了してから実行すること
- ステップをスキップすることは原則として許可されません
- 例外的にスキップする場合は、ユーザーに明示的な確認を求めること
- エラーが発生した場合は、該当ステップを完了するまで次に進まないこと

**必須開発フロー：**

1. **要件理解・分解** → `/requirement-analyzer`
   - **完了条件**: 要件が明確に分解され、実装範囲が確定している
   - **出力**: 機能要件、非機能要件、制約事項の明確な定義

2. **開発設計** → `/development-designer`  
   - **完了条件**: アーキテクチャ設計と技術選定が完了している
   - **出力**: システム設計書、技術スタック、実装方針

3. **重複コード発見（1回目）** → `/code-duplication-detector`
   - **完了条件**: 設計内容と既存コードの照合が完了し、共通化機会が特定されている
   - **出力**: 設計に対する共通化提案、既存コードでの代替案、重複箇所の一覧

4. **design docs作成** → `/design-docs-creator` 
   - **完了条件**: ユーザー承認を得た詳細設計書が作成されている
   - **出力**: 実装可能レベルの詳細設計書
   - **ユーザー承認必須**: この段階で必ずユーザーの承認を得ること

5. **実装** → `/implementation-agent`
   - **完了条件**: design docsに基づく実装が完了している
   - **出力**: 動作する実装コード、適切なテストコード

6. **コードレビュー** → `/code-reviewer`
   - **完了条件**: コード品質、セキュリティ、パフォーマンスチェックが完了している
   - **出力**: レビュー結果、改善提案

7. **重複コード再確認（2回目）** → `/code-duplication-detector`
   - **完了条件**: 実装後の重複コードが確認されている
   - **出力**: 新たな重複の有無、クリーンアップ提案
   - **重要**: このステップは1回目と異なり、実装後の状態をチェックします

8. **テスト** → `/test-agent`
   - **完了条件**: 包括的なテストが実行され、品質が保証されている
   - **出力**: テスト結果、カバレッジ報告

9. **UI動作確認** → `/playwright-mcp-verifier` （UI変更がある場合は必須）
   - **完了条件**: UIの動作が期待通りに確認されている
   - **出力**: E2Eテスト結果、UI動作確認レポート

**ステップスキップポリシー:**
- やむを得ずステップをスキップする場合は、以下の手順を踏むこと：
  1. スキップする理由を明確に説明
  2. ユーザーに明示的にスキップの許可を求める
  3. スキップによるリスクを説明
  4. 後でそのステップを実行するタイミングを提示

#### 2. その他のタスクの場合
**開発フローは適用されません**。タスクの性質に応じて、実装されている8つのサブエージェントから適切なものを選択して使用します：

- **実装調査・コード解析**: 既存エージェントを組み合わせて対応
- **バグ修正**: `/code-reviewer` で問題箇所を特定し、`/implementation-agent` で修正
- **リファクタリング**: `/code-duplication-detector` と `/code-reviewer` を活用
- **テストのみ**: `/test-agent` を直接使用

**重要**: その他のタスクでも、可能な限り作業はサブエージェントに委譲し、自分でコードを読み書きすることは避けてください。

### 実行ルール

#### 開発フロー実行時の厳格なルール
- **ステップ順序の厳守**: 新規開発・改修時は必ず1→2→3→...→9の順序で実行
- **ステップ完了確認**: 各ステップの完了条件を満たすまで次のステップに進まない
- **スキップ禁止原則**: 原則としてステップのスキップは許可しない
- **エラー時の処理**: エラーが発生した場合は該当ステップを完了するまで継続
- **ユーザー承認の徹底**: design docs作成後は必ずユーザー承認を得る
- **code-duplication-detectorの2回実行**: ステップ3と7で必ず実行すること

#### フロー戻りルール（問題発生時の対応）
- **テストエージェントで失敗**: ステップ5（実装）に戻り、実装を修正
- **コードレビューで重大な問題**: ステップ5（実装）に戻り、指摘事項を修正
- **重複コード再確認で問題**: ステップ5（実装）に戻り、リファクタリング実施
- **UI動作確認で問題**: 問題の性質により適切なステップに戻る
  - 実装の問題: ステップ5（実装）へ
  - 設計の問題: ステップ2（開発設計）へ
- **戻り後の再実行**: 戻ったステップから順番に再度実行する

#### 一般的な実行ルール
- **Task toolの使用必須**: 各エージェントの呼び出しはTask toolを使用
- **1ステップずつ実行**: 前のステップの結果を確認してから次へ
- **エラー時は適切なステップに戻る**: ユーザー指示または問題発見時
- **自分でコードは触らない**: 全てのコード操作はサブエージェントに委任
- **タスクに応じた判断**: 新規開発・改修以外では開発フローに縛られず、柔軟に対応

#### 効率化ルール（開発フロー以外）
- **並列実行の推奨**: 作業上可能な限りサブエージェントは並列で実行する
- **複数エージェントの同時起動**: 同じ種類のサブエージェントでも複数並列で呼び出して良い
- **独立タスクの同時実行**: 独立したタスクは同時に複数のサブエージェントに依頼する
- **効率的な作業の実現**: 並列実行により効率的な作業を実現する

#### ステップ進行チェック
メインオーケストレーターは以下の確認を行うこと：
1. **前ステップの完了確認**: 完了条件が満たされているか
2. **出力の品質確認**: 次のステップに必要な情報が揃っているか
3. **エラーの有無確認**: 問題がある場合は修正完了まで待機
4. **ユーザー承認確認**: 必要な場合は承認を得ているか

### サブエージェント呼び出し形式
```
Task(
    description="[エージェント名]による[タスク内容]",
    prompt="/[エージェント名] [具体的な指示]",
    subagent_type="general-purpose"
)
```

## モード管理コマンドへの応答
- モードコマンドが入力された場合、フックが自動的に処理して結果を表示します
- 【重要】フックが出力した内容（【利用可能なモード】【アクティブなモード】など）をそのまま表示してください
- 追加の説明や独自の解釈は不要です
- フックの出力を無視して独自の応答を作らないでください

## 図表作成ルール
- **すべてのサブエージェントが図を作成する際は、必ずMermaid.jsを使用すること**
- フローチャート、シーケンス図、クラス図、ER図など、あらゆる図表はMermaid.js形式で記述する
- Mermaid.jsの記法に従い、```mermaidブロックで囲んで記述する
- 図の説明が必要な場合は、図の前後に日本語で説明を追加する
- ASCII アートや他の図表形式は使用しない

## 重要な警告事項

### 開発フローの厳格な実行について
- **新規開発・改修タスクにおいて、開発フローのステップスキップは原則禁止です**
- **各ステップが完了するまで、絶対に次のステップに進んではいけません**
- **code-duplication-detectorは必ず2回（ステップ3と7）実行すること**
- **ユーザーがステップスキップを要求した場合でも、リスクを説明し確認を求めること**
- **エラーや問題が発生した場合は、問題解決まで同じステップを継続すること**

### メインオーケストレーターの責務
- **開発フローの進行管理**: 各ステップの完了を厳密に管理
- **品質保証**: 手抜きや省略を許さない品質管理
- **リスク管理**: ステップスキップのリスクを適切に伝達
- **ユーザーとの対話**: 承認が必要な場面での適切な確認

これらのルールに従って、オーケストレーターとして適切にサブエージェントを管理してください。
"""

def get_session_id():
    """Claude CodeのセッションIDを取得"""
    # プロジェクトディレクトリをエスケープ
    project_dir = os.getcwd()
    escaped_dir = project_dir.replace('/', '-')
    
    # Claude履歴ディレクトリ
    claude_project_dir = Path.home() / ".claude" / "projects" / escaped_dir
    
    if claude_project_dir.exists():
        # 最新の.jsonlファイルを探す
        jsonl_files = list(claude_project_dir.glob("*.jsonl"))
        if jsonl_files:
            # 最新のファイルを取得
            latest_file = max(jsonl_files, key=lambda f: f.stat().st_mtime)
            # ファイル名からセッションIDを取得
            session_id = latest_file.stem
            return session_id
    
    # フォールバック: プロセスIDベース
    ppid = os.getppid()
    session_string = f"{project_dir}_{ppid}"
    return hashlib.md5(session_string.encode()).hexdigest()[:12]

def load_all_contexts():
    """全コンテキストを読み込み、古いセッションを削除"""
    context_file = Path.home() / ".claude" / "hook_contexts.json"
    
    if context_file.exists():
        try:
            with open(context_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {}
    else:
        data = {}
    
    # 最新100セッションのみ保持
    if len(data) > 100:
        # アクセス時刻でソートして古いものを削除
        sorted_sessions = sorted(data.items(), key=lambda x: x[1].get('last_access', ''), reverse=True)
        data = dict(sorted_sessions[:100])
    
    return data

def save_all_contexts(data):
    """全コンテキストを保存"""
    context_file = Path.home() / ".claude" / "hook_contexts.json"
    context_file.parent.mkdir(exist_ok=True)
    with open(context_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

def is_after_compact():
    """compact後のセッションかどうかを判定（エラーハンドリング強化）"""
    from datetime import datetime, timedelta
    
    try:
        session_id = get_session_id()
        all_contexts = load_all_contexts()
        session_data = all_contexts.get(session_id, {})
        
        # compactフラグがTrueの場合
        if session_data.get("is_compacted", False):
            return True
        
        # セッション作成から5分以内の場合もcompact後と判定
        if session_data.get("created_at"):
            try:
                created_at = datetime.fromisoformat(session_data["created_at"])
                if datetime.now() - created_at < timedelta(minutes=5):
                    return True
            except Exception as e:
                # 日付解析エラーでも継続
                print(f"Warning: Date parsing error in is_after_compact: {e}", file=sys.stderr)
        
        return False
    except Exception as e:
        # 予期せぬエラーが発生しても継続
        print(f"Error in is_after_compact: {e}", file=sys.stderr)
        return False

def get_recent_context():
    """直近のコンテキストを取得（compact後のセッションのみ、安全性向上）"""
    try:
        session_id = get_session_id()
        all_contexts = load_all_contexts()
        
        session_data = all_contexts.get(session_id, {})
        
        # recent_promptsが存在する場合にコンテキストを返す
        recent_prompts = session_data.get("recent_prompts", [])
        if recent_prompts:
            context = "\n【直近の作業内容】\n"
            for i, prompt in enumerate(recent_prompts[:3], 1):
                # 各プロンプトの安全性チェック
                if prompt and isinstance(prompt, str):
                    context += f"{i}. {prompt}\n"
            return context
        return ""
    except Exception as e:
        # エラー時も空文字列を返して継続
        print(f"Error in get_recent_context: {e}", file=sys.stderr)
        return ""

def save_current_prompt(prompt_text):
    """現在のプロンプトを保存"""
    from datetime import datetime
    
    session_id = get_session_id()
    all_contexts = load_all_contexts()
    
    # セッションデータを初期化または取得
    if session_id not in all_contexts:
        all_contexts[session_id] = {
            "recent_prompts": [],
            "created_at": datetime.now().isoformat(),
            "last_access": datetime.now().isoformat(),
            "is_compacted": False
        }
    
    session_data = all_contexts[session_id]
    session_data["last_access"] = datetime.now().isoformat()
    
    # compactコマンドの検出
    if "/compact" in prompt_text.lower():
        session_data["is_compacted"] = True
    else:
        # 新しいプロンプトを追加（最大3件）
        if prompt_text:
            session_data["recent_prompts"].insert(0, prompt_text[:300])
            session_data["recent_prompts"] = session_data["recent_prompts"][:3]
    
    # 全コンテキストを保存
    save_all_contexts(all_contexts)

def load_explanation_mode_rules():
    """解説モードがアクティブな場合ルールを取得"""
    code_explainer_path = Path(__file__).parent / "code_explainer.py"
    if code_explainer_path.exists():
        spec = importlib.util.spec_from_file_location("code_explainer", code_explainer_path)
        module = importlib.util.module_from_spec(spec)
        try:
            spec.loader.exec_module(module)
            if hasattr(module, "is_explanation_mode_active") and module.is_explanation_mode_active():
                if hasattr(module, "get_explanation_rules"):
                    return module.get_explanation_rules()
        except:
            pass
    
    return ""

def process_mode_updates(input_data):
    """モード更新処理を実行"""
    # mode_managerを通じて全モードを管理
    from mode_manager import ModeManager
    manager = ModeManager()
    user_prompt = input_data.get("prompt", "")
    return manager.update_modes(user_prompt)

def main():
    mode_message = ""
    try:
        # stdinからJSONデータを読み込む
        input_data = json.load(sys.stdin)
        user_prompt = input_data.get("prompt", "")

        # 現在のプロンプトを保存
        save_current_prompt(user_prompt)
        
        # モード更新をチェック
        mode_message = process_mode_updates(input_data)
        if mode_message:
            print(mode_message)
            
        # code_explainerを別プロセスで実行（ルール表示のため）
        code_explainer_path = Path(__file__).parent / "code_explainer.py"
        if code_explainer_path.exists():
            os.system(f"echo '{json.dumps(input_data)}' | python3 {code_explainer_path}")
        
    except:
        # JSONの読み込みに失敗しても続行
        pass

    rules = get_workflow_rules()
    
    # コンテキストはcompact後のみ取得（デバッグ情報付き）
    is_compact_session = is_after_compact()
    if is_compact_session:
        context = get_recent_context()
        # compact後セッション情報をユーザーに表示
        compact_info = "\n【Compact後セッション検出】\n" + \
                      "過去のコンテキストが復元され、開発ルールが適用されます。\n"
        context = compact_info + context
    else:
        context = ""
    
    explanation_rules = load_explanation_mode_rules()
    
    # モードコマンドが実行された場合の追加指示
    mode_command_notice = ""
    if mode_message:
        mode_command_notice = "\n\n【モードコマンド実行結果】\n上記のフック出力をそのまま表示してください。追加の説明は不要です。\n"

    # プロンプトに追加する内容を出力
    print(rules + context + explanation_rules + mode_command_notice)

    sys.exit(0)

if __name__ == "__main__":
    main()
