import pandas as pd
from fastapi import APIRouter, Depends, UploadFile, File, HTTPException
from io import BytesIO

from app.auth import get_current_user, AuthedUser
from app.db import supabase

router = APIRouter(prefix="/po", tags=["purchase-orders"])

REQUIRED_COLUMNS = {"order_ref", "buyer", "style", "order_qty", "ship_date", "status"}


@router.post("/upload")
async def upload_po_file(
    file: UploadFile = File(...),
    user: AuthedUser = Depends(get_current_user),
):
    """
    Manual upload fallback: replaces this org's PO data with the contents
    of the uploaded .xlsx file. Google Sheets / ERP auto-sync will call the
    same underlying upsert logic in Step 2.
    """
    if not file.filename.endswith((".xlsx", ".xls")):
        raise HTTPException(400, "Please upload an .xlsx or .xls file")

    contents = await file.read()
    df = pd.read_excel(BytesIO(contents))

    missing = REQUIRED_COLUMNS - set(df.columns)
    if missing:
        raise HTTPException(400, f"Missing required columns: {sorted(missing)}")

    df["ship_date"] = pd.to_datetime(df["ship_date"]).dt.strftime("%Y-%m-%d")
    df["org_id"] = user.org_id

    # Wipe and replace this org's data. Fine for v1; Step 2 can move to
    # a proper upsert keyed on order_ref once sync sources are added.
    supabase.table("purchase_orders").delete().eq("org_id", user.org_id).execute()
    records = df[list(REQUIRED_COLUMNS) + ["org_id"]].to_dict(orient="records")
    supabase.table("purchase_orders").insert(records).execute()

    return {"inserted": len(records)}
