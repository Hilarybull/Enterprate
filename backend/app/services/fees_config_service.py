"""Fees configuration service for dynamic business registration fees"""
from datetime import datetime, timezone
from typing import List


class FeesConfigService:
    """Service for managing dynamic registration fees configuration"""
    
    # UK Companies House fees (as of 2024-2025)
    # Source: https://www.gov.uk/government/publications/companies-house-fees/companies-house-fees
    UK_REGISTRATION_FEES = [
        {
            "id": "ltd",
            "businessType": "ltd",
            "title": "Private Company Limited by Shares (Ltd)",
            "registrationAuthority": "Companies House",
            "onlineFee": "£50",
            "paperFee": "£71",
            "sameDayFee": "£78",
            "notes": "Same-day service available online only",
            "sourceUrl": "https://www.gov.uk/government/publications/companies-house-fees/companies-house-fees",
            "lastUpdated": "2024-05-01"
        },
        {
            "id": "ltd_guarantee",
            "businessType": "ltd_guarantee",
            "title": "Private Company Limited by Guarantee",
            "registrationAuthority": "Companies House",
            "onlineFee": "£50",
            "paperFee": "£71",
            "sameDayFee": "£78",
            "notes": "Same structure as Ltd but without share capital",
            "sourceUrl": "https://www.gov.uk/government/publications/companies-house-fees/companies-house-fees",
            "lastUpdated": "2024-05-01"
        },
        {
            "id": "plc",
            "businessType": "plc",
            "title": "Public Limited Company (PLC)",
            "registrationAuthority": "Companies House",
            "onlineFee": "£50",
            "paperFee": "£71",
            "sameDayFee": "£78",
            "notes": "Requires minimum £50,000 share capital",
            "sourceUrl": "https://www.gov.uk/government/publications/companies-house-fees/companies-house-fees",
            "lastUpdated": "2024-05-01"
        },
        {
            "id": "unlimited",
            "businessType": "unlimited",
            "title": "Unlimited Company",
            "registrationAuthority": "Companies House",
            "onlineFee": "£50",
            "paperFee": "£71",
            "sameDayFee": "£78",
            "notes": "Members have unlimited liability",
            "sourceUrl": "https://www.gov.uk/government/publications/companies-house-fees/companies-house-fees",
            "lastUpdated": "2024-05-01"
        },
        {
            "id": "llp",
            "businessType": "llp",
            "title": "Limited Liability Partnership (LLP)",
            "registrationAuthority": "Companies House",
            "onlineFee": "£50",
            "paperFee": "£71",
            "sameDayFee": "£78",
            "notes": "Hybrid partnership and limited company",
            "sourceUrl": "https://www.gov.uk/government/publications/companies-house-fees/companies-house-fees",
            "lastUpdated": "2024-05-01"
        },
        {
            "id": "lp",
            "businessType": "lp",
            "title": "Limited Partnership (LP)",
            "registrationAuthority": "Companies House",
            "onlineFee": "N/A",
            "paperFee": "£20",
            "sameDayFee": None,
            "notes": "Paper registration only",
            "sourceUrl": "https://www.gov.uk/government/publications/companies-house-fees/companies-house-fees",
            "lastUpdated": "2024-05-01"
        },
        {
            "id": "cic_shares",
            "businessType": "cic_shares",
            "title": "Community Interest Company (CIC) - Limited by Shares",
            "registrationAuthority": "Companies House + CIC Regulator",
            "onlineFee": "£35",
            "paperFee": "£71",
            "sameDayFee": None,
            "notes": "Additional CIC36 form required",
            "sourceUrl": "https://www.gov.uk/government/publications/companies-house-fees/companies-house-fees",
            "lastUpdated": "2024-05-01"
        },
        {
            "id": "cic_guarantee",
            "businessType": "cic_guarantee",
            "title": "Community Interest Company (CIC) - Limited by Guarantee",
            "registrationAuthority": "Companies House + CIC Regulator",
            "onlineFee": "£35",
            "paperFee": "£71",
            "sameDayFee": None,
            "notes": "No share capital, all profits reinvested",
            "sourceUrl": "https://www.gov.uk/government/publications/companies-house-fees/companies-house-fees",
            "lastUpdated": "2024-05-01"
        },
        {
            "id": "overseas",
            "businessType": "overseas",
            "title": "Overseas Company (UK Establishment)",
            "registrationAuthority": "Companies House",
            "onlineFee": "£50",
            "paperFee": "£71",
            "sameDayFee": None,
            "notes": "For non-UK companies operating in UK",
            "sourceUrl": "https://www.gov.uk/government/publications/companies-house-fees/companies-house-fees",
            "lastUpdated": "2024-05-01"
        },
        {
            "id": "sole_trader",
            "businessType": "sole_trader",
            "title": "Sole Trader",
            "registrationAuthority": "HMRC",
            "onlineFee": "Free",
            "paperFee": "Free",
            "sameDayFee": None,
            "notes": "Register for Self Assessment with HMRC",
            "sourceUrl": "https://www.gov.uk/register-for-self-assessment",
            "lastUpdated": "2024-05-01"
        },
        {
            "id": "cio",
            "businessType": "cio",
            "title": "Charitable Incorporated Organisation (CIO)",
            "registrationAuthority": "Charity Commission",
            "onlineFee": "Free",
            "paperFee": "Free",
            "sameDayFee": None,
            "notes": "Registered with Charity Commission, not Companies House",
            "sourceUrl": "https://www.gov.uk/setting-up-charity/register-your-charity",
            "lastUpdated": "2024-05-01"
        },
        {
            "id": "coop",
            "businessType": "coop",
            "title": "Co-operative / Community Benefit Society",
            "registrationAuthority": "Financial Conduct Authority (FCA)",
            "onlineFee": "Varies",
            "paperFee": "Varies",
            "sameDayFee": None,
            "notes": "Fee depends on type and rules complexity",
            "sourceUrl": "https://www.fca.org.uk/firms/mutual-societies",
            "lastUpdated": "2024-05-01"
        },
        {
            "id": "royal_charter",
            "businessType": "royal_charter",
            "title": "Royal Charter Company",
            "registrationAuthority": "Privy Council",
            "onlineFee": "By application",
            "paperFee": "By application",
            "sameDayFee": None,
            "notes": "Extremely rare, requires Privy Council approval",
            "sourceUrl": "https://privycouncil.independent.gov.uk/royal-charters/",
            "lastUpdated": "2024-05-01"
        }
    ]
    
    @staticmethod
    async def get_all_fees() -> dict:
        """Get all registration fees configuration"""
        return {
            "fees": FeesConfigService.UK_REGISTRATION_FEES,
            "lastUpdated": "2024-05-01",
            "source": "UK Government - Companies House Official Fees"
        }
    
    @staticmethod
    async def get_fee_by_type(business_type: str) -> dict:
        """Get fee for a specific business type"""
        for fee in FeesConfigService.UK_REGISTRATION_FEES:
            if fee["businessType"] == business_type:
                return fee
        return None
    
    @staticmethod
    async def get_companies_house_fees() -> List[dict]:
        """Get only Companies House registered business types"""
        ch_types = ["ltd", "ltd_guarantee", "plc", "unlimited", "llp", "lp", "cic_shares", "cic_guarantee", "overseas"]
        return [fee for fee in FeesConfigService.UK_REGISTRATION_FEES if fee["businessType"] in ch_types]
    
    @staticmethod
    async def get_other_authority_fees() -> List[dict]:
        """Get business types registered with other authorities"""
        other_types = ["sole_trader", "cio", "coop", "royal_charter"]
        return [fee for fee in FeesConfigService.UK_REGISTRATION_FEES if fee["businessType"] in other_types]
