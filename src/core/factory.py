from typing import TYPE_CHECKING

from django.core.files.uploadedfile import SimpleUploadedFile

from core.test.factory import register

if TYPE_CHECKING:
    from core.test.factory import FixtureFactory


@register
def image(self: "FixtureFactory", name: str = "image.gif", content_type: str = "image/gif") -> SimpleUploadedFile:
    return SimpleUploadedFile(name=name, content=self.faker.image(), content_type=content_type)


@register
def pdf(self: "FixtureFactory", name: str = "document.pdf", content_type: str = "application/pdf") -> SimpleUploadedFile:  # noqa: ARG001
    # Minimal valid PDF content
    pdf_content = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\ntrailer\n<<\n/Root 1 0 R\n>>\n%%EOF"
    return SimpleUploadedFile(name=name, content=pdf_content, content_type=content_type)


@register
def prosemirror(self: "FixtureFactory", text: str) -> dict:  # noqa: ARG001
    return {
        "type": "doc",
        "content": [
            {
                "type": "paragraph",
                "content": [
                    {
                        "type": "text",
                        "text": text,
                    }
                ],
            }
        ],
    }
