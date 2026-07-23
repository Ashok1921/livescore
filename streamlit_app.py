import streamlit as st
import requests
import os
from streamlit_autorefresh import st_autorefresh




API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

# --- Session state initialization ---
if "token" not in st.session_state:
    st.session_state.token = None
if "username" not in st.session_state:
    st.session_state.username = None
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "flash_message" not in st.session_state:
    st.session_state.flash_message = None
if "flash_type" not in st.session_state:
    st.session_state.flash_type = None  # "success" or "error"



def login(username: str, password: str) -> bool:
    """Calls /auth/login and populates session state on success."""
    try:
        response = requests.post(
            f"{API_URL}/auth/login",
            json={"username": username, "password": password},
        )
        if response.status_code == 200:
            data = response.json()
            st.session_state.token = data["access_token"]
            st.session_state.username = username
            st.session_state.logged_in = True
            return True
        else:
            return False
    except requests.exceptions.RequestException:
        return False


def logout():
    st.session_state.token = None
    st.session_state.username = None
    st.session_state.logged_in = False
    
    
def auth_headers():
    """Returns the Authorization header if logged in, else empty dict."""
    if st.session_state.token:
        return {"Authorization": f"Bearer {st.session_state.token}"}
    return {}    
    


st.set_page_config(page_title="LiveScore", page_icon="🏏", layout="centered")
st.title("🏏 LiveScore")
# Auto-refresh every 3 seconds (3000 ms)
st_autorefresh(interval=3000, key="score_autorefresh")

# ---------- Flash message display (shown once, then cleared) ----------
if st.session_state.flash_message:
    if st.session_state.flash_type == "success":
        st.success(st.session_state.flash_message)
    else:
        st.error(st.session_state.flash_message)
    st.session_state.flash_message = None
    st.session_state.flash_type = None


# ---------- Sidebar: Login / Logout ----------
with st.sidebar:
    if st.session_state.logged_in:
        st.write(f"Logged in as **{st.session_state.username}**")
        if st.button("Logout"):
            logout()
            st.session_state.flash_message = "Logged out successfully"
            st.session_state.flash_type = "success"
            st.rerun()
    else:
        st.subheader("Admin Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            if submitted:
                if login(username, password):
                    st.session_state.flash_message = "Logged in successfully"
                    st.session_state.flash_type = "success"
                    st.rerun()
                else:
                    st.session_state.flash_message = "Invalid username or password"
                    st.session_state.flash_type = "error"
                    st.rerun()


# ---------- Helper functions to call the FastAPI backend ----------

def get_matches():
    response = requests.get(f"{API_URL}/matches/")
    response.raise_for_status()
    return response.json()


def create_match(team_a, team_b):
    response = requests.post(
        f"{API_URL}/matches/",
        json={"team_a": team_a, "team_b": team_b},
        headers=auth_headers(),
    )
    return response  # changed from raise_for_status so we can handle 401 in the UI

def update_score(match_id, score_a, score_b):
    response = requests.patch(
        f"{API_URL}/matches/{match_id}/score",
        json={"score_a": score_a, "score_b": score_b},
        headers=auth_headers(),
    )
    return response

def delete_match(match_id):
    response = requests.delete(f"{API_URL}/matches/{match_id}", headers=auth_headers())
    return response

def complete_match(match_id):
    response = requests.patch(f"{API_URL}/matches/{match_id}/complete", headers=auth_headers())
    return response  # changed from raise_for_status, same reason as others


# ---------- Section 1: Create a new match ----------

st.header("Create a new match")
with st.form("create_match_form"):
    col1, col2 = st.columns(2)
    team_a = col1.text_input("Team A")
    team_b = col2.text_input("Team B")
    submitted = st.form_submit_button("Create Match")

    if submitted:
        if not team_a or not team_b:
            st.warning("Please enter both team names.")
        elif not st.session_state.logged_in:
            st.session_state.flash_message = "Please log in to create a match."
            st.session_state.flash_type = "error"
            st.rerun()
        else:
            resp = create_match(team_a, team_b)
            if resp.status_code in (200, 201):
                new_match = resp.json()
                st.session_state.flash_message = f"Match created: {new_match['team_a']} vs {new_match['team_b']}"
                st.session_state.flash_type = "success"
            elif resp.status_code == 401:
                st.session_state.flash_message = "Session expired. Please log in again."
                st.session_state.flash_type = "error"
            else:
                st.session_state.flash_message = f"Failed to create match: {resp.text}"
                st.session_state.flash_type = "error"
            st.rerun()

# ---------- Section 2: List all matches ----------

st.header("All Matches")

try:
    matches = get_matches()
except requests.exceptions.RequestException as e:
    st.error(f"Could not reach backend. Is FastAPI running? ({e})")
    matches = []

if not matches:
    st.info("No matches yet. Create one above.")
else:
    for match in matches:
        with st.container(border=True):
            st.subheader(f"{match['team_a']} vs {match['team_b']}")
            st.write(f"**Status:** {match['status']}")
            st.write(f"**Score:** {match['score_a']} - {match['score_b']}")

            # Only show update controls if match is not completed
            if match["status"] != "COMPLETED":
                col1, col2, col3 = st.columns([1, 1, 1])
                new_score_a = col1.number_input(
                    f"{match['team_a']} score", min_value=0,
                    value=match["score_a"], key=f"score_a_{match['id']}"
                )
                new_score_b = col2.number_input(
                    f"{match['team_b']} score", min_value=0,
                    value=match["score_b"], key=f"score_b_{match['id']}"
                )

                if col3.button("Update Score", key=f"update_{match['id']}"):
                    resp = update_score(match["id"], new_score_a, new_score_b)
                    if resp.status_code == 200:
                        st.session_state.flash_message = "Score updated!"
                        st.session_state.flash_type = "success"
                    elif resp.status_code == 401:
                        st.session_state.flash_message = "Please log in to update score."
                        st.session_state.flash_type = "error"
                    else:
                        st.session_state.flash_message = resp.json().get("detail", "Failed to update score")
                        st.session_state.flash_type = "error"
                    st.rerun()

                if st.button("Mark Completed", key=f"complete_{match['id']}"):
                    resp = complete_match(match["id"])
                    if resp.status_code == 200:
                        st.session_state.flash_message = "Match marked as completed!"
                        st.session_state.flash_type = "success"
                    elif resp.status_code == 401:
                        st.session_state.flash_message = "Please log in to complete a match."
                        st.session_state.flash_type = "error"
                    else:
                        st.session_state.flash_message = "Failed to mark match completed"
                        st.session_state.flash_type = "error"
                    st.rerun()
            else:
                st.write("✅ Match completed — score locked.")
                
            if st.button("🗑️ Delete Match", key=f"delete_{match['id']}"):
                resp = delete_match(match["id"])
                if resp.status_code == 204:
                    st.session_state.flash_message = "Match deleted!"
                    st.session_state.flash_type = "success"
                elif resp.status_code == 401:
                    st.session_state.flash_message = "Please log in to delete a match."
                    st.session_state.flash_type = "error"
                else:
                    st.session_state.flash_message = "Failed to delete match"
                    st.session_state.flash_type = "error"
                st.rerun()