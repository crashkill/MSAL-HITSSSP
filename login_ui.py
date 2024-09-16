import streamlit as st
from msal_streamlit_authentication import msal_authentication


login_token = msal_authentication(
    auth={
        "clientId": st.secrets["CLIENT_ID"],
        "authority": f"https://login.microsoftonline.com/d6c7d4eb-ad17-46c8-a404-f6a92cbead96",
        "redirectUri": "https://msal-hitsssp.streamlit.app:8501/",
        "postLogoutRedirectUri": "/"
    }, # Corresponds to the 'auth' configuration for an MSAL Instance
    cache={
        "cacheLocation": "sessionStorage",
        "storeAuthStateInCookie": False
    }, # Corresponds to the 'cache' configuration for an MSAL Instance
    login_request={
        "scopes": ["User.Read"]
    }, # Optional
    logout_request={}, # Optional
    login_button_text="Login", # Optional, defaults to "Login"
    logout_button_text="Logout", # Optional, defaults to "Logout"
    class_name="css_button_class_selector", # Optional, defaults to None. Corresponds to HTML class.
    html_id="html_id_for_button", # Optional, defaults to None. Corresponds to HTML id.
    key=1 # Optional if only a single instance is needed
)
st.write("Recevied login token:", login_token)