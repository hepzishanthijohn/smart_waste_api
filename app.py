from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import datetime

app = FastAPI()

# Gas status model to capture gas-related information in the bin
class GasStatus(BaseModel):
    status: str  # 'safe', 'dangerous', 'methane_detected'
    message: str  # Detailed message about the gas detected
    concentration: str  # Gas concentration (ppm)
    last_checked: str  # Timestamp of last gas check

# Bin model to represent the state of a bin
class Bin(BaseModel):
    id: int
    load_status: str  # 'empty' or 'full'
    gas_status: GasStatus  # Gas status information
    weight: float  # Weight of trash in the bin (kg)
    alert: bool  # Whether an alert is triggered
    light_indicator: bool  # Light indicator: True (on) or False (off)
    buzzer: bool  # Whether the buzzer is triggered
    last_updated: str  # Timestamp of last status update

# Sample bin data (this could be populated dynamically or via database in real-world scenarios)
bins_db = [
    Bin(id=1, load_status="empty", gas_status=GasStatus(status="safe", message="No harmful gases detected", concentration="0 ppm", last_checked="2024-11-24T12:00:00"), weight=0.0, alert=False, light_indicator=False, buzzer=False, last_updated="2024-11-24T12:00:00"),
    Bin(id=2, load_status="full", gas_status=GasStatus(status="safe", message="No harmful gases detected", concentration="0 ppm", last_checked="2024-11-24T12:00:00"), weight=48.0, alert=False, light_indicator=True, buzzer=True, last_updated="2024-11-24T12:00:00"),
    Bin(id=3, load_status="full", gas_status=GasStatus(status="methane_detected", message="Methane gas detected", concentration="150 ppm", last_checked="2024-11-24T12:10:00"), weight=50.0, alert=True, light_indicator=True, buzzer=True, last_updated="2024-11-24T12:10:00"),
]

# Helper function to check the bin's condition and trigger alerts
def check_alerts(bin: Bin):
    if bin.load_status == "full" and bin.weight >= 50.0:
        bin.alert = True
        bin.buzzer = True
        bin.light_indicator = True
        bin.last_updated = str(datetime.datetime.now())
        bin.load_status = "full"
    
    if bin.gas_status.status == "methane_detected":
        bin.alert = True
        bin.buzzer = True
        bin.light_indicator = True
        bin.last_updated = str(datetime.datetime.now())
        bin.operational_status = "Critical"
    
    return bin

#### Step 2: Define API Endpoints

# Get all bins' statuses
@app.get("/bins", response_model=List[Bin])
def get_bins():
    return bins_db

# Get status of a specific bin
@app.get("/bins/{bin_id}", response_model=Bin)
def get_bin(bin_id: int):
    bin = next((bin for bin in bins_db if bin.id == bin_id), None)
    if not bin:
        raise HTTPException(status_code=404, detail="Bin not found")
    return bin

# Update a specific bin's status, including weight and gas status
@app.post("/bins/{bin_id}/update", response_model=Bin)
def update_bin(bin_id: int, load_status: str, weight: float, gas_status: str, concentration: str):
    bin = next((bin for bin in bins_db if bin.id == bin_id), None)
    if not bin:
        raise HTTPException(status_code=404, detail="Bin not found")
    
    # Update the bin's status based on the input
    bin.load_status = load_status
    bin.weight = weight
    bin.gas_status = GasStatus(status=gas_status, message="Updated", concentration=concentration, last_checked=str(datetime.datetime.now()))
    
    # Check if an alert should be triggered
    bin = check_alerts(bin)
    
    return {"message": "Bin status updated", "bin": bin}
