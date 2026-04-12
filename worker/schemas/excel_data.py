from typing import Optional, List
from pydantic import BaseModel, Field


class ExcelGeneral(BaseModel):
    name: Optional[str] = None
    method: Optional[str] = None
    notes: Optional[str] = None


class ExcelItem(BaseModel):
    position: int
    name: str
    article: Optional[str] = None
    manufacturer: Optional[str] = None
    qty: float
    unit: str
    npp: Optional[str] = None
    category: Optional[str] = None
    unit_price: Optional[float] = None
    currency: Optional[str] = None
    delivery_date: Optional[str] = None
    delivery_location: Optional[str] = None
    analog_allowed: Optional[bool] = None
    original_reference: Optional[str] = None
    linked_service: Optional[str] = None
    source: Optional[str] = None
    notes: Optional[str] = None


class ExcelCustomer(BaseModel):
    name: Optional[str] = None
    full_name: Optional[str] = None
    inn: Optional[str] = None
    kpp: Optional[str] = None
    address: Optional[str] = None
    contact_persons: Optional[list] = None
    procurement_org: Optional[str] = None
    procurement_group: Optional[str] = None
    notes: Optional[str] = None


class ExcelRequirements(BaseModel):
    condition: Optional[str] = None
    warranty_months: Optional[int] = None
    warranty_start: Optional[str] = None
    analog_allowed: Optional[bool] = None
    analog_rules: Optional[str] = None
    import_substitution_required: Optional[bool] = None
    import_substitution_registry: Optional[str] = None
    origin_restrictions: Optional[str] = None
    notes: Optional[str] = None


class ExcelPaymentTerms(BaseModel):
    description: Optional[str] = None
    type: Optional[str] = None
    advance_pct: Optional[float] = None
    days_min: Optional[int] = None
    days_max: Optional[int] = None
    base_date: Optional[str] = None
    notes: Optional[str] = None


class ExcelIncoterms(BaseModel):
    primary: Optional[str] = None
    location: Optional[str] = None
    alternative: Optional[str] = None


class ExcelPenalties(BaseModel):
    late_delivery_pct: Optional[float] = None
    late_delivery_base: Optional[str] = None
    max_penalty_pct: Optional[float] = None
    other_penalties: Optional[str] = None
    unilateral_termination: Optional[str] = None
    notes: Optional[str] = None


class ExcelSecurity(BaseModel):
    amount: Optional[float] = None
    form: Optional[str] = None


class ExcelFinancials(BaseModel):
    nmck: Optional[float] = None
    bid_security: Optional[ExcelSecurity] = None
    contract_security: Optional[ExcelSecurity] = None
    auction_step: Optional[float] = None
    currencies: Optional[List[str]] = None
    base_currency: Optional[str] = None
    vat_rate: Optional[float] = None
    prices_include_vat: Optional[bool] = None
    payment_terms: Optional[ExcelPaymentTerms] = None
    incoterms: Optional[ExcelIncoterms] = None
    penalties: Optional[ExcelPenalties] = None
    notes: Optional[str] = None


class ExcelDates(BaseModel):
    publication_date: Optional[str] = None
    submission_deadline: Optional[str] = None
    submission_time: Optional[str] = None
    submission_timezone: Optional[str] = None
    opening_date: Optional[str] = None
    opening_time: Optional[str] = None
    results_date: Optional[str] = None
    clarification_request_deadline: Optional[str] = None
    delivery_start: Optional[str] = None
    delivery_end: Optional[str] = None
    early_delivery_allowed: Optional[bool] = None
    notes: Optional[str] = None


class ExcelData(BaseModel):
    general: Optional[ExcelGeneral] = None
    items: List[ExcelItem] = Field(default_factory=list)
    customer: Optional[ExcelCustomer] = None
    requirements: Optional[ExcelRequirements] = None
    financials: Optional[ExcelFinancials] = None
    dates: Optional[ExcelDates] = None


def create_excel_data(extraction_result: dict) -> Optional[ExcelData]:
    if not extraction_result:
        return None

    general_data = extraction_result.get("general", {})
    procurement_items = extraction_result.get("procurement_items", [])
    parties = extraction_result.get("parties", {})
    product_requirements = extraction_result.get("product_requirements", {})
    financials = extraction_result.get("financials", {})
    dates = extraction_result.get("dates", {})

    excel_general = None
    if general_data:
        excel_general = ExcelGeneral(
            name=general_data.get("name"),
            method=general_data.get("method"),
            notes=general_data.get("notes"),
        )

    excel_items = []
    for item in procurement_items:
        excel_items.append(
            ExcelItem(
                position=item.get("position"),
                name=item.get("name"),
                article=item.get("article"),
                manufacturer=item.get("manufacturer"),
                qty=item.get("qty"),
                unit=item.get("unit"),
                npp=item.get("npp"),
                category=item.get("category"),
                unit_price=item.get("unit_price"),
                currency=item.get("currency"),
                delivery_date=item.get("delivery_date"),
                delivery_location=item.get("delivery_location"),
                analog_allowed=item.get("analog_allowed"),
                original_reference=item.get("original_reference"),
                linked_service=item.get("linked_service"),
                source=item.get("source"),
                notes=item.get("notes"),
            )
        )

    customer_data = parties.get("customer") if parties else None
    excel_customer = None
    if customer_data:
        excel_customer = ExcelCustomer(
            name=customer_data.get("name"),
            full_name=customer_data.get("full_name"),
            inn=customer_data.get("inn"),
            kpp=customer_data.get("kpp"),
            address=customer_data.get("address"),
            contact_persons=customer_data.get("contact_persons"),
            procurement_org=customer_data.get("procurement_org"),
            procurement_group=customer_data.get("procurement_group"),
            notes=customer_data.get("notes"),
        )

    excel_requirements = None
    if product_requirements:
        excel_requirements = ExcelRequirements(
            condition=product_requirements.get("condition"),
            warranty_months=product_requirements.get("warranty_months"),
            warranty_start=product_requirements.get("warranty_start"),
            analog_allowed=product_requirements.get("analog_allowed"),
            analog_rules=product_requirements.get("analog_rules"),
            import_substitution_required=product_requirements.get(
                "import_substitution_required"
            ),
            import_substitution_registry=product_requirements.get(
                "import_substitution_registry"
            ),
            origin_restrictions=product_requirements.get("origin_restrictions"),
            notes=product_requirements.get("notes"),
        )

    excel_financials = None
    if financials:
        bid_security = financials.get("bid_security")
        contract_security = financials.get("contract_security")
        payment_terms = financials.get("payment_terms")
        incoterms = financials.get("incoterms")
        penalties = financials.get("penalties")

        excel_financials = ExcelFinancials(
            nmck=financials.get("nmck"),
            bid_security=ExcelSecurity(
                amount=bid_security.get("amount") if bid_security else None,
                form=bid_security.get("form") if bid_security else None,
            )
            if bid_security
            else None,
            contract_security=ExcelSecurity(
                amount=contract_security.get("amount") if contract_security else None,
                form=contract_security.get("form") if contract_security else None,
            )
            if contract_security
            else None,
            auction_step=financials.get("auction_step"),
            currencies=financials.get("currencies"),
            base_currency=financials.get("base_currency"),
            vat_rate=financials.get("vat_rate"),
            prices_include_vat=financials.get("prices_include_vat"),
            payment_terms=ExcelPaymentTerms(
                description=payment_terms.get("description") if payment_terms else None,
                type=payment_terms.get("type") if payment_terms else None,
                advance_pct=payment_terms.get("advance_pct") if payment_terms else None,
                days_min=payment_terms.get("days_min") if payment_terms else None,
                days_max=payment_terms.get("days_max") if payment_terms else None,
                base_date=payment_terms.get("base_date") if payment_terms else None,
                notes=payment_terms.get("notes") if payment_terms else None,
            )
            if payment_terms
            else None,
            incoterms=ExcelIncoterms(
                primary=incoterms.get("primary") if incoterms else None,
                location=incoterms.get("location") if incoterms else None,
                alternative=incoterms.get("alternative") if incoterms else None,
            )
            if incoterms
            else None,
            penalties=ExcelPenalties(
                late_delivery_pct=penalties.get("late_delivery_pct")
                if penalties
                else None,
                late_delivery_base=penalties.get("late_delivery_base")
                if penalties
                else None,
                max_penalty_pct=penalties.get("max_penalty_pct") if penalties else None,
                other_penalties=penalties.get("other_penalties") if penalties else None,
                unilateral_termination=penalties.get("unilateral_termination")
                if penalties
                else None,
                notes=penalties.get("notes") if penalties else None,
            )
            if penalties
            else None,
            notes=financials.get("notes"),
        )

    excel_dates = None
    if dates:
        excel_dates = ExcelDates(
            publication_date=dates.get("publication_date"),
            submission_deadline=dates.get("submission_deadline"),
            submission_time=dates.get("submission_time"),
            submission_timezone=dates.get("submission_timezone"),
            opening_date=dates.get("opening_date"),
            opening_time=dates.get("opening_time"),
            results_date=dates.get("results_date"),
            clarification_request_deadline=dates.get("clarification_request_deadline"),
            delivery_start=dates.get("delivery_start"),
            delivery_end=dates.get("delivery_end"),
            early_delivery_allowed=dates.get("early_delivery_allowed"),
            notes=dates.get("notes"),
        )

    return ExcelData(
        general=excel_general,
        items=excel_items,
        customer=excel_customer,
        requirements=excel_requirements,
        financials=excel_financials,
        dates=excel_dates,
    )
