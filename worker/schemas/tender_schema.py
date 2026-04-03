from typing import Optional, List, Literal
from pydantic import BaseModel, Field


class TenderSchema(BaseModel):
    _meta: "MetaInfo"
    tender_id: str
    tender_types: List[str]
    identification: "Identification"
    general: "GeneralInfo"
    parties: "Parties"
    dates: "Dates"
    financials: "Financials"
    procurement_items: List["ProcurementItem"]
    special_items: Optional[List["SpecialItem"]] = None
    items_summary: "ItemsSummary"
    product_requirements: "ProductRequirements"
    service_scope: Optional["ServiceScope"] = None
    engineering_scope: Optional["EngineeringScope"] = None
    participant_requirements: Optional["ParticipantRequirements"] = None
    submission_documents: Optional["SubmissionRequirements"] = None
    scoring_signals: Optional["ScoringSignals"] = None


class SourceFile(BaseModel):
    filename: str = Field(description="Имя файла")
    file_type: str = Field(
        description="Тип: 'ТЗ', 'спецификация', 'КП', 'чертеж', 'договор'...",
    )
    description: str = Field(description="Краткое описание что в файле")


class MetaInfo(BaseModel):
    source_files: List[SourceFile] = Field(description="Список исходных файлов с описанием и типами")
    tender_types: List[Literal['закупка', 'сервис', 'реинж']] = Field(
        description="Типы тендера: 'закупка', 'сервис', 'реинж'. "
        "Определяет какие блоки заполнять."
    )
    package_comments: Optional[str] = Field(
        description="Свободный комментарий: что есть в пакете, чего не хватает",
        default=None,
    )


class Identification(BaseModel):
    tender_id: Optional[str] = Field(
        description="Номер тендера / реестровый номер", default=None
    )
    external_id: Optional[str] = Field(
        description="ID на торговой площадке (если отличается)", default=None
    )
    source: Optional[str] = Field(
        description="Источник данных: файл, система", default=None
    )


class GeneralInfo(BaseModel):
    name: Optional[str] = Field(description="Наименование тендера", default=None)
    method: Optional[str] = Field(
        description="Способ закупки: 'запрос предложений', 'конкурс', 'аукцион', 'запрос котировок'...",
        default=None,
    )
    status: Optional[str] = Field(
        description="Статус: 'active', 'closed', 'cancelled', 'pre_active'",
        default=None,
    )
    platform: Optional[str] = Field(
        description="Название площадки: 'SAP SRM', 'ЭТП ГПБ', 'Tender.Pro'...",
        default=None,
    )
    platform_url: Optional[str] = Field(description="URL площадки", default=None)
    lot_divisible: Optional[bool] = Field(
        description="Можно ли участвовать частично по позициям", default=None
    )
    rebidding_allowed: Optional[bool] = Field(
        description="Возможен ли переторг", default=None
    )
    notes: Optional[str] = Field(
        description="Свободное поле: прочие особенности", default=None
    )


class PartyContact(BaseModel):
    name: Optional[str] = None
    role: Optional[str] = Field(description="Должность / роль", default=None)
    phone: Optional[str] = None
    email: Optional[str] = None


class Party(BaseModel):
    name: Optional[str] = Field(description="Наименование организации", default=None)
    full_name: Optional[str] = Field(description="Полное наименование", default=None)
    inn: Optional[str] = None
    kpp: Optional[str] = None
    address: Optional[str] = None
    contact_persons: Optional[List[PartyContact]] = Field(
        description="Контактные лица", default=None
    )
    procurement_org: Optional[str] = Field(
        description="Закупочная организация (для SAP SRM)", default=None
    )
    procurement_group: Optional[str] = Field(
        description="Группа закупок (для SAP SRM)", default=None
    )
    notes: Optional[str] = Field(description="Свободное поле", default=None)


class Parties(BaseModel):
    customer: Party = Field(description="Заказчик / инициатор закупки")
    notes: Optional[str] = None


class Dates(BaseModel):
    publication_date: Optional[str] = Field(
        description="Дата публикации YYYY-MM-DD", default=None
    )
    submission_deadline: Optional[str] = Field(
        description="Крайний срок подачи YYYY-MM-DD", default=None
    )
    submission_time: Optional[str] = Field(description="Время HH:MM:SS", default=None)
    submission_timezone: Optional[str] = Field(
        description="Часовой пояс: 'UTC+8', 'Europe/Moscow', 'МСК+5'...", default=None
    )
    opening_date: Optional[str] = Field(
        description="Дата вскрытия YYYY-MM-DD", default=None
    )
    opening_time: Optional[str] = None
    results_date: Optional[str] = Field(
        description="Дата подведения итогов YYYY-MM-DD", default=None
    )
    clarification_request_deadline: Optional[str] = Field(
        description="Срок подачи запросов на разъяснения YYYY-MM-DD", default=None
    )
    delivery_start: Optional[str] = Field(
        description="Начало поставки YYYY-MM-DD", default=None
    )
    delivery_end: Optional[str] = Field(
        description="Окончание поставки YYYY-MM-DD", default=None
    )
    early_delivery_allowed: Optional[bool] = Field(
        description="Допускается ли досрочная поставка", default=None
    )
    notes: Optional[str] = Field(description="Свободное поле", default=None)


class PaymentTerms(BaseModel):
    description: Optional[str] = Field(description="Текстовое описание", default=None)
    type: Optional[str] = Field(
        description="Тип: 'по факту', 'аванс', 'поэтапная', 'предоплата'...",
        default=None,
    )
    advance_pct: Optional[float] = Field(description="Процент аванса", default=None)
    days_min: Optional[int] = Field(
        description="Минимальный срок оплаты в днях", default=None
    )
    days_max: Optional[int] = Field(
        description="Максимальный срок оплаты в днях", default=None
    )
    base_date: Optional[str] = Field(
        description="База отсчёта: 'PPPS', 'дата поставки', 'дата счёта'...",
        default=None,
    )
    notes: Optional[str] = None


class Incoterms(BaseModel):
    primary: Optional[str] = Field(
        description="Основной Incoterms: DDP, DAP, FCA, EXW...", default=None
    )
    location: Optional[str] = Field(description="Место / город", default=None)
    alternative: Optional[str] = Field(
        description="Альтернативный базис (если есть)", default=None
    )


class Penalties(BaseModel):
    late_delivery_pct: Optional[float] = Field(
        description="Процент пени за просрочку поставки", default=None
    )
    late_delivery_base: Optional[str] = Field(
        description="База начисления", default=None
    )
    max_penalty_pct: Optional[float] = Field(
        description="Максимальный размер штрафа в %", default=None
    )
    other_penalties: Optional[str] = Field(description="Прочие штрафы", default=None)
    unilateral_termination: Optional[str] = Field(
        description="Условия одностороннего расторжения", default=None
    )
    notes: Optional[str] = None


class Security(BaseModel):
    amount: Optional[float] = None
    form: Optional[str] = Field(
        description="Форма: 'банковская гарантия', 'денежный залог'...", default=None
    )


class Financials(BaseModel):
    nmck: Optional[float] = Field(
        description="Начальная (максимальная) цена контракта", default=None
    )
    bid_security: Optional[Security] = Field(
        description="Обеспечение заявки", default=None
    )
    contract_security: Optional[Security] = Field(
        description="Обеспечение контракта", default=None
    )
    auction_step: Optional[float] = Field(description="Шаг аукциона", default=None)
    currencies: Optional[List[str]] = Field(
        description="Допустимые валюты: ['RUB', 'USD', 'EUR']", default=None
    )
    base_currency: Optional[str] = Field(description="Базовая валюта", default=None)
    vat_rate: Optional[float] = Field(description="Ставка НДС (0.20)", default=None)
    prices_include_vat: Optional[bool] = Field(
        description="Цены указаны с НДС", default=None
    )
    payment_terms: Optional[PaymentTerms] = None
    incoterms: Optional[Incoterms] = None
    penalties: Optional[Penalties] = None
    notes: Optional[str] = Field(description="Свободное поле", default=None)


class ProcurementItem(BaseModel):
    position: int = Field(description="Порядковый номер позиции")
    name: str = Field(description="Полное наименование (не сокращать)")
    article: Optional[str] = Field(description="Партномер / артикул OEM", default=None)
    manufacturer: Optional[str] = Field(description="Производитель", default=None)
    qty: float = Field(description="Количество")
    unit: str = Field(description="Единица измерения: ШТ, М, КГ, Л...")
    npp: Optional[str] = Field(description="Код НПП / МТР заказчика", default=None)
    category: Optional[str] = Field(
        description="Категория / группа товара", default=None
    )
    unit_price: Optional[float] = Field(description="Цена за единицу", default=None)
    currency: Optional[str] = Field(description="Валюта цены", default=None)
    delivery_date: Optional[str] = Field(
        description="Срок поставки YYYY-MM-DD", default=None
    )
    delivery_location: Optional[str] = Field(description="Место поставки", default=None)
    analog_allowed: Optional[bool] = Field(
        description="Допускается ли аналог / эквивалент", default=None
    )
    original_reference: Optional[str] = Field(
        description="Ссылка на оригинал: год, номер в заявке...", default=None
    )
    linked_service: Optional[str] = Field(
        description="ID связанной услуги (ШМР/ПНР) — заполнять если тип 'сервис'",
        default=None,
    )
    source: Optional[str] = Field(description="Файл-источник", default=None)
    notes: Optional[str] = Field(description="Свободное поле", default=None)


class SpecialItem(BaseModel):
    position: int
    name: str
    article: Optional[str] = None
    manufacturer: Optional[str] = None
    qty: float
    unit: str
    npp: Optional[str] = None
    unit_price: Optional[float] = None
    currency: Optional[str] = None
    delivery_date: Optional[str] = None
    delivery_location: Optional[str] = None
    analog_allowed: Optional[bool] = None
    special_note: str = Field(
        description="Описание отличия: 'требует поставки в сборе', "
        "'отдельное ТЗ приложено', 'нестандартный срок'..."
    )
    source: Optional[str] = None
    notes: Optional[str] = None


class ItemsSummary(BaseModel):
    total_positions: Optional[int] = None
    total_qty_units: Optional[float] = Field(description="Сумма всех qty", default=None)
    price_filled: Optional[bool] = Field(
        description="Заполнены ли цены в форме", default=None
    )
    manufacturers_unique: Optional[List[str]] = Field(
        description="Уникальные производители", default=None
    )
    is_single_manufacturer: Optional[bool] = Field(
        description="Все позиции от одного производителя", default=None
    )


class ProductRequirements(BaseModel):
    condition: Optional[str] = Field(
        description="Состояние: 'новый', 'б/у', 'не указано'", default=None
    )
    warranty_months: Optional[int] = Field(
        description="Гарантийный срок в месяцах", default=None
    )
    warranty_start: Optional[str] = Field(
        description="Точка отсчёта: 'с даты поставки', 'с ввода в эксплуатацию'...",
        default=None,
    )
    analog_allowed: Optional[bool] = Field(
        description="Допустимость эквивалентов", default=None
    )
    analog_rules: Optional[str] = Field(
        description="Правила замены партномера", default=None
    )
    import_substitution_required: Optional[bool] = Field(
        description="Требуется ли импортозамещение", default=None
    )
    import_substitution_registry: Optional[str] = Field(
        description="Ссылка на реестр: КТРУ, ПП-719...", default=None
    )
    origin_restrictions: Optional[str] = Field(
        description="Ограничения по стране происхождения", default=None
    )
    notes: Optional[str] = None


class ServiceWork(BaseModel):
    id: str = Field(description="ID для связи с procurement_items.linked_service")
    name: str
    volume: Optional[float] = None
    unit: Optional[str] = None
    unit_price: Optional[float] = None


class ServiceScope(BaseModel):
    works: Optional[List[ServiceWork]] = None
    location: Optional[str] = Field(description="Место выполнения работ", default=None)
    equipment_types: Optional[List[str]] = Field(
        description="Типы оборудования для ремонта/работ", default=None
    )
    access_conditions: Optional[str] = Field(
        description="Условия доступа: пропуск, инструктаж...", default=None
    )
    pass_lead_time_days: Optional[int] = Field(
        description="Срок оформления пропуска в днях", default=None
    )
    work_schedule: Optional[str] = Field(
        description="Режим работы: 'пн-пт 08:00-17:00', 'круглосуточно'...",
        default=None,
    )
    min_headcount: Optional[int] = Field(
        description="Минимальное количество специалистов", default=None
    )
    certifications_required: Optional[List[str]] = Field(
        description="Обязательные удостоверения: ['НАКС', 'группа допуска по ЭБ III']",
        default=None,
    )
    sro_required: Optional[bool] = Field(
        description="Требуется ли членство в СРО", default=None
    )
    sro_type: Optional[str] = Field(
        description="Тип СРО: 'строительство', 'проектирование'", default=None
    )
    experience_years: Optional[int] = Field(
        description="Минимальный опыт в годах", default=None
    )
    equipment_provided_by_customer: Optional[bool] = Field(
        description="Оборудование предоставляет заказчик", default=None
    )
    equipment_required: Optional[List[str]] = Field(
        description="Оборудование которое исполнитель обязан иметь", default=None
    )
    travel_included: Optional[bool] = Field(
        description="Командировочные включены в цену", default=None
    )
    travel_reimbursement: Optional[str] = Field(
        description="Схема возмещения", default=None
    )
    acceptance_documents: Optional[List[str]] = Field(
        description="Состав сдаточного пакета: акты, протоколы...", default=None
    )
    schedule_approval_required: Optional[bool] = Field(
        description="Требуется ли согласование графика", default=None
    )
    notes: Optional[str] = None


class DesignStage(BaseModel):
    name: str
    copies: Optional[int] = None
    format: Optional[str] = Field(
        description="Формат: 'бумажный', 'электронный', 'оба'", default=None
    )


class EngineeringScope(BaseModel):
    object_description: Optional[str] = Field(
        description="Описание изделия / системы", default=None
    )
    original_item_provided: Optional[bool] = Field(
        description="Заказчик передаёт оригинальное изделие", default=None
    )
    access_location: Optional[str] = Field(
        description="Адрес для ознакомления", default=None
    )
    access_duration_days: Optional[int] = None
    provided_documents: Optional[List[str]] = Field(
        description="Документы переданные заказчиком", default=None
    )
    design_stages_required: Optional[List[str]] = Field(
        description="Стадии КД: 'эскизный проект', 'РКД'...", default=None
    )
    output_documents: Optional[List[DesignStage]] = Field(
        description="Требуемые документы на выходе", default=None
    )
    materials_customer_supplied: Optional[bool] = None
    gost_required: Optional[bool] = Field(
        description="Обязательно соответствие ГОСТ/ОСТ", default=None
    )
    prototype_required: Optional[bool] = Field(
        description="Требуется опытный образец", default=None
    )
    series_qty: Optional[int] = Field(
        description="Количество серийных изделий", default=None
    )
    test_bench_customer: Optional[bool] = Field(
        description="Испытательный стенд предоставляет заказчик", default=None
    )
    test_program_required: Optional[bool] = None
    acceptance_location: Optional[str] = None
    acceptance_committee: Optional[str] = None
    ip_transfers_to_customer: Optional[bool] = None
    replication_allowed: Optional[bool] = None
    notes: Optional[str] = None


class ParticipantRequirements(BaseModel):
    licenses_required: Optional[List[str]] = Field(
        description="Лицензии и свидетельства", default=None
    )
    sro_required: Optional[bool] = None
    sro_type: Optional[str] = None
    experience_requirements: Optional[str] = Field(
        description="Требования к опыту", default=None
    )
    origin_restrictions: Optional[str] = Field(
        description="Ограничения: 'только РФ', 'МСП'...", default=None
    )
    other_requirements: Optional[str] = Field(
        description="Прочие ограничения", default=None
    )
    notes: Optional[str] = None


class RequiredDoc(BaseModel):
    name: str
    stage: Optional[str] = Field(
        description="Этап: 'submission' (подача), 'contract' (подписание), "
        "'shipping' (отгрузка/приёмка)",
        default=None,
    )
    description: Optional[str] = Field(
        description="Что должен содержать документ", default=None
    )
    format_required: Optional[str] = Field(
        description="Формат: 'xlsx', 'pdf', 'бумажный', 'email'...", default=None
    )
    restrictions: Optional[str] = Field(
        description="Что запрещено: 'не менять формулы', 'не превышать НМЦ'...",
        default=None,
    )
    requirements: Optional[str] = Field(
        description="Что обязательно: 'все поля', 'приложить сертификат'...",
        default=None,
    )
    template_provided: Optional[bool] = None
    template_url: Optional[str] = None
    special_requirements: Optional[str] = Field(
        description="Особые условия: 'нотариус', 'ЭЦП'...", default=None
    )


class DeadlineRules(BaseModel):
    submission_deadline: Optional[str] = None
    submission_time: Optional[str] = None
    timezone: Optional[str] = None
    amendments_until: Optional[str] = Field(
        description="До какого момента можно вносить изменения", default=None
    )
    withdrawal_rules: Optional[str] = Field(
        description="Правила отзыва заявки", default=None
    )


class SubmissionRequirements(BaseModel):
    platform_name: Optional[str] = Field(description="Название площадки", default=None)
    platform_url: Optional[str] = None
    submission_method: Optional[str] = Field(
        description="Способ подачи: 'электронно', 'email', 'бумажно'...", default=None
    )
    deadline_rules: Optional[DeadlineRules] = None
    required_docs: Optional[List[RequiredDoc]] = None
    form_rules: Optional[List[str]] = Field(
        description="Общие правила заполнения форм", default=None
    )
    special_notes: Optional[str] = Field(
        description="Свободное поле: нюансы подачи", default=None
    )


class ScoringSignals(BaseModel):
    customer_industry: Optional[str] = Field(
        description="Отрасль заказчика: 'нефтегаз', 'энергетика'...", default=None
    )
    customer_region: Optional[str] = Field(
        description="Регион / город доставки", default=None
    )
    order_complexity: Optional[str] = Field(
        description="Сложность: 'низкая', 'средняя', 'высокая'", default=None
    )
    order_complexity_reason: Optional[str] = Field(
        description="Обоснование (1 предложение)", default=None
    )
    is_single_manufacturer: Optional[bool] = None
    brand_lock: Optional[str] = Field(
        description="Жёсткая привязка к бренду", default=None
    )
    import_substitution_risk: Optional[str] = Field(
        description="Риск импортозамещения: 'низкий', 'средний', 'высокий'",
        default=None,
    )
    import_substitution_risk_reason: Optional[str] = Field(
        description="Причина риска", default=None
    )
    lot_partial_participation: Optional[bool] = Field(
        description="Можно ли участвовать частично", default=None
    )
    penalty_risk: Optional[str] = Field(
        description="Риск штрафов: 'низкая', 'средняя', 'высокая'", default=None
    )
    penalty_risk_reason: Optional[str] = Field(description="Обоснование", default=None)
    notes: Optional[str] = None
