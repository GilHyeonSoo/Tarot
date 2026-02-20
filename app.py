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
TOKENS_NORMAL = 1000   # 1~9번 카드 (더 자세한 해석)
TOKENS_FINAL = 2500    # 10번 카드 (종합 요약 포함)

# 카드 위치별 의미
POSITION_MEANINGS = [
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
]

# 카테고리 한글 매핑
CATEGORY_NAMES = {
    "love": "연애운",
    "job": "취업운",
    "business": "사업운",
    "money": "금전운",
    "study": "학업운"
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
    
    # 입력값 검증
    if not isinstance(card_index, int) or not 0 <= card_index <= 9:
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
    is_last_card = card_index == 9  # 0-indexed
    
    position_name, position_desc = POSITION_MEANINGS[card_index]
    category_name = CATEGORY_NAMES.get(category.get('id', ''), '운세')
    
    # DeepSeek API 키가 없으면 기본 해석 반환
    if not client:
        fallback = f"**{card['name_kr']}** ({direction})\n\n{card['meaning']}\n\n이 카드는 {position_name}을(를) 나타냅니다."
        if is_last_card:
            fallback += "\n\n---\n\n## ✨ 종합 요약\n\n10장의 카드가 모두 공개되었습니다. 각 카드의 메시지를 종합하면, 당신에게 밝은 미래가 기다리고 있습니다."
        return jsonify({"success": True, "interpretation": fallback, "note": "API 키 없음"})
    
    # 프롬프트 생성
    if is_last_card:
        # 마지막 카드: 해당 카드 해석 + 종합 요약
        cards_summary = ""
        for i, c in enumerate(all_cards):
            card_info = get_card_by_id(c.get('id'))
            if card_info:
                c_direction = "역방향" if c.get('isReversed') else "정방향"
                cards_summary += f"- {i+1}. {POSITION_MEANINGS[i][0]}: {card_info['name_kr']} ({c_direction})\n"
        
        prompt = f"""당신은 40년 경력의 타로 점술가 할머니입니다. 사용자가 {category_name}에 대해 질문했습니다.
상황: {situation if situation else "(입력하지 않음)"}

**마지막 10번째 카드:**
위치: {position_name}
카드: {card['name_kr']} ({direction})

지금까지 선택된 10장의 카드:
{cards_summary}

다음 규칙으로 해석을 작성해주세요:
1. 제목 없이 바로 해석 시작
2. **중요한 키워드**는 강조
3. 문장 사이에 적절한 줄바꿈으로 가독성 향상
4. 먼저 이 카드({card['name_kr']})의 해석을 4-6문장으로 자세히 (카드의 상징, 위치와의 관계, 질문자에게 주는 의미)
5. 빈 줄 후 "---" 구분선
6. 그 다음 종합 운세 요약을 6-8문장으로 자세히 작성:
   - 과거 카드들이 보여준 흐름 분석
   - 현재 상황에 대한 구체적 진단
   - 미래에 대한 명확한 방향 제시
   - 실생활에서 실천할 수 있는 구체적인 핵심 조언 1-2가지
   - 따뜻하고 희망적인 마무리
7. 60대 할머니의 자연스러운 말투로 작성
8. 카드의 의미가 긍정적일 때는 따뜻하게 감싸주고, 부정적이거나 경고가 필요할 때는 냉정하고 직설적으로 따끔하게
9. 매번 같은 표현을 반복하지 말고 매 카드마다 다양한 어투와 표현을 사용
10. 카드의 그림에 담긴 상징이나 의미를 구체적으로 언급하며 설명
11. 사용자의 상황(질문 분야)에 딱 맞는 실질적인 조언 포함

예시 형식:
얘야, 마지막으로 나온 이 카드를 보렴. {card['name_kr']}가 **최종 결과** 자리에 떡 하니 나왔구나.

이 카드에 그려진 모습이 보이지? 이건 **변화와 성장**을 뜻하는 거란다. 네가 지금까지 겪어온 고생이 헛되지 않았다는 걸 카드가 말해주고 있어.

할머니가 오래 카드를 봐왔지만, 이 자리에 이 카드가 나오면 **좋은 징조**인 경우가 많았단다. *마음을 열고* 다가오는 기회를 놓치지 마렴.

---

자, 이제 열 장의 카드를 다 펼쳐봤으니 처음부터 정리를 해볼게.

첫 번째 카드에서부터 할머니 눈엔 이미 네 안에 있는 **잠재력**이 보였단다...

(과거-현재-미래 흐름을 구체적으로 분석, 핵심 조언, 따뜻한 마무리)"""
        max_tokens = TOKENS_FINAL
    else:
        # 일반 카드 (1~9번)
        prompt = f"""당신은 40년 경력의 타로 점술가 할머니입니다. 사용자가 {category_name}에 대해 질문했습니다.
상황: {situation if situation else "(입력하지 않음)"}

**{card_index + 1}번째 카드:**
위치: {position_name} - {position_desc}
카드: {card['name_kr']} ({direction})

다음 규칙으로 해석을 작성해주세요:
1. 제목 없이 바로 해석 시작
2. **중요한 키워드**는 강조 표시
3. 문장 사이에 적절한 줄바꿈으로 가독성 향상
4. 5-7문장으로 자세하게 해석:
   - 이 카드가 이 위치({position_name})에서 나온 의미를 구체적으로 설명
   - 카드에 담긴 핵심 상징과 메시지를 풀이
   - 사용자의 질문 분야({category_name})에 맞게 실생활과 연결하여 조언
   - 앞으로 어떻게 하면 좋을지 구체적인 행동 방향 제시
5. 역방향이면 반대/지연/내면의 의미로 해석하되 어두운 느낌이 아닌 주의와 긨달음의 메시지로
6. 60대 할머니의 자연스러운 말투로 작성
7. 카드의 의미가 긍정적일 때는 따뜻하게, 부정적이거나 경고가 필요할 때는 냉정하고 직설적으로
8. 매번 같은 표현을 반복하지 말고 매 카드마다 다양한 어투와 표현을 사용해서 신선하게
9. 카드의 그림에 담긴 상징을 구체적으로 언급하며 설명"""
        max_tokens = TOKENS_NORMAL
    
    # 스트리밍 응답
    def generate():
        try:
            stream = client.chat.completions.create(
                model="deepseek-chat",
                messages=[
                    {"role": "system", "content": "당신은 40년 경력의 타로 점술가 할머니입니다. 60대의 할머니 말투로 자연스럽게 이야기합니다. 카드의 의미에 따라 따뜻하게 감싸줄 때도 있고, 냉정하고 직설적으로 따끔하게 말할 때도 있습니다. 매번 같은 표현을 반복하지 않고, 매 카드마다 다양하고 신선한 어투로 이야기합니다. '아이고'라는 표현은 절대 사용하지 않습니다. 오냐오냐만 하는 것이 진정한 도움이 아니라는 철학을 가지고 있습니다."},
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
    app.run(debug=DEBUG_MODE, port=PORT)
