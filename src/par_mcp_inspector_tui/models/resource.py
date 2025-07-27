"""MCP resource models."""

from pydantic import BaseModel, Field


class ResourceTemplate(BaseModel):
    """Resource URI template."""

    model_config = {"populate_by_name": True}

    uri_template: str = Field(alias="uriTemplate")
    name: str | None = None
    description: str | None = None
    mime_type: str | None = Field(None, alias="mimeType")


class Resource(BaseModel):
    """MCP resource definition."""

    model_config = {"populate_by_name": True}

    uri: str
    name: str
    description: str | None = None
    mime_type: str | None = Field(None, alias="mimeType")

    @classmethod
    def from_template(cls, template: ResourceTemplate, uri: str) -> "Resource":
        """Create a resource from a template and URI."""
        return cls(
            uri=uri,
            name=template.name or uri,
            description=template.description,
            mimeType=template.mime_type,
        )
