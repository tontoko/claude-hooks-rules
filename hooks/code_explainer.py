#!/usr/bin/env python3
"""コード解説書を逐次生成・更新するHook"""
import json
import sys
from pathlib import Path
from datetime import datetime
sys.path.append(str(Path(__file__).parent))
from mode_manager import ModeManager

def is_explanation_mode_active():
    """解説モードがアクティブか確認"""
    manager = ModeManager()
    return manager.is_mode_active("explain") or manager.is_mode_active("explanation")

def get_explanation_rules():
    """解説モード用のルール"""
    return """

【コード解説モード有効】

コードを編集・作成する際は、必ず以下を実行してください：

1. 解説ドキュメントの更新
   - `docs/code-explanation/` ディレクトリに解説を保存
   - ファイル名: `{機能名}_explanation.md`
   - 初心者でも理解できるレベルで記述

2. 各ファイル編集時の記録内容
   - なぜこのファイルを編集するのか
   - どのような処理を行っているか
   - 他のファイルとの関係性
   - よくある誤解や注意点

3. 解説の構成
   ```markdown
   # [機能名]の実装解説
   
   ## 概要
   この機能が何をするのか、なぜ必要なのか
   
   ## 実装の流れ
   1. ステップバイステップの説明
   2. 各ステップで何が起きているか
   
   ## コード解説
   - 重要な関数やクラスの説明
   - なぜその実装方法を選んだか
   - 設計上の意図と判断理由
   
   ## 関連ファイル
   - どのファイルと連携しているか
   - データの流れ
   ```

4. 図やダイアグラムの追加推奨
   - mermaidやasciiアートで視覚化
   - 複雑な処理フローは必ず図解

このモードでは、コード品質よりも理解しやすさを優先してください。
"""

def main():
    """解説モードがアクティブな場合のみルールを出力"""
    # 解説モードがアクティブな場合はルールを表示
    if is_explanation_mode_active():
        print(get_explanation_rules())
    
    sys.exit(0)

if __name__ == "__main__":
    main()