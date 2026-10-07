from flask import Flask, jsonify, request, Response, stream_with_context
from flask_cors import CORS
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
from openai import OpenAI
from httpx import Timeout
import os
import logging
import re
import requests
from datetime import datetime, timezone, timedelta
from dotenv import load_dotenv
from tarot_data import get_all_cards, get_card_by_id

load_dotenv()
from reading_stream import stream_reading
from reading_prompts import build_reading_messages

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# CORS 설정 - 허용할 도메인 지정 (프로덕션에서는 실제 도메인으로 변경)
ALLOWED_ORIGINS = [origin.strip().rstrip('/') for origin in os.getenv(
    "ALLOWED_ORIGINS", "http://localhost:5173,http://localhost:3000,http://127.0.0.1:3000"
).split(",") if origin.strip()]
CORS(app, origins=ALLOWED_ORIGINS, max_age=600)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024

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
        base_url="https://api.deepseek.com",
        timeout=Timeout(30.0, connect=10.0, write=10.0, pool=5.0),
        max_retries=0
    )

DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
KST = timezone(timedelta(hours=9))

# 토큰 설정 (조절 가능)
TOKENS_NORMAL = 350   # 개별 카드 해석
TOKENS_SUMMARY = {    # 스프레드별 종합 요약 (오늘의 운세 기준)
    'one': 600,      # 오늘의 운세
    'three': 900,    # 흐름 운세 = 1.5배
    'celtic': 1200,   # 종합 운세 = 2배
}

# 스프레드별 카드 수
SPREAD_COUNTS = {
    'one': 1,
    'three': 3,
    'celtic': 10,
}

# 카드 위치별 의미 (다국어 · 스프레드별)
POSITION_MEANINGS = {
    'ko': {
        'one': [
            ("오늘의 메시지", "지금 당신에게 전하는 카드의 핵심 메시지"),
        ],
        'three': [
            ("과거", "지나온 상황과 그 영향"),
            ("현재", "지금 직면한 상황과 에너지"),
            ("미래", "앞으로 펼쳐질 가능성과 방향"),
        ],
        'celtic': [
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
    },
    'en': {
        'one': [("Today's Message", "The core message this card brings you now")],
        'three': [
            ("Past", "What has led to the present moment"),
            ("Present", "Your current situation and energy"),
            ("Future", "Where things may be heading"),
        ],
        'celtic': [
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
    },
    'zh': {
        'one': [("今日信息", "这张牌此刻带给你的核心信息")],
        'three': [
            ("过去", "已经发生的事及其影响"),
            ("现在", "你当前的处境与能量"),
            ("未来", "事情可能发展的方向"),
        ],
        'celtic': [
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
    },
    'ja': {
        'one': [("今日のメッセージ", "今あなたに届くカードの核心メッセージ")],
        'three': [
            ("過去", "これまでの流れとその影響"),
            ("現在", "今直面している状況とエネルギー"),
            ("未来", "これから向かう可能性と方向性"),
        ],
        'celtic': [
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
        ],
    },
}

# 카테고리 매핑 (다국어)
CATEGORY_NAMES = {
    'ko': {"love": "연애운", "job": "취업운", "business": "사업운", "money": "금전운", "study": "학업운"},
    'en': {"love": "Love", "job": "Career", "business": "Business", "money": "Finance", "study": "Education"},
    'zh': {"love": "爱情运", "job": "事业运", "business": "生意运", "money": "财运", "study": "学业运"},
    'ja': {"love": "恋愛運", "job": "仕事運", "business": "事業運", "money": "金運", "study": "学業運"}
}

_SENTENCE_END = re.compile(r'[.!?…。]["\'”’」』]*')


def trim_to_complete_sentences(text):
    """Drop a trailing fragment so the reading never ends mid-sentence."""
    if not text:
        return text
    stripped = text.rstrip()
    if re.search(r'[.!?…。]["\'”’」』]*\s*$', stripped):
        return stripped
    last_end = None
    for match in _SENTENCE_END.finditer(stripped):
        last_end = match.end()
    if last_end is None:
        return stripped
    return stripped[:last_end].rstrip()


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
    
    if not isinstance(data, dict):
        return jsonify({"success": False, "error": "요청은 JSON 객체여야 합니다."}), 400

    card_data = data.get('card', {})
    card_index = data.get('cardIndex', 0)
    category = data.get('category', {})
    situation = data.get('situation', '')
    all_cards = data.get('allCards', [])
    spread = data.get('spread', 'celtic')
    lang = data.get('language', 'ko')
    if (not isinstance(card_data, dict) or not isinstance(category, dict)
            or not isinstance(situation, str) or not isinstance(all_cards, list)
            or not isinstance(spread, str) or not isinstance(lang, str)
            or not isinstance(category.get('id', ''), str)):
        return jsonify({"success": False, "error": "요청 데이터 형식이 올바르지 않습니다."}), 400
    if lang not in POSITION_MEANINGS:
        lang = 'ko'
    if spread not in SPREAD_COUNTS:
        spread = 'celtic'

    card_count = SPREAD_COUNTS[spread]
    summary_index = card_count

    # 입력값 검증 (summary_index = 해당 스프레드 종합 요약 전용)
    if type(card_index) is not int or not 0 <= card_index <= summary_index:
        return jsonify({"success": False, "error": "유효하지 않은 카드 인덱스입니다."}), 400

    if len(situation) > 500:
        return jsonify({"success": False, "error": "상황 설명은 500자를 초과할 수 없습니다."}), 400

    if len(all_cards) > card_count:
        return jsonify({"success": False, "error": f"카드는 최대 {card_count}장까지 가능합니다."}), 400

    for submitted_card in [card_data, *all_cards]:
        if (not isinstance(submitted_card, dict)
                or type(submitted_card.get('id')) is not int
                or type(submitted_card.get('isReversed', False)) is not bool
                or not get_card_by_id(submitted_card['id'])):
            return jsonify({"success": False, "error": "유효하지 않은 카드입니다."}), 400
    if card_index == summary_index and (
            len(all_cards) != card_count or len({c['id'] for c in all_cards}) != card_count):
        return jsonify({"success": False, "error": "선택한 카드 전체를 보내주세요."}), 400

    card = get_card_by_id(card_data.get('id'))
    if not card:
        return jsonify({"success": False, "error": "유효하지 않은 카드입니다."}), 400

    is_summary_request = card_index == summary_index

    category_name = CATEGORY_NAMES.get(lang, CATEGORY_NAMES['ko']).get(category.get('id', ''), '')
    positions = POSITION_MEANINGS[lang][spread]

    if not client:
        return jsonify({"success": False, "error": "AI 해설 서버 설정을 확인해주세요.",
                        "code": "configuration", "retryable": False}), 503

    selected = all_cards if is_summary_request else [card_data]
    prompt_cards = []
    for index, selected_card in enumerate(selected):
        card_info = get_card_by_id(selected_card['id'])
        reversed_card = selected_card.get('isReversed', False)
        position_index = index if is_summary_request else card_index
        prompt_cards.append({
            'position': positions[position_index][0],
            'name': card_info.get(f'name_{lang}', card_info['name'] if lang == 'en' else card_info['name_kr']),
            'reversed': reversed_card,
            'meaning': card_info['meaning_rev' if reversed_card else 'meaning_up'],
        })
    messages = build_reading_messages(
        prompt_cards, spread, situation, lang, category_name, is_summary=is_summary_request,
    )
    max_tokens = TOKENS_SUMMARY[spread] if is_summary_request else TOKENS_NORMAL
    return Response(
        stream_with_context(stream_reading(
            client, messages, max_tokens,
        )),
        mimetype='text/event-stream',
        headers={
            'Cache-Control': 'no-store, no-transform',
            'X-Accel-Buffering': 'no',
        },
    )


@app.errorhandler(429)
def too_many_readings(_error):
    return jsonify({"success": False, "error": "요청이 많습니다. 잠시 후 다시 시도해주세요.",
                    "code": "busy", "retryable": True}), 429, {'Retry-After': '5'}


def _parse_iso_datetime(value):
    if not value:
        return None
    try:
        normalized = value.replace('Z', '+00:00')
        return datetime.fromisoformat(normalized)
    except (TypeError, ValueError):
        return None


def _format_kst(dt):
    if not dt:
        return '-'
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(KST).strftime('%Y-%m-%d %H:%M')


def _format_duration(started_at, ended_at):
    start = _parse_iso_datetime(started_at)
    end = _parse_iso_datetime(ended_at)
    if not start or not end:
        return '알 수 없음'
    seconds = max(0, int((end - start).total_seconds()))
    if seconds < 60:
        return '1분 미만'
    minutes = seconds // 60
    return f'{minutes}분'


def _summarize_user_agent(user_agent):
    if not user_agent:
        return '-'
    compact = re.sub(r'\s+', ' ', user_agent.strip())
    if len(compact) <= 220:
        return compact
    return f'{compact[:217]}...'


def _build_discord_session_message(data):
    device = data.get('device') or {}
    situation = (data.get('situation') or '').strip() or '(없음)'
    completed = '예' if data.get('completed') else '아니오'
    touch = '예' if device.get('touch') else '아니오'
    started = _format_kst(_parse_iso_datetime(data.get('startedAt')))
    ended = _format_kst(_parse_iso_datetime(data.get('endedAt')))
    duration = _format_duration(data.get('startedAt'), data.get('endedAt'))

    lines = [
        '루미나 타로 이용 로그',
        '━━━━━━━━━━━━━━━━━━',
        f'질문: {situation}',
        f'세션: {data.get("sessionId", "-")}',
        f'완료: {completed}',
        f'기기: {device.get("summary", "-")}',
        f'- 플랫폼: {device.get("platform", "-")}',
        f'- 브라우저: {device.get("browser", "-")}',
        f'- 화면: {device.get("screen", "-")}',
        f'- 터치: {touch}',
        f'- User-Agent: {_summarize_user_agent(device.get("userAgent"))}',
        f'이용: {started} ~ {ended} ({duration})',
        f'스프레드: {data.get("spreadLabel") or data.get("spread") or "-"}',
        f'언어: {data.get("language") or "ko"}',
    ]
    return '\n'.join(lines)


def _send_discord_session_log(data):
    if not DISCORD_WEBHOOK_URL:
        logger.warning('DISCORD_WEBHOOK_URL이 설정되지 않아 세션 로그를 건너뜁니다.')
        return False

    message = _build_discord_session_message(data)
    response = requests.post(
        DISCORD_WEBHOOK_URL,
        json={'content': message},
        timeout=8,
    )
    response.raise_for_status()
    return True


@app.route('/api/log-session', methods=['POST'])
@limiter.limit("30 per minute")
def log_session():
    """이용 세션을 Discord 웹훅으로 전송"""
    try:
        data = request.get_json()
        if not data:
            return jsonify({"success": False, "error": "요청 데이터가 없습니다."}), 400
    except Exception:
        return jsonify({"success": False, "error": "잘못된 JSON 형식입니다."}), 400

    session_id = data.get('sessionId', '')
    if not isinstance(session_id, str) or not re.fullmatch(
        r'[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}',
        session_id,
        re.IGNORECASE,
    ):
        return jsonify({"success": False, "error": "유효하지 않은 세션 ID입니다."}), 400

    situation = data.get('situation', '')
    if not isinstance(situation, str) or len(situation) > 500:
        return jsonify({"success": False, "error": "질문 내용이 유효하지 않습니다."}), 400

    spread_label = data.get('spreadLabel', '')
    if not isinstance(spread_label, str) or len(spread_label) > 120:
        spread_label = str(data.get('spread', ''))[:120]

    language = data.get('language', 'ko')
    if not isinstance(language, str) or len(language) > 10:
        language = 'ko'

    device = data.get('device') if isinstance(data.get('device'), dict) else {}

    payload = {
        'sessionId': session_id,
        'situation': situation,
        'completed': bool(data.get('completed')),
        'startedAt': data.get('startedAt'),
        'endedAt': data.get('endedAt'),
        'spread': data.get('spread', ''),
        'spreadLabel': spread_label,
        'language': language,
        'device': {
            'summary': str(device.get('summary', '-'))[:120],
            'platform': str(device.get('platform', '-'))[:40],
            'browser': str(device.get('browser', '-'))[:60],
            'screen': str(device.get('screen', '-'))[:20],
            'touch': bool(device.get('touch')),
            'userAgent': str(device.get('userAgent', ''))[:500],
        },
    }

    try:
        _send_discord_session_log(payload)
    except Exception as exc:
        logger.error(f'Discord 세션 로그 전송 실패: {exc}')

    return jsonify({"success": True})


@app.route('/api/health', methods=['GET'])
@limiter.exempt
def health_check():
    """서버 상태 확인"""
    return jsonify({
        "status": "healthy",
        "api_configured": bool(DEEPSEEK_API_KEY),
        "tokens_normal": TOKENS_NORMAL,
        "tokens_summary": TOKENS_SUMMARY,
    })


if __name__ == '__main__':
    DEBUG_MODE = os.getenv('DEBUG', 'False').lower() == 'true'
    PORT = int(os.getenv('PORT', 5000))
    logger.info(f"서버 시작: port={PORT}, debug={DEBUG_MODE}")
    app.run(host='0.0.0.0', debug=DEBUG_MODE, port=PORT)
