"""
distributors.py — Curated list of real NYC-area food distributors.

Static list chosen to cover a broad range of restaurant ingredient needs:
broadline, specialty produce, proteins, dairy, and dry goods.
Emails are mock addresses for demo purposes.
"""

from dataclasses import dataclass


@dataclass
class Distributor:
    name: str
    email: str
    phone: str
    address: str


DISTRIBUTORS: list[Distributor] = [
    Distributor(
        name="Sysco New York",
        email="rfp@sysco-newyork-demo.com",
        phone="(718) 893-4600",
        address="355 Food Center Dr, Bronx, NY 10474",
    ),
    Distributor(
        name="Baldor Specialty Foods",
        email="procurement@baldor-demo.com",
        phone="(718) 860-9100",
        address="155 Food Center Dr, Bronx, NY 10474",
    ),
    Distributor(
        name="US Foods New York",
        email="quotes@usfoods-ny-demo.com",
        phone="(212) 736-3800",
        address="808 Newark Ave, Elizabeth, NJ 07208",
    ),
    Distributor(
        name="FreshPoint New York",
        email="quotes@freshpoint-ny-demo.com",
        phone="(718) 378-6000",
        address="1500 Hunts Point Ave, Bronx, NY 10474",
    ),
    Distributor(
        name="Arrow Reliance (d'Artagnan)",
        email="sales@dartagnan-demo.com",
        phone="(800) 327-8246",
        address="600 Green Lane, Union, NJ 07083",
    ),
]
