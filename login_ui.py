import requests
import streamlit as st
from msal import ConfidentialClientApplication


def initialize_app():
    client_id = st.secrets.get("CLIENT_ID")
    tenant_id = st.secrets.get("TENANT_ID")
    client_secret = st.secrets.get("CLIENT_SECRET")
    if not client_id or not tenant_id or not client_secret:
        st.error("Configurações de autenticação não encontradas. Verifique os secrets.")
        return None
    authority_url = f"https://login.microsoftonline.com/{tenant_id}"
    return ConfidentialClientApplication(client_id, authority=authority_url, client_credential=client_secret)


def acquire_access_token(app, code, scopes, redirect_uri):
    if not app or not code:
        st.error("Aplicativo MSAL ou código de autenticação não disponível.")
        return None
    return app.acquire_token_by_authorization_code(code, scopes=scopes, redirect_uri=redirect_uri)


def fetch_user_data(access_token):
    if not access_token:
        st.error("Token de acesso não encontrado.")
        return None
    headers = {"Authorization": f"Bearer {access_token}"}
    graph_api_endpoint = "https://graph.microsoft.com/v1.0/me"
    response = requests.get(graph_api_endpoint, headers=headers)
    if response.status_code != 200:
        st.error(f"Erro ao buscar dados do usuário: {response.text}")
        return None
    return response.json()


def authentication_process(app, user_email, user_password):
    scopes = ["User.Read"]
    redirect_uri = st.secrets.get("REDIRECT_URI")
    
    if not redirect_uri:
        st.error("Redirect URI não configurado nos secrets.")
        return
    
    auth_url = app.get_authorization_request_url(scopes, redirect_uri=redirect_uri)

    # Obtém os parâmetros da URL usando st.query_params (como um dicionário)
    query_params = st.query_params

    # Verificar se "code" existe nos query_params e se não está vazio
    if query_params and "code" in query_params:
        st.session_state["auth_code"] = query_params["code"][0]
        token_result = acquire_access_token(app, st.session_state["auth_code"], scopes, redirect_uri)
        
        if token_result and "access_token" in token_result:
            user_data = fetch_user_data(token_result["access_token"])
            return user_data
        else:
            st.error("Falha ao adquirir token. Verifique as credenciais e tente novamente.")
    else:
        # Exibir uma mensagem indicando o início da autenticação
        st.write(f"Tentando autenticar com o email: {user_email}")
        st.markdown(f'<meta http-equiv="refresh" content="0; url={auth_url}">', unsafe_allow_html=True)


def login_ui():
    st.title("Autenticação Microsoft")

    # Inicializar as chaves do session_state, se ainda não existirem
    if "authenticated" not in st.session_state:
        st.session_state["authenticated"] = False
    if "display_name" not in st.session_state:
        st.session_state["display_name"] = ""

    # Se o usuário não estiver autenticado, exibir o formulário de login
    if not st.session_state["authenticated"]:
        user_email = st.text_input("Azure Email", placeholder="Digite seu email Azure", key="email_input")
        user_password = st.text_input("Senha", placeholder="Digite sua senha Azure", type="password", key="password_input")

        if st.button("Login com Azure", key="login_button"):
            if not user_email or not user_password:
                st.warning("Por favor, insira o email e a senha.")
            else:
                app = initialize_app()
                if app:
                    user_data = authentication_process(app, user_email, user_password)
                    if user_data:
                        st.session_state["authenticated"] = True
                        st.session_state["display_name"] = user_data.get("displayName")
                        st.experimental_rerun()  # Reinicializa a aplicação para refletir o estado atualizado
    else:
        st.write(f"Bem-vindo, {st.session_state['display_name']}")


# Chamar a interface de login
login_ui()
