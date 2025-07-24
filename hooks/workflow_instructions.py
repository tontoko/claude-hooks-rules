#!/usr/bin/env python3
"""ワークフロー指示を注入"""
import json
import sys
from pathlib import Path
import importlib.util
import os

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

def get_recent_context():
    """直近のコンテキストを取得"""
    context_file = Path.home() / ".claude" / "hook_context.json"
    if context_file.exists():
        try:
            with open(context_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get("recent_prompts"):
                    context = "\n【直近の作業内容】\n"
                    for i, prompt in enumerate(data["recent_prompts"][:3], 1):
                        context += f"{i}. {prompt}\n"
                    return context
        except:
            pass
    return ""

def save_current_prompt(prompt_text):
    """現在のプロンプトを保存"""
    context_file = Path.home() / ".claude" / "hook_context.json"
    context_file.parent.mkdir(exist_ok=True)

    # 既存のコンテキストを読み込む
    if context_file.exists():
        try:
            with open(context_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except:
            data = {"recent_prompts": []}
    else:
        data = {"recent_prompts": []}

    # 新しいプロンプトを追加（最大3件）
    if prompt_text and "/compact" not in prompt_text.lower():
        data["recent_prompts"].insert(0, prompt_text[:300])
        data["recent_prompts"] = data["recent_prompts"][:3]

        # 保存
        with open(context_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

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
