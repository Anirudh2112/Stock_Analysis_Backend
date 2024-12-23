from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import io

from app.models.schemas import AnalysisRequest
from app.services.analysis import StockAnalysisService

app = FastAPI(title="Stock Breakout Analysis API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/analyze")
async def analyze_stock(request: AnalysisRequest):
    try:
        # Get analysis results
        results_df, summary = StockAnalysisService.calculate_breakout_returns(
            request.ticker,
            request.start_date,
            request.end_date,
            request.volume_threshold,
            request.price_threshold,
            request.holding_period
        )
        
        # Create CSV in memory
        output = io.StringIO()
        
        # Write summary statistics
        output.write("Summary Statistics\n")
        for key, value in summary.items():
            output.write(f"{key},{value}\n")
        
        output.write("\nDetailed Trade List\n")
        results_df.to_csv(output, index=False)
        
        # Create response
        response = StreamingResponse(
            iter([output.getvalue()]),
            media_type="text/csv",
            headers={
                'Content-Disposition': f'attachment; filename="{request.ticker}_analysis.csv"'
            }
        )
        
        return response
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    return {"status": "healthy"}