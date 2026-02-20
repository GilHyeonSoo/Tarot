# 타로 카드 데이터 (78장) - 이미지 경로 포함
import urllib.parse

# 이미지 경로 생성 함수
def get_major_image_path(index, filename):
    return f"/cards/iloveimg-compressed-1/{urllib.parse.quote(filename)}"

def get_minor_image_path(folder, filename):
    return f"/cards/{folder}/{urllib.parse.quote(filename)}"

# 메이저 아르카나 파일명 매핑
MAJOR_ARCANA_FILES = [
    "0. 바보 카드.jpg", "1. 마법사 카드.jpg", "2. 여사제 카드.jpg",
    "3. 여황제 카드.jpg", "4. 황제 카드.jpg", "5. 교황 카드.jpg",
    "6. 연인 카드.jpg", "7. 전차 카드.jpg", "8. 힘 카드.jpg",
    "9. 은둔자 카드.jpg", "10. 운명의 수레바퀴.jpg", "11. 정의 카드.jpg",
    "12. 행맨 카드.jpg", "13. 죽음 카드.jpg", "14. 절제 카드.jpg",
    "15. 악마 카드.jpg", "16. 타워 카드.jpg", "17. 별 카드.jpg",
    "18. 달 카드.jpg", "19. 태양 카드.jpg", "20. 심판 카드.jpg",
    "21. 세계 카드.jpg"
]

MAJOR_ARCANA = [
    {"id": 0, "name": "The Fool", "name_kr": "바보", 
     "meaning_up": "새로운 도전, 기대감, 모험심, 새로운 일 시작, 이사, 여행", 
     "meaning_rev": "준비 부족, 무계획적 행동, 진지하지 않음, 중요한 결정을 고민 없이 내림, 자금관리 어려움",
     "image": get_major_image_path(0, MAJOR_ARCANA_FILES[0])},
    {"id": 1, "name": "The Magician", "name_kr": "마법사", 
     "meaning_up": "다재다능, 문제해결 능력, 창의성, 의지력, 프로젝트 성공, 자신감 있는 태도", 
     "meaning_rev": "자신의 능력을 과대평가하거나 주변사람을 속임, 과시, 허세",
     "image": get_major_image_path(1, MAJOR_ARCANA_FILES[1])},
    {"id": 2, "name": "The High Priestess", "name_kr": "여사제", 
     "meaning_up": "직감적 판단, 침착한, 성찰하는, 중요한 선택에서 올바른 길 발견, 비밀 유지", 
     "meaning_rev": "지나친 신비주의, 소극적 태도, 문제를 직시하지 않고 회피, 자신만의 세계에 갇힘",
     "image": get_major_image_path(2, MAJOR_ARCANA_FILES[2])},
    {"id": 3, "name": "The Empress", "name_kr": "여황제", 
     "meaning_up": "풍요로움, 모성애, 창조성, 새로운 아이디어 실현, 육아, 가정에서 만족감", 
     "meaning_rev": "독립하지 못하고 다른 사람에게 의존, 과잉보호, 의존성",
     "image": get_major_image_path(3, MAJOR_ARCANA_FILES[3])},
    {"id": 4, "name": "The Emperor", "name_kr": "황제", 
     "meaning_up": "질서, 규율, 안정성, 회사 운명에서 리더십 발휘, 목표를 향한 강한 의지", 
     "meaning_rev": "타인의 의견에 귀를 기울이지 않음, 독선적 태도, 융통성 없음",
     "image": get_major_image_path(4, MAJOR_ARCANA_FILES[4])},
    {"id": 5, "name": "The Hierophant", "name_kr": "교황", 
     "meaning_up": "전통 존중, 교육과 상담의 역할, 전통적인 방식으로 문제 해결, 조언자로서 신뢰를 얻음", 
     "meaning_rev": "고지식함, 편협함, 새로운 방식을 거부하거나 지나치게 보수적인 태도",
     "image": get_major_image_path(5, MAJOR_ARCANA_FILES[5])},
    {"id": 6, "name": "The Lovers", "name_kr": "연인", 
     "meaning_up": "관계의 조화, 육체적 호감, 서로의 매력 확인, 로맨틱한 발전", 
     "meaning_rev": "결혼대 부족, 삼각관계, 진지하지 않은 관계, 선택의 갈등",
     "image": get_major_image_path(6, MAJOR_ARCANA_FILES[6])},
    {"id": 7, "name": "The Chariot", "name_kr": "전차", 
     "meaning_up": "목표 달성, 끈기, 자기 통제력, 경쟁에서 승리, 목표를 위해 장애물 극복", 
     "meaning_rev": "방향 상실, 무리한 행동, 자기 지나치게 무리한 경쟁, 배타주의적인 태도",
     "image": get_major_image_path(7, MAJOR_ARCANA_FILES[7])},
    {"id": 8, "name": "Strength", "name_kr": "힘", 
     "meaning_up": "내면의 용기, 인내심, 자제력, 어려운 상황에서 침착하게 대처, 관계에서 신뢰를 쌓음", 
     "meaning_rev": "무력감, 통제하는 능력 부족, 자신감 상실, 스트레스나 긴장 상태",
     "image": get_major_image_path(8, MAJOR_ARCANA_FILES[8])},
    {"id": 9, "name": "The Hermit", "name_kr": "은둔자", 
     "meaning_up": "자기 탐구, 지식과 통찰, 자신만의 시간을 통해 결정, 지혜로운 문제 해결", 
     "meaning_rev": "고립, 외로움, 주변 사람과의 단절이나 지나치게 폐쇄적인 태도",
     "image": get_major_image_path(9, MAJOR_ARCANA_FILES[9])},
    {"id": 10, "name": "Wheel of Fortune", "name_kr": "운명의 수레바퀴", 
     "meaning_up": "운명적 기회, 변화, 예상치 못한 기쁨으로 인한 상승, 긍정적 변화의 시작", 
     "meaning_rev": "미래를 예측하기 어려운 상황, 뜻밖의 불운, 갑작스러운 하락세",
     "image": get_major_image_path(10, MAJOR_ARCANA_FILES[10])},
    {"id": 11, "name": "Justice", "name_kr": "정의", 
     "meaning_up": "균형, 주관적인 판단 판단, 공정한 계약이나 제결, 법적 문제에서 공정한 결과", 
     "meaning_rev": "불공정함, 편파적 결정, 타인을 부당하게 대하거나 자신의 권리를 침해당함",
     "image": get_major_image_path(11, MAJOR_ARCANA_FILES[11])},
    {"id": 12, "name": "The Hanged Man", "name_kr": "매달린 남자", 
     "meaning_up": "새로운 관점, 자기 희생, 다른 시각에서 상황을 이해, 잠시 멈춰서 고민", 
     "meaning_rev": "무기력함, 변화의 기회를 놓치거나 상황에 순응하지 못함",
     "image": get_major_image_path(12, MAJOR_ARCANA_FILES[12])},
    {"id": 13, "name": "Death", "name_kr": "죽음", 
     "meaning_up": "끝맺음과 새로운 시작, 과거 관계를 종료, 새로운 인연 시작, 새로운 챕터 시작", 
     "meaning_rev": "끝을 맺지 못하거나 헤어지기 어려움, 변화를 두려워함, 집착",
     "image": get_major_image_path(13, MAJOR_ARCANA_FILES[13])},
    {"id": 14, "name": "Temperance", "name_kr": "절제", 
     "meaning_up": "균형, 최적화, 조화로운 관계, 관계에서의 의미, 일과 삶의 균형 유지", 
     "meaning_rev": "감정의 불균형, 지나친 욕심이나 과잉 경쟁을 내려놓기 어려움, 모순적인 행동",
     "image": get_major_image_path(14, MAJOR_ARCANA_FILES[14])},
    {"id": 15, "name": "The Devil", "name_kr": "악마", 
     "meaning_up": "강렬한 열정, 집착, 새로운 자극, 파격적인 매력", 
     "meaning_rev": "중독, 통제 상실, 관계에서 건강하지 않은 집착, 문제 인식의 어려움",
     "image": get_major_image_path(15, MAJOR_ARCANA_FILES[15])},
    {"id": 16, "name": "The Tower", "name_kr": "타워", 
     "meaning_up": "문제의 근본을 깨닫고 새로운 방향으로 전환, 변화를 통한 성장", 
     "meaning_rev": "예상치 못한 실직, 관계의 급격한 파탄, 비인싱적인 상황이나 실현 불가능한 계획",
     "image": get_major_image_path(16, MAJOR_ARCANA_FILES[16])},
    {"id": 17, "name": "The Star", "name_kr": "별", 
     "meaning_up": "희망, 영감, 긍정적인 전망, 잠재력, 새로운 목표를 세우고, 미래에 대한 낙관", 
     "meaning_rev": "현실 도피, 환상, 너무 이상적인 기대나 현실과 멀어진 희망",
     "image": get_major_image_path(17, MAJOR_ARCANA_FILES[17])},
    {"id": 18, "name": "The Moon", "name_kr": "달", 
     "meaning_up": "직감의 활성화, 내면 탐구, 꿈이나 직감을 통해 답을 발견, 예술적 영감", 
     "meaning_rev": "감정의 혼란, 의심이 커져서 결정을 내리기 어려움, 모순적 행동",
     "image": get_major_image_path(18, MAJOR_ARCANA_FILES[18])},
    {"id": 19, "name": "The Sun", "name_kr": "태양", 
     "meaning_up": "성공, 행복, 밝은 에너지, 프로젝트 성공, 관계에서의 만족감", 
     "meaning_rev": "자신감 부족, 과도한 낙관, 지나친 긍정이 현실 문제를 가릴 수 있음",
     "image": get_major_image_path(19, MAJOR_ARCANA_FILES[19])},
    {"id": 20, "name": "Judgement", "name_kr": "심판", 
     "meaning_up": "각성, 반성과 새로운 출발, 새로운 인식의 생김, 과거 반성, 새 기회", 
     "meaning_rev": "실수를 반복하거나 기회를 놓침, 변화에 대한 두려움",
     "image": get_major_image_path(20, MAJOR_ARCANA_FILES[20])},
    {"id": 21, "name": "The World", "name_kr": "세계", 
     "meaning_up": "성취, 완성, 여행과 확장, 중요한 목표 달성, 커리어에서 성공", 
     "meaning_rev": "미완성된 일, 새로운 시작에 대한 두려움, 완벽주의로 인한 지연",
     "image": get_major_image_path(21, MAJOR_ARCANA_FILES[21])}
]

# 마이너 아르카나 설정
SUIT_CONFIG = {
    "Wands": {"kr": "완드", "folder": "iloveimg-compressed-2", "prefix": "완드"},
    "Cups": {"kr": "컵", "folder": "iloveimg-compressed-3", "prefix": "컵"},
    "Swords": {"kr": "소드", "folder": "iloveimg-compressed-4", "prefix": "소드"},
    "Pentacles": {"kr": "펜타클", "folder": "iloveimg-compressed", "prefix": "펜타클"}
}

COURT_NAMES = ["에이스", "2", "3", "4", "5", "6", "7", "8", "9", "10", "페이지", "나이트", "퀸", "킹"]
COURT_ENGLISH = ["Ace", "2", "3", "4", "5", "6", "7", "8", "9", "10", "Page", "Knight", "Queen", "King"]

# 마이너 아르카나 의미 데이터
MINOR_MEANINGS = {
    "Wands": [
        {"meaning_up": "새로운 시작, 열정의 불꽃, 새로운 프로젝트 시작, 창의적 아이디어 탄생", "meaning_rev": "준비 부족, 방향성 부족, 열정만 앞서고 구체적인 계획이 없음"},
        {"meaning_up": "계획과 전망, 성취의 갈림길, 미래를 계획하며 선택의 기로에 서 있음", "meaning_rev": "결단력 부족, 우유부단함, 중요한 결정을 미루거나 기회를 놓침"},
        {"meaning_up": "확장과 탐험, 새로운 가능성, 해외 진출, 관계에서 새로운 국면 진입", "meaning_rev": "무모한 모험, 현실과의 괴리, 준비 없이 너무 큰 목표를 세움"},
        {"meaning_up": "안정과 축하, 중요한 성취 후 축하, 결혼식이나 모임", "meaning_rev": "안주함, 변화를 두려워함, 현재 상태에 만족하며 발전을 멈춤"},
        {"meaning_up": "경쟁, 갈등, 팀워크 향상을 위한 건강한 논의나 경쟁", "meaning_rev": "불필요한 갈등, 소모적인 논쟁, 관계에서 사소한 다툼이 계속됨"},
        {"meaning_up": "승리, 인정, 프로젝트 성공 후 인정받음, 대중 앞에서의 성취", "meaning_rev": "자만심, 겸손 부족, 과도한 자신감으로 인해 타인의 반발 초래"},
        {"meaning_up": "방어, 자기보호, 자신의 입장이나 성취를 방어", "meaning_rev": "과도한 방어적 태도, 타인과 협력하지 않고 혼자 모든 것을 해결하려 함"},
        {"meaning_up": "빠른 진전, 변화, 빠른 소통, 갑작스러운 변화", "meaning_rev": "과속, 충동적 행동, 충분한 검토 없이 서두름"},
        {"meaning_up": "회복력, 경계심, 도전에 굴하지 않고 끝까지 견딤", "meaning_rev": "피로감, 지친 반항, 더이상 진행할 의력이 없는데도 억지로 버팀"},
        {"meaning_up": "책임감, 목표 달성, 어려운 일을 마침내 완수", "meaning_rev": "과중한 부담, 지나치게 많은 책임을 떠안아 지치고 있음"},
        {"meaning_up": "호기심, 모험심, 새로운 학습이나 프로젝트에 대한 열정", "meaning_rev": "미숙함, 조급함, 충분한 준비 없이 시작함"},
        {"meaning_up": "열정적인 추진력, 적극적이고 자신감 있는 행동", "meaning_rev": "충동적 행동, 무모함, 계획 없이 일을 벌이고 실패"},
        {"meaning_up": "자기 확신, 따뜻함, 다른 사람을 격려하고 이끄는 리더십", "meaning_rev": "자기중심적 태도, 타인의 의견을 무시하거나 독단적 행동"},
        {"meaning_up": "리더십, 비전, 큰 그림을 보고 사람들을 이끄는 지도력", "meaning_rev": "독선적 태도, 자신의 방식만을 고집하며 타인과 충돌"},
    ],
    "Cups": [
        {"meaning_up": "새로운 감정, 사랑의 시작, 새로운 연애의 시작, 감정적 치유", "meaning_rev": "감정 억제, 고립, 새로운 관계를 두려워하거나 감정을 억누름"},
        {"meaning_up": "조화로운 관계, 소울메이트, 깊은 이해를 바탕으로 한 관계 형성", "meaning_rev": "의존적 관계, 서로의 독립성을 침해하는 지나친 의존"},
        {"meaning_up": "축하, 우정, 친구들과의 즐거운 모임, 좋은 소식 공유", "meaning_rev": "방탕함, 소모적 모임, 책임 없는 즐거움에 몰두"},
        {"meaning_up": "자기 반성, 내면 탐구, 현재 상황에서 새로운 기회를 탐색", "meaning_rev": "무기력, 무관심, 주어진 기회를 놓치거나 나태함"},
        {"meaning_up": "상실, 후회, 과거의 상처를 인정하고 앞으로 나아감", "meaning_rev": "과거에 얽매임, 지나간 실패에 매달려 현재를 망침"},
        {"meaning_up": "추억, 순수함, 과거의 좋은 기억을 통해 영감을 얻음", "meaning_rev": "지나친 과거회상, 현실을 무시하고 과거에 집착"},
        {"meaning_up": "상상력, 선택의 다양성, 다양한 가능성 탐구", "meaning_rev": "환상, 결단력 부족, 현실과 동떨어진 계획"},
        {"meaning_up": "떠남, 새로운 시작, 힘들었던 상황을 정리하고 떠남", "meaning_rev": "회피, 문제를 해결하지 않고 떠나버림"},
        {"meaning_up": "만족, 성취, 감정적으로 안정되고 행복한 상태", "meaning_rev": "나태함, 더 나아가려는 노력이 부족"},
        {"meaning_up": "완벽한 행복, 가족의 조화, 가정에서의 행복한 시간", "meaning_rev": "이상화된 기대, 비현실적인 행복을 추구하며 현재를 놓침"},
        {"meaning_up": "순수한 감정, 창의적 영감, 새롭게 싹트는 사랑", "meaning_rev": "감정적 미숙함, 비현실적 기대, 충동적으로 감정을 표현"},
        {"meaning_up": "낭만, 헌신, 사랑을 표현하는 매력적인 자세", "meaning_rev": "바람끼, 바람둥이에게 자주 속음"},
        {"meaning_up": "공감, 이해, 타인의 감정을 잘 이해하고 보살핌", "meaning_rev": "감정적 과민, 과도한 감정적 반응"},
        {"meaning_up": "감정적 균형, 냉철하면서도 따뜻한 관계 유지", "meaning_rev": "감정적, 자신의 감정을 표현하지 않음"},
    ],
    "Swords": [
        {"meaning_up": "명확한 생각, 진실 발견, 문제를 직시하고 해결책을 모색", "meaning_rev": "과도한 비판, 공격적 태도, 타인을 지나치게 비판하거나 냉혹한 결정"},
        {"meaning_up": "균형, 중립, 갈등 속에서 공정한 결정을 내리려 힘", "meaning_rev": "우유부단함, 결정 지연, 선택을 미루며 상황이 악화됨"},
        {"meaning_up": "표면으로 드러나는, 진실 발견, 환상이 깨지고 객관적으로 판단", "meaning_rev": "배신, 깊은 상처, 관계나 일에서 겪는 큰 상실"},
        {"meaning_up": "휴식, 치유, 재충전을 통해 문제를 다시 바라봄", "meaning_rev": "회피, 게으름, 상황을 방치하거나 적극적으로 해결하지 않음"},
        {"meaning_up": "승리, 갈등 해결, 불리한 상황을 극복함", "meaning_rev": "비윤리적 승리, 타인을 희생하며 이익을 얻음"},
        {"meaning_up": "이주, 변화, 어려운 상황을 떠나 새로운 환경으로 이동", "meaning_rev": "도망, 미해결 문제, 문제를 해결하지 않고 떠나버림"},
        {"meaning_up": "전략, 지혜, 고묘한 방법으로 문제를 해결", "meaning_rev": "속임수, 불신, 타인이나 자신에게 정직하지 않음"},
        {"meaning_up": "인식의 전환, 문제를 객관적으로 바라보고 새로운 해결책을 찾는 계기", "meaning_rev": "스스로 가둠, 두려움이나 걱정에 갇혀 행동하지 않음"},
        {"meaning_up": "문제의 실체 파악, 걱정을 통해 해결의 실마리를 발견하고 개선", "meaning_rev": "과도한 걱정, 문제를 과장하여 스스로 괴로워함"},
        {"meaning_up": "끝, 재생의 기회, 어려움을 끝내고 새롭게 시작", "meaning_rev": "배신, 극심한 고통, 중요한 관계나 일에서 큰 상처"},
        {"meaning_up": "호기심, 새로운 관점, 상황을 면밀히 관찰하고 배움", "meaning_rev": "지나친 의심, 타인의 행동을 과도하게 분석함"},
        {"meaning_up": "빠른 행동, 결단력, 적극적으로 문제를 해결", "meaning_rev": "성급함, 충동적 행동, 충분히 생각하지 않고 돌진"},
        {"meaning_up": "지혜, 독립, 상황을 명확히 판단하고 결정", "meaning_rev": "차가움, 외로움, 감정적으로 단절되어 인간관계 악화"},
        {"meaning_up": "명료함, 공정함, 이성적으로 문제를 해결", "meaning_rev": "독선적 태도, 지나치게 권위적이고 비타협적"},
    ],
    "Pentacles": [
        {"meaning_up": "새로운 기회, 물질적 시작, 새로운 사업 시작, 재정적 기회", "meaning_rev": "잠재력 부족, 주어진 기회를 제대로 활용하지 못함"},
        {"meaning_up": "균형, 조화, 일과 삶의 균형을 유지", "meaning_rev": "불안정, 혼란, 지나치게 많은 일을 감당하며 집중력 부족"},
        {"meaning_up": "협력, 공동의 노력, 팀워크를 통해 성과를 얻음", "meaning_rev": "협업 부족, 타인과의 의견 충돌로 프로젝트 실패"},
        {"meaning_up": "안정성, 절약, 재정적 안정을 위해 절약", "meaning_rev": "집착, 인색함, 물질에 과도하게 집착하며 성장 저해"},
        {"meaning_up": "어려움 속의 연대, 힘든 상황에서도 도움을 얻음", "meaning_rev": "빈곤, 소외, 재정적 어려움과 인간관계의 단절"},
        {"meaning_up": "나눔, 균형, 자원을 나누고 타인을 돕는 관대함", "meaning_rev": "불균형, 의존, 지나치게 의존하거나 일방적인 관계"},
        {"meaning_up": "평가, 재조정, 결과를 분석하고 전략을 수정", "meaning_rev": "인내 부족, 결과를 서두르디 실패"},
        {"meaning_up": "숙련, 노력, 꾸준한 노력으로 기술 향상", "meaning_rev": "반복적인 일, 단조로움에 지쳐 의욕 상실"},
        {"meaning_up": "풍요, 독립, 경제적 독립과 성취", "meaning_rev": "고립, 스스로 만족하며 타인과의 관계를 단절"},
        {"meaning_up": "유산, 전통, 가족과 함께하는 안정된 삶", "meaning_rev": "지나친 보수, 변화에 대한 두려움으로 정체"},
        {"meaning_up": "호기심, 물질적 기회, 새로운 기술을 배우고 발전", "meaning_rev": "시작은 했지만 실행력이 부족, 꿈만 꿈"},
        {"meaning_up": "실용성, 끈기, 꾸준히 노력하여 목표를 달성", "meaning_rev": "완고함, 느림, 변화를 거부하며 속도가 느림"},
        {"meaning_up": "실질적 지원, 타인을 보살피며 현실적 도움을 줌", "meaning_rev": "근심, 걱정, 고립, 타인의 자율성을 침해하며 간섭"},
        {"meaning_up": "안정성, 풍요, 재정적 성공과 권위를 유지", "meaning_rev": "물질주의, 감정이나 인간관계를 소홀히 함"},
    ]
}

MINOR_ARCANA = []
card_id = 22

for suit, config in SUIT_CONFIG.items():
    meanings = MINOR_MEANINGS[suit]
    for i, court_name in enumerate(COURT_NAMES):
        # 파일명 생성
        if court_name in ["에이스", "페이지", "나이트", "퀸", "킹"]:
            filename = f"{config['prefix']} {court_name}.jpg"
        else:
            filename = f"{config['prefix']}{court_name}.jpg"
        
        card_name = f"{COURT_ENGLISH[i]} of {suit}"
        card_name_kr = f"{config['kr']} {court_name}"
        
        MINOR_ARCANA.append({
            "id": card_id,
            "name": card_name,
            "name_kr": card_name_kr,
            "suit": suit,
            "meaning_up": meanings[i]["meaning_up"],
            "meaning_rev": meanings[i]["meaning_rev"],
            "image": get_minor_image_path(config['folder'], filename)
        })
        card_id += 1

# 전체 카드 덱
ALL_CARDS = MAJOR_ARCANA + MINOR_ARCANA


def get_all_cards():
    """모든 카드 반환"""
    return ALL_CARDS


def get_card_by_id(card_id):
    """ID로 카드 찾기"""
    for card in ALL_CARDS:
        if card["id"] == card_id:
            return card
    return None


def get_cards_by_ids(card_ids):
    """여러 ID로 카드들 찾기"""
    return [get_card_by_id(cid) for cid in card_ids if get_card_by_id(cid)]
