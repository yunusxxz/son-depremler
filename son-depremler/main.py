import pandas as pd
import streamlit as st
import requests as req
from bs4 import BeautifulSoup as bs
import re
import plotly.express as px
import plotly.graph_objs as go

url = 'http://www.koeri.boun.edu.tr/scripts/sondepremler.asp'
iller = ["adana", "adiyaman", "afyon", "agri", "amasya", "ankara", "antalya", "artvin", "aydin", "balikesir", "bilecik",
         "bingol", "bitlis", "bolu", "burdur", "bursa", "canakkale", "cankiri", "corum", "denizli", "diyarbakir",
         "edirne", "elazig", "erzincan", "erzurum", "eskisehir", "gaziantep", "giresun", "gumushane", "hakkari",
         "hatay", "isparta", "icel (mersin)", "istanbul", "izmir", "kars", "kastamonu", "kayseri", "kirklareli",
         "kirsehir", "kocaeli", "konya", "kutahya", "malatya", "manisa", "kahramanmaras", "mardin", "mugla", "mus",
         "nevsehir", "nigde", "ordu", "rize", "sakarya", "samsun", "siirt", "sinop", "sivas", "tekirdag", "tokat",
         "trabzon", "tunceli", "sanliurfa", "usak", "van", "yozgat", "zonguldak", "aksaray", "bayburt", "karaman",
         "kirikkale", "batman", "sirnak", "bartin", "ardahan", "igdir", "yalova", "karabuk", "kilis", "osmaniye",
         "duzce"]

iller = [x.upper() for x in iller]

res = req.get(url)
if res.status_code == 200:
    soup = bs(res.content, "html.parser")
    data = soup.find('pre')
    lines = data.text.splitlines()[7:-1]
    deprem_data = []
    for line in lines:
        l = line.replace('-.-', '0.0')
        values = re.split('\s{2,}', l)
        deprem_data.append({
            'tarihSaat': values[0],
            'enlem': values[1],
            'boylam': values[2],
            'derinlik': values[3],
            'md': values[4],
            'ml': values[5],
            'mw': values[6],
            'yer': values[7]
        })
    df = pd.DataFrame(deprem_data)
    df = df.astype({
        'tarihSaat': 'datetime64[ns]',
        'enlem': float,
        'boylam': float,
        'derinlik': float,
        'md': float,
        'ml': float,
        'mw': float
    })
    df['tarihSaat'] = pd.to_datetime(df['tarihSaat'])
    df_filtered = df
    with st.sidebar:
        st.header('Depremleri Filtreleyin')
        m_range = st.slider(
            label="Şiddet Aralığı",
            min_value=df['ml'].min(),
            max_value=df['ml'].max(),
            value=(df['ml'].min(), df['ml'].max()))
        m_filter = (m_range[0] <= df['ml']) & (m_range[1] >= df['ml'])
        df_filtered = df_filtered[m_filter]

        select_cities = st.multiselect("İllere Göre:", iller)
        if select_cities:
            c_filter = df_filtered['yer'].str.contains("|".join(select_cities), case=False, na=False)
            df_filtered = df_filtered[c_filter]

        st.subheader("Tarih Aralığına Göre")
        dt1, dt2 = st.columns(2, gap="small")
        with dt1:
            start = st.date_input(
                "Başlangıç:",
                min_value=df['tarihSaat'].min(),
                max_value=df['tarihSaat'].max(),
                value=df['tarihSaat'].min()
            )

        with dt2:
            end = st.date_input(
                "Bitiş:",
                min_value=df['tarihSaat'].min(),
                max_value=df['tarihSaat'].max(),
                value=df['tarihSaat'].max()
            )
        df_filter = (pd.to_datetime(start) <= df_filtered['tarihSaat']) & (
                pd.to_datetime(end) >= df_filtered['tarihSaat'])
        df_filtered = df_filtered[df_filter]

    # Ekrana yayınlanıyor.
    st.title("TÜRKİYE VE YAKIN ÇEVRESİNDEKİ SON DEPREMLER")
    st.subheader(f"Son {len(df_filtered)} deprem listelenmiştir.")
    st.divider()
    st.dataframe(df_filtered, hide_index=True, use_container_width=True)
    # Harita Dağılım Grafiği:
    # fig= px.scatter_geo(
    #     df_filtered,
    #     lat='enlem',
    #     lon='boylam',
    #     text='yer',
    #     size='ml',
    #     title=f'f"Son {len(df_filtered)} deprem dağılım haritası',
    #     projection= 'natural earth'
    # )
    fig = go.Figure()
    fig.add_trace(go.Scattergeo(
        lat=df_filtered['enlem'],
        lon=df_filtered['boylam'],
        text=df['yer'],
        marker=dict(size=df['ml'] * 7 , color='red', opacity=.7, line=dict(width=.5, color='black')),
        name="Konumlar"
    ))
    fig.update_layout(
        title=f"Son{len(df_filtered)} deprem dağılım haritası",
        geo=dict(showland=True, lataxis=dict(range=[35,43]), lonaxis=dict(range=[25,45]), landcolor='lightgray', countrycolor='white', subunitcolor= 'white')
    )

    st.plotly_chart(fig)

else:
    st.error(f"{res.status_code}: Adrese erişim başarısız.")
