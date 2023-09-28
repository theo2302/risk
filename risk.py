import streamlit as st
import pandas as pd
import numpy as np
import joblib
import plotly.graph_objects as go
np.set_printoptions(suppress=True, precision=6)

# Streamlit app
st.title("Empréstimo Inteligente BR")




# Input fields for user

st.sidebar.header("Informações Pessoais :man:")
person_age = st.sidebar.slider("Idade", min_value=20, max_value=80)
person_income = st.sidebar.slider("Salário (Mês)", min_value=1000, max_value=30000, step=1000)
person_emp_length = st.sidebar.slider("Tempo Empregado (anos)", min_value=0, max_value=40)
cred_hist_len = st.sidebar.slider("Histórico de Crédito (anos)", 0, 60)
hist_inad = st.sidebar.selectbox("Possui histórico de inadimplência?", ["Não", "Sim"])
housing_options = ["Própria", "Hipoteca", "Aluguel", "Outros"]
housing = st.sidebar.selectbox("Tipo de Moradia", housing_options, index=None,
   placeholder="Escolha uma opção...")
st.sidebar.header("Informações sobre o empréstimo :dollar:")
loan_amt = st.sidebar.number_input("Valor do empréstimo (Somente Números)", min_value=1, step=1, value=1)
loan_intent_options = ("Educação", "Investimento", "Pagamento Divida", "Pessoal", "Reforma Residencial", "Saúde")
loan_intent = st.sidebar.selectbox( "Motivo do Empréstimo", options= loan_intent_options, index=None, placeholder="Escolha uma opção...")
loan_int_rate = st.sidebar.select_slider("Taxa de juros (5-25%)", np.arange(5, 26, 1))
grade = st.sidebar.select_slider("Nível de risco", ["Baixo", "Médio", "Alto"])
loan_intent_options = ("Educação", "Investimento", "Pagamento Divida", "Pessoal", "Reforma Residencial", "Saúde")


# Add other input fields as needed

# Create a function to preprocess user input data
def preprocess_user_input(user_data):
    # Ensure that the column names match the training data
    # Preprocess user input data (scaling)
    user_data.iloc[:, :8] = scaler.transform(user_data.iloc[:, :8])
    user_data_scaled = user_data

    return user_data_scaled

# Store user data in session state
if 'user_data' not in st.session_state:
    st.session_state.user_data = None
    st.session_state.profile_created = False

def callback():
    st.session_state.user_data = True

# User input data
user_data = pd.DataFrame({
    'person_age': [person_age],
    'person_income': [(person_income) * 12],
    'person_emp_length': [person_emp_length],
    'loan_grade': [0],  # Add default values for other columns
    'loan_amnt': [loan_amt],
    'loan_int_rate': [loan_int_rate],
    'cb_person_cred_hist_length': [cred_hist_len],
    'hist_inadimplencia': [0],
    'loan_intent_DEBTCONSOLIDATION': [0],
    'loan_intent_EDUCATION': [0],
    'loan_intent_HOMEIMPROVEMENT': [0],
    'loan_intent_MEDICAL': [0],
    'loan_intent_PERSONAL': [0],
    'loan_intent_VENTURE': [0],
    'person_home_ownership_MORTGAGE': [0],
    'person_home_ownership_OTHER': [0],
    'person_home_ownership_OWN': [0],
    'person_home_ownership_RENT': [0]
})

if (st.sidebar.button("Criar Beneficiário", on_click=callback) or st.session_state.profile_created):

    if loan_intent == "Educação":
        user_data['loan_intent_EDUCATION'] = 1
    elif loan_intent == "Investimento":
        user_data['loan_intent_VENTURE'] = 1
    elif loan_intent == "Pagamento Divida":
        user_data['loan_intent_DEBTCONSOLIDATION'] = 1
    elif loan_intent == "Pessoal":
        user_data['loan_intent_PERSONAL'] = 1
    elif loan_intent == "Reforma Residencial":
        user_data['loan_intent_HOMEIMPROVEMENT'] = 1
    else:
        user_data['loan_intent_MEDICAL'] = 1
    if housing == "Própria":
        user_data['person_home_ownership_OWN'] = 1
    elif housing == "Hipoteca":
        user_data['person_home_ownership_MORTGAGE'] = 1
    elif housing == "Aluguel":
        user_data['person_home_ownership_RENT'] = 1
    else:
        user_data['person_home_ownership_OTHER'] = 1
    if hist_inad == "Sim":
        user_data['hist_inadimplencia'] = 1

    st.session_state.user_data = user_data
    st.session_state.profile_created = True

    # Display confirmation message


    # Display user information
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.markdown("")
    st.subheader("Informações do Beneficiário")
    st.write(f"**Idade: {person_age}**")
    st.write(f"**Salário (mês): R$ {person_income}**")
    st.write(f"**Nível de risco: {grade}**")
    st.write(f"**Tempo Empregado: {person_emp_length} Anos**")
    st.write(f"**Valor do empréstimo: R$ {loan_amt}**")
    st.write(f"**Taxa de juros: {loan_int_rate}%**")
    st.write(f"**Motivo do Empréstimo: {loan_intent}**")
    st.write(f"**Tipo de Moradia: {housing}**")

    st.success("Perfil de beneficiário criado com sucesso!")

    if (st.button("Realizar Análise", on_click=callback)):

        model = joblib.load('trained_model.pkl') 
        scaler = joblib.load('scaler.pkl')  

        def preprocess_user_input(user_data):
            user_data.iloc[:, :7] = scaler.transform(user_data.iloc[:, :7])
            user_data_scaled = user_data
            return user_data_scaled


        with st.spinner("Avaliando o perfil do beneficiário..."):
            # Make predictions
            np.set_printoptions(suppress=True)
            user_data_scaled = preprocess_user_input(user_data)
            prediction = model.predict(user_data_scaled)
            prediction_prob = model.predict_proba(user_data_scaled)[:, 1]  # For probability scores

        # Remove the loading spinner once predictions are done
        st.spinner(False)

        # Display prediction result using a bar chart
        st.subheader("Resultado da Avaliação")

        # Display prediction status
        if prediction[0] == 1:
            st.write("<h3 style='color:red;'>Status: Negado</h3>", unsafe_allow_html=True)
        else:
            st.write("<h3 style='color:green;'>Status: Aprovado</h3>", unsafe_allow_html=True)

        percentage = round(prediction_prob[0] * 100, 2)

        # Create a gauge figure using Plotly
        gauge_fig = go.Figure(go.Indicator(
            mode="gauge+number",
            value=percentage,
            title={'text': "Probabilidade de Inadimplência"},
            number={'suffix': "%"},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "red" if prediction[0] == 1 else "green"},
                'steps': [
                    {'range': [0, 100], 'color': "lightgray"},
                ],
            }
        ))

        # Display the gauge using st.plotly_chart
        st.plotly_chart(gauge_fig)



    # Rest of your code remains unchanged
    # ...

else:
    st.subheader("**Crie um perfil**")

# Display a disclaimer with emphasis on potential bias
st.warning(
    '''
    Aviso Importante: Os resultados e previsões não devem ser interpretados como uma representação fiel da realidade
    
    Este webapp tem como meta ilustrar a aplicação de machine learning em tarefas ordinárias de forma simples.
    
    A precisão deste modelo é de aproximadamente 92% com base nos dados em que foi treinado. No entanto, é importante notar que modelos de Machine Learning têm limitações e podem conter vieses.
    
    A qualidade dos resultados de modelos depende da qualidade e representatividade dos dados em que foi treinado. Pode haver vieses ocultos nos dados que influenciem as previsões deste modelo.
    
    Para decisões financeiras importantes, recomendamos consultar com profissionais qualificados e considerar múltiplas fontes de informação.
    '''
)
