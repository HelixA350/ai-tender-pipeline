import logging

logger = logging.getLogger(__name__)


class CreateProcurementRequestStage:
    """Create procurement request in procurement department"""

    async def execute(self, context):
        from worker.schemas.excel_data import create_excel_data
        from worker.excel_generator import create_excel_file
        from worker.storage import save_file

        excel_data = create_excel_data(context.extraction_result)
        context.excel_data = excel_data

        excel_bytes = create_excel_file(excel_data)

        filename = f"{context.task_id}.xlsx"
        save_file(filename, excel_bytes)

        context.procurement_request_url = f"/tenders/download/{context.task_id}"
        logger.info(f"Created procurement request for task {context.task_id}")
