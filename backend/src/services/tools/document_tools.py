"""Document tools for LangChain."""
from typing import Any, Dict, Optional
from uuid import UUID

from langchain_core.tools import tool
from sqlalchemy.orm import Session

from src.services.document_service import DocumentService
from src.services.llm_service import LLMService


def create_document_tool(db: Session, user_id: UUID):
    """
    Create document tool with database session and user context.

    Args:
        db: Database session
        user_id: User ID

    Returns:
        LangChain tool
    """

    @tool
    def create_document(title: str, kind: str = "text") -> Dict[str, Any]:
        """
        Create a document for writing or content creation activities.

        Args:
            title: Document title
            kind: Document kind (text, code, image, sheet)

        Returns:
            Created document information
        """
        # Validate kind
        valid_kinds = ["text", "code", "image", "sheet"]
        if kind not in valid_kinds:
            return {
                "error": f"Invalid document kind. Must be one of: {', '.join(valid_kinds)}"
            }

        # Create document
        document = DocumentService.create_document(
            db=db, user_id=user_id, title=title, content="", kind=kind
        )

        return {
            "id": str(document.id),
            "title": document.title,
            "kind": document.kind,
            "content": "A document was created and is now visible to the user.",
        }

    return create_document


def update_document_tool(db: Session, user_id: UUID, llm_service: LLMService):
    """
    Create update document tool with database session and user context.

    Args:
        db: Database session
        user_id: User ID
        llm_service: LLM service for generating updates

    Returns:
        LangChain tool
    """

    @tool
    def update_document(document_id: str, description: str) -> Dict[str, Any]:
        """
        Update a document with the given description.

        Args:
            document_id: The ID of the document to update
            description: The description of changes that need to be made

        Returns:
            Updated document information
        """
        try:
            doc_uuid = UUID(document_id)
        except ValueError:
            return {"error": "Invalid document ID format"}

        # Get document
        document = DocumentService.get_document(db, doc_uuid, user_id)
        if not document:
            return {"error": "Document not found"}

        # Generate updated content using LLM
        prompt = f"""Update the following {document.kind} document based on this description:

Description: {description}

Current content:
{document.content}

Generate the updated content:"""

        try:
            updated_content = llm_service.generate_chat(
                messages=[{"role": "user", "content": prompt}], temperature=0.3
            )

            # Update document
            document = DocumentService.update_document(db, doc_uuid, user_id, updated_content)

            return {
                "id": str(document.id),
                "title": document.title,
                "kind": document.kind,
                "content": "The document has been updated successfully.",
            }
        except Exception as e:
            return {"error": f"Failed to update document: {str(e)}"}

    return update_document


def request_suggestions_tool(db: Session, user_id: UUID, llm_service: LLMService):
    """
    Create request suggestions tool with database session and user context.

    Args:
        db: Database session
        user_id: User ID
        llm_service: LLM service for generating suggestions

    Returns:
        LangChain tool
    """

    @tool
    def request_suggestions(document_id: str) -> Dict[str, Any]:
        """
        Request suggestions for improving a document.

        Args:
            document_id: The ID of the document to request suggestions for

        Returns:
            Suggestions information
        """
        try:
            doc_uuid = UUID(document_id)
        except ValueError:
            return {"error": "Invalid document ID format"}

        # Get document
        document = DocumentService.get_document(db, doc_uuid, user_id)
        if not document or not document.content:
            return {"error": "Document not found or has no content"}

        # Generate suggestions using LLM
        prompt = f"""You are a helpful writing assistant. Given a piece of writing, please offer suggestions to improve it.

Provide up to 5 suggestions. For each suggestion:
- Include the original sentence/phrase
- Provide the suggested improvement
- Explain why this change improves the text

Document content:
{document.content}

Format each suggestion as:
ORIGINAL: [original text]
SUGGESTED: [suggested text]
REASON: [explanation]

Suggestions:"""

        try:
            response = llm_service.generate_chat(
                messages=[{"role": "user", "content": prompt}], temperature=0.7
            )

            # Parse suggestions (simple parsing - could be improved)
            suggestions_created = 0
            lines = response.split("\n")
            current_suggestion = {}

            for line in lines:
                line = line.strip()
                if line.startswith("ORIGINAL:"):
                    current_suggestion["original"] = line.replace("ORIGINAL:", "").strip()
                elif line.startswith("SUGGESTED:"):
                    current_suggestion["suggested"] = line.replace("SUGGESTED:", "").strip()
                elif line.startswith("REASON:"):
                    current_suggestion["reason"] = line.replace("REASON:", "").strip()

                    # If we have all parts, create suggestion
                    if all(
                        k in current_suggestion for k in ["original", "suggested", "reason"]
                    ):
                        DocumentService.create_suggestion(
                            db=db,
                            document_id=doc_uuid,
                            user_id=user_id,
                            original_text=current_suggestion["original"],
                            suggested_text=current_suggestion["suggested"],
                            description=current_suggestion["reason"],
                        )
                        suggestions_created += 1
                        current_suggestion = {}

            return {
                "id": document_id,
                "title": document.title,
                "kind": document.kind,
                "message": f"{suggestions_created} suggestions have been added to the document",
            }
        except Exception as e:
            return {"error": f"Failed to generate suggestions: {str(e)}"}

    return request_suggestions

