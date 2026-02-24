from flask import Flask, request, jsonify, render_template
import google.generativeai as genai
import os
import json
import re

app = Flask(__name__)

genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-1.5-flash")

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

    prompt = f"""あなたはSNS・ブログ副業のプロコーチです。以下のアンケート結果から発信軸診断レポートを作成してください。

【アンケート結果】
・よく相談されること: {consult}
・褒められた経験: {praise}
・熱中できること: {time_hobby}
・現在のSNS状況: {status}
・月の副業収入: {income}
・週に使える時間: {time_per_week}時間
・6ヶ月後のゴール: {goal}

必ず以下のJSON形式のみで返答してください：
{{
  "strengths": [
    {{"icon": "絵文字", "name": "強みの名前（10文字以内）", "desc": "説明（40文字以内）"}},
    {{"icon": "絵文字", "name": "強みの名前", "desc": "説明"}},
    {{"icon": "絵文字", "name": "強みの名前", "desc": "説明"}}
  ],
  "concept_title": "発信コンセプト（20文字以内）",
  "concept_desc": "説明（100文字程度）",
  "niche_tags": ["タグ1", "タグ2", "タグ3", "タグ4"],
  "tagline": "キャッチフレーズ（30文字以内）",
  "roadmap": [
    {{"period": "期間", "title": "フェーズ名", "tasks": ["タスク1", "タスク2", "タスク3"], "isCurrent": true}},
    {{"period": "期間", "title": "フェーズ名", "tasks": ["タスク1", "タスク2", "タスク3"], "isCurrent": false}},
    {{"period": "期間", "title": "フェーズ名", "tasks": ["タスク1", "タスク2", "タスク3"], "isCurrent": false}},
    {{"period": "期間", "title": "フェーズ名", "tasks": ["タスク1", "タスク2", "タスク3"], "isCurrent": false}}
  ],
  "income_3months": "3000",
  "income_6months": "30000",
  "income_message": "励ましメッセージ（60文字程度）",
  "prompts": {{
    "niche_research": [
      {{"label": "ネタ発掘①", "text": "プロンプト文"}},
      {{"label": "ネタ発掘②", "text": "プロンプト文"}},
      {{"label": "競合分析", "text": "プロンプト文"}}
    ],
    "content_creation": [
      {{"label": "投稿文生成", "text": "プロンプト文"}},
      {{"label": "タイトル作成", "text": "プロンプト文"}},
      {{"label": "キャッチコピー", "text": "プロンプト文"}}
    ],
    "monetization": [
      {{"label": "収益化アイデア", "text": "プロンプト文"}},
      {{"label": "DM営業文", "text": "プロンプト文"}},
      {{"label": "商品企画", "text": "プロンプト文"}}
    ]
  }}
}}"""

    try:
        response = model.generate_content(prompt)
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
