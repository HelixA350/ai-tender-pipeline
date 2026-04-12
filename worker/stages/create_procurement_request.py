import logging

logger = logging.getLogger(__name__)


class CreateProcurementRequestStage:
    """Create procurement request in procurement department"""

    async def execute(self, context):
        from worker.schemas.excel_data import create_excel_data
        from worker.excel_generator import create_excel_file
        from worker.storage import save_file_to_minio, generate_presigned_url

        excel_data = create_excel_data(context.extraction_result)

        excel_bytes = create_excel_file(excel_data)

        bucket_name = context.task_id
        filename = "zakupka.xlsx"
        save_file_to_minio(bucket_name, filename, excel_bytes)

        presigned_url = generate_presigned_url(bucket_name, filename, expires=600)

        context.procurement_request_url = presigned_url
        logger.info(
            f"Created procurement request for task {context.task_id}: {presigned_url}"
        )
