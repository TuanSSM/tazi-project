import streamlit as st
import json
import requests
import pandas as pd
import plotly.figure_factory as ff

st.title('TAZI - Project')

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

z = [[m["true_B"], m["false_B"]],
     [m["true_A"], m["false_A"]]]

x = ['A', 'B']
y = ['B', 'A']
z_text = [[str(y) for y in x] for x in z]

fig = ff.create_annotated_heatmap(z, x=x, y=y, annotation_text=z_text, colorscale='Viridis')

fig.update_layout(title_text='<i><b>Confusion matrix</b></i>',
                 )

fig.add_annotation(dict(font=dict(color="white",size=14),
                        x=0.5,
                        y=-0.15,
                        showarrow=False,
                        text="Predicted value",
                        xref="paper",
                        yref="paper"))

fig.add_annotation(dict(font=dict(color="white",size=14),
                        x=-0.35,
                        y=0.5,
                        showarrow=False,
                        text="Real value",
                        textangle=-90,
                        xref="paper",
                        yref="paper"))

fig.update_layout(margin=dict(t=50, l=50, r=150))

fig['data'][0]['showscale'] = True

st.markdown(f'**In the *Matrix {number+1}*:**')

if ex_res == next_res:
    st.markdown(f'*Results will remain same*')
else:
    col1, col2 = st.columns(2)
    with col1:
        st.markdown(f'*Prediction {number}* `{ex_res}` will be discarded')
    with col2:
        st.markdown(f'*Prediction {number+1000}* `{next_res}` will included')

st.plotly_chart(fig)
