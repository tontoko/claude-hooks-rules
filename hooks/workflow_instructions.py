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

1. TDD厳守
   - 実装を書く前に必ずテストを先に書く
   - テストが失敗することを確認してから実装

2. 実装前の確認
   - ユーザーの意図が曖昧な場合は、最適な順序で質問して明確化
   - 複数の実装方法がある場合は選択肢を提示
   - 影響範囲を考慮した設計を検討

3. コードレビューの視点
   - 機能が完成したら作業範囲のみならず全体を俯瞰
   - 冗長なコードや改善可能な設計を指摘
   - より良いパターンがあれば提案

4. 設計ドキュメント
   - プロジェクトにdesign docsなどのドキュメントがあるか確認
   - 重要な意思決定は記録

これらのルールに従って、あなたの判断で適切に対応してください。
"""

def get_session_id():
    """現在のセッションIDを取得"""
    # プロジェクトディレクトリとプロセスIDからセッション識別子を生成
    project_dir = os.getcwd()
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

def get_recent_context():
    """直近のコンテキストを取得"""
    session_id = get_session_id()
    all_contexts = load_all_contexts()
    
    session_data = all_contexts.get(session_id, {})
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
            "last_access": datetime.now().isoformat()
        }
    
    session_data = all_contexts[session_id]
    session_data["last_access"] = datetime.now().isoformat()
    
    # 新しいプロンプトを追加（最大3件）
    if prompt_text and "/compact" not in prompt_text.lower():
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
    context = get_recent_context()
    explanation_rules = load_explanation_mode_rules()

    # プロンプトに追加する内容を出力
    print(rules + context + explanation_rules)

    sys.exit(0)

if __name__ == "__main__":
    main()
