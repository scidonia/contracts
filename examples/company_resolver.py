"""
Company name resolution example using Design by Contract.

This module demonstrates how to develop a function that resolves company names
in text using a database of company IDs and URLs.
"""

from typing import List, Dict, Any
from pydantic import BaseModel
from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage
from langchain_core.output_parsers import PydanticOutputParser
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


class CompanyMatchList(BaseModel):
    """Pydantic model for list of company matches."""

    matches: List[CompanyMatch]


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

    # If database is empty, result should be empty
    if len(company_database) == 0:
        return len(result) == 0

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
    # If database is empty, return empty list immediately
    if len(company_database) == 0:
        return []

    # Initialize GPT-4 model
    llm = ChatOpenAI(model_name="gpt-4", temperature=0)

    # Set up Pydantic output parser
    parser = PydanticOutputParser(pydantic_object=CompanyMatchList)

    # Create company database context for the LLM
    company_context = "\n".join(
        [
            f"ID: {company['id']}, Name: {company['name']}, URL: {company['url']}"
            for company in company_database
        ]
    )

    # Create the prompt
    prompt = f"""
You are an expert at entity resolution. Given a text and a database of companies, identify any company names or variations mentioned in the text and match them to the correct company ID from the database.

Company Database:
{company_context}

Text to analyze:
"{text}"

For each company you find in the text:
1. Extract the exact text that refers to the company
2. Match it to the correct company ID from the database
3. Assign a confidence score between 0.0 and 1.0 based on how certain you are of the match

Rules:
- Only match companies that actually appear in the text (even if abbreviated or slightly different)
- Use exact text spans from the input text for matched_text
- Confidence should be 1.0 for exact matches, lower for fuzzy matches
- If no companies are found, return an empty list

{parser.get_format_instructions()}
"""

    # Send request to LLM
    message = HumanMessage(content=prompt)
    response = llm.invoke([message])

    # Parse the response
    try:
        parsed_result = parser.parse(response.content)
        return parsed_result.matches
    except Exception as e:
        # Fallback to empty list if parsing fails
        return []


if __name__ == "__main__":
    from contracts import enable_contracts

    # Enable contract checking
    enable_contracts()

    # Example usage
    sample_text = "Apple and Microsoft are major tech companies. Google's parent company and Facebook are also big players."
    sample_database = [
        {"id": 1, "name": "Apple Inc.", "url": "https://apple.com"},
        {"id": 2, "name": "Microsoft Corporation", "url": "https://microsoft.com"},
        {"id": 3, "name": "Alphabet Inc.", "url": "https://google.com"},
        {"id": 4, "name": "Meta Platforms Inc.", "url": "https://meta.com"},
    ]

    print("Testing entity_resolve_llm function:")
    try:
        llm_result = entity_resolve_llm(sample_text, sample_database)
        print(f"LLM resolved companies: {llm_result}")
        for match in llm_result:
            print(
                f"  - Found '{match.matched_text}' -> Company ID {match.company_id} (confidence: {match.confidence})"
            )
    except Exception as e:
        print(f"Error: {e}")

    print("\n" + "="*50)
    print("TESTING CONTRACT VIOLATIONS AND EDGE CASES")
    print("="*50)

    # Test 1: Empty text (should violate precondition)
    print("\nTest 1: Empty text (precondition violation)")
    try:
        result = entity_resolve_llm("", sample_database)
        print(f"Unexpected success: {result}")
    except PreconditionViolation as e:
        print(f"Expected precondition violation: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    # Test 2: None text (should violate precondition)
    print("\nTest 2: None text (precondition violation)")
    try:
        result = entity_resolve_llm(None, sample_database)
        print(f"Unexpected success: {result}")
    except (PreconditionViolation, TypeError) as e:
        print(f"Expected error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    # Test 3: Invalid database - missing required fields
    print("\nTest 3: Invalid database - missing required fields (precondition violation)")
    invalid_db = [
        {"id": 1, "name": "Apple Inc."},  # Missing 'url' field
        {"id": 2, "name": "Microsoft Corporation", "url": "https://microsoft.com"},
    ]
    try:
        result = entity_resolve_llm(sample_text, invalid_db)
        print(f"Unexpected success: {result}")
    except PreconditionViolation as e:
        print(f"Expected precondition violation: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    # Test 4: Invalid database - wrong data types
    print("\nTest 4: Invalid database - wrong data types (precondition violation)")
    invalid_db2 = [
        {"id": "1", "name": "Apple Inc.", "url": "https://apple.com"},  # id should be int
        {"id": 2, "name": "Microsoft Corporation", "url": "https://microsoft.com"},
    ]
    try:
        result = entity_resolve_llm(sample_text, invalid_db2)
        print(f"Unexpected success: {result}")
    except PreconditionViolation as e:
        print(f"Expected precondition violation: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

    # Test 5: Empty database (should work but return empty results)
    print("\nTest 5: Empty database (should work)")
    try:
        # Temporarily disable contracts to see what LLM actually returns
        from contracts import disable_contracts
        disable_contracts()
        
        result = entity_resolve_llm(sample_text, [])
        print(f"LLM raw result with empty database: {result}")
        print(f"Result type: {type(result)}")
        if result:
            for i, match in enumerate(result):
                print(f"  Match {i}: company_id={match.company_id}, matched_text='{match.matched_text}', confidence={match.confidence}")
        
        # Re-enable contracts
        enable_contracts()
        
        # Now test with contracts enabled
        result_with_contracts = entity_resolve_llm(sample_text, [])
        print(f"Empty database result with contracts: {result_with_contracts}")
    except Exception as e:
        print(f"Error: {e}")
        # Make sure contracts are re-enabled
        enable_contracts()

    # Test 6: Text with no company mentions (should work but return empty results)
    print("\nTest 6: Text with no company mentions (should work)")
    try:
        result = entity_resolve_llm("This is just some random text about weather and food.", sample_database)
        print(f"No companies result: {result}")
    except Exception as e:
        print(f"Error: {e}")

    # Test 7: Very long text (stress test)
    print("\nTest 7: Very long text (stress test)")
    long_text = "Apple " * 100 + "and Microsoft " * 50 + "are mentioned many times."
    try:
        result = entity_resolve_llm(long_text, sample_database)
        print(f"Long text result: Found {len(result)} matches")
        for match in result:
            print(f"  - '{match.matched_text}' -> ID {match.company_id} (confidence: {match.confidence})")
    except Exception as e:
        print(f"Error: {e}")
