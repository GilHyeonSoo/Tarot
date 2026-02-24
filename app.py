from flask import Flask, jsonify, request, Response
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from openai import OpenAI
import os
import json
import logging
from dotenv import load_dotenv
from tarot_data import get_all_cards, get_card_by_id

load_dotenv()

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# CORS 설정 - 허용할 도메인 지정 (프로덕션에서는 실제 도메인으로 변경)
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000").split(",")
CORS(app, origins=ALLOWED_ORIGINS)

# Rate Limiter 설정
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)

# DeepSeek API 설정
client = None
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY")

if DEEPSEEK_API_KEY:
    client = OpenAI(
        api_key=DEEPSEEK_API_KEY,
        base_url="https://api.deepseek.com"
    )

# 토큰 설정 (조절 가능)
TOKENS_NORMAL = 600   # 1~9번 카드 (더 자세한 해석)
TOKENS_FINAL = 2500   # 10번 카드 (종합 요약 포함)

# 카드 위치별 의미 (다국어)
POSITION_MEANINGS = {
    'ko': [
        ("현재 상황", "질문하는 사람의 현재 상황"),
        ("방해 요소", "현재 상황을 가로막는 방해물"),
        ("잠재의식", "무의식, 잠재의식, 문제의 본질"),
        ("과거", "가까운 과거의 상황"),
        ("가능성", "앞으로 발전할 가능성"),
        ("가까운 미래", "가까운 미래의 상황"),
        ("자기 인식", "스스로 인식하는 자신의 감정"),
        ("주변 환경", "주변사람들의 생각이나 영향력"),
        ("희망과 두려움", "바라는 점, 두려워하는 것"),
        ("최종 결과", "최종적인 결과, 결론")
    ],
    'en': [
        ("Present Situation", "The querent's current circumstances"),
        ("Obstacle", "Challenges blocking the current path"),
        ("Subconscious", "Hidden desires, subconscious, root of the matter"),
        ("Past", "Recent past events"),
        ("Potential", "Emerging influences and possibilities"),
        ("Near Future", "What the near future holds"),
        ("Self-Perception", "How you perceive yourself"),
        ("Environment", "Others' thoughts and influence"),
        ("Hopes & Fears", "Deepest hopes and hidden fears"),
        ("Outcome", "Final result and conclusion")
    ],
    'zh': [
        ("当前状况", "提问者目前的处境"),
        ("阻碍因素", "正在阻碍前行的障碍"),
        ("潜意识", "隐藏的欲望、潜意识、问题根源"),
        ("过去", "近期的过去"),
        ("可能性", "正在浮现的影响力和未来机遇"),
        ("近期未来", "不久后即将发生的事"),
        ("自我认知", "自己对自己的看法和内在感受"),
        ("周围环境", "周围人的想法和影响"),
        ("希望与恐惧", "内心深处的期望和隐忧"),
        ("最终结果", "事情的最终结局")
    ],
    'ja': [
        ("現在の状況", "質問者の現在の状況"),
        ("障害", "現状を妨げている障害や課題"),
        ("潜在意識", "隠された願望、潜在意識、問題の本質"),
        ("過去", "近い過去の出来事"),
        ("可能性", "現れつつある影響力と今後の可能性"),
        ("近い将来", "近い将来に起こること"),
        ("自己認識", "自分自身をどう見ているか"),
        ("周囲の環境", "周囲の人々の考えや影響"),
        ("希望と恐れ", "心の奥にある願いと恐れ"),
        ("最終結果", "物事の最終的な結果")
    ]
}

# 카테고리 매핑 (다국어)
CATEGORY_NAMES = {
    'ko': {"love": "연애운", "job": "취업운", "business": "사업운", "money": "금전운", "study": "학업운"},
    'en': {"love": "Love", "job": "Career", "business": "Business", "money": "Finance", "study": "Education"},
    'zh': {"love": "爱情运", "job": "事业运", "business": "生意运", "money": "财运", "study": "学业运"},
    'ja': {"love": "恋愛運", "job": "仕事運", "business": "事業運", "money": "金運", "study": "学業運"}
}

# 시스템 메시지 (다국어 - 할머니 캐릭터 유지)
SYSTEM_MESSAGES = {
    'ko': "당신은 40년 경력의 타로 점술가 할머니입니다. 60대의 할머니 말투로 자연스럽게 이야기합니다. 카드의 의미에 따라 따뜻하게 감싸줄 때도 있고, 냉정하고 직설적으로 따끔하게 말할 때도 있습니다. 매번 같은 표현을 반복하지 않고, 매 카드마다 다양하고 신선한 어투로 이야기합니다. '아이고'라는 표현은 절대 사용하지 않습니다. 오냐오냐만 하는 것이 진정한 도움이 아니라는 철학을 가지고 있습니다.",
    'en': "You are a wise grandmother with 40 years of experience as a tarot reader. You speak warmly and naturally, like a caring but honest grandmother. Depending on the card's meaning, sometimes you offer comfort and warmth, other times you give direct, no-nonsense advice. You never repeat the same phrases — each card gets a fresh, unique interpretation. You believe that sugarcoating everything is not true help. Respond in natural, fluent English.",
    'zh': "你是一位拥有40年经验的塔罗占卜奶奶。你用慈祥但坦率的语气说话，像一位关关但诚实的奶奶。根据牌的含义，有时温暖地安慰，有时直率地给出忠告。你从不重复相同的表达——每张牌都有独特、新颖的解读。你相信一味地说好话并不是真正的帮助。请用自然流畅的中文回答。",
    'ja': "あなたは40年の経験を持つタロット占い師のおばあちゃんです。温かく自然な口調で話しますが、カードの意味によっては優しく包み込むこともあれば、率直に厳しいアドバイスをすることもあがあります。毎回同じ表現を繰り返さず、カードごとに新鮮でユニークな解釈をします。甘やかすだけが本当の助けではないという信念を持っています。自然で流暢な日本語で答えてください。"
}

# 최종 요약 프롬프트 (다국어)
SUMMARY_PROMPTS = {
    'ko': """당신은 40년 경력의 타로 점술가 할머니입니다. 사용자가 {category_name}에 대해 질문했습니다.
상황: {situation}

지금까지 선택된 10장의 카드:
{cards_summary}

이제 10장의 카드를 모두 살펴봤으니, 종합 운세 요약을 작성해주세요.
다음 규칙으로 작성해주세요:
1. 제목 없이 바로 시작
2. **중요한 키워드**는 강조
3. 문장 사이에 적절한 줄바꿈으로 가독성 향상
4. 6-8문장으로 종합 요약 작성:
   - 과거 카드들이 보여준 흐름 분석
   - 현재 상황에 대한 구체적 진단
   - 미래에 대한 명확한 방향 제시
   - 실생활에서 실천할 수 있는 구체적인 핵심 조언 1-2가지
   - 따뜻하고 희망적인 마무리
5. 60대 할머니의 자연스러운 말투로 작성
6. 매번 같은 표현을 반복하지 말고 다양한 어투와 표현 사용
7. 사용자의 상황(질문 분야)에 딱 맞는 실질적인 조언 포함
8. 카드의 의미가 긍정적일 때는 따뜻하게, 부정적이거나 경고가 필요할 때는 냉정하고 직설적으로""",
    'en': """You are a wise grandmother with 40 years of experience as a tarot reader. The user is asking about {category_name}.
Situation: {situation}

The 10 cards drawn so far:
{cards_summary}

Now that all 10 cards are revealed, please provide a comprehensive tarot reading summary.
Follow these rules:
1. Start directly without a title.
2. Emphasize **important keywords**.
3. Use proper line breaks for readability.
4. Write the summary in 6-8 sentences:
   - Analyze the flow from the past cards
   - Diagnose the current situation specifically
   - Provide a clear direction for the future
   - Give 1-2 practical, actionable pieces of advice
   - End warmly and hopefully
5. Write in the natural tone of a caring grandmother.
6. Use varied expressions; do not repeat the same phrases.
7. Give practical advice tailored to the user's situation and question category.
8. Be warm and comforting for positive cards, but direct and honest for warnings.""",
    'zh': """你是一位拥有40年经验的塔罗占卜奶奶。用户在询问关于{category_name}的运势。
状况：{situation}

目前抽出的10张牌：
{cards_summary}

现在10张牌已经全部揭晓，请写一份综合运势解读。
请遵循以下规则：
1. 没有标题，直接开始正文
2. 强调**重要关键字**
3. 段落之间适度换行以提高可读性
4. 用6-8句话写出综合解读：
   - 分析过去牌面显示的趋势
   - 具体诊断当前状况
   - 为未来指出明确的方向
   - 给出1-2个切实可行的核心建议
   - 给出温暖并充满希望的结语
5. 用慈祥奶奶自然流畅的语气写作
6. 每次使用不同的表达方式，不要重复相同的句子
7. 给出完全贴合用户提问领域的具体建议
8. 牌意好时要温暖，需要警告时要坦率直接""",
    'ja': """あなたは40年の経験を持つタロット占い師のおばあちゃんです。ユーザーは{category_name}について質問しています。
状況：{situation}

これまでに選ばれた10枚のカード：
{cards_summary}

10枚すべてのカードが出揃いました。総合的な運勢の解読を作成してください。
以下のルールに従ってください：
1. タイトルなしで直接始める
2. **重要なキーワード**は強調する
3. 読みやすさのため適切な改行を入れる
4. 6〜8文で総合的な解読を書く：
   - 過去のカードが示す流れの分析
   - 現在の状況の具体的な診断
   - 未来への明確な方向性の提示
   - 実生活で実践できる具体的で重要なアドバイスを1〜2つ
   - 温かく希望に満ちた締めくくり
5. 60代のおばあちゃんの自然な口調で書く
6. 毎回同じ表現を繰り返さず、多様な言い回しを使う
7. ユーザーの状況（質問の分野）にぴったり合った実践的なアドバイスを含める
8. カードの意味が肯定的な時は温かく、警告が必要な時は率直で厳しく"""
}

# 일반 카드 프롬프트 (다국어)
NORMAL_PROMPTS = {
    'ko': """당신은 40년 경력의 타로 점술가 할머니입니다. 사용자가 {category_name}에 대해 질문했습니다.
상황: {situation}

**{card_index}번째 카드:**
위치: {position_name} - {position_desc}
카드: {card_name} ({direction})

다음 규칙으로 해석을 작성해주세요:
1. 제목 없이 바로 해석 시작
2. **중요한 키워드**는 강조 표시
3. 문장 사이에 적절한 줄바꿈으로 가독성 향상
4. 2문장으로 자세하게 해석:
   - 이 카드가 이 위치({position_name})에서 나온 의미를 구체적으로 설명
   - 카드에 담긴 핵심 상징과 메시지를 풀이
   - 사용자의 질문 분야({category_name})에 맞게 실생활과 연결하여 조언
   - 앞으로 어떻게 하면 좋을지 구체적인 행동 방향 제시
5. 역방향이면 반대/지연/내면의 의미로 해석하되 어두운 느낌이 아닌 주의와 깨달음의 메시지로
6. 60대 할머니의 자연스러운 말투로 작성
7. 카드의 의미가 긍정적일 때는 따뜻하게, 부정적이거나 경고가 필요할 때는 냉정하고 직설적으로
8. 매번 같은 표현을 반복하지 말고 매 카드마다 다양한 어투와 표현을 사용해서 신선하게
9. 카드의 그림에 담긴 상징을 구체적으로 언급하며 설명""",
    'en': """You are a wise grandmother with 40 years of experience as a tarot reader. The user is asking about {category_name}.
Situation: {situation}

**Card #{card_index}:**
Position: {position_name} - {position_desc}
Card: {card_name} ({direction})

Please provide a tarot reading following these rules:
1. Start directly without a title.
2. Emphasize **important keywords**.
3. Use proper line breaks for readability.
4. Write a detailed interpretation in 2 sentences:
   - Explain what this card means in this specific position ({position_name})
   - Include the core symbolism and message of the card
   - Connect the advice practically to the user's question ({category_name})
   - Suggest specific actionable steps they can take
5. If reversed, interpret as opposite/delay/internal obstacles, but frame it as a lesson rather than doom.
6. Write in the natural tone of a caring grandmother.
7. Be warm and comforting for positive cards, but direct and honest for warnings.
8. Use varied expressions; do not repeat the same phrases across cards.
9. Specifically mention the imagery and symbols on the card.""",
    'zh': """你是一位拥有40年经验的塔罗占卜奶奶。用户在询问关于{category_name}的运势。
状况：{situation}

**第{card_index}张牌：**
位置：{position_name} - {position_desc}
牌：{card_name} ({direction})

请遵循以下规则进行解读：
1. 没有标题，直接开始正文
2. 强调**重要关键字**
3. 段落之间适度换行以提高可读性
4. 用2句话详细解读：
   - 详细解释这张牌出现在这个位置（{position_name}）的意义
   - 解析牌本身的核心象征与传达的信息
   - 结合用户提问的领域（{category_name}），给出现实生活中的建议
   - 提供具体的行动方向，告诉他们接下来可以怎么做
5. 如果是逆位，解读为相反/延迟/内在障碍，但要当作警示与启示，而不是注定的厄运
6. 用慈祥奶奶自然流畅的语气写作
7. 牌意好时要温暖，需要警告时要坦率直接
8. 每次使用不同的表达方式，针对每张牌使用新鲜生动的词汇
9. 解释时要具体提及牌面上的图案与象征意义""",
    'ja': """あなたは40年の経験を持つタロット占い師のおばあちゃんです。ユーザーは{category_name}について質問しています。
状況：{situation}

**{card_index}枚目のカード：**
位置：{position_name} - {position_desc}
カード：{card_name} ({direction})

以下のルールに従って解読を作成してください：
1. タイトルなしで直接始める
2. **重要なキーワード**は強調する
3. 読みやすさのため適切な改行を入れる
4. 2文で詳細に解読する：
   - このカードがこの位置（{position_name}）に出た意味を具体的に説明
   - カードに込められた核心的な象徴とメッセージを解説
   - ユーザーの質問分野（{category_name}）に合わせて、実生活に結びつけたアドバイス
   - 今後どうすればよいか、具体的な行動の方向性を提示
5. 逆位置の場合は反対・遅延・内面的な意味として解読するが、暗い感じではなく気づきと注意のメッセージとして伝える
6. 60代のおばあちゃんの自然な口調で書く
7. カードの意味が肯定的な時は温かく、警告が必要な時は率直で厳しく
8. 毎回同じ表現を繰り返さず、カードごとに多様な言い回しを使う
9. カードの絵柄に描かれている象徴を具体的に言及しながら説明する"""
}


@app.route('/api/cards', methods=['GET'])
@limiter.limit("30 per minute")
def get_cards():
    """78장의 타로 카드 데이터 반환"""
    cards = get_all_cards()
    return jsonify({
        "success": True,
        "cards": cards,
        "total": len(cards)
    })


@app.route('/api/interpret-card', methods=['POST'])
@limiter.limit("10 per minute")  # 분당 10회 제한 (토큰 보호)
def interpret_single_card():
    """단일 카드 해석 (스트리밍)"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "요청 데이터가 없습니다."}), 400
    except Exception:
        return jsonify({"success": False, "error": "잘못된 JSON 형식입니다."}), 400
    
    card_data = data.get('card', {})
    card_index = data.get('cardIndex', 0)
    category = data.get('category', {})
    situation = data.get('situation', '')
    all_cards = data.get('allCards', [])
    lang = data.get('language', 'ko')
    if lang not in POSITION_MEANINGS:
        lang = 'ko'
    
    # 입력값 검증 (10 = 최종 요약 전용)
    if not isinstance(card_index, int) or not 0 <= card_index <= 10:
        return jsonify({"success": False, "error": "유효하지 않은 카드 인덱스입니다."}), 400
    
    if len(situation) > 500:
        return jsonify({"success": False, "error": "상황 설명은 500자를 초과할 수 없습니다."}), 400
    
    if len(all_cards) > 10:
        return jsonify({"success": False, "error": "카드는 최대 10장까지 가능합니다."}), 400
    
    card = get_card_by_id(card_data.get('id'))
    if not card:
        return jsonify({"success": False, "error": "유효하지 않은 카드입니다."}), 400
    
    is_reversed = card_data.get('isReversed', False)
    direction = "역방향" if is_reversed else "정방향"
    is_summary_request = card_index == 10  # 최종 요약 전용 요청
    
    category_name = CATEGORY_NAMES.get(lang, CATEGORY_NAMES['ko']).get(category.get('id', ''), '운세')
    positions = POSITION_MEANINGS.get(lang, POSITION_MEANINGS['ko'])
    system_msg = SYSTEM_MESSAGES.get(lang, SYSTEM_MESSAGES['ko'])
    
    # DeepSeek API 키가 없으면 기본 해석 반환
    if not client:
        if is_summary_request:
            fallback = "## ✨ 종합 요약\n\n10장의 카드가 모두 공개되었습니다. 각 카드의 메시지를 종합하면, 당신에게 밝은 미래가 기다리고 있습니다."
        else:
            fallback = f"**{card['name_kr']}** ({direction})\n\n{card['meaning']}\n\n이 카드는 {POSITION_MEANINGS[card_index][0]}을(를) 나타냅니다."
        return jsonify({"success": True, "interpretation": fallback, "note": "API 키 없음"})
    
    # 프롬프트 생성
    if is_summary_request:
        # 최종 요약 전용 (카드 해석 없이 종합 요약만)
        cards_summary = ""
        for i, c in enumerate(all_cards):
            card_info = get_card_by_id(c.get('id'))
            if card_info:
                c_direction = "역방향" if c.get('isReversed') else "정방향"
                card_name_display = card_info.get(f'name_{lang}', card_info.get('name_kr', 'Card'))
                cards_summary += f"- {i+1}. {positions[i][0]}: {card_name_display} ({c_direction})\n"
        
        prompt_template = SUMMARY_PROMPTS.get(lang, SUMMARY_PROMPTS['ko'])
        prompt = prompt_template.format(
            category_name=category_name,
            situation=situation if situation else "(빈 내용/Not provided)",
            cards_summary=cards_summary
        )
        max_tokens = TOKENS_FINAL
    else:
        # 일반 카드 (1~10번 모두 동일한 형식)
        position_name, position_desc = positions[card_index]
        card_name_display = card.get(f'name_{lang}', card.get('name_kr', card.get('name', 'Card')))
        
        prompt_template = NORMAL_PROMPTS.get(lang, NORMAL_PROMPTS['ko'])
        prompt = prompt_template.format(
            category_name=category_name,
            situation=situation if situation else "(빈 내용/Not provided)",
            card_index=card_index + 1,
            position_name=position_name,
            position_desc=position_desc,
            card_name=card_name_display,
            direction=direction
        )
        max_tokens = TOKENS_NORMAL
    
    # 스트리밍 응답
    def generate():
        try:
            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.8,
                max_tokens=max_tokens,
                stream=True
            )
            
            for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    yield f"data: {json.dumps({'content': content})}\n\n"
            
            yield f"data: {json.dumps({'done': True})}\n\n"
            
        except Exception as e:
            logger.error(f"AI 해석 오류: {str(e)}")
            yield f"data: {json.dumps({'error': '해석 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.'})}\n\n"
    
    return Response(generate(), mimetype='text/event-stream')


@app.route('/api/health', methods=['GET'])
def health_check():
    """서버 상태 확인"""
    return jsonify({
        "status": "healthy",
        "api_configured": bool(DEEPSEEK_API_KEY),
        "tokens_normal": TOKENS_NORMAL,
        "tokens_final": TOKENS_FINAL
    })


if __name__ == '__main__':
    DEBUG_MODE = os.getenv('DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    logger.info(f"서버 시작: port={PORT}, debug={DEBUG_MODE}")
    app.run(host='0.0.0.0', debug=DEBUG_MODE, port=PORT)
