import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import os
from datetime import datetime

# --- Configuração da Página ---
st.set_page_config(page_title="Minhas Finanças", layout="wide", page_icon="💲")

# --- Constantes e Setup ---
DATA_FILE = "financas.csv"
VALOR_SALARIO = 3800.00
VALOR_VALE = 350.00

# Mapeamento de Meses
MAPA_MESES = {
    1: "Janeiro", 2: "Fevereiro", 3: "Março", 4: "Abril",
    5: "Maio", 6: "Junho", 7: "Julho", 8: "Agosto",
    9: "Setembro", 10: "Outubro", 11: "Novembro", 12: "Dezembro"
}
MAPA_MESES_INV = {v: k for k, v in MAPA_MESES.items()}

# --- Funções de Dados ---
def load_data():
    if os.path.exists(DATA_FILE):
        df = pd.read_csv(DATA_FILE)
        # Garante que a coluna Data seja datetime
        df["Data"] = pd.to_datetime(df["Data"])
        return df
    else:
        return pd.DataFrame(columns=["Data", "Categoria", "Descricao", "Valor", "Tipo"])

def save_data(df):
    df.to_csv(DATA_FILE, index=False)

# --- Interface Principal ---
st.title("💸 Controle Financeiro Pessoal")

df = load_data()

# --- SIDEBAR: FILTROS ---
st.sidebar.header("📅 Controle de Visualização")

if not df.empty:
    # 1. Filtro de Ano (Dinâmico baseados nos dados)
    anos_disponiveis = sorted(df["Data"].dt.year.unique())
    if not anos_disponiveis:
        anos_disponiveis = [datetime.now().year]
        
    ano_sel = st.sidebar.selectbox("Ano de Referência", anos_disponiveis, index=len(anos_disponiveis)-1)
    
    # 2. Filtro de Mês (Fixo Jan-Dez)
    mes_atual_idx = datetime.now().month - 1
    nome_mes_sel = st.sidebar.selectbox("Mês de Detalhe", list(MAPA_MESES.values()), index=mes_atual_idx)
    mes_sel_num = MAPA_MESES_INV[nome_mes_sel]

    # --- DATAFRAMES FILTRADOS ---
    # DF Ano: Usado para evolução e acumulado
    df_ano = df[df["Data"].dt.year == ano_sel].copy()
    
    # DF Mês: Usado para KPIs e Rosca
    df_mes = df_ano[df_ano["Data"].dt.month == mes_sel_num].copy()
else:
    st.sidebar.warning("Nenhum dado encontrado.")
    df_ano = pd.DataFrame()
    df_mes = pd.DataFrame()
    ano_sel = datetime.now().year
    nome_mes_sel = MAPA_MESES[datetime.now().month]


# --- ESTRUTURA DE ABAS ---
tab1, tab2, tab3 = st.tabs(["📝 Lançamentos", "📊 Dashboard & Gráficos", "📂 Extrato"])

# ==========================================
# ABA 1: LANÇAMENTOS
# ==========================================
with tab1:
    col_input1, col_input2 = st.columns([1, 2])
    
    with col_input1:
        st.info("### 1. Renda Fixa")
        st.write(f"**Salário:** R$ {VALOR_SALARIO}")
        st.write(f"**Vale:** R$ {VALOR_VALE}")
        st.caption("Clique abaixo quando receber seu pagamento.")
        
        if st.button("💰 Lançar Renda Mensal (Hoje)"):
            data_hoje = datetime.now().strftime("%Y-%m-%d")
            novos_lancamentos = [
                {"Data": data_hoje, "Categoria": "Salário", "Descricao": "Salário Mensal", "Valor": VALOR_SALARIO, "Tipo": "Receita"},
                {"Data": data_hoje, "Categoria": "Benefícios", "Descricao": "Vale Alimentação", "Valor": VALOR_VALE, "Tipo": "Receita"}
            ]
            novo_df = pd.DataFrame(novos_lancamentos)
            novo_df["Data"] = pd.to_datetime(novo_df["Data"])
            
            df = pd.concat([df, novo_df], ignore_index=True)
            save_data(df)
            st.success("Salário e Vale lançados!")
            st.rerun()

    with col_input2:
        st.info("### 2. Transações Variáveis")
        with st.form("entry_form", clear_on_submit=True):
            col_f1, col_f2 = st.columns(2)
            with col_f1:
                data_in = st.date_input("Data", datetime.now())
                tipo_in = st.selectbox("Tipo", ["Despesa", "Receita (Extra)"])
            with col_f2:
                valor_in = st.number_input("Valor (R$)", min_value=0.01, format="%.2f")
                cat_in = st.selectbox("Categoria", [
                    "Contas Fixas", "Moradia", "Alimentação", "Transporte", "Lazer", 
                    "Educação", "Investimentos", "Saúde", "Empréstimos", "Outros"
                ])
            
            desc_in = st.text_input("Descrição (Ex: Pizza, Freela, Gasolina)")
            
            submitted = st.form_submit_button("💾 Salvar Lançamento")
            
            if submitted:
                tipo_real = "Receita" if "Receita" in tipo_in else "Despesa"
                
                new_row = pd.DataFrame({
                    "Data": [pd.to_datetime(data_in)],
                    "Categoria": [cat_in],
                    "Descricao": [desc_in],
                    "Valor": [valor_in],
                    "Tipo": [tipo_real]
                })
                df = pd.concat([df, new_row], ignore_index=True)
                save_data(df)
                st.toast("Transação salva!")
                st.rerun()

# ==========================================
# ABA 2: DASHBOARD
# ==========================================
with tab2:
    if df.empty:
        st.warning("Adicione dados para visualizar o dashboard.")
    else:
        # --- SEÇÃO 1: DETALHES DO MÊS SELECIONADO ---
        st.markdown(f"### 📅 Visão Detalhada: **{nome_mes_sel}/{ano_sel}**")
        
        receitas_mes = df_mes[df_mes["Tipo"] == "Receita"]["Valor"].sum()
        despesas_mes = df_mes[df_mes["Tipo"] == "Despesa"]["Valor"].sum()
        saldo_mes = receitas_mes - despesas_mes
        
        col1, col2, col3 = st.columns(3)
        col1.metric("Entradas", f"R$ {receitas_mes:,.2f}")
        col2.metric("Saídas", f"R$ {despesas_mes:,.2f}", delta_color="inverse")
        col3.metric("Saldo Líquido", f"R$ {saldo_mes:,.2f}", delta=f"{saldo_mes:,.2f}")
        
        st.divider()

        # --- SEÇÃO 2: GRÁFICO DE ROSCA ---
        c_spacer1, c_chart, c_spacer2 = st.columns([1, 2, 1])
        with c_chart:
            df_pizza = df_mes[df_mes["Tipo"] == "Despesa"]
            if not df_pizza.empty:
                st.subheader(f"🍩 Composição de Gastos ({nome_mes_sel})")
                fig_pizza = px.pie(
                    df_pizza, 
                    values="Valor", 
                    names="Categoria", 
                    hole=0.5,
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                fig_pizza.update_traces(textposition='inside', textinfo='percent+label')
                fig_pizza.update_layout(margin=dict(t=30, b=0, l=0, r=0))
                st.plotly_chart(fig_pizza, use_container_width=True)
            else:
                st.info(f"Nenhuma despesa registrada em {nome_mes_sel}.")

        st.divider()

        if not df_ano.empty:
            # Preparação dos dados para os gráficos anuais
            df_ano['Mes_Num'] = df_ano['Data'].dt.month
            df_ano['Mes_Nome'] = df_ano['Mes_Num'].map(MAPA_MESES)
            
            # --- SEÇÃO 3: EVOLUÇÃO (BARRAS + LINHA TENDENCIA) ---
            st.subheader(f"📈 Panorama Mensal: Entradas vs Saídas")
            
            df_chart = df_ano.groupby(['Mes_Num', 'Mes_Nome', 'Tipo'])['Valor'].sum().reset_index()
            df_chart = df_chart.sort_values('Mes_Num')

            # Prepara DF de Saldo (Receita - Despesa)
            df_saldo = df_ano.groupby('Mes_Num').apply(
                lambda x: pd.Series({
                    'Saldo': x[x['Tipo'] == 'Receita']['Valor'].sum() - x[x['Tipo'] == 'Despesa']['Valor'].sum(),
                    'Mes_Nome': MAPA_MESES[x.name]
                })
            ).reset_index()
            df_saldo = df_saldo.sort_values('Mes_Num')

            # Gráfico de Barras
            fig_bar = px.bar(
                df_chart, x="Mes_Nome", y="Valor", color="Tipo", barmode="group",
                color_discrete_map={"Receita": "#00CC96", "Despesa": "#EF553B"},
                text_auto='.2s'
            )
            # Linha de Saldo Mensal
            fig_bar.add_trace(go.Scatter(
                x=df_saldo['Mes_Nome'], y=df_saldo['Saldo'], mode='lines+markers+text', 
                name='Saldo do Mês', text=df_saldo['Saldo'].apply(lambda x: f"{x:.0f}"),
                textposition="top center", line=dict(color='white', width=3, dash='dot')
            ))
            fig_bar.update_layout(xaxis_title=None, yaxis_title="Valor (R$)")
            st.plotly_chart(fig_bar, use_container_width=True)

            # --- SEÇÃO 4: ACUMULADO (NOVO GRÁFICO) ---
            st.divider()
            st.subheader(f"💰 Evolução do Saldo Acumulado (Patrimônio no Ano)")
            
            # Cálculo do Acumulado (Cumsum)
            df_saldo['Saldo_Acumulado'] = df_saldo['Saldo'].cumsum()
            
            # Gráfico de Área
            fig_area = px.area(
                df_saldo, 
                x="Mes_Nome", 
                y="Saldo_Acumulado",
                markers=True,
                title="Quanto sobrou somando mês a mês?",
            )
            
            # Customização visual
            fig_area.update_traces(
                line_color='#636EFA', 
                fillcolor='rgba(99, 110, 250, 0.2)',
                text=df_saldo['Saldo_Acumulado'].apply(lambda x: f"R$ {x:,.2f}"),
                textposition="top left"
            )
            
            # Adiciona linha zero para referência visual
            fig_area.add_hline(y=0, line_dash="dash", line_color="gray")
            
            st.plotly_chart(fig_area, use_container_width=True)

        else:
            st.info("Sem dados para este ano.")

# ==========================================
# ABA 3: EXTRATO COMPLETO (Com Filtros)
# ==========================================
with tab3:
    st.subheader("📝 Edição e Visualização de Dados")
    
    if not df.empty:
        # --- FILTROS ---
        c1, c2, c3 = st.columns([1, 1, 2])
        
        # 1. Filtro de Ano
        years = sorted(df["Data"].dt.year.unique(), reverse=True)
        sel_year = c1.selectbox("Filtrar Ano", years, key="filter_year")
        
        # 2. Filtro de Mês (Só mostra meses que existem naquele ano)
        df_year = df[df["Data"].dt.year == sel_year]
        months_avail = sorted(df_year["Data"].dt.month.unique())
        # Cria lista com opção 'Todos' + nomes dos meses
        month_options = ["Todos"] + [MAPA_MESES[m] for m in months_avail]
        sel_month_name = c2.selectbox("Filtrar Mês", month_options, key="filter_month")
        
        # 3. Busca Texto (Descrição ou Categoria)
        search_txt = c3.text_input("Buscar (Ex: Uber, Mercado)", key="filter_text")

        # --- APLICAÇÃO DOS FILTROS ---
        # Começa com o ano selecionado
        df_filtered = df_year.copy()
        
        # Aplica mês se não for "Todos"
        if sel_month_name != "Todos":
            sel_month_num = MAPA_MESES_INV[sel_month_name]
            df_filtered = df_filtered[df_filtered["Data"].dt.month == sel_month_num]
            
        # Aplica busca de texto
        if search_txt:
            mask = df_filtered["Descricao"].str.contains(search_txt, case=False, na=False) | \
                   df_filtered["Categoria"].str.contains(search_txt, case=False, na=False)
            df_filtered = df_filtered[mask]

        st.caption(f"Mostrando {len(df_filtered)} registros.")

        # --- EDITOR DE DADOS ---
        # O data_editor retorna apenas o dataframe que está sendo visto/editado
        edited_subset = st.data_editor(
            df_filtered.sort_values(by="Data", ascending=False),
            num_rows="dynamic", # Permite adicionar linhas novas direto no filtro
            use_container_width=True,
            key="editor_grid"
        )
        
        # --- LÓGICA DE SALVAMENTO SEGURO ---
        if st.button("💾 Salvar Alterações na Tabela"):
            try:
                # 1. Identifica os índices originais que foram carregados no filtro
                indices_originais = df_filtered.index
                
                # 2. Remove esses registros do DataFrame principal (df)
                # (Isso apaga a versão antiga desse mês/filtro)
                df_limpo = df.drop(indices_originais)
                
                # 3. Adiciona a versão editada (edited_subset) ao DataFrame limpo
                # O concat junta o que não foi tocado + o que foi editado
                df_final = pd.concat([df_limpo, edited_subset], ignore_index=True)
                
                # 4. Salva no CSV
                # Garante que a data está correta antes de salvar
                df_final["Data"] = pd.to_datetime(df_final["Data"])
                save_data(df_final)
                
                st.success("Dados atualizados com sucesso! (Merge realizado)")
                st.rerun()
            except Exception as e:
                st.error(f"Erro ao salvar: {e}")

    else:
        st.info("Nenhum dado cadastrado.")