#!/usr/bin/env python3
"""Stop時のレビューリマインダー"""
import json
import sys
from pathlib import Path

def should_remind_review():
    """レビューのリマインドが必要か判定"""
    # セッション情報からコード変更があったかチェック
    state_file = Path.home() / ".claude" / "hook_state.json"
    
    if state_file.exists():
        try:
            with open(state_file, 'r', encoding='utf-8') as f:
                state = json.load(f)
                return state.get("code_modified", False)
        except:
            pass
    return False

def main():
    # Stopイベントデータを読み込む
    try:
        event = json.load(sys.stdin)
    except:
        sys.exit(0)
    
    # レビューが必要な場合のみリマインド
    if should_remind_review():
        print("\n【コードレビューのリマインド】")
        print("機能実装が完了しました。以下の観点でレビューを検討してください：")
        print("- 冗長なコードはないか")
        print("- より良い設計パターンが適用できないか")
        print("- テストカバレッジは十分か")
    
    sys.exit(0)

if __name__ == "__main__":
    main()