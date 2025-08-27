#!/usr/bin/env python3
"""
Google Sheets Agent Example using OpenAI Agents SDK

This example demonstrates how to build an AI agent that can interact with Google Sheets
to read, write, analyze, and manage spreadsheet data.

Requirements:
1. Set up Google Cloud Platform project
2. Enable Google Sheets API
3. Create a service account and download credentials.json
4. Install required packages: pip install openai-agents google-api-python-client

Setup Instructions:
1. Go to Google Cloud Platform Console
2. Create a new project or select existing one
3. Enable Google Sheets API
4. Go to IAM & Admin > Service Accounts
5. Create a new service account
6. Download the JSON key file and save as 'credentials.json' in this directory
7. Share your Google Sheets with the service account email (found in credentials.json)
"""

import asyncio
import json
import os
from typing import List, Dict, Any, Optional
import pandas as pd
from googleapiclient.discovery import build
from google.oauth2 import service_account

from agents import Agent, Runner, function_tool
from agents.run import RunConfig
from agents import trace

# Configuration
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
CREDENTIALS_FILE = 'credentials.json'

class SheetsSession:
    """Session manager for Google Sheets operations"""
    
    def __init__(self):
        self.current_spreadsheet_id = None
        self.current_sheet_name = None
        self.service = None
        self._setup_service()
    
    def _setup_service(self):
        """Initialize Google Sheets API service"""
        if not os.path.exists(CREDENTIALS_FILE):
            raise FileNotFoundError(
                f"Google credentials file '{CREDENTIALS_FILE}' not found. "
                "Please download it from Google Cloud Platform."
            )
        
        credentials = service_account.Credentials.from_service_account_file(
            CREDENTIALS_FILE, scopes=SCOPES
        )
        self.service = build('sheets', 'v4', credentials=credentials)
    
    def set_active_sheet(self, spreadsheet_id: str, sheet_name: str = None):
        """Set the active spreadsheet and sheet"""
        self.current_spreadsheet_id = spreadsheet_id
        self.current_sheet_name = sheet_name or "Sheet1"
    
    def get_sheet_info(self):
        """Get current sheet information"""
        if not self.current_spreadsheet_id:
            return "No active spreadsheet set"
        return f"Active: {self.current_spreadsheet_id}, Sheet: {self.current_sheet_name}"

# Global session instance
sheets_session = SheetsSession()

@function_tool
def read_sheet_data(spreadsheet_id: str, range_name: str, sheet_name: str = "Sheet1") -> str:
    """
    Read data from a Google Sheet
    
    Args:
        spreadsheet_id: The Google Sheets document ID (from the URL)
        range_name: The range to read (e.g., 'A1:E10', 'A:E', 'Sales Data')
        sheet_name: Name of the sheet tab (default: Sheet1)
    
    Returns:
        JSON string containing the sheet data
    """
    try:
        # Update session
        sheets_session.set_active_sheet(spreadsheet_id, sheet_name)
        
        # Construct full range
        full_range = f"{sheet_name}!{range_name}" if sheet_name else range_name
        
        # Read data
        result = sheets_session.service.spreadsheets().values().get(
            spreadsheetId=spreadsheet_id,
            range=full_range
        ).execute()
        
        values = result.get('values', [])
        
        if not values:
            return json.dumps({"message": "No data found in the specified range"})
        
        # Convert to structured format
        if len(values) > 1:
            headers = values[0]
            data_rows = values[1:]
            data = []
            for row in data_rows:
                # Handle rows with missing values
                row_dict = {}
                for i, header in enumerate(headers):
                    row_dict[header] = row[i] if i < len(row) else ""
                data.append(row_dict)
            
            return json.dumps({
                "range": full_range,
                "headers": headers,
                "data": data,
                "row_count": len(data_rows)
            }, indent=2)
        else:
            return json.dumps({
                "range": full_range,
                "raw_data": values,
                "row_count": len(values)
            }, indent=2)
            
    except Exception as e:
        return json.dumps({"error": f"Failed to read sheet data: {str(e)}"})

@function_tool
def write_sheet_data(spreadsheet_id: str, range_name: str, data: List[List[str]], sheet_name: str = "Sheet1") -> str:
    """
    Write data to a specific range in Google Sheets
    
    Args:
        spreadsheet_id: The Google Sheets document ID
        range_name: The range to write to (e.g., 'A1:C3')
        data: 2D list of values to write
        sheet_name: Name of the sheet tab
    
    Returns:
        Success message with details
    """
    try:
        # Update session
        sheets_session.set_active_sheet(spreadsheet_id, sheet_name)
        
        # Construct full range
        full_range = f"{sheet_name}!{range_name}" if sheet_name else range_name
        
        # Prepare the request body
        body = {
            'values': data
        }
        
        # Write data
        result = sheets_session.service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id,
            range=full_range,
            valueInputOption='USER_ENTERED',
            body=body
        ).execute()
        
        return json.dumps({
            "success": True,
            "message": f"Updated {result.get('updatedCells', 0)} cells in {full_range}",
            "range": full_range,
            "updated_rows": result.get('updatedRows', 0),
            "updated_columns": result.get('updatedColumns', 0)
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to write sheet data: {str(e)}"})

@function_tool
def append_sheet_data(spreadsheet_id: str, data: List[List[str]], sheet_name: str = "Sheet1") -> str:
    """
    Append new rows to the end of a Google Sheet
    
    Args:
        spreadsheet_id: The Google Sheets document ID
        data: 2D list of values to append
        sheet_name: Name of the sheet tab
    
    Returns:
        Success message with details
    """
    try:
        # Update session
        sheets_session.set_active_sheet(spreadsheet_id, sheet_name)
        
        # Construct range for the entire sheet
        range_name = f"{sheet_name}!A:Z"
        
        # Prepare the request body
        body = {
            'values': data
        }
        
        # Append data
        result = sheets_session.service.spreadsheets().values().append(
            spreadsheetId=spreadsheet_id,
            range=range_name,
            valueInputOption='USER_ENTERED',
            insertDataOption='INSERT_ROWS',
            body=body
        ).execute()
        
        return json.dumps({
            "success": True,
            "message": f"Appended {len(data)} rows to {sheet_name}",
            "updated_range": result.get('updates', {}).get('updatedRange', ''),
            "updated_rows": result.get('updates', {}).get('updatedRows', 0),
            "updated_cells": result.get('updates', {}).get('updatedCells', 0)
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to append sheet data: {str(e)}"})

@function_tool
def clear_sheet_range(spreadsheet_id: str, range_name: str, sheet_name: str = "Sheet1") -> str:
    """
    Clear data from a specific range in Google Sheets
    
    Args:
        spreadsheet_id: The Google Sheets document ID
        range_name: The range to clear (e.g., 'A1:E10')
        sheet_name: Name of the sheet tab
    
    Returns:
        Success message
    """
    try:
        # Update session
        sheets_session.set_active_sheet(spreadsheet_id, sheet_name)
        
        # Construct full range
        full_range = f"{sheet_name}!{range_name}" if sheet_name else range_name
        
        # Clear the range
        result = sheets_session.service.spreadsheets().values().clear(
            spreadsheetId=spreadsheet_id,
            range=full_range
        ).execute()
        
        return json.dumps({
            "success": True,
            "message": f"Cleared range {full_range}",
            "cleared_range": result.get('clearedRange', full_range)
        }, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to clear sheet range: {str(e)}"})

@function_tool
def analyze_sheet_data(spreadsheet_id: str, range_name: str, analysis_type: str = "summary", sheet_name: str = "Sheet1") -> str:
    """
    Analyze data from a Google Sheet and provide insights
    
    Args:
        spreadsheet_id: The Google Sheets document ID
        range_name: The range to analyze
        analysis_type: Type of analysis ('summary', 'statistics', 'trends')
        sheet_name: Name of the sheet tab
    
    Returns:
        Analysis results as JSON string
    """
    try:
        # First, read the data
        data_result = read_sheet_data(spreadsheet_id, range_name, sheet_name)
        data_json = json.loads(data_result)
        
        if "error" in data_json:
            return data_result
        
        if "data" not in data_json:
            return json.dumps({"error": "No structured data available for analysis"})
        
        data = data_json["data"]
        headers = data_json["headers"]
        
        # Convert to pandas DataFrame for analysis
        df = pd.DataFrame(data)
        
        analysis_result = {
            "analysis_type": analysis_type,
            "range": f"{sheet_name}!{range_name}",
            "total_rows": len(data),
            "total_columns": len(headers),
            "columns": headers
        }
        
        if analysis_type == "summary":
            # Basic summary
            analysis_result["summary"] = {
                "row_count": len(data),
                "column_count": len(headers),
                "non_empty_cells": sum(1 for row in data for value in row.values() if str(value).strip()),
                "sample_data": data[:3] if len(data) > 3 else data
            }
            
        elif analysis_type == "statistics":
            # Statistical analysis for numeric columns
            numeric_analysis = {}
            for col in headers:
                try:
                    values = [float(row[col]) for row in data if str(row[col]).replace('.', '').replace('-', '').isdigit()]
                    if values:
                        numeric_analysis[col] = {
                            "count": len(values),
                            "mean": sum(values) / len(values),
                            "min": min(values),
                            "max": max(values)
                        }
                except:
                    continue
            analysis_result["numeric_statistics"] = numeric_analysis
            
        elif analysis_type == "trends":
            # Basic trend analysis
            analysis_result["trends"] = {
                "most_common_values": {},
                "data_quality": {
                    "empty_cells": sum(1 for row in data for value in row.values() if not str(value).strip()),
                    "total_cells": len(data) * len(headers)
                }
            }
            
            # Find most common values in each column
            for col in headers:
                values = [str(row[col]).strip() for row in data if str(row[col]).strip()]
                if values:
                    value_counts = {}
                    for value in values:
                        value_counts[value] = value_counts.get(value, 0) + 1
                    # Get top 3 most common values
                    sorted_values = sorted(value_counts.items(), key=lambda x: x[1], reverse=True)[:3]
                    analysis_result["trends"]["most_common_values"][col] = sorted_values
        
        return json.dumps(analysis_result, indent=2)
        
    except Exception as e:
        return json.dumps({"error": f"Failed to analyze sheet data: {str(e)}"})

@function_tool
def create_summary_report(spreadsheet_id: str, source_range: str, report_title: str = "Data Summary", sheet_name: str = "Sheet1") -> str:
    """
    Create a summary report based on sheet data and write it to a new location
    
    Args:
        spreadsheet_id: The Google Sheets document ID
        source_range: The range to analyze for the report
        report_title: Title for the summary report
        sheet_name: Name of the sheet tab
    
    Returns:
        Report summary and location where it was written
    """
    try:
        # Get analysis of the data
        analysis_result = analyze_sheet_data(spreadsheet_id, source_range, "summary", sheet_name)
        analysis_data = json.loads(analysis_result)
        
        if "error" in analysis_data:
            return analysis_result
        
        # Create report data
        report_data = [
            [report_title],
            ["Generated on:", pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")],
            ["Source Range:", f"{sheet_name}!{source_range}"],
            [""],
            ["Summary Statistics:"],
            ["Total Rows:", str(analysis_data["summary"]["row_count"])],
            ["Total Columns:", str(analysis_data["summary"]["column_count"])],
            ["Non-empty Cells:", str(analysis_data["summary"]["non_empty_cells"])],
            [""],
            ["Column Names:"]
        ]
        
        # Add column names
        for i, col in enumerate(analysis_data["columns"], 1):
            report_data.append([f"{i}.", col])
        
        # Add sample data
        report_data.extend([
            [""],
            ["Sample Data (first 3 rows):"]
        ])
        
        if analysis_data["summary"]["sample_data"]:
            # Add headers
            headers = analysis_data["columns"]
            report_data.append(headers)
            
            # Add sample rows
            for row_data in analysis_data["summary"]["sample_data"]:
                row = [str(row_data.get(col, "")) for col in headers]
                report_data.append(row)
        
        # Find empty space to write the report (starting from column H)
        report_range = f"H1:K{len(report_data)}"
        
        # Write the report
        write_result = write_sheet_data(spreadsheet_id, report_range, report_data, sheet_name)
        write_data = json.loads(write_result)
        
        if write_data.get("success"):
            return json.dumps({
                "success": True,
                "message": f"Created summary report '{report_title}' in range {sheet_name}!{report_range}",
                "report_location": f"{sheet_name}!{report_range}",
                "report_rows": len(report_data),
                "source_data_summary": analysis_data["summary"]
            }, indent=2)
        else:
            return write_result
            
    except Exception as e:
        return json.dumps({"error": f"Failed to create summary report: {str(e)}"})

# Create the spreadsheet agent
spreadsheet_agent = Agent(
    name="Spreadsheet Assistant",
    instructions="""You are a helpful assistant that specializes in working with Google Sheets.

You can help users:
- Read and analyze data from Google Sheets
- Write and update data in sheets
- Create summary reports and insights
- Manage sheet data efficiently

When working with spreadsheets:
1. Always ask for the spreadsheet ID (found in the Google Sheets URL)
2. Confirm the sheet name (tab) they want to work with
3. Be specific about ranges (e.g., A1:E10, A:C, etc.)
4. Provide clear explanations of what operations you're performing
5. Handle errors gracefully and suggest solutions

For data analysis, offer insights such as:
- Data summaries and statistics
- Trends and patterns
- Data quality observations
- Recommendations for data organization

Remember to be helpful, accurate, and clear in your responses.""",
    model="gpt-4",
    tools=[
        read_sheet_data,
        write_sheet_data,
        append_sheet_data,
        clear_sheet_range,
        analyze_sheet_data,
        create_summary_report
    ]
)

async def run_example_session():
    """Run an example session with the spreadsheet agent"""
    
    print("🔧 Google Sheets Agent - OpenAI Agents SDK Example")
    print("=" * 50)
    
    # Example spreadsheet ID (replace with your own)
    # This would typically come from user input
    example_spreadsheet_id = "your_spreadsheet_id_here"
    
    print(f"📊 Current session: {sheets_session.get_sheet_info()}")
    print()
    
    # Example interactions
    example_queries = [
        "Help me read data from my sales spreadsheet. The ID is '1abc123...' and I want to see the data in range A1:E10 from the 'Sales Data' sheet.",
        "Can you analyze the sales data I just showed you and give me a summary of trends?",
        "I need to add new sales records. Can you append this data: [['2024-01-15', 'Product A', '100', '50', '5000']] to my sales sheet?",
        "Create a summary report of my sales data and place it starting at column H."
    ]
    
    for i, query in enumerate(example_queries, 1):
        print(f"Example Query {i}:")
        print(f"User: {query}")
        print()
        
        with trace(f"Spreadsheet Query {i}"):
            try:
                # In a real scenario, you would replace the spreadsheet ID in the query
                if "1abc123..." in query:
                    print("⚠️  Note: Replace '1abc123...' with your actual Google Sheets ID")
                    print("   (This is just an example - the agent would handle real data)")
                    print()
                
                # For demonstration, we'll show what the agent would do
                result = await Runner.run(
                    spreadsheet_agent, 
                    query,
                    run_config=RunConfig(
                        tracing_enabled=True,
                        metadata={"query_type": "spreadsheet_operation"}
                    )
                )
                
                print("🤖 Agent Response:")
                print(result.final_output)
                
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                print("   This is expected in the demo since we're using placeholder data")
        
        print("-" * 50)
        print()

def run_interactive_session():
    """Run an interactive session with the spreadsheet agent"""
    
    print("🔧 Interactive Google Sheets Agent")
    print("=" * 40)
    print()
    print("Instructions:")
    print("1. Make sure you have credentials.json in this directory")
    print("2. Share your Google Sheets with the service account email")
    print("3. Get your spreadsheet ID from the URL")
    print("4. Type 'quit' to exit")
    print()
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            
            if not user_input:
                continue
            
            print()
            print("🤖 Processing...")
            
            with trace("Interactive Spreadsheet Query"):
                result = Runner.run_sync(
                    spreadsheet_agent,
                    user_input,
                    run_config=RunConfig(
                        tracing_enabled=True,
                        metadata={"session_type": "interactive"}
                    )
                )
                
                print("🤖 Agent:")
                print(result.final_output)
                print()
        
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print()

if __name__ == "__main__":
    print("🚀 Google Sheets Agent with OpenAI Agents SDK")
    print("=" * 50)
    print()
    
    # Check for credentials
    if not os.path.exists(CREDENTIALS_FILE):
        print("⚠️  Setup Required:")
        print("1. Download credentials.json from Google Cloud Platform")
        print("2. Place it in this directory")
        print("3. Share your Google Sheets with the service account email")
        print()
        print("See the comments at the top of this file for detailed setup instructions.")
        exit(1)
    
    print("Choose an option:")
    print("1. Run example session (demo)")
    print("2. Run interactive session")
    print()
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        asyncio.run(run_example_session())
    elif choice == "2":
        run_interactive_session()
    else:
        print("Invalid choice. Running example session...")
        asyncio.run(run_example_session())