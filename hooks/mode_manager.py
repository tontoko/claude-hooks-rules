#!/usr/bin/env python3
"""統一モード管理システム"""
import json
from pathlib import Path
from datetime import datetime

class ModeManager:
    def __init__(self):
        self.mode_file = Path.home() / ".claude" / "active_modes.json"
        self.mode_file.parent.mkdir(exist_ok=True)
        
    def load_modes(self):
        """アクティブなモードを読み込む"""
        if self.mode_file.exists():
            try:
                with open(self.mode_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except:
                pass
        return {"modes": [], "updated_at": None}
    
    def save_modes(self, modes_data):
        """モード情報を保存"""
        modes_data["updated_at"] = datetime.now().isoformat()
        with open(self.mode_file, 'w', encoding='utf-8') as f:
            json.dump(modes_data, f, ensure_ascii=False, indent=2)
    
    def parse_mode_command(self, prompt):
        """モードコマンドをパース"""
        import re
        
        # 様々なフォーマットに対応
        patterns = [
            # mode on: xxx yyy
            (r'mode\s+on:\s*(.+?)(?:\n|$)', 'add'),
            # mode off: xxx yyy
            (r'mode\s+off:\s*(.+?)(?:\n|$)', 'remove'),
            # mode: xxx yyy (デフォルトは有効化)
            (r'mode:\s*(.+?)(?:\n|$)', 'set'),
            # mode list / mode status
            (r'mode\s+(list|status)(?:\n|$)', 'list'),
            # mode clear / mode reset
            (r'mode\s+(clear|reset|none)(?:\n|$)', 'clear'),
        ]
        
        prompt_lower = prompt.lower()
        
        for pattern, action in patterns:
            match = re.search(pattern, prompt_lower)
            if match:
                if action == 'list' or action == 'clear':
                    return {"action": action}
                else:
                    modes_str = match.group(1).strip()
                    # カンマまたはスペースで分割
                    modes = [m.strip() for m in re.split(r'[,\s]+', modes_str) if m.strip()]
                    
                    # 特殊ケース: mode: off は clear として扱う
                    if action == 'set' and modes == ['off']:
                        return {"action": "clear"}
                    
                    return {"action": action, "modes": modes}
        
        return None
    
    def update_modes(self, prompt):
        """プロンプトに基づいてモードを更新"""
        command = self.parse_mode_command(prompt)
        
        if not command:
            return None
        
        modes_data = self.load_modes()
        current_modes = modes_data.get("modes", [])
        
        if command["action"] == "clear":
            modes_data["modes"] = []
            self.save_modes(modes_data)
            return "【全モード解除】\n通常のコーディングモードに戻りました。"
            
        elif command["action"] == "list":
            if current_modes:
                return f"【アクティブなモード】\n" + ", ".join(current_modes)
            else:
                return "【アクティブなモード】\nなし（通常モード）"
                
        elif command["action"] == "set":
            modes_data["modes"] = command["modes"]
            self.save_modes(modes_data)
            return f"【モード設定】\n有効: " + ", ".join(command["modes"])
            
        elif command["action"] == "add":
            # 既存のモードに追加
            new_modes = list(set(current_modes + command["modes"]))
            modes_data["modes"] = new_modes
            self.save_modes(modes_data)
            added = [m for m in command["modes"] if m not in current_modes]
            if added:
                return f"【モード追加】\n追加: {', '.join(added)}\n現在有効: {', '.join(new_modes)}"
            else:
                return f"【モード追加】\n既に有効です: {', '.join(command['modes'])}"
                
        elif command["action"] == "remove":
            # 指定されたモードを削除
            removed = [m for m in command["modes"] if m in current_modes]
            new_modes = [m for m in current_modes if m not in command["modes"]]
            modes_data["modes"] = new_modes
            self.save_modes(modes_data)
            if removed:
                if new_modes:
                    return f"【モード削除】\n削除: {', '.join(removed)}\n現在有効: {', '.join(new_modes)}"
                else:
                    return f"【モード削除】\n削除: {', '.join(removed)}\n全モード無効（通常モード）"
            else:
                return f"【モード削除】\n指定されたモードは有効ではありません: {', '.join(command['modes'])}"
        
        return None
    
    def is_mode_active(self, mode_name):
        """特定のモードがアクティブかチェック"""
        modes_data = self.load_modes()
        return mode_name in modes_data.get("modes", [])
    
    def get_active_modes(self):
        """アクティブなモードのリストを取得"""
        modes_data = self.load_modes()
        return modes_data.get("modes", [])