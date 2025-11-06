import streamlit as st
from pymongo import MongoClient
import pandas as pd
import os
from utils.data_generator import generate_customer, generate_product, generate_order

MONGO_URI = os.environ.get("MONGO_URI", "mongodb://localhost:27017/eshop")
client = MongoClient(MONGO_URI)
db = client.get_database()

st.set_page_config(layout="wide", page_title="E-Shop Brasil - Demo")
st.title("E-Shop Brasil — Painel de Gestão (Demo)")

tabs = st.tabs(["Visão Geral", "Clientes", "Produtos",
               "Pedidos", "Gerar Dados", "Segurança / LGPD"])

with tabs[0]:
    st.header("Visão Geral")
    col1, col2, col3 = st.columns(3)
    total_customers = db.customers.count_documents({})
    total_products = db.products.count_documents({})
    total_orders = db.orders.count_documents({})
    col1.metric("Clientes", total_customers)
    col2.metric("Produtos", total_products)
    col3.metric("Pedidos", total_orders)
    if st.checkbox("Mostrar amostra de pedidos"):
        df = pd.DataFrame(list(db.orders.find().limit(20)))
        st.dataframe(df)

with tabs[1]:
    st.header("Clientes")
    with st.expander("Inserir cliente manualmente"):
        name = st.text_input("Nome")
        email = st.text_input("Email")
        if st.button("Inserir cliente"):
            cust = generate_customer()
            cust["name"] = name or cust["name"]
            cust["email"] = email or cust["email"]
            db.customers.insert_one(cust)
            st.success("Cliente inserido com id: " + cust["_id"])

    st.markdown("#### Buscar / Editar / Excluir")
    query = st.text_input("Buscar por email ou nome")
    if st.button("Buscar clientes"):
        cursor = db.customers.find({"$or": [{"email": {"$regex": query, "$options": "i"}}, {
                                   "name": {"$regex": query, "$options": "i"}}]}) if query else db.customers.find().limit(50)
        df = pd.DataFrame(list(cursor))
        if not df.empty:
            df["name_email"] = df["name"].astype(
                str) + " <" + df["email"].astype(str) + ">"
        st.dataframe(df)
        if not df.empty:
            idx = st.selectbox(
                "Escolha um cliente para editar/excluir", df["_id"].tolist())
            selected = db.customers.find_one({"_id": idx})
            new_name = st.text_input("Nome", value=selected["name"])
            new_email = st.text_input("Email", value=selected["email"])
            if st.button("Salvar alterações"):
                db.customers.update_one(
                    {"_id": idx}, {"$set": {"name": new_name, "email": new_email}})
                st.success("Atualizado")
            if st.button("Excluir cliente"):
                db.customers.delete_one({"_id": idx})
                st.warning("Cliente excluído")

with tabs[2]:
    st.header("Produtos")
    if st.button("Listar produtos"):
        df = pd.DataFrame(list(db.products.find().limit(100)))
        st.dataframe(df)
    with st.expander("Inserir produto rápido"):
        p = generate_product()
        if st.button("Inserir produto gerado"):
            db.products.insert_one(p)
            st.success("Produto inserido: " + p["sku"])

with tabs[3]:
    st.header("Pedidos")
    if st.button("Listar últimos pedidos"):
        df = pd.DataFrame(
            list(db.orders.find().sort("created_at", -1).limit(50)))
        st.dataframe(df)
    st.markdown("#### Consultas de exemplo")
    status = st.selectbox("Filtrar por status", [
                          "all", "pending", "confirmed", "shipped", "delivered", "cancelled"])
    if st.button("Aplicar filtro"):
        if status == "all":
            cursor = db.orders.find().limit(200)
        else:
            cursor = db.orders.find({"status": status})
        df = pd.DataFrame(list(cursor))
        st.dataframe(df)

with tabs[4]:
    st.header("Gerar dados de exemplo")
    n_customers = st.number_input(
        "Clientes", min_value=0, max_value=5000, value=50)
    n_products = st.number_input(
        "Produtos", min_value=0, max_value=2000, value=100)
    n_orders = st.number_input(
        "Pedidos", min_value=0, max_value=2000, value=200)
    if st.button("Gerar dados"):
        customers = [generate_customer() for _ in range(n_customers)]
        products = [generate_product() for _ in range(n_products)]
        db.customers.insert_many(customers)
        db.products.insert_many(products)
        orders = [generate_order(customers, products) for _ in range(n_orders)]
        db.orders.insert_many(orders)
        st.success(
            f"Gerados {n_customers} clientes, {n_products} produtos, {n_orders} pedidos.")

with tabs[5]:
    st.header("Segurança e LGPD - Boas práticas")
    st.markdown("""
- **Criptografia:** TLS para conexões, dados sensíveis criptografados em repouso.
- **Pseudonimização:** evitar identificação direta em pipelines de análise.
- **Consentimento:** registrar opt-in para comunicações de marketing.
- **Retenção:** políticas de retenção e exclusão sob demanda (direito de ser esquecido).
- **Acesso:** RBAC e logs de auditoria.
""")
