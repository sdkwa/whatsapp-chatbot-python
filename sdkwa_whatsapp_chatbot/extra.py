"""Extra module for additional message options."""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class ExtraOptions:
    """Extra options for messages."""

    # Message options
    quoted_message_id: Optional[str] = None
    link_preview: bool = True

    # File options
    file_name: Optional[str] = None
    caption: Optional[str] = None

    # Location options
    name_location: Optional[str] = None
    address: Optional[str] = None

    # Contact options
    phone_contact: Optional[str] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    company: Optional[str] = None

    # Additional options
    custom_options: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        result = {}

        if self.quoted_message_id:
            result["quoted_message_id"] = self.quoted_message_id

        if not self.link_preview:
            result["link_preview"] = self.link_preview

        if self.file_name:
            result["file_name"] = self.file_name

        if self.caption:
            result["caption"] = self.caption

        if self.name_location:
            result["name_location"] = self.name_location

        if self.address:
            result["address"] = self.address

        if self.phone_contact:
            result["phone_contact"] = self.phone_contact

        if self.first_name:
            result["first_name"] = self.first_name

        if self.last_name:
            result["last_name"] = self.last_name

        if self.company:
            result["company"] = self.company

        # Add custom options
        result.update(self.custom_options)

        return result


class Extra:
    """Factory class for creating extra options."""

    @staticmethod
    def reply_to(message_id: str) -> ExtraOptions:
        """Create extra options for replying to a message."""
        return ExtraOptions(quoted_message_id=message_id)

    @staticmethod
    def no_link_preview() -> ExtraOptions:
        """Create extra options to disable link preview."""
        return ExtraOptions(link_preview=False)

    @staticmethod
    def with_caption(caption: str) -> ExtraOptions:
        """Create extra options with caption."""
        return ExtraOptions(caption=caption)

    @staticmethod
    def with_filename(filename: str) -> ExtraOptions:
        """Create extra options with filename."""
        return ExtraOptions(file_name=filename)

    @staticmethod
    def location(name: str, address: str = "") -> ExtraOptions:
        """Create extra options for location."""
        return ExtraOptions(name_location=name, address=address)

    @staticmethod
    def contact(
        phone: str, first_name: str, last_name: str = "", company: str = ""
    ) -> ExtraOptions:
        """Create extra options for contact."""
        return ExtraOptions(
            phone_contact=phone,
            first_name=first_name,
            last_name=last_name or None,
            company=company or None,
        )

    @staticmethod
    def custom(**kwargs) -> ExtraOptions:
        """Create extra options with custom parameters."""
        return ExtraOptions(custom_options=kwargs)

    @staticmethod
    def combine(*extras: ExtraOptions) -> ExtraOptions:
        """Combine multiple extra options."""
        combined = ExtraOptions()

        for extra in extras:
            if extra.quoted_message_id:
                combined.quoted_message_id = extra.quoted_message_id

            if not extra.link_preview:
                combined.link_preview = extra.link_preview

            if extra.file_name:
                combined.file_name = extra.file_name

            if extra.caption:
                combined.caption = extra.caption

            if extra.name_location:
                combined.name_location = extra.name_location

            if extra.address:
                combined.address = extra.address

            if extra.phone_contact:
                combined.phone_contact = extra.phone_contact

            if extra.first_name:
                combined.first_name = extra.first_name

            if extra.last_name:
                combined.last_name = extra.last_name

            if extra.company:
                combined.company = extra.company

            combined.custom_options.update(extra.custom_options)

        return combined


# Convenience functions for common use cases
def reply_to(message_id: str) -> ExtraOptions:
    """Create extra options for replying to a message."""
    return Extra.reply_to(message_id)


def no_link_preview() -> ExtraOptions:
    """Create extra options to disable link preview."""
    return Extra.no_link_preview()


def with_caption(caption: str) -> ExtraOptions:
    """Create extra options with caption."""
    return Extra.with_caption(caption)


def with_filename(filename: str) -> ExtraOptions:
    """Create extra options with filename."""
    return Extra.with_filename(filename)
