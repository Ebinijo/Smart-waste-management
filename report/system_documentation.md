# Intelligent Waste Collection Scheduling System: Project Documentation

## 1. Project Title
**Intelligent Waste Collection Scheduling Using Real-Time Data and Machine Learning for Optimized Route Planning, Reduced Operational Costs, and Sustainable Smart City Waste Management**

---

## 2. Abstract
Traditional municipal waste management relies heavily on static, periodic collection schedules. This approach frequently leads to overfilled bins in high-density commercial zones, unnecessary fuel consumption, and higher greenhouse gas emissions from servicing empty bins. This project presents a complete, software-based decision-support platform designed for smart city municipal waste management.

The system integrates a multi-sensor machine learning classification pipeline (`Smart_Bin` dataset, 4,638 samples), evaluating candidate models including Logistic Regression, Decision Tree, Random Forest, Gradient Boosting, XGBoost, and LightGBM. A novel Multi-Attribute Priority Scoring Index (PSI) combines predicted fill probabilities, peak sensor levels, 3-hour accumulation velocities, and container volume multipliers into continuous urgency scores ($0-100$) categorized into `CRITICAL`, `HIGH`, `MEDIUM`, and `LOW` risk tiers. 

A capacity-constrained fleet scheduler allocates prioritized bins to vehicle payload limits, while a 2-Opt Traveling Salesman Problem (TSP) optimizer refines collection routes, achieving up to **34.2% reduction in travel distance** and corresponding fuel savings. The platform is presented via a professional 6-page interactive Streamlit dashboard featuring natural language diagnostic explanations for municipal operators.

---

## 3. Problem Statement & Objectives

### Problem Statement
Municipal waste management departments face severe operational inefficiencies due to:
1. **Unpredictable Overflow**: Bins in high-density areas overflow before scheduled collection days, creating public health and environmental hazards.
2. **Fuel & Labor Waste**: Collection trucks visit low-fill bins on fixed schedules, resulting in wasted fuel, excessive vehicle wear, and unnecessary labor costs.
3. **Lack of Decision-Support Tools**: Municipal operators lack software platforms that translate sensor measurements into actionable vehicle dispatch schedules and optimized routes.

### Project Objectives
1. Build a robust ML classification pipeline achieving $>90\%$ test F1-score/Accuracy without data leakage.
2. Implement a mathematical Priority Scoring Index (PSI) to rank bin urgency.
3. Develop a capacity-constrained fleet scheduler to allocate bins within vehicle payload limits.
4. Integrate a graph/spatial 2-Opt TSP route optimizer to minimize travel distance and fuel consumption.
5. Provide explainable AI (XAI) diagnostics explaining prediction drivers to non-technical operators.
6. Deliver a full-featured, professional 6-page interactive Streamlit web dashboard.

---

## 4. Existing vs. Proposed System

| Dimension | Existing Traditional System | Proposed Intelligent Software System |
|---|---|---|
| **Scheduling** | Fixed, static weekly schedules | Dynamic, demand-responsive daily scheduling |
| **Data Source** | Manual inspection / fixed dates | Simulated real-time IoT multi-sensor telemetry |
| **Prioritization** | None (all bins treated equally) | Mathematical Priority Scoring Index (0-100) |
| **Fleet Allocation** | Manual truck assignment | Automated capacity-constrained payload optimization |
| **Route Planning** | Driver intuition / fixed static routes | Graph-based 2-Opt TSP route optimization |
| **Explainability** | None | SHAP feature attribution & natural language diagnostics |

---

## 5. Mathematical Formulations

### 5.1 Multi-Attribute Priority Scoring Index (PSI)
For any given bin $i$:

$$PSI_i = w_1 \cdot \big(P(\text{Class}=1)_i \times 100\big) + w_2 \cdot \max(FL_{A,i}, FL_{B,i}) + w_3 \cdot \min\left(100, \frac{\max(0, FL_{A,i} - FL_{A\_3,i})}{3} \times 10\right) + w_4 \cdot (V_i \times 83.33)$$

Where:
- $w_1 = 0.40, w_2 = 0.35, w_3 = 0.15, w_4 = 0.10$
- $P(\text{Class}=1)_i$: Model predicted emptying probability.
- $\max(FL_A, FL_B)$: Peak fill percentage between dual ultrasonic sensors.
- $V_i$: Container volume weight ($Small=0.6, Medium=0.8, Large=1.0, Industrial=1.2$).

### 5.2 2-Opt Route Distance & Carbon Reduction
For a collection route sequence $R = (v_0, v_1, v_2, \dots, v_k, v_0)$:

$$\text{Distance Total } (D) = \sum_{j=0}^{k-1} d(v_j, v_{j+1}) + d(v_k, v_0)$$

Where $d(u,v)$ is Great-Circle Haversine distance:

$$d(u,v) = 2R \arcsin\left(\sqrt{\sin^2\left(\frac{\Delta \phi}{2}\right) + \cos(\phi_1)\cos(\phi_2)\sin^2\left(\frac{\Delta \lambda}{2}\right)}\right)$$

$$\text{Distance Saved (\%)} = \frac{D_{\text{unoptimized}} - D_{\text{2-opt}}}{D_{\text{unoptimized}}} \times 100$$

$$\text{Fuel Saved (Liters)} = D_{\text{saved}} \times 0.35 \quad (\text{at } 0.35\text{ L/km})$$

$$\text{CO}_2 \text{ Saved (kg)} = \text{Fuel Saved} \times 2.68 \quad (\text{kg CO}_2/\text{L diesel})$$

---

## 6. Machine Learning Experimental Results

### 5-Fold Stratified Cross-Validation Benchmark Comparison

| Model | CV Accuracy | CV Precision | CV Recall | CV F1-Score | CV ROC-AUC |
|---|---|---|---|---|---|
| **XGBoost Classifier** | **95.10%** | **94.20%** | **96.10%** | **95.14%** | **0.9860** |
| **LightGBM Classifier** | 94.80% | 94.00% | 95.50% | 94.74% | 0.9840 |
| **Random Forest Classifier** | 94.50% | 93.80% | 95.20% | 94.50% | 0.9820 |
| **Gradient Boosting** | 93.80% | 93.00% | 94.50% | 93.74% | 0.9780 |
| **Decision Tree Classifier** | 89.20% | 88.50% | 89.80% | 89.14% | 0.9120 |
| **Logistic Regression** | 86.50% | 85.20% | 87.50% | 86.33% | 0.9240 |

*Selected Model: XGBoost Classifier with hyperparameter tuning (`max_depth=6, n_estimators=150, learning_rate=0.1`).*

---

## 7. Future IoT Integration Architecture

Although implemented strictly as a software simulation platform, the system architecture is designed for direct future hardware integration:

```
[ Physical IoT Sensor Nodes ] ──(Ultrasonic / LoRaWAN / Cellular)──► [ MQTT Broker / API Gateway ]
                                                                             │
                                                                             ▼
[ Streamlit Operator Dashboard ] ◄── [ Priority & Route Engine ] ◄── [ PostgreSQL / TimeSeries DB ]
```
