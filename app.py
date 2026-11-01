import requests
import streamlit as st

from chatbox import render_chatbox

API_URL = "http://127.0.0.1:8000"


st.set_page_config(page_title="Users", page_icon="👤", layout="centered")
render_chatbox(API_URL)
st.title("Add User")
st.caption("Enter user details below. They will be saved to the database via the API.")


def fetch_users():
    response = requests.get(f"{API_URL}/users", timeout=15)
    response.raise_for_status()
    return response.json()


with st.form("add_user_form", clear_on_submit=True):
    name = st.text_input("Name")
    email = st.text_input("Email")
    age = st.number_input("Age", min_value=1, max_value=120, value=25, step=1)
    submitted = st.form_submit_button("Save user", type="primary")

    if submitted:
        if not name.strip() or not email.strip():
            st.error("Name and email are required.")
        else:
            try:
                response = requests.post(
                    f"{API_URL}/users",
                    json={"name": name.strip(), "email": email.strip(), "age": int(age)},
                    timeout=15,
                )
                if response.status_code == 201:
                    user = response.json()
                    st.success(f"Saved {user['name']} (id {user['id']}) to the database.")
                    st.session_state["refresh_users"] = True
                else:
                    detail = response.json().get("detail", response.text)
                    st.error(f"Could not save user: {detail}")
            except requests.RequestException as exc:
                st.error(
                    f"Could not reach the API at {API_URL}. "
                    f"Make sure FastAPI is running. ({exc})"
                )


st.divider()
st.subheader("Users in database")

if st.button("Refresh list") or st.session_state.get("refresh_users"):
    st.session_state["refresh_users"] = False

try:
    users = fetch_users()
    if users:
        st.dataframe(users, use_container_width=True, hide_index=True)
    else:
        st.info("No users found yet.")
except requests.RequestException as exc:
    st.warning(
        f"Could not load users from {API_URL}. "
        f"Start the API with `fastapi run main.py`. ({exc})"
    )
