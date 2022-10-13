import streamlit as st
import json
import requests
import pandas as pd
import plotly.express as px

from streamlit_option_menu import option_menu

#st.set_page_config(layout="wide")

st.title('Tazı Project')

hide_st_style = '''
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            thead tr th:first-child {display:none}
            tbody th {display:none}
            </style>
            '''

st.markdown(hide_st_style, unsafe_allow_html=True)

base_url = 'http://tazi-app:8000/'

st.subheader('Confusion Matrices')

number = st.number_input('Index', min_value=1, max_value=99001)

matrix = requests.get(base_url + 'matrix/' + str(number))
ex_item = requests.get(base_url + 'predict?id=' + str(number))
next_item = requests.get(base_url + 'predict?id=' + str(number+1000))

def parse_predict(info):
    res = ''
    if info == '"AA"':
        res = 'True A'
    elif info == '"BA"':
        res = 'False A'
    elif info == '"BB"':
        res = 'True B'
    elif info == '"AB"':
        res = 'False B'
    return res

ex_res = parse_predict(ex_item.text)
next_res = parse_predict(next_item.text)

m = matrix.json()['result']

t_A = m["true_A"]
f_A = m["false_A"]
t_B = m["true_B"]
f_B = m["false_B"]

bar_data = {'Prediction': ['True A', 'False A', 'True B', 'False B'], 'Occurence' : [t_A,f_A,t_B,f_B]}
fig = px.bar(bar_data,
             color='Prediction',
             x='Prediction',
             y='Occurence')

col1, col2 = st.columns(2)

with col1:
    st.table(pd.DataFrame({
        'A': [t_A,f_A],
        'B': [t_B,f_B]}))
    st.markdown(f'##### Prediction {number} will be discarded')
    st.markdown(f'>{ex_res}\n Actual label is **{ex_item.text[1]}** \n Prediction is **{ex_item.text[2]}**')
    st.markdown(f'##### Prediction {number+1000} will included')
    st.markdown(f'>{next_res}\n Actual label is **{next_item.text[1]}** \n Prediction is **{next_item.text[2]}**')
with col2:
    st.plotly_chart(fig, use_container_width=True)
