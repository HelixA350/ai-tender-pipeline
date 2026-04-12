import pytest
from worker.schemas.excel_data import (
    create_excel_data,
    ExcelData,
    ExcelItem,
    ExcelCustomer,
    ExcelGeneral,
    ExcelRequirements,
    ExcelFinancials,
    ExcelDates,
)


class TestCreateExcelData:
    def test_create_excel_data_from_full_result(self):
        test_result = {
            "general": {"name": "Test Tender", "method": "Open", "notes": "Some notes"},
            "procurement_items": [
                {
                    "position": 1,
                    "name": "Item 1",
                    "article": "ART001",
                    "manufacturer": "Manuf 1",
                    "qty": 10,
                    "unit": "PCS",
                },
                {
                    "position": 2,
                    "name": "Item 2",
                    "qty": 5,
                    "unit": "KG",
                },
            ],
            "parties": {
                "customer": {
                    "name": "Customer Org",
                    "full_name": "Full Customer Name",
                    "inn": "1234567890",
                    "kpp": "123456789",
                    "address": "Address 123",
                }
            },
            "product_requirements": {
                "condition": "new",
                "warranty_months": 12,
                "warranty_start": "from delivery",
                "analog_allowed": False,
            },
            "financials": {
                "nmck": 100000.0,
                "vat_rate": 0.2,
                "prices_include_vat": True,
            },
            "dates": {
                "submission_deadline": "2025-12-31",
                "delivery_start": "2026-01-15",
                "delivery_end": "2026-03-01",
            },
        }

        excel_data = create_excel_data(test_result)

        assert excel_data is not None
        assert excel_data.general.name == "Test Tender"
        assert excel_data.general.method == "Open"
        assert excel_data.general.notes == "Some notes"

        assert len(excel_data.items) == 2
        assert excel_data.items[0].name == "Item 1"
        assert excel_data.items[0].article == "ART001"
        assert excel_data.items[1].name == "Item 2"

        assert excel_data.customer.name == "Customer Org"
        assert excel_data.customer.inn == "1234567890"

        assert excel_data.requirements.condition == "new"
        assert excel_data.requirements.warranty_months == 12

        assert excel_data.financials.nmck == 100000.0
        assert excel_data.financials.vat_rate == 0.2

        assert excel_data.dates.submission_deadline == "2025-12-31"
        assert excel_data.dates.delivery_start == "2026-01-15"

    def test_create_excel_data_with_empty_result(self):
        assert create_excel_data({}) is None
        assert create_excel_data(None) is None

    def test_create_excel_data_with_only_items(self):
        test_result = {
            "procurement_items": [
                {"position": 1, "name": "Item", "qty": 1, "unit": "PCS"}
            ]
        }

        excel_data = create_excel_data(test_result)

        assert excel_data is not None
        assert excel_data.general is None
        assert len(excel_data.items) == 1
        assert excel_data.items[0].name == "Item"

    def test_create_excel_data_with_nested_financials(self):
        test_result = {
            "financials": {
                "nmck": 50000.0,
                "bid_security": {"amount": 5000.0, "form": "bank_guarantee"},
                "contract_security": {"amount": 10000.0, "form": "deposit"},
                "payment_terms": {
                    "type": "advance",
                    "advance_pct": 30.0,
                    "days_min": 10,
                    "days_max": 30,
                },
                "incoterms": {"primary": "DDP", "location": "Moscow"},
                "penalties": {
                    "late_delivery_pct": 0.1,
                    "max_penalty_pct": 10.0,
                },
            }
        }

        excel_data = create_excel_data(test_result)

        assert excel_data.financials.nmck == 50000.0
        assert excel_data.financials.bid_security.amount == 5000.0
        assert excel_data.financials.bid_security.form == "bank_guarantee"
        assert excel_data.financials.contract_security.amount == 10000.0
        assert excel_data.financials.payment_terms.type == "advance"
        assert excel_data.financials.payment_terms.advance_pct == 30.0
        assert excel_data.financials.incoterms.primary == "DDP"
        assert excel_data.financials.penalties.late_delivery_pct == 0.1


class TestExcelDataModels:
    def test_excel_general(self):
        general = ExcelGeneral(name="Test", method="Open", notes="Notes")
        assert general.name == "Test"
        assert general.method == "Open"
        assert general.notes == "Notes"

    def test_excel_item(self):
        item = ExcelItem(
            position=1,
            name="Test Item",
            article="ART001",
            manufacturer="Manuf",
            qty=10.0,
            unit="PCS",
        )
        assert item.position == 1
        assert item.name == "Test Item"
        assert item.qty == 10.0

    def test_excel_customer(self):
        customer = ExcelCustomer(name="Org", inn="1234567890", kpp="123456789")
        assert customer.name == "Org"
        assert customer.inn == "1234567890"

    def test_excel_requirements(self):
        req = ExcelRequirements(
            condition="new", warranty_months=24, analog_allowed=False
        )
        assert req.condition == "new"
        assert req.warranty_months == 24

    def test_excel_financials(self):
        financials = ExcelFinancials(nmck=100000.0, vat_rate=0.2)
        assert financials.nmck == 100000.0
        assert financials.vat_rate == 0.2

    def test_excel_dates(self):
        dates = ExcelDates(
            submission_deadline="2025-12-31", delivery_start="2026-01-01"
        )
        assert dates.submission_deadline == "2025-12-31"
