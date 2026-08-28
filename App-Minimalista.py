import streamlit as st
import pandas as pd
import instaloader
from datetime import datetime, timedelta
import matplotlib.pyplot as plt

st.set_page_config(page_title="Analisador @", layout="centered")

# CSS minimalista
st.markdown("""
<style>
body {background:#0f0f0f}
h1 {color:#ff3b30 !important}
.stButton>button {background:#ff3b30; color:white; border-radius:12px; width:100%; height:50px; font-weight:bold; border:none}
</style>
""", unsafe_allow_html=True)

st.title("Analisador de @")
st.caption("Digite qualquer conta pública. Máx 2 buscas/dia. 100% seguro - sem login.")

username = st.text_input(" @", placeholder="southamericamemes", label_visibility="collapsed")

@st.cache_data(ttl=86400, show_spinner=False)
def buscar(username):
    L = instaloader.Instaloader(download_pictures=False, download_videos=False, download_video_thumbnails=False, download_geotags=False, download_comments=False, save_metadata=False)
    profile = instaloader.Profile.from_username(L.context, username)
    dados = []
    for i, post in enumerate(profile.get_posts()):
        if i >= 20: break
        dados.append({
            "hora": post.date_local.hour,
            "dia": ["Seg","Ter","Qua","Qui","Sex","Sáb","Dom"][post.date_local.weekday()],
            "likes": post.likes,
            "views": post.video_view_count if post.is_video else 0,
            "tipo": "REEL" if post.is_video else "IMG",
            "data": post.date_local.strftime("%d/%m %H:%M")
        })
    df = pd.DataFrame(dados)
    return df, profile.followers

if st.button("BUSCAR E GERAR GRÁFICO"):
    if not username:
        st.warning("Digite um @")
    else:
        user = username.replace("@","").strip()
        with st.spinner(f"Analisando @{user}... 20s"):
            try:
                df, followers = buscar(user)
                
                # Insights
                melhor_hora = df.groupby('hora')['likes'].mean().idxmax()
                melhor_dia = df.groupby('dia')['likes'].mean().idxmax()
                
                c1, c2, c3 = st.columns(3)
                c1.metric("Seguidores", f"{followers:,}".replace(",","."))
                c2.metric("Melhor horário", f"{melhor_hora}h")
                c3.metric("Melhor dia", melhor_dia)
                
                # Gráfico 1 - Hora
                st.subheader("Likes médios por horário")
                por_hora = df.groupby('hora')['likes'].mean()
                fig, ax = plt.subplots()
                ax.bar(por_hora.index, por_hora.values, color="#ff3b30")
                ax.set_facecolor("#1c1c1c")
                st.pyplot(fig)
                
                # Gráfico 2 - Dia
                st.subheader("Por dia da semana")
                por_dia = df.groupby('dia')['likes'].mean().reindex(["Seg","Ter","Qua","Qui","Sex","Sáb","Dom"])
                fig2, ax2 = plt.subplots()
                ax2.bar(por_dia.index, por_dia.values, color="#ff3b30")
                st.pyplot(fig2)
                
                # Tabela
                st.subheader(f"Últimos {len(df)} posts")
                st.dataframe(df[["data","hora","tipo","likes","views"]], use_container_width=True)
                
                csv = df.to_csv(index=False).encode('utf-8')
                st.download_button("Baixar CSV", csv, f"dados_{user}.csv", "text/csv")
                
            except Exception as e:
                st.error(f"Erro: {e}\n\nPode ser conta privada ou block de 10 min. Tente outro @ ou aguarde.")

st.markdown("---")
st.caption("Seguro: sem login, só dados públicos. 2 buscas/dia recomendado. Cache 24h.")
