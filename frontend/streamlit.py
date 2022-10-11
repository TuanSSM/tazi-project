import streamlit as st
import json
import requests
import pandas as pd

from streamlit_option_menu import option_menu

st.title('Tazi Project')

about_md = '''
About lorem ipsum
'''

prediction_md = '''
Model Prediction lorem ipsum
'''

matrix_md = '''
Model Prediction lorem ipsum
'''

choice = option_menu(None, ['Matrix'] ,#[ 'About', 'Model Predictions', 'Matrix'],#'Image', , 'Office File'
    icons= ['table'],#['house', 'list-ol', 'table'],
    menu_icon='cast', default_index=0, orientation='horizontal',
    styles={
        'container': {'padding': '5!important'} #, 'background-color': '#fafafa'},
        #'icon': {'color': 'orange', 'font-size': '25px'}, 
        #'nav-link': {'font-size': '25px', 'text-align': 'left', 'margin':'0px', '--hover-color': '#eee'},
        #'nav-link-selected': {'background-color': 'green'},
    }
                     )

hide_st_style = '''
            <style>
            #MainMenu {visibility: hidden;}
            header {visibility: hidden;}
            footer {visibility: hidden;}
            </style>
            '''

st.markdown(hide_st_style, unsafe_allow_html=True)

base_url = 'http://127.0.0.1:8000/'

if choice == 'Model Predictions':
    st.subheader('Model Predictions')
    st.markdown(prediction_md)

    if st.button('Get'):
        res = requests.get(url = base_url + 'prediction/1')

    st.subheader(f'Response from API = {res.text}')

elif choice == 'Matrix':
    st.subheader('Matrix')
    st.markdown(matrix_md)

    number = st.number_input('Index', min_value=1, max_value=99001)

    window = requests.get(base_url + 'sliding_window?id=' + str(number))
    matrix = requests.get(base_url + 'matrix/' + str(number))

    w_df = pd.DataFrame.from_dict(window.json())
    st.dataframe(w_df)

    m = matrix.json()['result']

    st.markdown(f'True A: {m["true_A"]} | False A: {m["false_A"]}')
    st.markdown(f'True B: {m["true_B"]} | False B: {m["false_B"]}')

else:
    st.subheader('About')
    st.markdown(about_md)

