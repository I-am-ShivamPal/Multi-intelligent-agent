#!/usr/bin/env python3
"""Daily Infrastructure Health Rollup Aggregation"""
import pandas as pd
import os
from datetime import datetime, timedelta
from core.env_config import EnvironmentConfig

class DailyRollup:
    """Aggregates daily infrastructure health metrics."""
    
    def __init__(self, env='dev'):
        self.env = env
        self.env_config = EnvironmentConfig(env)
    
    def aggregate_daily_health(self, date=None):
        """Aggregate health metrics for a specific date."""
        if date is None:
            date = datetime.now().date()
        
        health_log = self.env_config.get_log_path('infra_health_log.csv')
        if not os.path.exists(health_log):
            return None
        
        df = pd.read_csv(health_log)
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['date'] = df['timestamp'].dt.date
        
        daily_data = df[df['date'] == date]
        if daily_data.empty:
            return None
        
        aggregated = {
            'date': date.isoformat(),
            'total_checks': len(daily_data),
            'healthy_checks': daily_data['healthy'].sum(),
            'uptime_percentage': (daily_data['healthy'].sum() / len(daily_data)) * 100,
            'avg_cpu_usage': daily_data['cpu_usage'].mean(),
            'avg_memory_usage': daily_data['memory_usage'].mean(),
            'max_cpu_usage': daily_data['cpu_usage'].max(),
            'max_memory_usage': daily_data['memory_usage'].max(),
            'downtime_minutes': (len(daily_data) - daily_data['healthy'].sum()) * 5,
            'environment': self.env
        }
        
        return aggregated
    
    def save_daily_rollup(self, aggregated_data):
        """Save aggregated data to rollup file."""
        rollup_file = self.env_config.get_log_path('daily_health_rollup.csv')
        
        if not os.path.exists(rollup_file):
            df = pd.DataFrame([aggregated_data])
        else:
            existing_df = pd.read_csv(rollup_file)
            df = pd.concat([existing_df, pd.DataFrame([aggregated_data])], ignore_index=True)
            df = df.drop_duplicates(subset=['date'], keep='last')
        
        df.to_csv(rollup_file, index=False)
        return rollup_file

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", choices=['dev', 'stage', 'prod'], default='dev')
    args = parser.parse_args()
    
    rollup = DailyRollup(args.env)
    aggregated = rollup.aggregate_daily_health()
    
    if aggregated:
        file_path = rollup.save_daily_rollup(aggregated)
        print(f"✅ Daily rollup saved: {file_path}")
        print(f"📊 Uptime: {aggregated['uptime_percentage']:.1f}%")
    else:
        print("❌ No health data available for today")