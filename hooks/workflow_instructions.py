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

### タスクの種類と対応方法

#### 1. 新規開発・改修の場合
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

#### 2. その他のタスクの場合
**開発フローは適用されません**。タスクの性質に応じて、実装されている8つのサブエージェントから適切なものを選択して使用します：

- **実装調査・コード解析**: 既存エージェントを組み合わせて対応
- **バグ修正**: `/code-reviewer` で問題箇所を特定し、`/implementation-agent` で修正
- **リファクタリング**: `/code-duplication-detector` と `/code-reviewer` を活用
- **テストのみ**: `/test-agent` を直接使用

**重要**: その他のタスクでも、可能な限り作業はサブエージェントに委譲し、自分でコードを読み書きすることは避けてください。

### 実行ルール
- **Task toolの使用必須**: 各エージェントの呼び出しはTask toolを使用
- **1ステップずつ実行**: 前のステップの結果を確認してから次へ
- **エラー時は適切なステップに戻る**: ユーザー指示または問題発見時
- **自分でコードは触らない**: 全てのコード操作はサブエージェントに委任
- **タスクに応じた判断**: 新規開発・改修以外では開発フローに縛られず、柔軟に対応
- **並列実行の推奨**: 作業上可能な限りサブエージェントは並列で実行する
- **複数エージェントの同時起動**: 同じ種類のサブエージェントでも複数並列で呼び出して良い
- **独立タスクの同時実行**: 独立したタスクは同時に複数のサブエージェントに依頼する
- **効率的な作業の実現**: 並列実行により効率的な作業を実現する

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
    """compact後のセッションかどうかを判定"""
    from datetime import datetime, timedelta
    
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
        except:
            pass
    
    return False

def get_recent_context():
    """直近のコンテキストを取得（compact後のセッションのみ）"""
    session_id = get_session_id()
    all_contexts = load_all_contexts()
    
    session_data = all_contexts.get(session_id, {})
    
    # recent_promptsが存在する場合にコンテキストを返す
    if session_data.get("recent_prompts"):
        context = "\n【直近の作業内容】\n"
        for i, prompt in enumerate(session_data["recent_prompts"][:3], 1):
            context += f"{i}. {prompt}\n"
        return context
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
    
    # コンテキストはcompact後のみ取得
    if is_after_compact():
        context = get_recent_context()
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
