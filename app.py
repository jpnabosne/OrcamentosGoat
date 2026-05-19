import streamlit as st
import pandas as pd
from docxtpl import DocxTemplate
import subprocess
import os
from datetime import datetime

st.set_page_config(page_title="Gerador de Orçamentos", page_icon="📄", layout="centered")

st.title("📄 Gerador Automático de Orçamentos")
st.markdown("Preencha os dados abaixo para gerar o orçamento em PDF instantaneamente.")

# --- DADOS DO CLIENTE ---
st.subheader("1. Informações do Cliente")
col1, col2 = st.columns(2)

with col1:
    cliente = st.text_input("Nome do Cliente / Empresa", value="Empresa Exemplo LTDA")
with col2:
    data_atual = datetime.now().strftime("%d/%m/%Y")
    data = st.text_input("Data do Orçamento", value=data_atual)

# --- TABELA DE ITENS ---
st.subheader("2. Itens do Orçamento")

dados_iniciais = pd.DataFrame([
    {"Item": "Consultoria Técnica", "Quantidade": 1, "Preço Unitário (R$)": 1500.00},
    {"Item": "Desenvolvimento de Feature", "Quantidade": 1, "Preço Unitário (R$)": 4500.00}
])

tabela_editavel = st.data_editor(
    dados_iniciais,
    num_rows="dynamic",
    column_config={
        "Item": st.column_config.TextColumn("Descrição do Item", width="large", required=True),
        "Quantidade": st.column_config.NumberColumn("Qtd", min_value=1, default=1, required=True),
        "Preço Unitário (R$)": st.column_config.NumberColumn("Preço Unitário (R$)", min_value=0.0, format="R$ %.2f", required=True),
    },
    hide_index=True,
)

tabela_editavel["Total Linha"] = tabela_editavel["Quantidade"] * tabela_editavel["Preço Unitário (R$)"]
total_geral = tabela_editavel["Total Linha"].sum()

st.markdown(f"### **Valor Total: R$ {total_geral:,.2f}**")

# --- GERADOR ---
st.subheader("3. Gerar Documento")

if st.button("🚀 Gerar Orçamento em PDF", use_container_width=True):
    if not cliente:
        st.error("Por favor, preencha o nome do cliente.")
    else:
        with st.spinner("Processando documento e convertendo para PDF na nuvem..."):
            try:
               itens_template = []
               for _, row in tabela_editavel.iterrows():
                    itens_template.append({
                        "nome": row["Item"],
                        "qtd": int(row["Quantidade"]),
                        "preco": f"{row['Preço Unitário (R$)']:.2f}",  # <--- Corrigido aqui!
                        "total": f"{row['Total Linha']:.2f}"
    })

                dados_contexto = {
                    "cliente": cliente,
                    "data": data,
                    "itens": itens_template,
                    "total_geral": f"{total_geral:.2f}"
                }

                # Carrega o template
                doc = DocxTemplate("template.docx")
                doc.render(dados_contexto)
                
                nome_docx = "orcamento_temp.docx"
                nome_pdf = f"Orcamento_{cliente.replace(' ', '_')}.pdf"
                doc.save(nome_docx)

                # Conversão utilizando o LibreOffice Headless (Padrão Linux Cloud)
                subprocess.run(["libreoffice", "--headless", "--convert-to", "pdf", nome_docx], check=True)
                
                # O LibreOffice gera por padrão um arquivo chamado 'orcamento_temp.pdf'
                if os.path.exists("orcamento_temp.pdf"):
                    os.rename("orcamento_temp.pdf", nome_pdf)

                # Fornece o arquivo para download no navegador
                with open(nome_pdf, "rb") as f:
                    pdf_bytes = f.read()

                st.success("✨ PDF gerado com sucesso!")
                st.download_button(
                    label="📥 Baixar Orçamento em PDF",
                    data=pdf_bytes,
                    file_name=nome_pdf,
                    mime="application/pdf",
                    use_container_width=True
                )

                # Limpa os arquivos temporários do servidor
                if os.path.exists(nome_docx): os.remove(nome_docx)
                if os.path.exists(nome_pdf): os.remove(nome_pdf)

            except Exception as e:
                st.error(f"Erro ao gerar o documento: {e}")
