from pathlib import Path
import pandas as pd
import plotly.express as px
import streamlit as st

st.set_page_config(page_title='World Pulse | 세계 발전 데이터', page_icon='🌍', layout='wide')
HERE = Path(__file__).parent

st.markdown('''<style>
.stApp {background: #0b1220; color: #e8eef8;}
.block-container {padding-top: 2rem; max-width: 1450px;}
h1,h2,h3 {color: #f5f8ff !important;}
[data-testid="stMetric"] {background: #17243a; padding: 18px; border: 1px solid #30435e; border-radius: 16px;}
[data-testid="stMetricLabel"] {color: #b9cbe4;}
[data-testid="stMetricValue"] {color: #ffffff;}
[data-testid="stSidebar"] {background: #111c2e;}
.hero {background: linear-gradient(115deg,#173963,#17213b 70%); padding: 27px 32px; border-radius: 20px; border: 1px solid #37537a; margin-bottom: 22px;}
.eyebrow {color:#7fdad2; letter-spacing:2px; font-size:13px; font-weight:700;}
.hero-title {font-size:37px; font-weight:800; margin:8px 0; color:#fff;}
.hero-sub {color:#b9cbe4; font-size:15px;}
</style>''', unsafe_allow_html=True)

@st.cache_data
def load_data():
    path = HERE / 'gapminder.csv'
    if not path.exists():
        st.error('gapminder.csv 파일이 없습니다. app.py와 같은 폴더에 넣어주세요.')
        st.stop()
    return pd.read_csv(path)

data = load_data()

st.markdown('''<div class="hero"><div class="eyebrow">GLOBAL DEVELOPMENT INTELLIGENCE</div>
<div class="hero-title">🌍 WORLD PULSE</div>
<div class="hero-sub">1952–2007 세계 발전의 궤적 · 기대수명 · 경제 수준 · 인구를 한눈에</div></div>''', unsafe_allow_html=True)

st.sidebar.title('🧭 탐색 필터')
years = sorted(data['year'].unique())
year = st.sidebar.select_slider('기준 연도', options=years, value=years[-1])
continents = st.sidebar.multiselect('대륙 선택', sorted(data['continent'].unique()), default=sorted(data['continent'].unique()))
filtered = data[(data['year'] == year) & data['continent'].isin(continents)].copy()
country_options = sorted(data[data['continent'].isin(continents)]['country'].unique())
default_countries = [c for c in ['South Korea', 'Japan', 'United States', 'China'] if c in country_options]
selected_countries = st.sidebar.multiselect('추이 비교 국가', country_options, default=default_countries)
metric_options = {'기대수명 (세)': 'lifeExp', '1인당 GDP (USD)': 'gdpPercap', '인구 (명)': 'pop'}
metric_label = st.sidebar.selectbox('지도·순위 지표', list(metric_options))
metric = metric_options[metric_label]
st.sidebar.caption('데이터: Gapminder / Plotly Express 내장 공개 데이터. 1952–2007년, 5년 간격. 최신 통계가 아닙니다.')

if filtered.empty:
    st.warning('선택한 대륙에 해당하는 데이터가 없습니다. 왼쪽에서 대륙을 선택해 주세요.')
    st.stop()

population = filtered['pop'].sum()
weighted_life = (filtered['lifeExp'] * filtered['pop']).sum() / population
weighted_gdp = (filtered['gdpPercap'] * filtered['pop']).sum() / population
c1, c2, c3, c4 = st.columns(4)
c1.metric('분석 국가', f'{len(filtered):,}개')
c2.metric('총 인구', f'{population/1e9:.2f}B')
c3.metric('인구가중 기대수명', f'{weighted_life:.1f}세')
c4.metric('인구가중 1인당 GDP', f'${weighted_gdp:,.0f}')

PLOT = dict(template='plotly_dark', paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font=dict(color='#dbe7f7'), margin=dict(l=10,r=10,t=55,b=15))
left, right = st.columns([1.3, 1])
with left:
    st.subheader('🗺️ 세계 발전 지도')
    fig = px.choropleth(filtered, locations='iso_alpha', color=metric, hover_name='country',
                        color_continuous_scale='Tealgrn', labels={metric: metric_label},
                        title=f'{year}년 · {metric_label}')
    fig.update_geos(showframe=False, showcoastlines=True, coastlinecolor='#53647e', bgcolor='rgba(0,0,0,0)', projection_type='natural earth')
    fig.update_layout(**PLOT, height=420)
    st.plotly_chart(fig, use_container_width=True)
with right:
    st.subheader('🏆 국가별 TOP 12')
    top = filtered.nlargest(12, metric).sort_values(metric)
    fig = px.bar(top, x=metric, y='country', orientation='h', color=metric,
                 color_continuous_scale='Tealgrn', title=f'{metric_label} 상위 국가', labels={'country':'국가',metric:metric_label})
    fig.update_layout(**PLOT, height=420, showlegend=False, coloraxis_showscale=False)
    st.plotly_chart(fig, use_container_width=True)

left2, right2 = st.columns([1, 1])
with left2:
    st.subheader('📈 국가별 장기 변화')
    trend = data[data['country'].isin(selected_countries) & data['continent'].isin(continents)]
    if trend.empty:
        st.info('왼쪽에서 비교할 국가를 한 개 이상 선택해 주세요.')
    else:
        fig = px.line(trend, x='year', y=metric, color='country', markers=True,
                      title=f'1952–2007 {metric_label} 추이', labels={'year':'연도',metric:metric_label,'country':'국가'})
        fig.update_layout(**PLOT, height=400)
        st.plotly_chart(fig, use_container_width=True)
with right2:
    st.subheader('🫧 경제와 기대수명의 관계')
    fig = px.scatter(filtered, x='gdpPercap', y='lifeExp', size='pop', color='continent',
                     hover_name='country', size_max=55, log_x=True,
                     labels={'gdpPercap':'1인당 GDP (USD, 로그 축)','lifeExp':'기대수명 (세)','continent':'대륙'},
                     title=f'{year}년 국가별 비교')
    fig.update_layout(**PLOT, height=400)
    st.plotly_chart(fig, use_container_width=True)

st.subheader('📋 원본 데이터 탐색 및 다운로드')
columns = {'country':'국가','continent':'대륙','year':'연도','lifeExp':'기대수명','pop':'인구','gdpPercap':'1인당 GDP','iso_alpha':'국가 코드'}
show = filtered[list(columns)].rename(columns=columns).sort_values('국가')
st.dataframe(show, use_container_width=True, hide_index=True)
st.download_button('⬇️ 선택한 데이터 CSV 다운로드', data=show.to_csv(index=False).encode('utf-8-sig'),
                   file_name=f'world_pulse_{year}.csv', mime='text/csv')
st.caption('출처: Gapminder 데이터셋 (Plotly Express 배포본). GDP는 1인당 GDP, 인구·기대수명은 각 국가의 해당 연도 값입니다. 대륙 선택에 따른 집계는 선택된 국가에 한정됩니다.')
