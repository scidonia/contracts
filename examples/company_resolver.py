"""
Company name resolution example using Design by Contract.

This module demonstrates how to develop a function that resolves company names
in text using a database of company IDs and URLs.
"""

from typing import List, Dict, Any
from pydantic import BaseModel
from contracts import (
    specification,
    pre_description,
    post_description,
    raises,
    precondition,
    postcondition,
    ImplementThis,
    PreconditionViolation,
    PostconditionViolation,
)


class CompanyMatch(BaseModel):
    """Pydantic model for LLM-resolved company matches."""

    company_id: int
    matched_text: str
    confidence: float


def resolve_company_names_precondition(
    text: str, company_database: List[Dict[str, Any]]
) -> bool:
    """Precondition: text must be non-empty and database must contain valid company records."""
    if not isinstance(text, str) or len(text.strip()) == 0:
        return False

    if not isinstance(company_database, list):
        return False

    for record in company_database:
        if not isinstance(record, dict):
            return False
        required_fields = {"id", "name", "url"}
        if not required_fields.issubset(record.keys()):
            return False
        if not isinstance(record["id"], int):
            return False
        if not isinstance(record["name"], str) or len(record["name"].strip()) == 0:
            return False
        if not isinstance(record["url"], str) or len(record["url"].strip()) == 0:
            return False

    return True


def resolve_company_names_postcondition(
    result: List[Dict[str, Any]], text: str, company_database: List[Dict[str, Any]]
) -> bool:
    """Postcondition: result must be a subset of database with valid structure."""
    if not isinstance(result, list):
        return False

    # All returned records must be from the original database
    for company in result:
        if not isinstance(company, dict):
            return False

        # Check that this company exists in the database
        found_in_db = False
        for db_record in company_database:
            if (
                company.get("id") == db_record.get("id")
                and company.get("name") == db_record.get("name")
                and company.get("url") == db_record.get("url")
            ):
                found_in_db = True
                break

        if not found_in_db:
            return False

        # Check required fields are present
        required_fields = {"id", "name", "url"}
        if not required_fields.issubset(company.keys()):
            return False

    # No duplicates in result
    seen_ids = set()
    for company in result:
        company_id = company.get("id")
        if company_id in seen_ids:
            return False
        seen_ids.add(company_id)

    return True


@specification("Resolves company names in text using database lookup")
@pre_description(
    "Text must be a non-empty string and database must be a list of valid company records with 'id', 'name', and 'url' fields"
)
@post_description(
    "Returns a list of company records that were found in the text, preserving database structure with id, name, and url"
)
@raises([ImplementThis, PreconditionViolation, PostconditionViolation])
@precondition(resolve_company_names_precondition)
@postcondition(resolve_company_names_postcondition)
def resolve_company_names(
    text: str, company_database: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Resolve company names found in text using company database.

    Args:
        text: The input text to search for company names
        company_database: List of company records with 'id', 'name', and 'url' fields

    Returns:
        List of resolved companies with their database information
    """
    resolved_companies = []

    for company in company_database:
        company_name = company["name"]

        # Check if the company name appears in the text
        if company_name in text:
            # Create a copy of the company record to return
            resolved_company = {
                "id": company["id"],
                "name": company["name"],
                "url": company["url"],
            }
            resolved_companies.append(resolved_company)

    return resolved_companies


def entity_resolve_llm_precondition(
    text: str, company_database: List[Dict[str, Any]]
) -> bool:
    """Precondition: text must be non-empty and database must contain valid company records."""
    if not isinstance(text, str) or len(text.strip()) == 0:
        return False

    if not isinstance(company_database, list):
        return False

    for record in company_database:
        if not isinstance(record, dict):
            return False
        required_fields = {"id", "name", "url"}
        if not required_fields.issubset(record.keys()):
            return False
        if not isinstance(record["id"], int):
            return False
        if not isinstance(record["name"], str) or len(record["name"].strip()) == 0:
            return False
        if not isinstance(record["url"], str) or len(record["url"].strip()) == 0:
            return False

    return True


def entity_resolve_llm_postcondition(
    result: List[CompanyMatch], text: str, company_database: List[Dict[str, Any]]
) -> bool:
    """Postcondition: result must be valid CompanyMatch objects with correct constraints."""
    if not isinstance(result, list):
        return False

    for match in result:
        if not isinstance(match, CompanyMatch):
            return False

        # Check that matched_text exists in the input text
        if match.matched_text not in text:
            return False

        # Check that company_id corresponds to a valid database entry
        found_in_db = False
        for db_record in company_database:
            if db_record.get("id") == match.company_id:
                found_in_db = True
                break

        if not found_in_db:
            return False

        # Check that confidence is between 0.0 and 1.0
        if not (0.0 <= match.confidence <= 1.0):
            return False

    # No duplicate company_ids in result
    seen_ids = set()
    for match in result:
        if match.company_id in seen_ids:
            return False
        seen_ids.add(match.company_id)

    return True


@specification(
    "We have a list of company names and their ids, we will send these to an LLM, along with a text and ask it to associate a new exact string name it finds with a company id if it appears to be the same entity. It should use a pydantic model to constrain the LLM output and return this instead of a dictionary."
)
@pre_description(
    "Text must be a non-empty string and database must be a list of valid company records with 'id', 'name', and 'url' fields"
)
@post_description(
    "Returns a list of CompanyMatch objects where each matched_text exists in the input text, company_id corresponds to a valid database entry, and confidence is between 0.0 and 1.0"
)
@raises([ImplementThis, PreconditionViolation, PostconditionViolation])
@precondition(entity_resolve_llm_precondition)
@postcondition(entity_resolve_llm_postcondition)
def entity_resolve_llm(
    text: str, company_database: List[Dict[str, Any]]
) -> List[CompanyMatch]:
    """
    Use an LLM to resolve company entities in text with structured output.

    Args:
        text: The input text to search for company names
        company_database: List of company records with 'id', 'name', and 'url' fields

    Returns:
        List of CompanyMatch objects with structured LLM output
    """
    matches = []
    
    # Simulate LLM entity resolution with fuzzy matching
    text_lower = text.lower()
    
    for company in company_database:
        company_name = company["name"]
        company_name_lower = company_name.lower()
        
        # Check for exact match
        if company_name in text:
            matches.append(CompanyMatch(
                company_id=company["id"],
                matched_text=company_name,
                confidence=1.0
            ))
        # Check for partial matches (simulate LLM fuzzy matching)
        elif company_name_lower in text_lower:
            # Find the actual matched text in original case
            start_idx = text_lower.find(company_name_lower)
            matched_text = text[start_idx:start_idx + len(company_name)]
            matches.append(CompanyMatch(
                company_id=company["id"],
                matched_text=matched_text,
                confidence=0.8
            ))
        # Check for common abbreviations or variations
        else:
            # Simple heuristic: check if company name words appear in text
            company_words = company_name_lower.split()
            found_words = 0
            matched_spans = []
            
            for word in company_words:
                if len(word) > 2 and word in text_lower:  # Skip short words
                    found_words += 1
                    start_idx = text_lower.find(word)
                    matched_spans.append(text[start_idx:start_idx + len(word)])
            
            # If we found significant portion of company name
            if found_words >= len(company_words) * 0.6 and found_words > 0:
                matched_text = " ".join(matched_spans)
                confidence = min(0.7, found_words / len(company_words))
                matches.append(CompanyMatch(
                    company_id=company["id"],
                    matched_text=matched_text,
                    confidence=confidence
                ))
    
    return matches


if __name__ == "__main__":
    # Example usage
    sample_text = "Apple Inc. and Microsoft Corporation are major tech companies."
    sample_database = [
        {"id": 1, "name": "Apple Inc.", "url": "https://apple.com"},
        {"id": 2, "name": "Microsoft Corporation", "url": "https://microsoft.com"},
        {"id": 3, "name": "Google LLC", "url": "https://google.com"},
    ]

    try:
        result = resolve_company_names(sample_text, sample_database)
        print(f"Resolved companies: {result}")
    except ImplementThis as e:
        print(f"Implementation needed: {e}")
