# 🎓 SLife - Preditor de Aluguel & Dashboard

## 📝 Sobre o Projeto
Sistema de inteligência de dados para a SLife. Integra uma calculadora de preços baseada em IA (Machine Learning) com um dashboard de gestão estratégica.

## 🎓 Integrantes
Pedro Gabriel Brum e Natália Morandi

## 🚀 Funcionalidades
1. **Calculadora de Aluguel (IA):**
   - Usa algoritmo Random Forest treinado com dados reais da empresa.
   - Considera: Tipo de imóvel, mobília, internet, localização e vagas.
2. **Dashboard Executivo:**
   - Visualização de Receita, Ocupação e Qualidade (Avaliações).
   - Integração com dados de contratos e usuários.

## 🛠️ Tecnologias
- Python
- Streamlit
- Scikit-Learn
- Pandas

## 📦 Instalação e Execução
1. Certifique-se de que os arquivos CSV (`slife_imoveis.csv`, etc.) estão na pasta.
2. Instale as dependências:
   `pip install -r requirements.txt`
3. Rode a aplicação:
   `streamlit run app.py ou python -m streamlit run app.py`