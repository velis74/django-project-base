from main.rest_df.internal_mail.services.save_to_internal_mail_storage_service_base import \
    SaveToInternalMailStorageServiceBase


class SaveToInternalMailStorageService(SaveToInternalMailStorageServiceBase):
    """Concrete class for saving InternalMail(main/internal_mail/internal_mail.py)
    object to storage"""

    def save(self, email_data: dict) -> int:
        """Save InternalMail object to storage"""
        return super().save(email_data)
