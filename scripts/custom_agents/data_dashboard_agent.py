"""
Personal Data Dashboard Agent (CSV/Excel Analysis)
===================================================

An agent that:
- Receives CSV or XLSX files (finance logs, gym progress, habit tracking)
- Cleans and validates data
- Outputs: summary statistics, anomaly detection, visualizations
- Can ask follow-up questions about analysis preferences

Demonstrates:
- Python-based data analysis tools
- Matplotlib/seaborn for visualizations
- Structured summaries with Pydantic
- Interactive follow-up capabilities

Requirements:
    pip install pandas matplotlib seaborn openpyxl
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Any
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
        # Load the file based on extension
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
                    "outlier_indices": outliers.index.tolist()[:10]  # First 10
                })

        # Check for sudden spikes (if date column exists)
        date_cols = df.select_dtypes(include=['datetime64']).columns.tolist()

        # Also try to detect date columns that are strings
        for col in df.columns:
            if 'date' in col.lower() or 'time' in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col])
                    date_cols.append(col)
                except:
                    pass

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
        matplotlib.use('Agg')  # Non-interactive backend
    except ImportError:
        return json.dumps({"error": "matplotlib not installed. Run: pip install matplotlib"})

    try:
        file_path = os.path.expanduser(file_path)

        if file_path.endswith('.csv'):
            df = pd.read_csv(file_path)
        else:
            df = pd.read_excel(file_path)

        # Set up the figure
        fig, ax = plt.subplots(figsize=(10, 6))

        # Create the appropriate chart
        if chart_type == "line":
            if y_column:
                ax.plot(df[x_column], df[y_column], marker='o', linewidth=2)
                ax.set_ylabel(y_column)
            else:
                ax.plot(df[x_column], marker='o', linewidth=2)

        elif chart_type == "bar":
            if y_column:
                ax.bar(df[x_column].astype(str), df[y_column])
                ax.set_ylabel(y_column)
            else:
                value_counts = df[x_column].value_counts()
                ax.bar(value_counts.index.astype(str), value_counts.values)

        elif chart_type == "scatter":
            if y_column:
                ax.scatter(df[x_column], df[y_column], alpha=0.6)
                ax.set_ylabel(y_column)
            else:
                return json.dumps({"error": "Scatter plot requires y_column"})

        elif chart_type == "histogram":
            ax.hist(df[x_column].dropna(), bins=30, edgecolor='black', alpha=0.7)
            ax.set_ylabel("Frequency")

        elif chart_type == "box":
            ax.boxplot(df[x_column].dropna())
            ax.set_ylabel(x_column)

        else:
            return json.dumps({"error": f"Unknown chart type: {chart_type}"})

        # Styling
        ax.set_xlabel(x_column)
        ax.set_title(title or f"{chart_type.capitalize()} Chart: {x_column}")
        plt.xticks(rotation=45, ha='right')
        plt.tight_layout()

        # Save the figure
        if output_path:
            save_path = os.path.expanduser(output_path)
        else:
            save_path = "./chart_output.png"

        plt.savefig(save_path, dpi=150, bbox_inches='tight')
        plt.close()

        return json.dumps({
            "success": True,
            "chart_type": chart_type,
            "output_path": save_path,
            "message": f"Chart saved to {save_path}"
        })

    except Exception as e:
        return json.dumps({"error": f"Error creating visualization: {str(e)}"})


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
            # Grouped statistics
            grouped = df.groupby(group_by)[numeric_cols].agg(['mean', 'sum', 'count', 'min', 'max'])

            # Flatten column names
            grouped.columns = ['_'.join(col).strip() for col in grouped.columns.values]

            stats = {
                "grouped_by": group_by,
                "groups": grouped.to_dict('index')
            }
        else:
            # Overall statistics
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
# Agent Definition
# ============================================

dashboard_agent = Agent(
    name="Data Dashboard Analyst",
    instructions="""You are a data analysis assistant that helps users understand
    their personal data from CSV and Excel files.

    Your analysis workflow:
    1. Load and examine the data structure
    2. Provide summary statistics for all numeric columns
    3. Detect anomalies (missing values, outliers, duplicates)
    4. Create appropriate visualizations based on the data
    5. Provide actionable insights

    When analyzing data:
    - Start by understanding what kind of data it is (finance, fitness, habits, etc.)
    - Focus on trends and patterns
    - Highlight anything unusual or noteworthy
    - Suggest visualizations that would be most useful
    - Be specific about what you find - include actual numbers

    For financial data: Look for spending spikes, unusual transactions, trends
    For fitness data: Look for progress trends, consistency, plateaus
    For habit data: Look for streaks, patterns, correlations

    Always explain your findings in plain language that non-technical users
    can understand.
    """,
    model="gpt-4o-mini",
    tools=[
        load_and_analyze_data,
        detect_anomalies,
        create_visualization,
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
    create_charts: bool = True
) -> DataAnalysisReport:
    """
    Run the data dashboard agent on a data file.

    Args:
        file_path: Path to CSV or Excel file
        analysis_focus: Optional focus area (e.g., "spending", "progress", "habits")
        create_charts: Whether to generate visualizations

    Returns:
        DataAnalysisReport with analysis results

    Example:
        >>> # Analyze a spending log
        >>> result = run_data_dashboard_agent("expenses.csv", analysis_focus="spending")
        >>> print(result.summary)
        >>> for insight in result.key_insights:
        ...     print(f"- {insight}")
    """
    query = f"Please analyze the data file at '{file_path}'."

    if analysis_focus:
        query += f" Focus on {analysis_focus} patterns and insights."

    if create_charts:
        query += " Create appropriate visualizations to highlight key findings."
    else:
        query += " Skip visualizations, just provide the analysis."

    query += """
    Include:
    1. Overview of the data structure
    2. Key statistics
    3. Any anomalies or data quality issues
    4. Important insights and trends
    """

    result = Runner.run_sync(dashboard_agent, query)
    return result.final_output


# ============================================
# Demo with Sample Data
# ============================================

def create_sample_data():
    """Create sample CSV for testing."""
    try:
        import pandas as pd
    except ImportError:
        print("pandas required. Install with: pip install pandas")
        return None

    # Create sample expense data
    import random

    dates = pd.date_range(start='2024-01-01', periods=100, freq='D')
    categories = ['Food', 'Transport', 'Entertainment', 'Shopping', 'Bills']

    data = {
        'date': dates,
        'category': [random.choice(categories) for _ in range(100)],
        'amount': [round(random.uniform(10, 200), 2) for _ in range(100)],
        'description': [f"Transaction {i}" for i in range(100)]
    }

    # Add some anomalies
    data['amount'][45] = 1500.00  # Spending spike
    data['amount'][67] = None  # Missing value

    df = pd.DataFrame(data)
    sample_path = "./sample_expenses.csv"
    df.to_csv(sample_path, index=False)

    return sample_path


if __name__ == "__main__":
    print("=" * 60)
    print("Personal Data Dashboard Agent")
    print("=" * 60)

    # Create sample data for demo
    print("\n📊 Creating sample expense data...")
    sample_file = create_sample_data()

    if sample_file:
        print(f"   Sample file created: {sample_file}")

        print("\n🔍 Analyzing data...")
        print("-" * 40)

        result = run_data_dashboard_agent(
            sample_file,
            analysis_focus="spending patterns",
            create_charts=True
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
            print(f"\n📈 Chart saved to: {result.visualization_path}")

        # Cleanup
        if os.path.exists(sample_file):
            os.remove(sample_file)
            print(f"\n🧹 Cleaned up sample file")

    print("\n" + "=" * 60)
    print("Dashboard analysis complete!")
