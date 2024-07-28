#!/usr/bin/env python
import sys
from insight_tracker.crew import InsightTrackerCrew
import streamlit as st

st.title("Insight Tracker")
name = st.text_input("Name")
company = st.text_input("Company")
if(st.button("Research")) :
    inputs = {
        'profile': name,
        'company': company
    }
    result = InsightTrackerCrew().crew().kickoff(inputs=inputs)
    st.markdown(result.tasks_output[1].raw)
    st.text_area(label='Draft Email to Reach' + name, value=result, height=300)

# This main file is intended to be a way for your to run your
# crew locally, so refrain from adding necessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

def run():
    """
    Run the crew.
    """
    inputs = {
        'profile': 'Nicolas escallon',
        'company': 'actis'
    }
    InsightTrackerCrew().crew().kickoff(inputs=inputs)


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs"
    }
    try:
        InsightTrackerCrew().crew().train(n_iterations=int(sys.argv[1]), inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        InsightTrackerCrew().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")
