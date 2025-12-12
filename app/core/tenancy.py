import re


def slugify_org_name(name: str) -> str:
    s = name.strip().lower()
    s = re.sub(r"[^a-z0-9]+", "_", s)
    s = re.sub(r"_+", "_", s).strip("_")
    if not s:
        raise ValueError("Invalid organization name")
    return s


def org_collection_name(org_name: str) -> str:
    return f"org_{slugify_org_name(org_name)}"
