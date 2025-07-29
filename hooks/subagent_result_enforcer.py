#!/usr/bin/env python3
"""SubagentStop時にメインエージェントへの結果報告を強制"""
import json
import sys

def main():
    try:
        # SubagentStopイベントデータを読み込む
        event = json.load(sys.stdin)
        subagent_response = event.get('response', '')
        subagent_name = event.get('subagent_name', '不明なサブエージェント')
        
        # サブエージェントの応答が結果報告形式になっているかチェック
        required_sections = [
            "実施した内容",
            "発見事項", 
            "次のステップへの推奨事項"
        ]
        
        missing_sections = []
        for section in required_sections:
            if section not in subagent_response:
                missing_sections.append(section)
        
        # 結果報告が不完全な場合の警告メッセージ
        if missing_sections:
            warning_message = f"""
⚠️ **サブエージェント結果報告不備**

サブエージェント「{subagent_name}」の結果報告に以下の必須項目が不足しています：
{chr(10).join(['- ' + section for section in missing_sections])}

**必須報告形式：**
## 作業結果報告

### 実施した内容
- 具体的に実行した作業内容

### 発見事項  
- 発見した問題、成功した点、分析結果

### 次のステップへの推奨事項
- 必要なアクション、推奨事項

### エラーや問題（該当する場合）
- 発生した問題とその対処法

**メインオーケストレーターは上記報告を受けて次の判断を行ってください。**
"""
            print(warning_message)
        else:
            # 結果報告が適切な場合の確認メッセージ
            print(f"✅ サブエージェント「{subagent_name}」から適切な結果報告を受信しました。")
            
    except Exception as e:
        print(f"SubagentStop処理エラー: {e}", file=sys.stderr)
    
    sys.exit(0)

if __name__ == "__main__":
    main()