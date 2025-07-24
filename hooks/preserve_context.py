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
    """コンテキストを保存（セッション管理版）"""
    # workflow_instructions.pyと同じロジックを使用
    import hashlib
    import os
    
    # セッションIDを生成
    project_dir = os.getcwd()
    ppid = os.getppid()
    session_string = f"{project_dir}_{ppid}"
    session_id = hashlib.md5(session_string.encode()).hexdigest()[:12]
    
    # 全コンテキストを読み込み
    context_file = Path.home() / ".claude" / "hook_contexts.json"
    if context_file.exists():
        try:
            with open(context_file, 'r', encoding='utf-8') as f:
                all_contexts = json.load(f)
        except:
            all_contexts = {}
    else:
        all_contexts = {}
    
    # セッションデータを更新
    if session_id not in all_contexts:
        all_contexts[session_id] = {}
    
    all_contexts[session_id].update({
        "recent_prompts": recent_prompts,
        "saved_at": datetime.now().isoformat(),
        "last_access": datetime.now().isoformat()
    })
    
    # 最新100セッションのみ保持
    if len(all_contexts) > 100:
        sorted_sessions = sorted(all_contexts.items(), key=lambda x: x[1].get('last_access', ''), reverse=True)
        all_contexts = dict(sorted_sessions[:100])
    
    # 保存
    context_file.parent.mkdir(exist_ok=True)
    with open(context_file, 'w', encoding='utf-8') as f:
        json.dump(all_contexts, f, ensure_ascii=False, indent=2)

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