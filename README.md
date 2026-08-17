# 📈 국내 주식 투자자별 수급동향 모바일 대시보드

국내 주식 시장(KOSPI / KOSDAQ)의 투자자별(외국인, 기관, 개인, 연기금 등) 순매수 수급 동향과 주가 추이를 모바일 화면에 최적화하여 시각화해 주는 반응형 Streamlit 대시보드 웹 애플리케이션입니다.

---

## 🌟 주요 기능

1. **모바일 우선 UI/UX (Mobile-First Design)**:
   - 스마트폰 세로 화면에서도 메트릭, 차트, 테이블이 잘리지 않고 최적의 가독성을 제공합니다.
   - 금액 단위(억원/백만원) 자동 환산 및 상승(빨강)/하락(파랑) 색상 명시.

2. **시장 전체 수급 요약 헤더**:
   - KOSPI / KOSDAQ의 개인, 외국인, 기관 최근 순매수 금액 요약 카드를 상단에 배치.

3. **인터랙티브 차트 (Plotly Dual-Axis & Bar Chart)**:
   - **이중 축(Dual-Axis) 차트**: 주가 캔들스틱/라인과 투자자별 누적 순매수 금액 추이 비교.
   - **일별 막대 그래프(Bar Chart)**: 외국인, 기관, 개인, 연기금 등 일별 순매수 현황 시각화.
   - 터치 및 모바일 제스처 지원.

4. **상세 데이터 테이블 & CSV 다운로드**:
   - 일별 거래대금, 종가, 등락률, 주요 투자자별 수급 데이터 제공.
   - 원클릭 엑셀/CSV 데이터 다운로드 지원.

5. **안정적인 데이터 파이프라인 (Data Cache & Fallback)**:
   - PyKRX / FinanceDataReader 데이터 수집 및 `@st.cache_data` 캐싱 적용.
   - API 네트워크 예외 상황 시 자동 모의(Mock) 데이터 생성 렌더링 Fallback 탑재.

---

## 📁 프로젝트 구조

```
Streamlit_stock_project/
├── app.py              # 메인 Streamlit 대시보드 UI 및 상태 제어
├── data_loader.py      # PyKRX / FDR 데이터 수집, Streamlit 캐싱 및 Mock Fallback
├── utils.py            # 단위 포맷팅, 커스텀 모바일 CSS 주입, Plotly 차트 헬퍼
├── requirements.txt    # 배포 및 필수 패키지 목록
└── README.md           # 프로젝트 안내 및 배포 가이드 문서
```

---

## 🚀 실행 방법 (uv 지원)

### ⚡ Option 1: `uv` 사용 (추천 - 가장 빠르고 간편함)

별도의 가상환경을 수동으로 생성하지 않아도 `uv`가 프로젝트 의존성을 자동으로 격리 설치하여 실행합니다.

```bash
# 디렉터리 이동
cd Streamlit_stock_project

# uv run으로 바로 실행
uv run streamlit run app.py
```

필요시 `uv sync` 명령어로 환경을 미리 동기화할 수도 있습니다:
```bash
uv sync
uv run streamlit run app.py
```

---

### 📦 Option 2: 기존 `pip` 방식 사용

```bash
# 가상환경 생성 및 활성화
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Mac/Linux:
source .venv/bin/activate

# 패키지 설치 및 실행
pip install -r requirements.txt
streamlit run app.py
```

---

## ☁️ Streamlit Community Cloud 무료 배포 가이드

1. **GitHub 저장소 생성 및 푸시**:
   ```bash
   git init
   git add .
   git commit -m "Feat: Add Mobile-First Korean Stock Supply & Demand Dashboard"
   git branch -M main
   git remote add origin https://github.com/YOUR_USERNAME/Streamlit_stock_project.git
   git push -u origin main
   ```

2. **Streamlit Community Cloud 접속**:
   - [Streamlit Community Cloud](https://share.streamlit.io/)에 접속하여 GitHub 계정으로 로그인합니다.

3. **New App 생성**:
   - **Repository**: `YOUR_USERNAME/Streamlit_stock_project` 선택
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **Deploy!** 버튼 클릭.

4. 약 1~2분 후 자동 빌드 및 개별 웹 URL 생성 완료! (스마트폰 및 PC에서 누구나 접속 가능)

---

## 🛠️ 기술 스택
- **Language**: Python 3.10+
- **Framework**: Streamlit
- **Visualization**: Plotly
- **Data Analysis**: Pandas, Numpy
- **Data Source**: PyKRX, FinanceDataReader

---

## 📜 License
This project is open source and available under the [MIT License](LICENSE).
