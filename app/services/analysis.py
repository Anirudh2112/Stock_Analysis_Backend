from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
import numpy as np
from typing import Tuple, Dict, Any

class StockAnalysisService:
    @staticmethod
    def calculate_breakout_returns(
        ticker: str,
        start_date: str,
        end_date: str,
        volume_threshold: float,
        price_threshold: float,
        holding_period: int
    ) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        # Add buffer days to get enough data for initial average calculation
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        buffered_start = (start_dt - timedelta(days=30)).strftime('%Y-%m-%d')
        
        # Fetch data from Yahoo Finance
        stock = yf.Ticker(ticker)
        df = stock.history(start=buffered_start, end=end_date)
        
        if df.empty:
            raise ValueError("No data found for the specified ticker and date range")
        
        # Calculate 20-day average volume
        df['Volume_MA20'] = df['Volume'].rolling(window=20).mean()
        
        # Calculate daily returns
        df['Daily_Return'] = df['Close'].pct_change()
        
        # Identify breakout days
        df['Volume_Ratio'] = df['Volume'] / df['Volume_MA20']
        breakout_days = df[
            (df['Volume_Ratio'] > volume_threshold / 100) &
            (df['Daily_Return'] > price_threshold / 100) &
            (df.index >= start_date)
        ].index
        
        results = []
        
        for day in breakout_days:
            entry_price = df.loc[day, 'Close']
            
            # Get future prices for holding period
            future_prices = df.loc[day:].head(holding_period + 1)
            
            if len(future_prices) < holding_period + 1:
                continue
                
            exit_price = future_prices.iloc[holding_period]['Close']
            total_return = (exit_price - entry_price) / entry_price * 100
            
            results.append({
                'Date': day.strftime('%Y-%m-%d'),
                'Entry_Price': round(entry_price, 2),
                'Exit_Price': round(exit_price, 2),
                'Volume_Ratio': round(df.loc[day, 'Volume_Ratio'], 2),
                'Daily_Return': round(df.loc[day, 'Daily_Return'] * 100, 2),
                'Total_Return': round(total_return, 2)
            })
        
        if not results:
            raise ValueError("No breakout events found for the specified criteria")
        
        results_df = pd.DataFrame(results)
        
        # Calculate summary statistics
        summary = {
            'Total_Trades': len(results),
            'Average_Return': round(results_df['Total_Return'].mean(), 2),
            'Median_Return': round(results_df['Total_Return'].median(), 2),
            'Win_Rate': round((results_df['Total_Return'] > 0).mean() * 100, 2),
            'Best_Trade': round(results_df['Total_Return'].max(), 2),
            'Worst_Trade': round(results_df['Total_Return'].min(), 2)
        }
        
        return results_df, summary