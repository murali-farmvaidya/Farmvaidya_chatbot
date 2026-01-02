"""
Local knowledge base for coconut cultivation
This is used when LightRAG doesn't have indexed documents or returns [no-context]
"""

# Fertilizer recommendations based on soil type and growth stage
FERTILIZER_RECOMMENDATIONS = {
    "red_soil": {
        "early": {
            "description": "Early stage coconut in red soil",
            "nutrients": "Nitrogen, Phosphorus, Potassium, Zinc, Boron",
            "doses": {
                "urea": "1.0 kg/tree/year",
                "ssp": "2.0 kg/tree/year",
                "mop": "2.0 kg/tree/year",
                "fym": "25 kg/tree/year",
                "zinc_sulphate": "50 g/tree (once in 2 years)",
                "borax": "25 g/tree (once in 2 years)"
            },
            "schedule": "Apply in split doses during June-September (SW monsoon)",
            "application": "Mix with irrigation water or apply near the base after first watering"
        },
        "mid": {
            "description": "Mid-stage coconut in red soil (prime production stage)",
            "nutrients": "High Nitrogen, Phosphorus, Potassium, Magnesium",
            "doses": {
                "urea": "1.2-1.5 kg/tree/year",
                "ssp": "2.0-2.5 kg/tree/year",
                "mop": "2.5-3.0 kg/tree/year",
                "fym": "25-30 kg/tree/year",
                "magnesium_sulphate": "500 g/tree/year",
                "zinc_sulphate": "50 g/tree (once in 2 years)",
                "borax": "25 g/tree (once in 2 years)"
            },
            "schedule": "Apply in 3-4 split doses from June-January",
            "application": "Apply in two halves: one in June-July, second in October-November via drip irrigation"
        },
        "near_harvest": {
            "description": "Mature/productive coconut in red soil",
            "nutrients": "Balanced NPK with micronutrients",
            "doses": {
                "urea": "1.0-1.2 kg/tree/year",
                "ssp": "2.0 kg/tree/year",
                "mop": "2.5 kg/tree/year",
                "fym": "25 kg/tree/year",
                "zinc_sulphate": "25-50 g/tree (once in 2 years)"
            },
            "schedule": "Apply in 2 split doses",
            "application": "June-July and October-November via drip system"
        }
    },
    "black_soil": {
        "early": {
            "description": "Early stage coconut in black soil",
            "nutrients": "Nitrogen, Potassium, Zinc (black soil is rich in P)",
            "doses": {
                "urea": "0.75 kg/tree/year",
                "ssp": "1.5 kg/tree/year",
                "mop": "2.5 kg/tree/year",
                "fym": "20 kg/tree/year",
                "zinc_sulphate": "75-100 g/tree (once in 2 years)"
            },
            "schedule": "Apply during monsoon (June-September)",
            "application": "Apply in split doses with irrigation"
        },
        "mid": {
            "description": "Mid-stage coconut in black soil",
            "nutrients": "High Nitrogen, Potassium, Micronutrients",
            "doses": {
                "urea": "1.25 kg/tree/year",
                "ssp": "1.5 kg/tree/year",
                "mop": "3.0 kg/tree/year",
                "fym": "25 kg/tree/year",
                "zinc_sulphate": "75-100 g/tree (once in 2 years)",
                "borax": "50 g/tree (once in 2 years)"
            },
            "schedule": "3 split applications",
            "application": "June-July, September-October, December-January via drip"
        },
        "near_harvest": {
            "description": "Mature coconut in black soil",
            "nutrients": "Balanced with emphasis on Potassium",
            "doses": {
                "urea": "1.0 kg/tree/year",
                "ssp": "1.5 kg/tree/year",
                "mop": "2.5-3.0 kg/tree/year",
                "fym": "20 kg/tree/year"
            },
            "schedule": "2 split doses",
            "application": "June-July and October-November"
        }
    },
    "loam_soil": {
        "early": {
            "description": "Early stage coconut in loam soil",
            "nutrients": "Balanced NPK with micronutrients",
            "doses": {
                "urea": "0.9 kg/tree/year",
                "ssp": "1.75 kg/tree/year",
                "mop": "2.25 kg/tree/year",
                "fym": "22 kg/tree/year",
                "zinc_sulphate": "50 g/tree (once in 2 years)"
            },
            "schedule": "Apply during SW monsoon",
            "application": "Split in 2-3 applications from June-September"
        },
        "mid": {
            "description": "Mid-stage coconut in loam soil (optimal fertility)",
            "nutrients": "High N and K, adequate P and micronutrients",
            "doses": {
                "urea": "1.3 kg/tree/year",
                "ssp": "2.0 kg/tree/year",
                "mop": "2.75 kg/tree/year",
                "fym": "25 kg/tree/year",
                "magnesium_sulphate": "400 g/tree/year",
                "zinc_sulphate": "50 g/tree (once in 2 years)",
                "borax": "25 g/tree (once in 2 years)"
            },
            "schedule": "3 split applications",
            "application": "June-July, September-October, December-January"
        },
        "near_harvest": {
            "description": "Mature coconut in loam soil",
            "nutrients": "Balanced with higher Potassium",
            "doses": {
                "urea": "1.0-1.1 kg/tree/year",
                "ssp": "1.75 kg/tree/year",
                "mop": "2.5 kg/tree/year",
                "fym": "22 kg/tree/year"
            },
            "schedule": "2 split doses",
            "application": "June-July and October-November"
        }
    }
}

# Irrigation recommendations
IRRIGATION_RECOMMENDATIONS = {
    "drip": {
        "schedule": "Daily or alternate day irrigation during dry season",
        "water_requirement": "40-50 liters per tree per day in summer (April-May)",
        "frequency": "2-3 days interval during monsoon",
        "method": "Apply near the base (drip lines 1m from trunk)",
        "efficiency": "90% water use efficiency, saves 40-50% water"
    },
    "sprinkler": {
        "schedule": "3-4 days interval in dry season",
        "water_requirement": "50-60 liters per tree per day in summer",
        "frequency": "5-7 days interval during monsoon",
        "method": "Apply in 2-3 hours before sunrise",
        "efficiency": "70-80% water use efficiency"
    },
    "flood": {
        "schedule": "7-10 days interval in dry season",
        "water_requirement": "60-80 liters per tree in one application",
        "frequency": "15-20 days during monsoon",
        "method": "Basin method, 1m radius around tree",
        "efficiency": "50-60% water use efficiency, less recommended"
    }
}

# Coconut varieties and their characteristics
COCONUT_VARIETIES = {
    "local_tall": {
        "yield": "60-80 nuts/tree/year",
        "earliness": "Very late (7-9 years to first production)",
        "height": "20-25m",
        "characteristics": "Tall, long-lived (60-80 years), mixed pollination, variable",
        "advantages": "Durable, long productive life",
        "disadvantages": "Late, tall, difficult harvesting"
    },
    "west_coast_tall": {
        "yield": "80-100 nuts/tree/year",
        "earliness": "Late (7-8 years)",
        "height": "20-25m",
        "characteristics": "Tall, adapted to wet climate",
        "advantages": "Better yield than local tall, disease resistant",
        "disadvantages": "Still tall, late production"
    },
    "dwarf_varieties": {
        "yield": "100-150 nuts/tree/year",
        "earliness": "Very early (3-4 years to production)",
        "height": "4-5m",
        "characteristics": "Compact, early bearing, consistent yield",
        "advantages": "Easy harvesting, early production, 2-3x yield of talls",
        "disadvantages": "Shorter productive life (40-50 years)"
    },
    "hybrid_dwarf": {
        "yield": "150-200 nuts/tree/year",
        "earliness": "Early (4-5 years)",
        "height": "5-6m",
        "characteristics": "Hybrid vigor, high productivity",
        "advantages": "Highest yield, good nut quality, easier management",
        "disadvantages": "Requires quality inputs, hybrid seeds needed"
    }
}

def get_fertilizer_recommendation(soil_type, growth_stage, existing_fertilizers=""):
    """
    Get fertilizer recommendation based on soil and growth stage
    
    Args:
        soil_type: 'red', 'black', or 'loam'
        growth_stage: 'early', 'mid', or 'near_harvest'
        existing_fertilizers: comma-separated list of already applied fertilizers
    
    Returns:
        Dictionary with fertilizer recommendation
    """
    soil_type_key = f"{soil_type}_soil".lower()
    
    if soil_type_key not in FERTILIZER_RECOMMENDATIONS:
        return {"error": f"Soil type '{soil_type}' not recognized. Use: red, black, or loam"}
    
    if growth_stage.lower() not in FERTILIZER_RECOMMENDATIONS[soil_type_key]:
        return {"error": f"Growth stage '{growth_stage}' not recognized. Use: early, mid, or near_harvest"}
    
    recommendation = FERTILIZER_RECOMMENDATIONS[soil_type_key][growth_stage.lower()].copy()
    
    # Add note if no previous fertilizers used
    if existing_fertilizers.lower() in ["none", "none used", "not yet", "no"]:
        recommendation["note"] = "This is your first application. Follow the schedule strictly for 2-3 years to build soil fertility."
    
    return recommendation

def get_irrigation_recommendation(irrigation_method):
    """Get irrigation management recommendations"""
    method_key = irrigation_method.lower().strip()
    
    if method_key in IRRIGATION_RECOMMENDATIONS:
        return IRRIGATION_RECOMMENDATIONS[method_key]
    else:
        return {"error": f"Irrigation method '{irrigation_method}' not found. Use: drip, sprinkler, or flood"}

def get_variety_recommendation():
    """Get coconut variety recommendations"""
    return {
        "recommendation": "For better yields and easier management, choose dwarf or hybrid varieties",
        "varieties": COCONUT_VARIETIES,
        "note": "If you currently have tall varieties, you can interplant with dwarf varieties for quick returns"
    }

def synthesize_answer(soil_type, growth_stage, irrigation_method, existing_fertilizers=""):
    """
    Synthesize a comprehensive answer combining soil, growth stage, irrigation, and fertilizer info
    """
    fert_rec = get_fertilizer_recommendation(soil_type, growth_stage, existing_fertilizers)
    irrig_rec = get_irrigation_recommendation(irrigation_method)
    
    if "error" in fert_rec or "error" in irrig_rec:
        return {"error": "Could not generate recommendation"}
    
    answer = f"""
📋 COCONUT YIELD IMPROVEMENT PLAN

🌾 Current Status:
- Growth Stage: {growth_stage}
- Soil Type: {soil_type}
- Irrigation: {irrigation_method}
- Previous Fertilizers: {existing_fertilizers if existing_fertilizers and existing_fertilizers.lower() != 'none' else 'None yet'}

🌱 FERTILIZER RECOMMENDATIONS (Per Tree Per Year):
"""
    
    for product, dose in fert_rec["doses"].items():
        answer += f"\n• {product.replace('_', ' ').title()}: {dose}"
    
    answer += f"\n\n📅 Application Schedule: {fert_rec['schedule']}"
    answer += f"\n💧 Application Method: {fert_rec['application']}"
    
    answer += f"\n\n💦 IRRIGATION MANAGEMENT:\n"
    answer += f"• Schedule: {irrig_rec['schedule']}\n"
    answer += f"• Water Requirement: {irrig_rec['water_requirement']}\n"
    answer += f"• Method: {irrig_rec['method']}\n"
    answer += f"• Efficiency: {irrig_rec['efficiency']}"
    
    answer += f"\n\n✅ FOLLOW THESE PRACTICES:\n"
    answer += f"1. Apply fertilizers in split doses as per schedule\n"
    answer += f"2. Maintain consistent irrigation, especially during March-May\n"
    answer += f"3. Remove dead leaves and maintain clean basin\n"
    answer += f"4. Scout for pests (rhinoceros beetle, mites) monthly\n"
    answer += f"5. Monitor for disease symptoms (leaf rot, bud rot)\n"
    answer += f"6. Ensure proper drainage to prevent waterlogging"
    
    return answer
