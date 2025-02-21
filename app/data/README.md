# Samsung Health GraphRAG - Dataset Documentation

## Overview
This repository contains a dataset extracted from **Samsung Health**, structured to support **Graph-based Retrieval-Augmented Generation (GraphRAG)**. The data includes various health-related records, such as activity tracking, nutrition, sleep patterns, and device profiles. 

The dataset is stored in the following directory:
```
.\samsunghealth-graphrag\app\data\samsunghealth_yaffazka_20250221140521.zip
```
It consists of multiple `.csv` files and two subdirectories (`files` and `jsons`).

## Directory Structure
```
.\samsunghealth-graphrag\app\data\samsunghealth_yaffazka_20250221140521
│-- files/  (Contains additional data files)
│-- jsons/  (Contains JSON formatted data)
│-- com.samsung.health.device_profile.20250221140521.csv
│-- com.samsung.health.food_intake.20250221140521.csv
│-- com.samsung.health.height.20250221140521.csv
│-- com.samsung.health.nutrition.20250221140521.csv
│-- com.samsung.health.user_profile.20250221140521.csv
│-- com.samsung.health.water_intake.20250221140521.csv
│-- com.samsung.health.weight.20250221140521.csv
│-- com.samsung.shealth.activity.day_summary.20250221140521.csv
│-- com.samsung.shealth.activity_level.20250221140521.csv
│-- com.samsung.shealth.badge.20250221140521.csv
│-- com.samsung.shealth.calories_burned.details.20250221140521.csv
│-- com.samsung.shealth.food_favorite.20250221140521.csv
│-- com.samsung.shealth.food_frequent.20250221140521.csv
│-- com.samsung.shealth.mood.20250221140521.csv
│-- com.samsung.shealth.preferences.20250221140521.csv
│-- com.samsung.shealth.service_preferences.20250221140521.csv
│-- com.samsung.shealth.sleep.20250221140521.csv
│-- com.samsung.shealth.social.service_status.20250221140521.csv
│-- com.samsung.shealth.step_daily_trend.20250221140521.csv
│-- com.samsung.shealth.tracker.floors_day_summary.20250221140521.csv
│-- com.samsung.shealth.tracker.pedometer_day_summary.20250221140521.csv
│-- com.samsung.shealth.tracker.pedometer_step_count.20250221140521.csv
```

## Dataset Description
Below is a summary of key `.csv` files included in the dataset:

### **Health-Related Data**
- **`com.samsung.health.device_profile.csv`** - Contains device-related health profile data.
- **`com.samsung.health.food_intake.csv`** - Logs food intake records including meal types and calories consumed.
- **`com.samsung.health.nutrition.csv`** - Captures detailed nutritional data.
- **`com.samsung.health.water_intake.csv`** - Tracks water intake logs.
- **`com.samsung.health.weight.csv`** - Logs weight tracking over time.
- **`com.samsung.health.height.csv`** - Stores recorded height data.
- **`com.samsung.health.user_profile.csv`** - Stores user profile metadata.

### **Activity & Exercise Data**
- **`com.samsung.shealth.activity.day_summary.csv`** - Daily activity summary, including step count and exercise duration.
- **`com.samsung.shealth.activity_level.csv`** - Tracks intensity levels of physical activity.
- **`com.samsung.shealth.calories_burned.details.csv`** - Detailed calorie burn information.
- **`com.samsung.shealth.tracker.pedometer_day_summary.csv`** - Daily pedometer data summary.
- **`com.samsung.shealth.tracker.pedometer_step_count.csv`** - Step count details over time.
- **`com.samsung.shealth.tracker.floors_day_summary.csv`** - Tracks floors climbed per day.

### **Sleep & Well-being Data**
- **`com.samsung.shealth.sleep.csv`** - Logs sleep patterns and durations.
- **`com.samsung.shealth.mood.csv`** - Captures mood and emotional well-being data.
- **`com.samsung.shealth.social.service_status.csv`** - Logs interactions with Samsung’s health-related social services.

### **Food Preferences & Habits**
- **`com.samsung.shealth.food_favorite.csv`** - Stores frequently eaten foods marked as favorites.
- **`com.samsung.shealth.food_frequent.csv`** - Tracks foods commonly consumed.

### **User Preferences & Settings**
- **`com.samsung.shealth.preferences.csv`** - General Samsung Health user preferences.
- **`com.samsung.shealth.service_preferences.csv`** - Stores settings related to health services.
- **`com.samsung.shealth.badge.csv`** - Data related to earned health-related badges.

## Usage Instructions
1. **Load the dataset in using this function:**
   ```python
   def clean_samsung_health_data(file_path):
    """
    Cleans the Samsung Health food intake CSV file by:
    1. Removing the first row (metadata)
    2. Extracting column names from the second row
    3. Removing the second row (so only data remains)
    4. Creating an empty DataFrame with extracted column names
    5. Integrating the remaining data into the new DataFrame while ensuring column consistency
    """
    
    # Read the file using csv.reader to ensure proper parsing
    with open(file_path, 'r', encoding='utf-8') as file:
        reader = list(csv.reader(file))
    
    # Remove the first row (metadata)
    reader = reader[1:]
    
    # Extract column names from the new first row
    column_names = reader[0]
    
    # Remove the column header row from the data
    data_lines = reader[1:]
    
    # Ensure all rows have the correct number of columns
    cleaned_data = []
    for row in data_lines:
        if len(row) > len(column_names):
            cleaned_data.append(row[:len(column_names)])  # Trim excess columns
        else:
            cleaned_data.append(row + [None] * (len(column_names) - len(row)))  # Fill missing columns with None
    
    # Create DataFrame
    df = pd.DataFrame(cleaned_data, columns=column_names)
    
    return df
   ```
2. **Integrate with Neo4j Graph Database:**
   - The dataset is structured to be used within a Neo4j graph database for knowledge retrieval.
   - Run `HealthGraphBuilder.extract_samsung_health_data()` to parse the data and populate the graph.


### **Contact & Support**
If you have any questions, reach out via GitHub issues or email me at **yaffazka@gmail.com**.