# Academic Viva Examination Q&A: Intelligent Waste Collection Scheduling System

This document contains 35 likely viva questions and technical answers designed to assist in defending the project during academic examination.

---

### Category 1: Project Scope, Motivation & Literature Review

#### Q1: What is the main objective of your project?
**Answer:** The objective is to build a software-based decision-support platform that uses machine learning and spatial optimization to predict waste bin overflow, assign mathematical priority scores, schedule vehicle fleets within capacity limits, and optimize collection routes to minimize fuel consumption and operational costs.

#### Q2: Why did you implement this as a software-based system instead of building physical IoT hardware?
**Answer:** Real-world municipal waste platforms rely on software decision-support engines to process telemetry. Implementing a software system allowed us to focus deeply on ML modeling, data leakage prevention, multi-attribute priority scoring, fleet capacity scheduling, 2-Opt route optimization, and interactive dashboard design, while maintaining complete compatibility for future physical IoT sensor integration.

#### Q3: How is your approach different from existing research papers?
**Answer:** Most papers treat smart waste management as isolated tasks—either pure binary ML classification or pure route optimization assuming static bin fill levels. Our project unifies both into an end-to-end decision workflow: ML Prediction $\rightarrow$ Priority Scoring Index (PSI) $\rightarrow$ Capacity Fleet Scheduling $\rightarrow$ 2-Opt TSP Route Optimization $\rightarrow$ Interactive Dashboard with SHAP Explainability.

#### Q4: Did you claim any unsupported novelty in your research?
**Answer:** No. We explicitly identified a practical combination and extension of existing techniques—combining multi-sensor feature engineering, multi-attribute priority index calculation, capacity-constrained scheduling, and 2-Opt TSP route optimization into a single explainable software workflow.

#### Q5: What dataset did you use for training your ML model?
**Answer:** We used the Kaggle benchmark `Smart_Bin.csv` dataset (~4,638 samples) containing sensor metrics such as dual ultrasonic fill levels (`FL_A`, `FL_B`), historical 3-hour and 12-hour fill levels (`FL_A_3`, `FL_A_12`), volume metric (`VS`), container type, and recyclable fraction.

---

### Category 2: Machine Learning, Preprocessing & Data Leakage

#### Q6: How did you prevent data leakage during model training?
**Answer:** We enforced strict separation by performing an 80/20 train/test split on the raw dataset *before* any feature scaling or encoder transformation. The `StandardScaler` was fitted strictly on `X_train`, and then applied to `X_test`. Feature engineering equations only used information available at time $T$ (historical fill levels $T-3h$, $T-12h$) without future information.

#### Q7: What engineered features did you create, and why?
**Answer:** We engineered:
1. `fill_diff_A_3` ($FL_A - FL_{A\_3}$) and `acc_rate_3h`: To capture short-term accumulation velocity (%/hr).
2. `max_fill` ($\max(FL_A, FL_B)$): To represent peak bin fill level across dual sensors.
3. `sensor_delta` ($|FL_A - FL_B|$): To detect sensor obstruction or hardware discrepancy.
4. `container_vol_weight`: To weight container capacity differences (Industrial = 1.2, Small = 0.6).

#### Q8: Which machine learning models did you compare, and which performed best?
**Answer:** We evaluated 6 models using 5-Fold Stratified Cross-Validation: Logistic Regression, Decision Tree, Random Forest, Gradient Boosting, XGBoost, and LightGBM. **XGBoost** achieved the highest F1-Score (~95.14%) and test accuracy (~95.10%), outperforming simpler models.

#### Q9: Why is accuracy alone insufficient for evaluating your ML model?
**Answer:** Accuracy can be misleading in imbalanced datasets. We evaluated Precision (minimizing false collection alerts), Recall (ensuring full bins are not missed), F1-Score (harmonic mean of precision and recall), and ROC-AUC (class discrimination capability).

#### Q10: How did you handle hyperparameter tuning?
**Answer:** We performed `GridSearchCV` on the top-performing model (XGBoost) over hyperparameters including `n_estimators` (100, 150), `max_depth` (4, 6, 8), and `learning_rate` (0.05, 0.1) using 5-Fold Stratified Cross-Validation.

---

### Category 3: Priority Scoring Index (PSI) & Scheduling

#### Q11: How is the Priority Scoring Index (PSI) calculated mathematically?
**Answer:** The score $S_i \in [0, 100]$ is calculated as:
$$PSI = w_1 (P_{\text{Empty}} \times 100) + w_2 \max(FL_A, FL_B) + w_3 (\text{AccRate}_{3h} \times 10) + w_4 (\text{VolWeight} \times 83.33)$$
With weights: $w_1 = 0.40$ (ML probability), $w_2 = 0.35$ (Peak fill level), $w_3 = 0.15$ (Accumulation rate), $w_4 = 0.10$ (Container volume factor).

#### Q12: What are the priority categories, and what do they mean?
**Answer:**
- **CRITICAL** ($\ge 80$): Immediate collection required today (Shift 1).
- **HIGH** ($65-79$): Collection required today (Shift 2).
- **MEDIUM** ($45-64$): Scheduled for next shift or tomorrow.
- **LOW** ($<45$): Defer collection; monitor sensor telemetry.

#### Q13: How does the fleet scheduling algorithm work when vehicle capacity is limited?
**Answer:** Bins are sorted strictly by descending Priority Score. The algorithm iteratively assigns bins to available vehicles up to the maximum truck payload capacity ($C_{\text{truck}}$). If the total daily fleet capacity is exceeded, lower-priority bins are safely deferred to the next collection window, preventing vehicle overload.

#### Q14: What happens if two bins have the exact same fill level?
**Answer:** The Priority Scoring Index differentiates them using 3-hour accumulation velocity ($\Delta FL_{3h}$) and container capacity multipliers. A large industrial bin rapidly accumulating waste will receive a higher priority score than a small bin with steady fill level.

---

### Category 4: Route Optimization & GIS Spatial Planning

#### Q15: What algorithm did you use for route optimization?
**Answer:** We used a 2-stage Traveling Salesman Problem (TSP) heuristic:
1. **Nearest Neighbor**: Generates a fast initial collection sequence starting from the Municipal Fleet Depot.
2. **2-Opt Local Search**: Iteratively swaps sub-route edges to eliminate crossing paths and minimize total round-trip distance.

#### Q16: How did you calculate travel distances between bins?
**Answer:** We computed a Great-Circle (Haversine) distance matrix using bin latitude and longitude GPS coordinates.

#### Q17: What performance improvements did your route optimization achieve?
**Answer:** Compared to static sequential collection order, the 2-Opt TSP route optimizer achieved up to **34.2% reduction in travel distance**, resulting in direct fuel savings (~0.35 L diesel per saved km) and reduced CO2 emissions (~2.68 kg CO2 per liter).

#### Q18: Do you claim that your route is globally optimal?
**Answer:** No. TSP is an NP-hard problem. We clearly label our solution as a 2-Opt heuristic approximation that significantly improves real-world collection paths while remaining computationally fast.

---

### Category 5: Dashboard, Explainability & Architecture

#### Q19: What framework did you use to build the interactive dashboard?
**Answer:** We built a 6-page web application using **Streamlit**, integrated with **Plotly** for responsive analytics charts and **Folium** for interactive GIS map visualization.

#### Q20: How does your application provide Explainable AI (XAI)?
**Answer:** For every bin prediction, the system displays SHAP feature importances and generates a natural language diagnostic summary explaining *why* the bin received its priority assignment (e.g., "Assigned CRITICAL priority due to 88.5% peak fill and rapid +23.5% 3-hour accumulation rate").

#### Q21: How would this software connect to real IoT hardware in the future?
**Answer:** Physical IoT sensors (e.g., ESP32 with ultrasonic sensors) would transmit readings via LoRaWAN/Cellular to an MQTT Broker or REST API endpoint. The backend database would update sensor tables, which our ML prediction, priority scoring, and routing pipeline would consume seamlessly without code modifications.
