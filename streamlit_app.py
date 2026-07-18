import streamlit as st
import requests
import os

API_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="LiveScore", page_icon="🏏", layout="centered")
st.title("🏏 LiveScore")

# ---------- Helper functions to call the FastAPI backend ----------

def get_matches():
    response = requests.get(f"{API_URL}/matches/")
    response.raise_for_status()
    return response.json()

def create_match(team_a, team_b):
    response = requests.post(f"{API_URL}/matches/", json={"team_a": team_a, "team_b": team_b})
    response.raise_for_status()
    return response.json()

def update_score(match_id, score_a, score_b):
    response = requests.patch(
        f"{API_URL}/matches/{match_id}/score",
        json={"score_a": score_a, "score_b": score_b},
    )
    return response  # returning raw response so we can check status code (e.g. 400 if completed)

def complete_match(match_id):
    response = requests.patch(f"{API_URL}/matches/{match_id}/complete")
    response.raise_for_status()
    return response.json()

#ADDED AFTER DELETE FUN IN MATCHES.PY TO DELETE IT
def delete_match(match_id):
    response = requests.delete(f"{API_URL}/matches/{match_id}")
    return response


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
        else:
            try:
                new_match = create_match(team_a, team_b)
                st.success(f"Match created: {new_match['team_a']} vs {new_match['team_b']}")
            except requests.exceptions.RequestException as e:
                st.error(f"Failed to create match: {e}")


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
                        st.success("Score updated!")
                        st.rerun()
                    else:
                        st.error(resp.json().get("detail", "Failed to update score"))

                if st.button("Mark Completed", key=f"complete_{match['id']}"):
                    complete_match(match["id"])
                    st.success("Match marked as completed!")
                    st.rerun()
            else:
                st.write("✅ Match completed — score locked.")
                
            if st.button("🗑️ Delete Match", key=f"delete_{match['id']}"):
                resp = delete_match(match["id"])
                if resp.status_code == 204:
                    st.success("Match deleted!")
                    st.rerun()
                else:
                    st.error("Failed to delete match")
                
                
                
                