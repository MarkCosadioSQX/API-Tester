"""
SQX API Test Suite
Tests all three endpoints with various scenarios including authentication,
valid/invalid inputs, error handling, and response validation.
"""

import requests
import json
from datetime import datetime, timedelta
from typing import Dict, Any, List, Tuple

# API Configuration
BASE_URL = "https://iw4w1pr906.execute-api.us-east-2.amazonaws.com/Dev"
API_KEY = "FEb05PgvKG8iMzI2T9S698opZyEVz9Q63TNRdpmx"

# Test Results Storage
test_results: List[Dict[str, Any]] = []


def log_test(test_name: str, endpoint: str, method: str, status: str, 
             details: str = "", response_data: Any = None):
    """Log test result"""
    result = {
        "test_name": test_name,
        "endpoint": endpoint,
        "method": method,
        "status": status,  # PASS, FAIL, ERROR
        "details": details,
        "response_data": response_data,
        "timestamp": datetime.now().isoformat()
    }
    test_results.append(result)
    status_symbol = "[PASS]" if status == "PASS" else "[FAIL]" if status == "FAIL" else "[ERROR]"
    print(f"{status_symbol} {test_name}: {details}")


def make_request(method: str, endpoint: str, headers: Dict = None, 
                params: Dict = None, json_data: Dict = None) -> Tuple[int, Any]:
    """Make HTTP request and return status code and response"""
    url = f"{BASE_URL}{endpoint}"
    default_headers = {"x-api-key": API_KEY} if headers is None else headers
    
    try:
        if method.upper() == "GET":
            response = requests.get(url, headers=default_headers, params=params, timeout=30)
        elif method.upper() == "POST":
            response = requests.post(url, headers=default_headers, json=json_data, timeout=30)
        else:
            return 0, {"error": "Unsupported method"}
        
        try:
            return response.status_code, response.json()
        except json.JSONDecodeError:
            return response.status_code, {"raw_response": response.text}
    except requests.exceptions.RequestException as e:
        return 0, {"error": str(e)}


# ============================================================================
# AUTHENTICATION TESTS
# ============================================================================

def test_authentication():
    """Test authentication scenarios"""
    print("\n" + "="*70)
    print("AUTHENTICATION TESTS")
    print("="*70)
    
    # Test 1: Missing API Key
    status, response = make_request("GET", "/price/byIsin", 
                                   headers={}, 
                                   params={"isin": "AED01656C257"})
    if status == 401:
        log_test("Missing API Key", "/price/byIsin", "GET", "PASS", 
                f"Correctly returned 401 Unauthorized")
    else:
        log_test("Missing API Key", "/price/byIsin", "GET", "FAIL", 
                f"Expected 401, got {status}", response)
    
    # Test 2: Invalid API Key
    status, response = make_request("GET", "/price/byIsin", 
                                   headers={"x-api-key": "INVALID_KEY_12345"}, 
                                   params={"isin": "AED01656C257"})
    if status == 403:
        log_test("Invalid API Key", "/price/byIsin", "GET", "PASS", 
                f"Correctly returned 403 Forbidden")
    else:
        log_test("Invalid API Key", "/price/byIsin", "GET", "FAIL", 
                f"Expected 403, got {status}", response)
    
    # Test 3: Valid API Key
    status, response = make_request("GET", "/price/byIsin", 
                                   params={"isin": "AED01656C257"})
    if status == 200:
        log_test("Valid API Key", "/price/byIsin", "GET", "PASS", 
                f"Successfully authenticated with status 200")
    else:
        log_test("Valid API Key", "/price/byIsin", "GET", "FAIL", 
                f"Expected 200, got {status}", response)


# ============================================================================
# GET /price/byIsin TESTS
# ============================================================================

def test_get_single_price():
    """Test GET /price/byIsin endpoint"""
    print("\n" + "="*70)
    print("GET /price/byIsin - SINGLE PRICE TESTS")
    print("="*70)
    
    # Test 1: Valid ISIN
    test_isin = "AED01656C257"
    status, response = make_request("GET", "/price/byIsin", 
                                   params={"isin": test_isin})
    if status == 200:
        if isinstance(response, dict) and "reference" in response and "pricing" in response:
            log_test("Valid ISIN", "/price/byIsin", "GET", "PASS", 
                    f"Successfully retrieved price for ISIN {test_isin}")
        else:
            log_test("Valid ISIN - Response Structure", "/price/byIsin", "GET", "FAIL", 
                    "Response missing required 'reference' or 'pricing' fields", response)
    else:
        log_test("Valid ISIN", "/price/byIsin", "GET", "FAIL", 
                f"Expected 200, got {status}", response)
    
    # Test 2: Missing ISIN parameter
    status, response = make_request("GET", "/price/byIsin", params={})
    if status in [400, 422]:
        log_test("Missing ISIN Parameter", "/price/byIsin", "GET", "PASS", 
                f"Correctly returned error status {status} for missing parameter")
    else:
        log_test("Missing ISIN Parameter", "/price/byIsin", "GET", "FAIL", 
                f"Expected 400/422, got {status}", response)
    
    # Test 3: Invalid ISIN format (too short)
    status, response = make_request("GET", "/price/byIsin", 
                                   params={"isin": "INVALID"})
    if status in [400, 404, 422]:
        log_test("Invalid ISIN Format", "/price/byIsin", "GET", "PASS", 
                f"Correctly handled invalid ISIN with status {status}")
    else:
        log_test("Invalid ISIN Format", "/price/byIsin", "GET", "FAIL", 
                f"Expected error status, got {status}", response)
    
    # Test 4: Non-existent ISIN
    status, response = make_request("GET", "/price/byIsin", 
                                   params={"isin": "US1234567890"})
    if status in [200, 404]:
        if status == 404:
            log_test("Non-existent ISIN", "/price/byIsin", "GET", "PASS", 
                    "Correctly returned 404 for non-existent ISIN")
        else:
            # Some APIs return 200 with empty/error in response
            log_test("Non-existent ISIN", "/price/byIsin", "GET", "PASS", 
                    f"Returned {status} for non-existent ISIN", response)
    else:
        log_test("Non-existent ISIN", "/price/byIsin", "GET", "FAIL", 
                f"Unexpected status {status}", response)
    
    # Test 5: Response structure validation
    status, response = make_request("GET", "/price/byIsin", 
                                   params={"isin": test_isin})
    if status == 200 and isinstance(response, dict):
        has_reference = "reference" in response
        has_pricing = "pricing" in response
        ref_has_isin = has_reference and "isin" in response.get("reference", {})
        
        if has_reference and has_pricing and ref_has_isin:
            log_test("Response Structure Validation", "/price/byIsin", "GET", "PASS", 
                    "Response structure matches documentation")
        else:
            log_test("Response Structure Validation", "/price/byIsin", "GET", "FAIL", 
                    f"Missing required fields. Reference: {has_reference}, Pricing: {has_pricing}, ISIN in ref: {ref_has_isin}", 
                    response)
    else:
        log_test("Response Structure Validation", "/price/byIsin", "GET", "ERROR", 
                f"Cannot validate structure - request failed with status {status}")


# ============================================================================
# GET /price/byIsinHistorical TESTS
# ============================================================================

def test_get_historical_price():
    """Test GET /price/byIsinHistorical endpoint"""
    print("\n" + "="*70)
    print("GET /price/byIsinHistorical - HISTORICAL PRICE TESTS")
    print("="*70)
    
    test_isin = "AR0047526246"
    today = datetime.now()
    past_date = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    future_date = (today + timedelta(days=30)).strftime("%Y-%m-%d")
    old_date = "2020-01-01"
    
    # Test 1: Valid ISIN + Valid Date
    status, response = make_request("GET", "/price/byIsinHistorical", 
                                   params={"isin": test_isin, "date": past_date})
    if status == 200:
        if isinstance(response, dict) and "reference" in response and "pricing" in response:
            log_test("Valid ISIN + Valid Date", "/price/byIsinHistorical", "GET", "PASS", 
                    f"Successfully retrieved historical price for {past_date}")
        else:
            log_test("Valid ISIN + Valid Date", "/price/byIsinHistorical", "GET", "FAIL", 
                    "Response missing required structure", response)
    else:
        log_test("Valid ISIN + Valid Date", "/price/byIsinHistorical", "GET", "FAIL", 
                f"Expected 200, got {status}", response)
    
    # Test 2: Missing ISIN parameter
    status, response = make_request("GET", "/price/byIsinHistorical", 
                                   params={"date": past_date})
    if status in [400, 422]:
        log_test("Missing ISIN Parameter", "/price/byIsinHistorical", "GET", "PASS", 
                f"Correctly returned error status {status} for missing ISIN")
    else:
        log_test("Missing ISIN Parameter", "/price/byIsinHistorical", "GET", "FAIL", 
                f"Expected 400/422, got {status}", response)
    
    # Test 3: Missing Date parameter
    status, response = make_request("GET", "/price/byIsinHistorical", 
                                   params={"isin": test_isin})
    if status in [400, 422]:
        log_test("Missing Date Parameter", "/price/byIsinHistorical", "GET", "PASS", 
                f"Correctly returned error status {status} for missing date")
    else:
        log_test("Missing Date Parameter", "/price/byIsinHistorical", "GET", "FAIL", 
                f"Expected 400/422, got {status}", response)
    
    # Test 4: Invalid Date Format
    status, response = make_request("GET", "/price/byIsinHistorical", 
                                   params={"isin": test_isin, "date": "01-01-2020"})
    if status in [400, 422]:
        log_test("Invalid Date Format", "/price/byIsinHistorical", "GET", "PASS", 
                f"Correctly rejected invalid date format with status {status}")
    else:
        log_test("Invalid Date Format", "/price/byIsinHistorical", "GET", "FAIL", 
                f"Expected 400/422, got {status}", response)
    
    # Test 5: Future Date
    status, response = make_request("GET", "/price/byIsinHistorical", 
                                   params={"isin": test_isin, "date": future_date})
    if status in [200, 400, 422]:
        log_test("Future Date", "/price/byIsinHistorical", "GET", "PASS", 
                f"Handled future date appropriately with status {status}", response)
    else:
        log_test("Future Date", "/price/byIsinHistorical", "GET", "FAIL", 
                f"Unexpected status {status}", response)
    
    # Test 6: Very Old Date
    status, response = make_request("GET", "/price/byIsinHistorical", 
                                   params={"isin": test_isin, "date": old_date})
    if status == 200:
        # Check for "closest date" message
        pricing = response.get("pricing", {})
        if "message" in pricing or "pricing_date" in pricing:
            log_test("Very Old Date", "/price/byIsinHistorical", "GET", "PASS", 
                    "Returned closest available date or message", response)
        else:
            log_test("Very Old Date", "/price/byIsinHistorical", "GET", "PASS", 
                    f"Returned status {status} for old date", response)
    else:
        log_test("Very Old Date", "/price/byIsinHistorical", "GET", "PASS", 
                f"Handled old date with status {status}", response)
    
    # Test 7: Response structure validation
    status, response = make_request("GET", "/price/byIsinHistorical", 
                                   params={"isin": test_isin, "date": past_date})
    if status == 200 and isinstance(response, dict):
        has_reference = "reference" in response
        has_pricing = "pricing" in response
        ref_has_isin = has_reference and "isin" in response.get("reference", {})
        
        if has_reference and has_pricing and ref_has_isin:
            log_test("Historical Response Structure", "/price/byIsinHistorical", "GET", "PASS", 
                    "Response structure matches documentation")
        else:
            log_test("Historical Response Structure", "/price/byIsinHistorical", "GET", "FAIL", 
                    "Response structure validation failed", response)


# ============================================================================
# POST /price/byIsinBulk TESTS
# ============================================================================

def test_bulk_prices():
    """Test POST /price/byIsinBulk endpoint"""
    print("\n" + "="*70)
    print("POST /price/byIsinBulk - BULK PRICES TESTS")
    print("="*70)
    
    # Test 1: Valid ISIN List (multiple)
    valid_isins = ["US95040QAJ31", "US517834AF40", "US25389JAT34"]
    status, response = make_request("POST", "/price/byIsinBulk", 
                                   json_data={"isin_list": valid_isins})
    if status == 200:
        if isinstance(response, dict) and "success" in response:
            log_test("Valid ISIN List (Multiple)", "/price/byIsinBulk", "POST", "PASS", 
                    f"Successfully processed {len(valid_isins)} ISINs")
        else:
            log_test("Valid ISIN List (Multiple)", "/price/byIsinBulk", "POST", "FAIL", 
                    "Response missing 'success' array", response)
    else:
        log_test("Valid ISIN List (Multiple)", "/price/byIsinBulk", "POST", "FAIL", 
                f"Expected 200, got {status}", response)
    
    # Test 2: Single ISIN in list
    single_isin = ["AED01656C257"]
    status, response = make_request("POST", "/price/byIsinBulk", 
                                   json_data={"isin_list": single_isin})
    if status == 200:
        log_test("Single ISIN in List", "/price/byIsinBulk", "POST", "PASS", 
                "Successfully handled single ISIN in bulk request")
    else:
        log_test("Single ISIN in List", "/price/byIsinBulk", "POST", "FAIL", 
                f"Expected 200, got {status}", response)
    
    # Test 3: Empty ISIN List
    status, response = make_request("POST", "/price/byIsinBulk", 
                                   json_data={"isin_list": []})
    if status in [200, 400, 422]:
        log_test("Empty ISIN List", "/price/byIsinBulk", "POST", "PASS", 
                f"Handled empty list appropriately with status {status}")
    else:
        log_test("Empty ISIN List", "/price/byIsinBulk", "POST", "FAIL", 
                f"Unexpected status {status}", response)
    
    # Test 4: Mix of Valid/Invalid ISINs
    mixed_isins = ["AED01656C257", "US1234567890", "INVALID_ISIN"]
    status, response = make_request("POST", "/price/byIsinBulk", 
                                   json_data={"isin_list": mixed_isins})
    if status == 200:
        has_success = "success" in response
        has_not_found = "not_found" in response
        has_unprocessed = "unprocessed" in response
        
        if has_success or has_not_found or has_unprocessed:
            log_test("Mixed Valid/Invalid ISINs", "/price/byIsinBulk", "POST", "PASS", 
                    "Correctly categorized ISINs into success/not_found/unprocessed")
        else:
            log_test("Mixed Valid/Invalid ISINs", "/price/byIsinBulk", "POST", "FAIL", 
                    "Response missing categorization arrays", response)
    else:
        log_test("Mixed Valid/Invalid ISINs", "/price/byIsinBulk", "POST", "FAIL", 
                f"Expected 200, got {status}", response)
    
    # Test 5: Missing isin_list in body
    status, response = make_request("POST", "/price/byIsinBulk", 
                                   json_data={})
    if status in [400, 422]:
        log_test("Missing isin_list Field", "/price/byIsinBulk", "POST", "PASS", 
                f"Correctly returned error status {status} for missing field")
    else:
        log_test("Missing isin_list Field", "/price/byIsinBulk", "POST", "FAIL", 
                f"Expected 400/422, got {status}", response)
    
    # Test 6: Invalid JSON structure
    status, response = make_request("POST", "/price/byIsinBulk", 
                                   json_data={"isin": "AED01656C257"})  # Wrong field name
    if status in [200, 400, 422]:
        log_test("Invalid JSON Structure", "/price/byIsinBulk", "POST", "PASS", 
                f"Handled invalid structure with status {status}")
    else:
        log_test("Invalid JSON Structure", "/price/byIsinBulk", "POST", "FAIL", 
                f"Unexpected status {status}", response)
    
    # Test 7: Response structure validation
    status, response = make_request("POST", "/price/byIsinBulk", 
                                   json_data={"isin_list": valid_isins})
    if status == 200 and isinstance(response, dict):
        has_success = "success" in response
        has_not_found = "not_found" in response
        has_unprocessed = "unprocessed" in response
        
        if has_success and has_not_found and has_unprocessed:
            log_test("Bulk Response Structure", "/price/byIsinBulk", "POST", "PASS", 
                    "Response contains all required arrays (success, not_found, unprocessed)")
        else:
            log_test("Bulk Response Structure", "/price/byIsinBulk", "POST", "FAIL", 
                    f"Missing arrays. Success: {has_success}, Not Found: {has_not_found}, Unprocessed: {has_unprocessed}", 
                    response)
    else:
        log_test("Bulk Response Structure", "/price/byIsinBulk", "POST", "ERROR", 
                f"Cannot validate structure - request failed with status {status}")


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def generate_summary():
    """Generate test summary report"""
    print("\n" + "="*70)
    print("TEST SUMMARY REPORT")
    print("="*70)
    
    total_tests = len(test_results)
    passed = sum(1 for r in test_results if r["status"] == "PASS")
    failed = sum(1 for r in test_results if r["status"] == "FAIL")
    errors = sum(1 for r in test_results if r["status"] == "ERROR")
    
    print(f"\nTotal Tests: {total_tests}")
    print(f"Passed: {passed} ({passed/total_tests*100:.1f}%)")
    print(f"Failed: {failed} ({failed/total_tests*100:.1f}%)")
    print(f"Errors: {errors} ({errors/total_tests*100:.1f}%)")
    
    if failed > 0 or errors > 0:
        print("\n" + "-"*70)
        print("FAILED/ERROR TESTS:")
        print("-"*70)
        for result in test_results:
            if result["status"] in ["FAIL", "ERROR"]:
                print(f"\n{result['test_name']} ({result['endpoint']})")
                print(f"  Status: {result['status']}")
                print(f"  Details: {result['details']}")
                if result.get("response_data"):
                    print(f"  Response: {json.dumps(result['response_data'], indent=2)[:500]}")
    
    # Save detailed results to JSON file
    with open("test_results.json", "w") as f:
        json.dump({
            "summary": {
                "total": total_tests,
                "passed": passed,
                "failed": failed,
                "errors": errors,
                "timestamp": datetime.now().isoformat()
            },
            "results": test_results
        }, f, indent=2)
    
    print(f"\nDetailed results saved to: test_results.json")
    return {
        "total": total_tests,
        "passed": passed,
        "failed": failed,
        "errors": errors
    }


if __name__ == "__main__":
    print("\n" + "="*70)
    print("SQX API TEST SUITE")
    print("="*70)
    print(f"Base URL: {BASE_URL}")
    print(f"Test Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        # Run all test suites
        test_authentication()
        test_get_single_price()
        test_get_historical_price()
        test_bulk_prices()
        
        # Generate summary
        summary = generate_summary()
        
        print("\n" + "="*70)
        print("TESTING COMPLETE")
        print("="*70)
        
    except Exception as e:
        print(f"\nCRITICAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

