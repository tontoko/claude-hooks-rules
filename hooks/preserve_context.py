#!/usr/bin/env python3
"""PreCompact時のコンテキスト保存"""
import json
import sys
from pathlib import Path
from datetime import datetime

def extract_recent_prompts(transcript_path, count=3):
    """トランスクリプトから直近のプロンプトを抽出"""
    recent_prompts = []
    
    try:
        with open(transcript_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        for line in reversed(lines[-100:]):
            try:
                entry = json.loads(line)
                if entry.get('type') == 'user':
                    message = entry.get('message', {})
                    content = message.get('content', '')
                    
                    # テキスト内容を抽出
                    if isinstance(content, str):
                        text = content[:300]
                    elif isinstance(content, list):
                        texts = [p.get('text', '') for p in content if p.get('type') == 'text']
                        text = ' '.join(texts)[:300]
                    else:
                        continue
                    
                    if text and "/compact" not in text.lower():
                        recent_prompts.append(text)
                        if len(recent_prompts) >= count:
                            break
            except:
                continue
    except Exception as e:
        print(f"Error reading transcript: {e}", file=sys.stderr)
    
    return recent_prompts

def save_context(recent_prompts):
    """コンテキストを保存"""
    context_file = Path.home() / ".claude" / "hook_context.json"
    context_file.parent.mkdir(exist_ok=True)
    
    context = {
        "recent_prompts": recent_prompts,
        "saved_at": datetime.now().isoformat()
    }
    
    with open(context_file, 'w', encoding='utf-8') as f:
        json.dump(context, f, ensure_ascii=False, indent=2)

def main():
    # PreCompact イベントデータを読み込む
    try:
        event = json.load(sys.stdin)
    except:
        print("Error parsing input", file=sys.stderr)
        sys.exit(1)
    
    transcript_path = event.get('transcript_path', '')
    trigger = event.get('trigger', 'unknown')
    custom_instructions = event.get('custom_instructions', '')
    
    # 直近のプロンプトを抽出して保存
    recent_prompts = extract_recent_prompts(transcript_path)
    save_context(recent_prompts)
    
    # ユーザーへのメッセージ
    print(f"\n[PreCompact] トリガー: {trigger}")
    print(f"直近の{len(recent_prompts)}件の指示を保存しました。")
    print("Compact実行後も作業を継続できます。")
    
    if custom_instructions:
        print(f"\nカスタム指示: {custom_instructions}")
    
    sys.exit(0)

if __name__ == "__main__":
    main()