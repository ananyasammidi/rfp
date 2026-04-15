"""
FastAPI running core logic sequentially
"""

import uuid
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from database import init_db, get_db, fetchall, fetchone
from scraper import scrape
from extractor import extract
from pricing import get_price
from distributors import DISTRIBUTORS
from email_sender import send_rfp

load_dotenv()
init_db()

app = FastAPI(title="Restaurant RFP Automation", version="1.0.0")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def index():
    return FileResponse("static/index.html")


class RunRequest(BaseModel):
    url: str = "https://www.rubyscafe.com/soho-menu/#all-day"

class StepResult(BaseModel):
    step: str
    status: str
    message: str

class RunResponse(BaseModel):
    menu_id: str
    restaurant: str
    url: str
    steps: list[StepResult]
    summary: dict


def _log(conn, menu_id, step, status, message):
    conn.execute(
        "INSERT INTO pipeline_logs (menu_id, step, status, message) VALUES (?,?,?,?)",
        (menu_id, step, status, message),
    )


@app.post("/pipeline/run", response_model=RunResponse)
def run_pipeline(req: RunRequest):
    menu_id = str(uuid.uuid4())
    steps = []

    with get_db() as conn:
        try:
            restaurant, dishes = scrape(req.url)
            conn.execute(
                "INSERT INTO menus (id, url, restaurant) VALUES (?,?,?)",
                (menu_id, req.url, restaurant),
            )
            dish_rows = []
            for d in dishes:
                dish_id = str(uuid.uuid4())
                conn.execute(
                    "INSERT INTO items (id, menu_id, name, description, price, category) VALUES (?,?,?,?,?,?)",
                    (dish_id, menu_id, d.name, d.description, d.price, d.category),
                )
                dish_rows.append({"id": dish_id, "name": d.name, "description": d.description})
            msg = f"Scraped {len(dishes)} dishes from {restaurant}"
            _log(conn, menu_id, "scrape", "ok", msg)
            steps.append(StepResult(step="scrape", status="ok", message=msg))
        except Exception as exc:
            _log(conn, menu_id, "scrape", "error", str(exc))
            raise HTTPException(status_code=502, detail=f"Scrape failed: {exc}")

        all_ingredients = []
        seen = set()
        for dish in dish_rows:
            for ing in extract(dish["name"], dish.get("description") or ""):
                conn.execute(
                    "INSERT INTO ingredients (id, dish_id, menu_id, raw_name, normalized_name, quantity, unit) VALUES (?,?,?,?,?,?,?)",
                    (str(uuid.uuid4()), dish["id"], menu_id, ing.raw_name, ing.normalized_name, ing.quantity, ing.unit),
                )
                if ing.normalized_name not in seen:
                    seen.add(ing.normalized_name)
                    all_ingredients.append({"normalized_name": ing.normalized_name, "quantity": ing.quantity, "unit": ing.unit})
        msg = f"Extracted {len(all_ingredients)} unique ingredients"
        _log(conn, menu_id, "extract", "ok", msg)
        steps.append(StepResult(step="extract", status="ok", message=msg))

        for ing in all_ingredients:
            est = get_price(ing["normalized_name"])
            conn.execute(
                "INSERT INTO pricing (id, menu_id, normalized_name, display_price, display_unit, trend, usda_category, usda_description, source) VALUES (?,?,?,?,?,?,?,?,?)",
                (str(uuid.uuid4()), menu_id, ing["normalized_name"], est.price, est.unit, est.trend, est.usda_category, est.usda_description, est.source),
            )
        msg = f"Priced {len(all_ingredients)} ingredients (USDA FoodData Central + ERS market estimates)"
        _log(conn, menu_id, "pricing", "ok", msg)
        steps.append(StepResult(step="pricing", status="ok", message=msg))

        dist_rows = []
        for d in DISTRIBUTORS:
            dist_id = str(uuid.uuid4())
            conn.execute(
                "INSERT INTO distributors (id, menu_id, name, email, phone, address) VALUES (?,?,?,?,?,?)",
                (dist_id, menu_id, d.name, d.email, d.phone, d.address),
            )
            dist_rows.append({"id": dist_id, "name": d.name, "email": d.email})
        msg = f"Loaded {len(dist_rows)} NYC distributors"
        _log(conn, menu_id, "distributors", "ok", msg)
        steps.append(StepResult(step="distributors", status="ok", message=msg))

        sent_count = mock_count = error_count = 0
        for dist in dist_rows:
            subject, body, error = send_rfp(
                to_address=dist["email"],
                distributor_name=dist["name"],
                restaurant=restaurant,
                ingredients=all_ingredients,
            )
            if error and error.startswith("mock:"):
                status = "mock"; mock_count += 1
            elif error:
                status = "failed"; error_count += 1
            else:
                status = "sent"; sent_count += 1
            conn.execute(
                "INSERT INTO emails (id, menu_id, distributor_id, to_address, subject, body, status, sent_at, error_msg) VALUES (?,?,?,?,?,?,?,?,?)",
                (str(uuid.uuid4()), menu_id, dist["id"], dist["email"], subject, body, status,
                 datetime.utcnow().isoformat() if status in ("sent", "mock") else None, error),
            )
        msg = f"Emails: {sent_count} sent, {mock_count} mock, {error_count} failed"
        _log(conn, menu_id, "emails", "ok", msg)
        steps.append(StepResult(step="emails", status="ok", message=msg))

    return RunResponse(
        menu_id=menu_id, restaurant=restaurant, url=req.url, steps=steps,
        summary={"dishes": len(dish_rows), "unique_ingredients": len(all_ingredients),
                 "distributors": len(dist_rows), "emails_sent": sent_count, "emails_mock": mock_count},
    )


@app.get("/runs")
def list_runs():
    with get_db() as conn:
        return fetchall(conn, "SELECT * FROM menus ORDER BY scraped_at DESC")

@app.get("/runs/{menu_id}")
def get_run(menu_id: str):
    with get_db() as conn:
        menu = fetchone(conn, "SELECT * FROM menus WHERE id=?", (menu_id,))
        if not menu:
            raise HTTPException(status_code=404, detail="Run not found")
        return {
            "menu": menu,
            "dishes": fetchall(conn, "SELECT * FROM items WHERE menu_id=?", (menu_id,)),
            "ingredients": fetchall(conn, "SELECT * FROM ingredients WHERE menu_id=?", (menu_id,)),
            "pricing": fetchall(conn, "SELECT * FROM pricing WHERE menu_id=?", (menu_id,)),
            "distributors": fetchall(conn, "SELECT * FROM distributors WHERE menu_id=?", (menu_id,)),
            "emails": fetchall(conn, "SELECT id, to_address, subject, status, sent_at, error_msg FROM emails WHERE menu_id=?", (menu_id,)),
        }

@app.get("/runs/{menu_id}/logs")
def get_logs(menu_id: str):
    with get_db() as conn:
        return fetchall(conn, "SELECT step, status, message, ts FROM pipeline_logs WHERE menu_id=? ORDER BY id", (menu_id,))

@app.get("/runs/{menu_id}/emails")
def get_emails(menu_id: str):
    with get_db() as conn:
        return fetchall(conn, "SELECT to_address, subject, body, status, sent_at FROM emails WHERE menu_id=?", (menu_id,))