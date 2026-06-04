import re

def resolve_company_slug(company_name: str) -> str:
    slug = company_name.lower()
    slug = re.sub(r'[^a-z0-9]+', '-', slug)
    return slug.strip('-')
