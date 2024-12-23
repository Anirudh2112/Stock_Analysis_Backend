import pytest
from datetime import datetime, timedelta
from app.services.analysis import StockAnalysisService

def test_calculate_breakout_returns():
    result_df, summary = StockAnalysisService.calculate_breakout_returns(
        ticker="AAPL",
        start_date=(datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d"),
        end_date=datetime.now().strftime("%Y-%m-%d"),
        volume_threshold=200,
        price_threshold=2,
        holding_period=10
    )
    
    expected_columns = [
        'Date', 'Entry_Price', 'Exit_Price', 
        'Volume_Ratio', 'Daily_Return', 'Total_Return'
    ]
    assert all(col in result_df.columns for col in expected_columns)
    
    expected_summary_keys = [
        'Total_Trades', 'Average_Return', 'Median_Return',
        'Win_Rate', 'Best_Trade', 'Worst_Trade'
    ]
    assert all(key in summary for key in expected_summary_keys)

def test_invalid_ticker():
    with pytest.raises(ValueError):
        StockAnalysisService.calculate_breakout_returns(
            ticker="INVALID_TICKER_123456",
            start_date=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),
            end_date=datetime.now().strftime("%Y-%m-%d"),
            volume_threshold=200,
            price_threshold=2,
            holding_period=10
        )

def test_invalid_date_range():
    with pytest.raises(ValueError):
        StockAnalysisService.calculate_breakout_returns(
            ticker="AAPL",
            start_date=datetime.now().strftime("%Y-%m-%d"),  
            end_date=(datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d"),  
            volume_threshold=200,
            price_threshold=2,
            holding_period=10
        )