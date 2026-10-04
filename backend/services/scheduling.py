"""
Scheduling and Intelligent Priority Logic Service.
Implements rule-based dispatch and priority classification based on current and ML-predicted fill levels.
"""

def evaluate_intelligent_priority(current_fill: float, predicted_fill: float) -> dict:
    """
    Evaluates bin priority based on project rules:
    HIGH: current fill >= 90 OR predicted fill >= 90 (Score: 3)
    MEDIUM: current fill >= 70 OR predicted fill >= 70 (Score: 2)
    LOW: otherwise (Score: 1)
    """
    cur = float(current_fill)
    pred = float(predicted_fill)
    
    if cur >= 90.0 or pred >= 90.0:
        priority_level = "HIGH"
        priority_score = 3
    elif cur >= 70.0 or pred >= 70.0:
        priority_level = "MEDIUM"
        priority_score = 2
    else:
        priority_level = "LOW"
        priority_score = 1
        
    return {
        "priority_level": priority_level,
        "priority_score": priority_score
    }

def evaluate_dispatch_decision(current_fill: float, predicted_fill: float) -> str:
    """
    Evaluates collection dispatch decision based on project rules:
    HIGH: current fill >= 90 OR predicted fill >= 90 -> 'Dispatch Immediately'
    MEDIUM: current fill >= 80 OR predicted fill >= 80 -> 'Schedule Collection'
    Otherwise -> 'No Dispatch'
    """
    cur = float(current_fill)
    pred = float(predicted_fill)
    
    if cur >= 90.0 or pred >= 90.0:
        return "Dispatch Immediately"
    elif cur >= 80.0 or pred >= 80.0:
        return "Schedule Collection"
    else:
        return "No Dispatch"

def evaluate_overflow_risk(current_fill: float, predicted_fill: float) -> bool:
    """
    Evaluates overflow risk condition.
    """
    cur = float(current_fill)
    pred = float(predicted_fill)
    return (cur >= 85.0 or pred >= 90.0)

def process_bin_decision(bin_record: dict) -> dict:
    """
    Enriches a bin record with intelligent priority, dispatch decision, and overflow risk.
    """
    cur_fill = float(bin_record.get("Fill_Level_Percent", 0.0))
    pred_fill = float(bin_record.get("Next_Fill_Level_Percent", cur_fill))
    
    prio_data = evaluate_intelligent_priority(cur_fill, pred_fill)
    dispatch = evaluate_dispatch_decision(cur_fill, pred_fill)
    overflow = evaluate_overflow_risk(cur_fill, pred_fill)
    collection_req = dispatch in ["Dispatch Immediately", "Schedule Collection"]
    
    capacity = float(bin_record.get("Bin_Capacity_L", 240))
    fill_fraction = round(cur_fill / 100.0, 4)
    est_volume = round(fill_fraction * capacity, 1)
    
    return {
        **bin_record,
        "Priority_Level": prio_data["priority_level"],
        "Priority_Score": prio_data["priority_score"],
        "Dispatch_Decision": dispatch,
        "Collection_Required": collection_req,
        "Overflow_Risk": overflow,
        "Fill_Level_Fraction": fill_fraction,
        "Estimated_Waste_Volume_L": est_volume,
        "Next_Fill_Level_Percent": round(pred_fill, 2)
    }
