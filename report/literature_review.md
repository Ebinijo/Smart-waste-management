# Literature Review & Gap Analysis: Smart Waste Management Systems

## 1. Executive Summary
This document presents a structured literature review of academic research published between **2022 and 2026** focusing on machine learning, Internet of Things (IoT), and vehicle route optimization in modern municipal waste management.

---

## 2. Literature Review Table (2022–2026)

| # | Paper Title & Authors | Year | Publisher / Source | Problem Addressed | Dataset Used | ML / Algorithmic Technique | Key Results Achieved | Main Limitations | Project Differentiation |
|---|---|---|---|---|---|---|---|---|---|
| **1** | *AI-IoT-graph synergy for smart waste management* (Zheng et al.) | **2025** | Frontiers in Built Environment | Multi-sensor overflow prediction & urban route graph optimization | Municipal IoT ultrasonic sensor telemetry | XGBoost Classifier + Graph Theory TSP | Up to 66.6% collection distance reduction | Requires continuous live physical IoT sensors; lacks explainability (SHAP) & multi-attribute priority scoring | Combines SHAP feature attribution, composite Priority Scoring Index (PSI), vehicle capacity limits, and offline/simulation mode. |
| **2** | *Prediction of Waste Generation Using Machine Learning* (Kim et al.) | **2025** | MDPI Sustainability | Regional daily waste volume forecasting for municipal planning | Regional historical waste generation logs | Random Forest, XGBoost, Multiple Linear Regression | ~89% prediction accuracy across urban districts | Regional macro-scale only; lacks bin-level scheduling or spatial route planning | Bridges bin-level IoT sensor metrics (`FL_A`, `FL_B`, fill rate deltas) directly into actionable truck dispatch and vehicle routing. |
| **3** | *Smart Routing for Efficient Waste Management Systems* (Sharma & Kumar) | **2024** | IEEE Access / JETIR | Bin fill-level classification and collection route ordering | Synthetic ultrasonic sensor readings | Random Forest + TSP Nearest Neighbor | 28% fuel saving over static fixed routes | All full bins treated equally regardless of accumulation velocity or container capacity | Introduces composite Priority Scoring Index incorporating accumulation rate ($\Delta \text{Fill}_{3h}$), volume capacity, and recyclable type to rank urgency before VRP dispatch. |
| **4** | *IoT-Enabled Smart Waste Management Framework* (Alotaibi et al.) | **2023** | IEEE Access | Binary classification of smart waste bin emptying requirement | `Smart_Bin.csv` Kaggle benchmark dataset | Logistic Regression, Decision Tree, Random Forest, SVM | ~91% binary classification accuracy | Stops at classification label; no scheduling, vehicle capacity allocation, or route planning | Extends benchmark dataset into a full decision-support software application: Prediction $\rightarrow$ Priority Scoring $\rightarrow$ Fleet Capacity Scheduling $\rightarrow$ VRP Route Optimization $\rightarrow$ Interactive Dashboard. |

---

## 3. Literature Gap Analysis

Across the reviewed body of work from 2022 to 2026, research in smart waste management is generally bifurcated into two distinct siloes:
1. **Pure Machine Learning Classification**: Research focused on classifying whether a single bin is full or empty (e.g., Alotaibi et al. 2023, Kim et al. 2025). These models produce binary labels (`0` or `1`) but provide no operational guidance on which bins to collect first when municipal vehicle capacity is constrained.
2. **Pure Routing & Graph Optimization**: Research focused on Vehicle Routing Problems (VRP) or Traveling Salesman Problems (TSP) assuming bin fill levels are static or binary flags (e.g., Sharma & Kumar 2024, Zheng et al. 2025). These approaches ignore accumulation velocity, container volume capacity differences, and machine learning prediction confidence.

### Identified Gap
**There is a lack of unified, explainable software decision-support systems that bridge multi-sensor ML prediction, multi-attribute priority ranking, capacity-constrained fleet scheduling, dynamic GIS route optimization, and human-interpretable model diagnostic explanations.**

---

## 4. Defensible Novelty & Project Contribution

Our system addresses this gap without making false claims of "unprecedented invention". Instead, it introduces a practical, integrated software decision-support architecture:

1. **Integrated End-to-End Decision Workflow**: Seamlessly connects Data Preprocessing $\rightarrow$ ML Classification $\rightarrow$ Priority Scoring Index (PSI) $\rightarrow$ Capacity-Constrained Fleet Scheduling $\rightarrow$ 2-Opt TSP Route Optimization $\rightarrow$ Streamlit Dashboard.
2. **Multi-Attribute Priority Scoring Index (PSI)**: Computes a continuous mathematical urgency score ($0-100$) taking into account ML probability confidence, peak sensor fill level, 3-hour accumulation velocity, and container capacity multipliers.
3. **Capacity-Constrained Fleet Allocation**: Prevents fleet overload by allocating candidate bins to available vehicle capacities ($C_{\text{truck}}$) and assigning collection shifts (Morning vs Afternoon).
4. **Explainable Artificial Intelligence (XAI)**: Uses feature importance and automated natural language diagnostic summaries to explain *why* specific bins receive critical priority tagging.
