"""
Personal Data Dashboard Agent V2 (Enhanced CSV/Excel Analysis)
==============================================================

An enhanced version that:
- Creates more engaging, realistic sample data (fitness tracker with workouts, mood, sleep)
- Generates visualizations AND displays them automatically
- Provides richer insights with trend analysis

Demonstrates:
- Python-based data analysis tools
- Matplotlib/seaborn for visualizations
- Structured summaries with Pydantic
- Interactive follow-up capabilities
- Automatic image display

Requirements:
    pip install pandas matplotlib seaborn openpyxl
"""

import os
import json
import subprocess
import sys
from datetime import datetime, timedelta
from typing import List, Optional
from pydantic import BaseModel, Field

import nest_asyncio
nest_asyncio.apply()

from agents import Agent, Runner, function_tool


# ============================================
# Structured Output Models
# ============================================

class ColumnStats(BaseModel):
    """Statistics for a single column."""
    column_name: str = Field(description="Name of the column")
    data_type: str = Field(description="Data type (numeric, text, date)")
    non_null_count: int = Field(description="Number of non-null values")
    unique_values: int = Field(description="Number of unique values")
    sample_values: List[str] = Field(description="Sample of values from this column")


class Anomaly(BaseModel):
    """Detected anomaly in the data."""
    description: str = Field(description="What the anomaly is")
    location: str = Field(description="Where in the data (row/column)")
    severity: str = Field(description="low, medium, or high")
    recommendation: str = Field(description="Suggested action")


class DataAnalysisReport(BaseModel):
    """Complete analysis report for a dataset."""
    file_name: str = Field(description="Name of the analyzed file")
    row_count: int = Field(description="Number of rows in the data")
    column_count: int = Field(description="Number of columns")
    columns: List[ColumnStats] = Field(description="Statistics for each column")
    anomalies: List[Anomaly] = Field(description="Detected anomalies or issues")
    key_insights: List[str] = Field(description="Key findings from the analysis")
    visualization_path: Optional[str] = Field(
        default=None, description="Path to generated visualization"
    )
    summary: str = Field(description="Executive summary of the analysis")


# ============================================
# Tools
# ============================================

@function_tool
def load_and_analyze_data(file_path: str) -> str:
    """
    Load a CSV or Excel file and perform basic analysis.

    Args:
        file_path: Path to the CSV or XLSX file

    Returns:
        JSON with data overview and statistics
    """
    try:
        import pandas as pd
    except ImportError:
        return json.dumps({"error": "pandas not installed. Run: pip install pandas openpyxl"})

    try:
        file_path = os.path.expanduser(file_path)

        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file_path.endswith(('.xlsx', '.xls')):
            df = pd.read_excel(file_path)
        else:
            return json.dumps({"error": "Unsupported file format. Use CSV or XLSX."})

        # Basic info
        info = {
            "file_name": os.path.basename(file_path),
            "row_count": len(df),
            "column_count": len(df.columns),
            "columns": [],
            "memory_usage_mb": round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
        }

        # Column statistics
        for col in df.columns:
            col_data = df[col]

            # Determine data type
            if pd.api.types.is_numeric_dtype(col_data):
                dtype = "numeric"
            elif pd.api.types.is_datetime64_any_dtype(col_data):
                dtype = "date"
            else:
                dtype = "text"

            # Get sample values
            sample = col_data.dropna().head(5).astype(str).tolist()

            col_stats = {
                "column_name": col,
                "data_type": dtype,
                "non_null_count": int(col_data.notna().sum()),
                "null_count": int(col_data.isna().sum()),
                "unique_values": int(col_data.nunique()),
                "sample_values": sample
            }

            # Add numeric stats if applicable
            if dtype == "numeric":
                col_stats.update({
                    "min": float(col_data.min()) if not pd.isna(col_data.min()) else None,
                    "max": float(col_data.max()) if not pd.isna(col_data.max()) else None,
                    "mean": round(float(col_data.mean()), 2) if not pd.isna(col_data.mean()) else None,
                    "median": float(col_data.median()) if not pd.isna(col_data.median()) else None,
                    "std": round(float(col_data.std()), 2) if not pd.isna(col_data.std()) else None
                })

            info["columns"].append(col_stats)

        return json.dumps(info, indent=2, default=str)

    except Exception as e:
        return json.dumps({"error": f"Error loading file: {str(e)}"})


@function_tool
def detect_anomalies(file_path: str, numeric_columns: Optional[str] = None) -> str:
    """
    Detect anomalies and data quality issues in a dataset.

    Args:
        file_path: Path to the data file
        numeric_columns: Comma-separated list of numeric columns to check (optional)

    Returns:
        JSON with detected anomalies and issues
    """
    try:
        import pandas as pd
        import numpy as np
    except ImportError:
        return json.dumps({"error": "pandas not installed"})

    try:
        file_path = os.path.expanduser(file_path)

        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        anomalies = []

        # Check for missing values
        missing = df.isnull().sum()
        for col, count in missing.items():
            if count > 0:
                pct = round(count / len(df) * 100, 1)
                severity = "high" if pct > 20 else "medium" if pct > 5 else "low"
                anomalies.append({
                    "type": "missing_values",
                    "description": f"Column '{col}' has {count} missing values ({pct}%)",
                    "location": f"Column: {col}",
                    "severity": severity,
                    "recommendation": f"Consider imputation or removal of rows with missing '{col}'"
                })

        # Check for duplicates
        dup_count = df.duplicated().sum()
        if dup_count > 0:
            anomalies.append({
                "type": "duplicates",
                "description": f"Found {dup_count} duplicate rows",
                "location": "Multiple rows",
                "severity": "medium",
                "recommendation": "Review and remove duplicate entries if appropriate"
            })

        # Check numeric columns for outliers using IQR method
        cols_to_check = []
        if numeric_columns:
            cols_to_check = [c.strip() for c in numeric_columns.split(",")]
        else:
            cols_to_check = df.select_dtypes(include=[np.number]).columns.tolist()

        for col in cols_to_check:
            if col not in df.columns:
                continue

            data = df[col].dropna()
            if len(data) < 10:
                continue

            Q1 = data.quantile(0.25)
            Q3 = data.quantile(0.75)
            IQR = Q3 - Q1

            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = df[(df[col] < lower_bound) | (df[col] > upper_bound)]

            if len(outliers) > 0:
                anomalies.append({
                    "type": "outliers",
                    "description": f"Column '{col}' has {len(outliers)} potential outliers",
                    "location": f"Column: {col}",
                    "severity": "low" if len(outliers) < 5 else "medium",
                    "recommendation": f"Review outliers in '{col}' - values outside [{round(lower_bound, 2)}, {round(upper_bound, 2)}]",
                    "outlier_indices": outliers.index.tolist()[:10]
                })

        return json.dumps({
            "file": os.path.basename(file_path),
            "total_anomalies": len(anomalies),
            "anomalies": anomalies
        }, indent=2)

    except Exception as e:
        return json.dumps({"error": f"Error detecting anomalies: {str(e)}"})


@function_tool
def create_visualization(
    file_path: str,
    chart_type: str,
    x_column: str,
    y_column: Optional[str] = None,
    title: Optional[str] = None,
    output_path: Optional[str] = None
) -> str:
    """
    Create a visualization from the data.

    Args:
        file_path: Path to the data file
        chart_type: Type of chart: 'line', 'bar', 'scatter', 'histogram', 'box'
        x_column: Column to use for x-axis (or single column for histogram)
        y_column: Column to use for y-axis (not needed for histogram)
        title: Chart title (optional)
        output_path: Where to save the chart (optional, defaults to ./chart_output.png)

    Returns:
        Path to the saved visualization or error
    """
    try:
        import pandas as pd
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')  # Non-interactive backend for saving
    except ImportError:
        return json.dumps({"error": "matplotlib not installed. Run: pip install matplotlib"})

    try:
        file_path = os.path.expanduser(file_path)

        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        # Set up the figure with a nice style
        plt.style.use('seaborn-v0_8-whitegrid')
        fig, ax = plt.subplots(figsize=(12, 7))

        # Color palette
        colors = ['#3498db', '#e74c3c', '#2ecc71', '#9b59b6', '#f39c12']

        # Create the appropriate chart
        if chart_type == "line":
            if y_column:
                ax.plot(df[x_column], df[y_column], marker='o', linewidth=2,
                       markersize=4, color=colors[0])
                ax.set_ylabel(y_column, fontsize=12)
            else:
                ax.plot(df[x_column], marker='o', linewidth=2, color=colors[0])

        elif chart_type == "bar":
            if y_column:
                bars = ax.bar(df[x_column].astype(str), df[y_column], color=colors)
                ax.set_ylabel(y_column, fontsize=12)
            else:
                value_counts = df[x_column].value_counts()
                bars = ax.bar(value_counts.index.astype(str), value_counts.values,
                             color=colors[:len(value_counts)])

        elif chart_type == "scatter":
            if y_column:
                ax.scatter(df[x_column], df[y_column], alpha=0.6, s=50, color=colors[0])
                ax.set_ylabel(y_column, fontsize=12)
            else:
                return json.dumps({"error": "Scatter plot requires y_column"})

        elif chart_type == "histogram":
            ax.hist(df[x_column].dropna(), bins=30, edgecolor='white',
                   alpha=0.8, color=colors[0])
            ax.set_ylabel("Frequency", fontsize=12)

        elif chart_type == "box":
            ax.boxplot(df[x_column].dropna(), patch_artist=True,
                      boxprops=dict(facecolor=colors[0], alpha=0.7))
            ax.set_ylabel(x_column, fontsize=12)

        else:
            return json.dumps({"error": f"Unknown chart type: {chart_type}"})

        # Enhanced styling
        ax.set_xlabel(x_column, fontsize=12)
        ax.set_title(title or f"{chart_type.capitalize()} Chart: {x_column}",
                    fontsize=14, fontweight='bold', pad=20)
        plt.xticks(rotation=45, ha='right')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        plt.tight_layout()

        # Save the figure
        if output_path:
            save_path = os.path.expanduser(output_path)
        else:
            save_path = "./chart_output_v2.png"

        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return json.dumps({
            "success": True,
            "chart_type": chart_type,
            "output_path": os.path.abspath(save_path),
            "message": f"Chart saved to {save_path}"
        })

    except Exception as e:
        return json.dumps({"error": f"Error creating visualization: {str(e)}"})


@function_tool
def create_multi_panel_dashboard(
    file_path: str,
    output_path: Optional[str] = None
) -> str:
    """
    Create a comprehensive multi-panel dashboard visualization.

    Args:
        file_path: Path to the data file
        output_path: Where to save the dashboard (optional)

    Returns:
        Path to the saved dashboard or error
    """
    try:
        import pandas as pd
        import matplotlib.pyplot as plt
        import matplotlib
        matplotlib.use('Agg')
        import numpy as np
    except ImportError:
        return json.dumps({"error": "matplotlib/pandas not installed"})

    try:
        file_path = os.path.expanduser(file_path)

        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        # Try to parse date column
        if 'date' in df.columns:
            df['date'] = pd.to_datetime(df['date'])

        # Set up the figure
        plt.style.use('seaborn-v0_8-whitegrid')
        fig = plt.figure(figsize=(16, 12))

        # Color scheme
        colors = {
            'primary': '#3498db',
            'secondary': '#e74c3c',
            'tertiary': '#2ecc71',
            'quaternary': '#9b59b6',
            'accent': '#f39c12'
        }

        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()

        # Panel 1: Main time series (top left)
        ax1 = fig.add_subplot(2, 2, 1)
        if 'date' in df.columns and len(numeric_cols) > 0:
            main_col = numeric_cols[0]
            ax1.plot(df['date'], df[main_col], linewidth=2, color=colors['primary'], alpha=0.8)
            ax1.fill_between(df['date'], df[main_col], alpha=0.3, color=colors['primary'])
            ax1.set_title(f'{main_col} Over Time', fontsize=12, fontweight='bold')
            ax1.set_xlabel('Date')
            ax1.set_ylabel(main_col)
            plt.setp(ax1.xaxis.get_majorticklabels(), rotation=45, ha='right')

        # Panel 2: Distribution (top right)
        ax2 = fig.add_subplot(2, 2, 2)
        if len(numeric_cols) > 0:
            col = numeric_cols[0]
            ax2.hist(df[col].dropna(), bins=25, color=colors['secondary'],
                    edgecolor='white', alpha=0.8)
            ax2.axvline(df[col].mean(), color='black', linestyle='--',
                       label=f'Mean: {df[col].mean():.1f}')
            ax2.set_title(f'Distribution of {col}', fontsize=12, fontweight='bold')
            ax2.legend()

        # Panel 3: Category breakdown (bottom left)
        ax3 = fig.add_subplot(2, 2, 3)
        categorical_cols = df.select_dtypes(include=['object']).columns.tolist()
        if categorical_cols:
            cat_col = categorical_cols[0]
            value_counts = df[cat_col].value_counts()
            bars = ax3.barh(value_counts.index, value_counts.values,
                           color=[colors['primary'], colors['secondary'],
                                  colors['tertiary'], colors['quaternary'],
                                  colors['accent']][:len(value_counts)])
            ax3.set_title(f'{cat_col} Breakdown', fontsize=12, fontweight='bold')
            ax3.set_xlabel('Count')

        # Panel 4: Correlation or secondary metric (bottom right)
        ax4 = fig.add_subplot(2, 2, 4)
        if len(numeric_cols) >= 2:
            ax4.scatter(df[numeric_cols[0]], df[numeric_cols[1]],
                       alpha=0.6, s=50, color=colors['tertiary'])
            ax4.set_xlabel(numeric_cols[0])
            ax4.set_ylabel(numeric_cols[1])
            ax4.set_title(f'{numeric_cols[0]} vs {numeric_cols[1]}',
                         fontsize=12, fontweight='bold')

            # Add trend line
            z = np.polyfit(df[numeric_cols[0]].dropna(), df[numeric_cols[1]].dropna(), 1)
            p = np.poly1d(z)
            ax4.plot(df[numeric_cols[0]], p(df[numeric_cols[0]]),
                    "r--", alpha=0.8, label='Trend')
            ax4.legend()

        # Overall title
        fig.suptitle('Data Dashboard Analysis', fontsize=16, fontweight='bold', y=1.02)

        plt.tight_layout()

        # Save
        if output_path:
            save_path = os.path.expanduser(output_path)
        else:
            save_path = "./dashboard_output_v2.png"

        plt.savefig(save_path, dpi=150, bbox_inches='tight', facecolor='white')
        plt.close()

        return json.dumps({
            "success": True,
            "output_path": os.path.abspath(save_path),
            "message": f"Dashboard saved to {save_path}"
        })

    except Exception as e:
        return json.dumps({"error": f"Error creating dashboard: {str(e)}"})


@function_tool
def generate_summary_stats(
    file_path: str,
    group_by: Optional[str] = None
) -> str:
    """
    Generate summary statistics, optionally grouped by a column.

    Args:
        file_path: Path to the data file
        group_by: Column to group by (optional)

    Returns:
        JSON with summary statistics
    """
    try:
        import pandas as pd
    except ImportError:
        return json.dumps({"error": "pandas not installed"})

    try:
        file_path = os.path.expanduser(file_path)

        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        numeric_cols = df.select_dtypes(include=['number']).columns.tolist()

        if group_by and group_by in df.columns:
            grouped = df.groupby(group_by)[numeric_cols].agg(['mean', 'sum', 'count', 'min', 'max'])
            grouped.columns = ['_'.join(col).strip() for col in grouped.columns.values]

            stats = {
                "grouped_by": group_by,
                "groups": grouped.to_dict('index')
            }
        else:
            stats = {
                "overall": {}
            }

            for col in numeric_cols:
                stats["overall"][col] = {
                    "mean": round(df[col].mean(), 2),
                    "sum": round(df[col].sum(), 2),
                    "min": round(df[col].min(), 2),
                    "max": round(df[col].max(), 2),
                    "median": round(df[col].median(), 2),
                    "std": round(df[col].std(), 2)
                }

        return json.dumps(stats, indent=2, default=str)

    except Exception as e:
        return json.dumps({"error": f"Error generating stats: {str(e)}"})


# ============================================
# Image Display Utility
# ============================================

def display_image(image_path: str):
    """
    Open and display an image using the system's default viewer.
    Works on macOS, Windows, and Linux.
    """
    image_path = os.path.abspath(os.path.expanduser(image_path))

    if not os.path.exists(image_path):
        print(f"   Image not found: {image_path}")
        return

    print(f"   Opening image: {image_path}")

    if sys.platform == "darwin":  # macOS
        subprocess.run(["open", image_path], check=True)
    elif sys.platform == "win32":  # Windows
        os.startfile(image_path)
    else:  # Linux and others
        subprocess.run(["xdg-open", image_path], check=True)


# ============================================
# Agent Definition
# ============================================

dashboard_agent = Agent(
    name="Data Dashboard Analyst V2",
    instructions="""You are an enhanced data analysis assistant that helps users understand
    their personal data from CSV and Excel files.

    Your analysis workflow:
    1. Load and examine the data structure
    2. Provide summary statistics for all numeric columns
    3. Detect anomalies (missing values, outliers, duplicates)
    4. Create a comprehensive multi-panel dashboard visualization
    5. Provide actionable insights with specific recommendations

    When analyzing data:
    - Start by understanding what kind of data it is (fitness, habits, finance, etc.)
    - Focus on trends, patterns, and correlations
    - Highlight anything unusual, noteworthy, or actionable
    - Always create the multi-panel dashboard for comprehensive view
    - Be specific about what you find - include actual numbers and percentages

    For fitness/health data: Look for progress trends, recovery patterns, correlations
    between metrics (e.g., sleep vs performance), and consistency

    For habit data: Look for streaks, patterns, correlations between habits

    For financial data: Look for spending spikes, unusual transactions, trends

    Always explain your findings in plain language that non-technical users
    can understand. Provide specific, actionable recommendations.
    """,
    model="gpt-4o-mini",
    tools=[
        load_and_analyze_data,
        detect_anomalies,
        create_visualization,
        create_multi_panel_dashboard,
        generate_summary_stats
    ],
    output_type=DataAnalysisReport
)


# ============================================
# Main Function
# ============================================

def run_data_dashboard_agent(
    file_path: str,
    analysis_focus: Optional[str] = None,
    create_charts: bool = True,
    display_charts: bool = True
) -> DataAnalysisReport:
    """
    Run the data dashboard agent on a data file.

    Args:
        file_path: Path to CSV or Excel file
        analysis_focus: Optional focus area (e.g., "fitness", "progress", "habits")
        create_charts: Whether to generate visualizations
        display_charts: Whether to automatically display the charts

    Returns:
        DataAnalysisReport with analysis results

    Example:
        >>> result = run_data_dashboard_agent("fitness_log.csv", analysis_focus="fitness")
        >>> print(result.summary)
        >>> for insight in result.key_insights:
        ...     print(f"- {insight}")
    """
    query = f"Please analyze the data file at '{file_path}'."

    if analysis_focus:
        query += f" Focus on {analysis_focus} patterns and insights."

    if create_charts:
        query += " Create a comprehensive multi-panel dashboard visualization to highlight key findings."
    else:
        query += " Skip visualizations, just provide the analysis."

    query += """
    Include:
    1. Overview of the data structure
    2. Key statistics
    3. Any anomalies or data quality issues
    4. Important insights, trends, and correlations
    5. Specific, actionable recommendations
    """

    result = Runner.run_sync(dashboard_agent, query)

    # Display charts if requested
    if display_charts and result.final_output.visualization_path:
        display_image(result.final_output.visualization_path)

    # Also try to display the dashboard if it was created
    if display_charts:
        dashboard_path = "./dashboard_output_v2.png"
        if os.path.exists(dashboard_path):
            display_image(dashboard_path)

    return result.final_output


# ============================================
# Enhanced Sample Data Generator
# ============================================

def create_sample_data():
    """Create engaging fitness tracker sample CSV with realistic patterns."""
    try:
        import pandas as pd
        import numpy as np
    except ImportError:
        print("pandas and numpy required. Install with: pip install pandas numpy")
        return None

    np.random.seed(42)

    # 90 days of fitness data
    dates = pd.date_range(start='2024-01-01', periods=90, freq='D')

    # Workout types with realistic distribution
    workout_types = ['Running', 'Weight Training', 'Yoga', 'HIIT', 'Swimming', 'Rest']
    workout_weights = [0.25, 0.3, 0.15, 0.1, 0.05, 0.15]

    # Generate base data with realistic patterns
    data = {
        'date': dates,
        'workout_type': np.random.choice(workout_types, size=90, p=workout_weights),
        'duration_mins': [],
        'calories_burned': [],
        'avg_heart_rate': [],
        'sleep_hours': [],
        'mood_score': [],  # 1-10 scale
        'energy_level': [],  # 1-10 scale
        'steps': [],
        'water_intake_oz': []
    }

    for i in range(90):
        workout = data['workout_type'][i]
        day_of_week = dates[i].dayofweek

        # Duration based on workout type
        if workout == 'Rest':
            duration = 0
        elif workout == 'Running':
            duration = np.random.normal(35, 10)
        elif workout == 'Weight Training':
            duration = np.random.normal(50, 15)
        elif workout == 'Yoga':
            duration = np.random.normal(45, 10)
        elif workout == 'HIIT':
            duration = np.random.normal(25, 5)
        else:  # Swimming
            duration = np.random.normal(40, 10)

        data['duration_mins'].append(max(0, round(duration)))

        # Calories based on duration and type
        cal_per_min = {'Running': 12, 'Weight Training': 8, 'Yoga': 4,
                       'HIIT': 15, 'Swimming': 10, 'Rest': 1}
        calories = data['duration_mins'][i] * cal_per_min.get(workout, 5)
        calories += np.random.normal(0, 30)
        data['calories_burned'].append(max(0, round(calories)))

        # Heart rate based on workout intensity
        hr_base = {'Running': 145, 'Weight Training': 120, 'Yoga': 90,
                   'HIIT': 160, 'Swimming': 135, 'Rest': 70}
        hr = hr_base.get(workout, 100) + np.random.normal(0, 10)
        data['avg_heart_rate'].append(max(60, round(hr)))

        # Sleep - weekends tend to be longer, gradual improvement trend
        base_sleep = 6.5 + (i / 90) * 0.5  # Improvement over time
        if day_of_week >= 5:  # Weekend
            base_sleep += 1
        sleep = base_sleep + np.random.normal(0, 0.8)
        data['sleep_hours'].append(round(max(4, min(10, sleep)), 1))

        # Mood correlates with sleep and workout
        mood_base = 5 + (data['sleep_hours'][i] - 6) * 0.8
        if workout != 'Rest':
            mood_base += 1
        mood = mood_base + np.random.normal(0, 1)
        data['mood_score'].append(round(max(1, min(10, mood))))

        # Energy correlates with sleep
        energy_base = 4 + (data['sleep_hours'][i] - 6) * 1.2
        energy = energy_base + np.random.normal(0, 1.2)
        data['energy_level'].append(round(max(1, min(10, energy))))

        # Steps - higher on workout days, lower on weekends
        if workout == 'Rest':
            steps = np.random.normal(4000, 1500)
        elif workout == 'Running':
            steps = np.random.normal(12000, 2000)
        else:
            steps = np.random.normal(8000, 2000)
        data['steps'].append(max(1000, round(steps)))

        # Water intake - correlates with activity
        water_base = 48 + (data['duration_mins'][i] / 60) * 24
        water = water_base + np.random.normal(0, 12)
        data['water_intake_oz'].append(max(20, round(water)))

    df = pd.DataFrame(data)

    # Add some interesting anomalies
    df.loc[15, 'calories_burned'] = 1200  # Exceptional workout day
    df.loc[45, 'sleep_hours'] = None  # Missing sleep data
    df.loc[60, 'steps'] = 25000  # Hiking day
    df.loc[72, 'mood_score'] = 2  # Bad day
    df.loc[73, 'mood_score'] = 9  # Recovery bounce

    # Add a "sick days" pattern
    df.loc[30:32, 'workout_type'] = 'Rest'
    df.loc[30:32, 'energy_level'] = [3, 2, 4]
    df.loc[30:32, 'mood_score'] = [4, 3, 5]

    sample_path = "./sample_fitness_tracker.csv"
    df.to_csv(sample_path, index=False)

    return sample_path


# ============================================
# Demo
# ============================================

if __name__ == "__main__":
    print("=" * 60)
    print("Personal Data Dashboard Agent V2 - Enhanced")
    print("=" * 60)

    # Create sample data
    print("\n📊 Creating sample fitness tracker data...")
    sample_file = create_sample_data()

    if sample_file:
        print(f"   Sample file created: {sample_file}")
        print("   Contains: 90 days of fitness data with workouts, sleep, mood, etc.")

        print("\n🔍 Analyzing data...")
        print("-" * 40)

        result = run_data_dashboard_agent(
            sample_file,
            analysis_focus="fitness progress and health patterns",
            create_charts=True,
            display_charts=True  # This will auto-open the charts!
        )

        # Display results
        print(f"\n📋 Analysis Report")
        print(f"   File: {result.file_name}")
        print(f"   Rows: {result.row_count}")
        print(f"   Columns: {result.column_count}")

        print(f"\n📝 Summary:\n{result.summary}")

        print(f"\n🔑 Key Insights:")
        for i, insight in enumerate(result.key_insights, 1):
            print(f"   {i}. {insight}")

        if result.anomalies:
            print(f"\n⚠️ Anomalies Detected:")
            for anomaly in result.anomalies:
                print(f"   [{anomaly.severity.upper()}] {anomaly.description}")

        if result.visualization_path:
            print(f"\n📈 Visualization: {result.visualization_path}")

        # Cleanup option
        print("\n" + "-" * 40)
        cleanup = input("Delete sample file? (y/n): ").strip().lower()
        if cleanup == 'y':
            if os.path.exists(sample_file):
                os.remove(sample_file)
                print("   Cleaned up sample file")

    print("\n" + "=" * 60)
    print("Dashboard analysis complete!")
