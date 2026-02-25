from flask import Flask, request, jsonify, render_template
from google import genai
import os
import json
import re

app = Flask(__name__)
client = genai.Client(api_key=os.environ.get("GEMINI_API_KEY"))

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/analyze", methods=["POST"])
def analyze():
    data = request.json
    consult = data.get("consult", "特になし")
    praise = data.get("praise", "記入なし")
    time_hobby = data.get("time", "記入なし")
    status = data.get("status", "不明")
    income = data.get("income", "不明")
    time_per_week = data.get("time_per_week", 7)
    goal = data.get("goal", "不明")

    prompt = f"""あなたはSNS副業のプロコーチです。以下のアンケート結果から発信軸診断レポートをJSON形式で作成してください。

アンケート結果:
- よく相談されること: {consult}
- 褒められた経験: {praise}
- 熱中できること: {time_hobby}
- 現在のSNS状況: {status}
- 月の副業収入: {income}
- 週に使える時間: {time_per_week}時間
- 6ヶ月後のゴール: {goal}

以下のJSON形式のみで返答してください。余分なテキストやコードブロックは不要です:
{{
  "strengths": [
    {{"icon": "絵文字", "name": "強みの名前10文字以内", "desc": "説明40文字以内"}},
    {{"icon": "絵文字", "name": "強みの名前", "desc": "説明"}},
    {{"icon": "絵文字", "name": "強みの名前", "desc": "説明"}}
  ],
  "concept_title": "発信コンセプト20文字以内",
  "concept_desc": "説明100文字程度",
  "niche_tags": ["タグ1", "タグ2", "タグ3", "タグ4"],
  "tagline": "キャッチフレーズ30文字以内",
  "roadmap": [
    {{"period": "1-2ヶ月目", "title": "フェーズ名", "tasks": ["タスク1", "タスク2", "タスク3"], "isCurrent": true}},
    {{"period": "3-4ヶ月目", "title": "フェーズ名", "tasks": ["タスク1", "タスク2", "タスク3"], "isCurrent": false}},
    {{"period": "5ヶ月目", "title": "フェーズ名", "tasks": ["タスク1", "タスク2", "タスク3"], "isCurrent": false}},
    {{"period": "6ヶ月目", "title": "フェーズ名", "tasks": ["タスク1", "タスク2", "タスク3"], "isCurrent": false}}
  ],
  "income_3months": "5000",
  "income_6months": "30000",
  "income_message": "励ましメッセージ60文字程度",
  "prompts": {{
    "niche_research": [
      {{"label": "ネタ発掘1", "text": "このニッチで視聴者が抱える悩みTop5と対応するコンテンツアイデアを教えてください。私のテーマ: {consult}"}},
      {{"label": "ネタ発掘2", "text": "季節やトレンドを活用したネタ10個をリストアップしてください。私のテーマ: {consult}"}},
      {{"label": "競合分析", "text": "このジャンルで人気のSNSアカウントの特徴を分析して、差別化できるポイントを3つ教えてください。テーマ: {consult}"}}
    ],
    "content_creation": [
      {{"label": "投稿文生成", "text": "以下のテーマで投稿文を書いてください。冒頭で読者の悩みに共感し、具体的なアドバイスを3つ、最後に行動を促す一言を入れてください。テーマ: {consult}"}},
      {{"label": "タイトル作成", "text": "クリックされやすいタイトルを10個考えてください。数字、疑問形、ベネフィットを意識して。テーマ: {consult}"}},
      {{"label": "プロフィール文", "text": "SNSのプロフィール文とキャッチコピーを3パターン作ってください。ターゲットは副業初心者。テーマ: {consult}"}}
    ],
    "monetization": [
      {{"label": "収益化アイデア", "text": "月3万円を稼ぐための収益化方法を5つ教えてください。アフィリエイト、note販売、コンサルなど具体的に。テーマ: {consult}"}},
      {{"label": "DM営業文", "text": "コンサルやサービスを売るためのDM文を書いてください。押しつけがましくなく相手の悩みに寄り添う内容で。テーマ: {consult}"}},
      {{"label": "商品企画", "text": "note有料記事またはデジタル商品のアイデアを3つ出してください。タイトル、価格、内容の概要も含めて。テーマ: {consult}"}}
    ]
  }}
}}"""

    try:
        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        text = response.text.strip()
        text = re.sub(r"```json|```", "", text).strip()
        start = text.find('{')
        end = text.rfind('}')
        if start != -1 and end != -1:
            text = text[start:end+1]
        result = json.loads(text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
