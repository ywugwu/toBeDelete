import streamlit as st
import pandas as pd
# from graphviz import Digraph
import os


# def create_detailed_decision_tree(harvest_value, detector_value, P_storm_given_storm_prediction,
#                                   P_no_storm_given_storm_prediction, P_storm_given_no_storm_prediction,
#                                   P_no_storm_given_no_storm_prediction, wait_case1_a, wait_case1_b,
#                                   wait_case2_a, wait_case2_b, case1, case2):
#     dot = Digraph()

#     # Root node
#     dot.attr('node', shape='ellipse', style='filled', color='lightblue')
#     dot.node('R', 'Decision: Buy Detector or Harvest Now')

#     # Harvest now node
#     dot.attr('node', shape='box', style='filled', color='lightgrey')
#     dot.node('H', f'Harvest Now\nRevenue: ${harvest_value}')
#     dot.edge('R', 'H')

#     # Buy detector node
#     dot.attr('node', shape='ellipse', style='filled', color='lightblue')
#     dot.node('B', 'Buy Detector')
#     dot.edge('R', 'B')

#     # Storm prediction branches
#     dot.attr('node', shape='diamond', style='filled', color='lightgreen')
#     dot.node('C1', 'Storm Prediction')
#     dot.node('D1', f'Actual Storm\nP={P_storm_given_storm_prediction}')
#     dot.node('E1', f'No Actual Storm\nP={P_no_storm_given_storm_prediction}')
#     dot.edge('B', 'C1')
#     dot.edge('C1', 'D1')
#     dot.edge('C1', 'E1')

#     # No storm prediction branches
#     dot.node('C2', 'No Storm Prediction')
#     dot.node('D2', f'Actual Storm\nP={P_storm_given_no_storm_prediction}')
#     dot.node('E2', f'No Actual Storm\nP={P_no_storm_given_no_storm_prediction}')
#     dot.edge('B', 'C2')
#     dot.edge('C2', 'D2')
#     dot.edge('C2', 'E2')

#     # Outcome nodes for each scenario
#     dot.attr('node', shape='box', style='filled', color='lightgrey')
#     dot.node('F1', f'Revenue: ${wait_case1_a}')
#     dot.node('G1', f'Revenue: ${wait_case1_b}')
#     dot.node('F2', f'Revenue: ${wait_case2_a}')
#     dot.node('G2', f'Revenue: ${wait_case2_b}')
#     dot.edge('D1', 'F1')
#     dot.edge('E1', 'G1')
#     dot.edge('D2', 'F2')
#     dot.edge('E2', 'G2')

#     # Value calculation nodes
#     dot.attr('node', shape='box', style='filled', color='gold')
#     dot.node('Val1', f'Value with Storm Pred.: ${case1}')
#     dot.node('Val2', f'Value with No Storm Pred.: ${case2}')
#     dot.node('ValB', f'Total Value by Detector: ${detector_value}')
#     dot.edge('F1', 'Val1')
#     dot.edge('G1', 'Val1')
#     dot.edge('F2', 'Val2')
#     dot.edge('G2', 'Val2')
#     dot.edge('Val1', 'ValB')
#     dot.edge('Val2', 'ValB')

#     # Save and display the graph
#     dot.render('detailed_decision_tree', format='png', cleanup=True)
#     return 'detailed_decision_tree.png'

# Data and initial setup
data = {
    'Riesling Type': ['Trocken', 'Kabinett', 'Spätlese', 'Auslese', 'Beerenauslese', 'Trockenbeerenauslese'],
    'Sweetness': ['dry', 'off-dry', 'sweet', 'sweeter', 'very sweet', 'super sweet'],
    'Market Revenue Per Bottle ($)': [5, 10, 15, 30, 40, 120],
    'Harvest Now': [6000, 2000, 2000, 0, 0, 0],
    'Storm-No Mold': [5000, 1000, 0, 0, 0, 0],
    'Storm-Mold': [5000, 1000, 0, 0, 0, 2000],
    'No Storm-No Sugar': [6000, 2000, 2000, 0, 0, 0],
    'No Storm-Typical Sugar': [5000, 1000, 2500, 1500, 0, 0],
    'No Storm-High Sugar': [4000, 2500, 2000, 1000, 500, 0]
}
riesling_df = pd.DataFrame(data)

# Probability adjustments via sliders
p_mold = st.slider('Chance of Botrytis (Mold)', 0.0, 1.0, 0.1)
p_no_sugar = st.slider('Chance of No Sugar Increase', 0.0, 1.0, 0.6)
p_typical_sugar = st.slider('Chance of Typical Sugar Increase', 0.0, 1.0, 0.3)
p_high_sugar = st.slider('Chance of High Sugar Increase', 0.0, 1.0, 0.1)

# Function to compute decision values
def compute_decision_values(df):
    harvest_now = sum(df['Harvest Now'] * df['Market Revenue Per Bottle ($)'])
    harvest_now_total = harvest_now * 12

    # Computing values for decision based on waiting and storm probabilities
    wait_case1_a = sum((df['Storm-No Mold']*0.9 + df['Storm-Mold']*0.1) * df['Market Revenue Per Bottle ($)'])
    wait_case1_b = sum((df['No Storm-No Sugar']*p_no_sugar + df['No Storm-Typical Sugar']*p_typical_sugar + df['No Storm-High Sugar']*p_high_sugar) * df['Market Revenue Per Bottle ($)'])
    wait_case1_a_total = wait_case1_a * 12
    wait_case1_b_total = wait_case1_b * 12

    # Sensitivity and specificity related calculations
    recall = 0.29  # Given as sensitivity
    specificity = 0.65

    P_storm_given_storm_prediction = recall
    P_no_storm_given_storm_prediction = 1 - recall
    P_no_storm_given_no_storm_prediction = specificity
    P_storm_given_no_storm_prediction = 1 - specificity

    case1 = int(P_storm_given_storm_prediction * wait_case1_a_total + P_no_storm_given_storm_prediction * wait_case1_b_total)
    case2 = int(P_storm_given_no_storm_prediction * wait_case1_a_total + P_no_storm_given_no_storm_prediction * wait_case1_b_total)

    ds = 0.33
    dns = 0.67

    buy_detector = int(ds * case1 + dns * case2)

    # Determine recommended action
    recommended_action = "Harvest Now" if harvest_now_total > buy_detector else "Buy Detector and Wait"

    return harvest_now_total, buy_detector, recommended_action

# Calculate values
# Calculate values
harvest_value, detector_value, recommended = compute_decision_values(riesling_df)

# Display results
st.write("Harvest Now Value: $", harvest_value)
st.write("Value if Buying Detector: $", detector_value)
st.write("Recommended Decision: ", recommended)


# # Generate and display the decision tree graph
# graph_path = create_detailed_decision_tree(harvest_value, detector_value, 0.29, 0.71, 0.65, 0.35, 0.33, 0.67, 0.33, 0.67, 0.33, 0.67)
# st.image(graph_path)

