const fieldNames = {
    tender_id: 'Номер тендера',
    external_id: 'Внешний ID',
    source: 'Источник данных',
    name: 'Наименование',
    method: 'Способ закупки',
    status: 'Статус',
    platform: 'Площадка',
    platform_url: 'URL площадки',
    lot_divisible: 'Лот делимый',
    rebidding_allowed: 'Переторг разрешён',
    notes: 'Заметки',
    customer: 'Заказчик',
    supplier: 'Поставщик',
    full_name: 'Полное наименование',
    inn: 'ИНН',
    kpp: 'КПП',
    address: 'Адрес',
    contact_persons: 'Контактные лица',
    procurement_org: 'Закупочная организация',
    procurement_group: 'Группа закупок',
    publication_date: 'Дата публикации',
    submission_deadline: 'Крайний срок подачи',
    submission_time: 'Время подачи',
    submission_timezone: 'Часовой пояс',
    opening_date: 'Дата вскрытия',
    opening_time: 'Время вскрытия',
    results_date: 'Дата подведения итогов',
    clarification_request_deadline: 'Срок подачи запросов на разъяснения',
    delivery_start: 'Начало поставки',
    delivery_end: 'Окончание поставки',
    early_delivery_allowed: 'Досрочная поставка',
    nmck: 'НМЦК',
    bid_security: 'Обеспечение заявки',
    contract_security: 'Обеспечение контракта',
    auction_step: 'Шаг аукциона',
    currencies: 'Валюты',
    base_currency: 'Базовая валюта',
    vat_rate: 'Ставка НДС',
    prices_include_vat: 'Цены с НДС',
    payment_terms: 'Условия оплаты',
    incoterms: 'Incoterms',
    penalties: 'Штрафы',
    position: 'Позиция',
    article: 'Артикул',
    manufacturer: 'Производитель',
    qty: 'Количество',
    unit: 'Единица измерения',
    npp: 'Код НПП',
    category: 'Категория',
    unit_price: 'Цена за единицу',
    currency: 'Валюта',
    delivery_date: 'Срок поставки',
    delivery_location: 'Место поставки',
    analog_allowed: 'Допускается аналог',
    original_reference: 'Оригинальная ссылка',
    linked_service: 'Связанная услуга',
    source_files: 'Исходные файлы',
    tender_types: 'Типы тендера',
    package_comments: 'Комментарии к пакету',
    filename: 'Имя файла',
    file_type: 'Тип файла',
    description: 'Описание',
    role: 'Должность/роль',
    phone: 'Телефон',
    email: 'Email',
    amount: 'Сумма',
    form: 'Форма',
    total_positions: 'Всего позиций',
    total_qty_units: 'Всего единиц',
    price_filled: 'Цены заполнены',
    manufacturers_unique: 'Уникальные производители',
    is_single_manufacturer: 'Единственный производитель',
    condition: 'Состояние',
    warranty_months: 'Гарантийный срок (мес.)',
    warranty_start: 'Начало гарантии',
    analog_rules: 'Правила аналогов',
    import_substitution_required: 'Требуется импортозамещение',
    import_substitution_registry: 'Реестр импортозамещения',
    origin_restrictions: 'Ограничения по происхождению',
    location: 'Место',
    equipment_types: 'Типы оборудования',
    access_conditions: 'Условия доступа',
    pass_lead_time_days: 'Срок оформления пропуска (дни)',
    work_schedule: 'Режим работы',
    min_headcount: 'Мин. численность',
    certifications_required: 'Требуемые удостоверения',
    sro_required: 'Требуется СРО',
    sro_type: 'Тип СРО',
    experience_years: 'Опыт (лет)',
    equipment_provided_by_customer: 'Оборудование от заказчика',
    equipment_required: 'Требуемое оборудование',
    travel_included: 'Командировочные включены',
    travel_reimbursement: 'Возмещение командировочных',
    acceptance_documents: 'Приёмочные документы',
    schedule_approval_required: 'Требуется согласование графика',
    object_description: 'Описание объекта',
    original_item_provided: 'Оригинал предоставлен',
    access_location: 'Адрес доступа',
    access_duration_days: 'Срок доступа (дни)',
    provided_documents: 'Предоставленные документы',
    design_stages_required: 'Требуемые стадии КД',
    output_documents: 'Выходные документы',
    materials_customer_supplied: 'Материалы заказчика',
    gost_required: 'Требуется ГОСТ',
    prototype_required: 'Требуется прототип',
    series_qty: 'Количество серийных',
    test_bench_customer: 'Испытательный стенд заказчика',
    test_program_required: 'Требуется программа испытаний',
    acceptance_location: 'Место приёмки',
    acceptance_committee: 'Приёмочная комиссия',
    ip_transfers_to_customer: 'ИС передаётся заказчику',
    replication_allowed: 'Разрешено тиражирование',
    copies: 'Количество экземпляров',
    format: 'Формат',
    licenses_required: 'Требуемые лицензии',
    experience_requirements: 'Требования к опыту',
    other_requirements: 'Прочие требования',
    platform_name: 'Название площадки',
    submission_method: 'Способ подачи',
    required_docs: 'Требуемые документы',
    form_rules: 'Правила заполнения форм',
    special_notes: 'Особые заметки',
    submission_deadline_rule: 'Срок подачи',
    amendments_until: 'Внесение изменений до',
    withdrawal_rules: 'Правила отзыва',
    stage: 'Этап',
    format_required: 'Требуемый формат',
    restrictions: 'Ограничения',
    requirements: 'Требования',
    template_provided: 'Шаблон предоставлен',
    template_url: 'URL шаблона',
    special_requirements: 'Особые требования',
    customer_industry: 'Отрасль заказчика',
    customer_region: 'Регион заказчика',
    order_complexity: 'Сложность заказа',
    order_complexity_reason: 'Обоснование сложности',
    brand_lock: 'Привязка к бренду',
    import_substitution_risk: 'Риск импортозамещения',
    import_substitution_risk_reason: 'Причина риска импортозамещения',
    lot_partial_participation: 'Частичное участие',
    penalty_risk: 'Риск штрафов',
    penalty_risk_reason: 'Причина риска штрафов',
    late_delivery_pct: 'Пеня за просрочку (%)',
    late_delivery_base: 'База начисления пени',
    max_penalty_pct: 'Макс. штраф (%)',
    other_penalties: 'Прочие штрафы',
    unilateral_termination: 'Одностороннее расторжение',
    primary: 'Основной',
    alternative: 'Альтернативный',
    advance_pct: 'Аванс (%)',
    days_min: 'Мин. срок (дни)',
    days_max: 'Макс. срок (дни)',
    base_date: 'База отсчёта',
    special_note: 'Особое примечание',
    id: 'ID',
    volume: 'Объём',
    works: 'Работы'
};

const sectionTitles = {
    meta: 'Метаинформация',
    identification: 'Идентификация',
    summary: 'Семантическая сводка',
    general: 'Общая информация',
    parties: 'Стороны',
    dates: 'Даты и сроки',
    financials: 'Финансовые условия',
    procurement_items: 'Позиции закупки',
    special_items: 'Специальные позиции',
    items_summary: 'Сводка по позициям',
    product_requirements: 'Требования к товару',
    service_scope: 'Сервисные работы',
    engineering_scope: 'Инжиниринг',
    participant_requirements: 'Требования к участнику',
    submission_documents: 'Документы для подачи',
    scoring_signals: 'Сигналы оценки'
};

const statusTexts = {
    pending: 'Ожидание запуска',
    processing: 'Обработка...',
    completed: 'Завершено',
    failed: 'Ошибка'
};

function getFieldName(key) {
    if (sectionTitles[key]) return sectionTitles[key];
    if (fieldNames[key]) return fieldNames[key];
    return key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
}

function isEmptyValue(value) {
    if (value === null || value === undefined) return true;
    if (typeof value === 'string' && value.trim() === '') return true;
    if (Array.isArray(value) && value.length === 0) return true;
    return false;
}

function formatValue(value) {
    if (isEmptyValue(value)) {
        return '<span class="json-value empty">Не указано</span>';
    }
    if (typeof value === 'boolean') {
        return `<span class="json-value ${value ? 'bool-true' : 'bool-false'}">${value ? 'Да' : 'Нет'}</span>`;
    }
    if (typeof value === 'number') {
        if (value > 1000) {
            return `<span class="json-value">${value.toLocaleString('ru-RU')}</span>`;
        }
        return `<span class="json-value">${value}</span>`;
    }
    return `<span class="json-value">${String(value)}</span>`;
}

function renderKeyValue(key, value, isListItem = false) {
    const name = getFieldName(key);
    const valueStr = formatValue(value);
    
    if (isListItem) {
        return `
            <div class="json-list-item">
                ${value !== null && typeof value === 'object' ? renderObject(value, name) : `<div class="json-list-item-header">${name}: ${valueStr}</div>`}
            </div>
        `;
    }
    
    return `
        <div class="json-key-value">
            <span class="json-key">${name}</span>
            <span class="json-value">${valueStr}</span>
        </div>
    `;
}

function renderObject(obj, title = null) {
    if (!obj || typeof obj !== 'object') {
        return formatValue(obj);
    }

    if (Array.isArray(obj)) {
        if (obj.length === 0) {
            return '<div class="json-value empty">Не указано</div>';
        }
        const items = obj.map((item, index) => {
            if (typeof item === 'object' && item !== null) {
                return renderObject(item, `Позиция ${index + 1}`);
            }
            return `<div class="json-list-item">${formatValue(item)}</div>`;
        }).join('');
        return `<div class="json-list">${items}</div>`;
    }

    const entries = Object.entries(obj).filter(([_, v]) => !isEmptyValue(v));
    
    if (entries.length === 0) {
        return '<div class="json-value empty">Не указано</div>';
    }

    let html = '';
    
    if (title) {
        html += `<div class="json-section-header">${title}</div>`;
    }
    
    html += '<div class="json-nested">';
    
    for (const [key, value] of entries) {
        if (typeof value === 'object' && value !== null) {
            html += `<div class="json-section">`;
            html += `<div class="json-section-header">${getFieldName(key)}</div>`;
            html += renderObject(value);
            html += '</div>';
        } else {
            html += renderKeyValue(key, value);
        }
    }
    
    html += '</div>';
    
    return html;
}

function renderResultJson(resultJson) {
    const viewer = document.getElementById('jsonViewer');
    viewer.innerHTML = '';
    
    if (!resultJson || typeof resultJson !== 'object') {
        viewer.innerHTML = '<div class="json-value empty">Данные отсутствуют</div>';
        return;
    }

    for (const [section, data] of Object.entries(resultJson)) {
        if (isEmptyValue(data)) continue;
        
        const sectionDiv = document.createElement('div');
        sectionDiv.className = 'json-section';
        sectionDiv.innerHTML = renderObject(data, getFieldName(section));
        viewer.appendChild(sectionDiv);
    }
}

function showSection(sectionId, show = true) {
    const section = document.getElementById(sectionId);
    if (section) {
        section.hidden = !show;
    }
}

function showError(message) {
    showSection('progressSection', false);
    showSection('resultSection', true);
    showSection('downloadCard', false);
    showSection('accordionContent', false);
    document.getElementById('errorCard').hidden = false;
    document.getElementById('errorMessage').textContent = message;
    document.getElementById('submitBtn').disabled = false;
}

function showResults(data) {
    showSection('progressSection', false);
    showSection('resultSection', true);
    showSection('errorCard', false);
    document.getElementById('submitBtn').disabled = false;
    
    if (data.summary_text) {
        document.getElementById('summaryContent').textContent = data.summary_text;
    }
    
    if (data.procurement_request_url) {
        document.getElementById('downloadCard').hidden = false;
        document.getElementById('downloadLink').href = data.procurement_request_url;
    } else {
        document.getElementById('downloadCard').hidden = true;
    }
    
    if (data.result_json) {
        renderResultJson(data.result_json);
    }
}

function updateProgress(status, stage) {
    const statusText = document.getElementById('statusText');
    const stageText = document.getElementById('stageText');
    
    statusText.textContent = statusTexts[status] || status;
    stageText.textContent = stage || '';
}

let pollingInterval = null;

async function pollTask(taskId) {
    try {
        const response = await fetch(`/tenders/extraction/${taskId}`);
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка запроса');
        }
        
        const data = await response.json();
        
        updateProgress(data.status, data.current_stage);
        
        if (data.status === 'completed') {
            clearInterval(pollingInterval);
            showResults(data);
        } else if (data.status === 'failed') {
            clearInterval(pollingInterval);
            showError(data.error_message || 'Произошла неизвестная ошибка');
        }
        
    } catch (error) {
        clearInterval(pollingInterval);
        showError(error.message);
    }
}

async function submitForm(event) {
    event.preventDefault();
    
    const tenderId = document.getElementById('tenderId').value.trim();
    const archiveUrl = document.getElementById('archiveUrl').value.trim();
    
    if (!tenderId || !archiveUrl) {
        return;
    }
    
    const submitBtn = document.getElementById('submitBtn');
    submitBtn.disabled = true;
    
    showSection('progressSection', true);
    showSection('resultSection', false);
    updateProgress('pending', '');
    
    try {
        const response = await fetch('/tenders/extraction', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                tender_id: tenderId,
                archive_url: archiveUrl
            })
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Ошибка при создании задачи');
        }
        
        const data = await response.json();
        const taskId = data.id;
        
        updateProgress('processing', 'Инициализация...');
        
        pollingInterval = setInterval(() => pollTask(taskId), 3000);
        
        pollTask(taskId);
        
    } catch (error) {
        showError(error.message);
    }
}

document.getElementById('uploadForm').addEventListener('submit', submitForm);

document.getElementById('accordionToggle').addEventListener('click', function() {
    const card = this.closest('.accordion-card');
    const content = document.getElementById('accordionContent');
    
    card.classList.toggle('open');
    content.hidden = !card.classList.contains('open');
});