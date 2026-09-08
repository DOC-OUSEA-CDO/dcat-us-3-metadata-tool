import datetime


def clean(value):
    """
    Clean a value before adding it to the DCAT-US JSON.
    Returns None for empty values.
    """
    if value is None:
        return None
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return None
    return value


def add_if_value(dictionary, key, value):
    """
    Add a key/value pair only if the value is not empty.
    """
    value = clean(value)

    if value is not None:
        dictionary[key] = value


def normalize_single_value(value):
    """
    Streamlit widgets can sometimes return a list even when
    DCAT-US expects a single string/object.

    Convert:
        ["value"] -> "value"

    and:
        ["value 1", "value 2"] -> "value 1, value 2"
    """

    if isinstance(value, list):

        if len(value) == 0:
            return None

        if len(value) == 1:
            return value[0]

        return ", ".join(
            str(item)
            for item in value
            if item is not None
        )

    return value


# ============================================================
# CONTACT
# ============================================================

def build_contact(
    name,
    email=None,
    phone=None,
    organization=None
):
    """
    Build a DCAT-US vCard Contact object.
    """

    contact = {
        "@type": "vcard:Contact"
    }

    add_if_value(
        contact,
        "fn",
        name
    )

    if email:
        email = email.strip()

        if (
            email
            and not email.lower().startswith("mailto:")
        ):
            email = f"mailto:{email}"

        add_if_value(
            contact,
            "hasEmail",
            email
        )

    add_if_value(
        contact,
        "hasTelephone",
        phone
    )

    add_if_value(
        contact,
        "organization-name",
        organization
    )

    return contact


# ============================================================
# PUBLISHER
# ============================================================

def build_publisher(
    office,
    bureau_info
):
    """
    Build the Dataset publisher object.
    """

    publisher = {
        "@type": "org:Organization"
    }

    add_if_value(
        publisher,
        "name",
        office
    )

    if bureau_info.get("homepage"):
        publisher["url"] = bureau_info["homepage"]

    return publisher


# ============================================================
# ACCESS RESTRICTION
# ============================================================

def build_access_restriction(
    access_restriction
):
    """
    Build an AccessRestriction object.

    DCAT-US expects Dataset.accessRestriction
    to be an ARRAY of AccessRestriction objects.

    The individual specificRestriction value must
    be a string or object, NOT an array.
    """

    if not access_restriction:
        return None

    restriction = {
        "@type": "AccessRestriction"
    }

    add_if_value(
        restriction,
        "restrictionStatus",
        normalize_single_value(
            access_restriction.get(
                "restrictionStatus"
            )
        )
    )

    add_if_value(
        restriction,
        "specificRestriction",
        normalize_single_value(
            access_restriction.get(
                "specificRestriction"
            )
        )
    )

    add_if_value(
        restriction,
        "restrictionNote",
        access_restriction.get(
            "restrictionNote"
        )
    )

    return restriction


# ============================================================
# CUI RESTRICTION
# ============================================================

def build_cui_restriction(
    cui_restriction
):
    """
    Build a CUIRestriction object.

    CUIRestriction remains an OBJECT.

    Values coming from Streamlit selection widgets
    are normalized in case they arrive as lists.
    """

    if not cui_restriction:
        return None

    restriction = {
        "@type": "CUIRestriction"
    }

    add_if_value(
        restriction,
        "cuiBannerMarking",
        normalize_single_value(
            cui_restriction.get(
                "cuiBannerMarking"
            )
        )
    )

    add_if_value(
        restriction,
        "designationIndicator",
        normalize_single_value(
            cui_restriction.get(
                "designationIndicator"
            )
        )
    )

    return restriction


# ============================================================
# USE RESTRICTION
# ============================================================

def build_use_restriction(
    use_restriction
):
    """
    Build a UseRestriction object.

    DCAT-US expects Dataset.useRestriction
    to be an ARRAY of UseRestriction objects.

    The individual specificRestriction value must
    be a string or object, NOT an array.
    """

    if not use_restriction:
        return None

    restriction = {
        "@type": "UseRestriction"
    }

    add_if_value(
        restriction,
        "restrictionStatus",
        normalize_single_value(
            use_restriction.get(
                "restrictionStatus"
            )
        )
    )

    add_if_value(
        restriction,
        "specificRestriction",
        normalize_single_value(
            use_restriction.get(
                "specificRestriction"
            )
        )
    )

    add_if_value(
        restriction,
        "restrictionNote",
        use_restriction.get(
            "restrictionNote"
        )
    )

    return restriction


# ============================================================
# SPATIAL
# ============================================================

def build_spatial(
    spatial
):
    """
    Build a DCAT-US Location object.

    A simple value such as:

        Washington

    becomes:

        [
            {
                "@type": "dct:Location",
                "name": "Washington"
            }
        ]
    """

    spatial = clean(spatial)

    if spatial is None:
        return None

    # Multiple locations
    if isinstance(spatial, list):

        locations = []

        for location in spatial:

            location = clean(location)

            if location:

                locations.append(
                    {
                        "@type": "dct:Location",
                        "name": location
                    }
                )

        if locations:
            return locations

        return None

    # Single location
    return [
        {
            "@type": "dct:Location",
            "name": spatial
        }
    ]


# ============================================================
# TEMPORAL
# ============================================================

def build_temporal(
    temporal_start,
    temporal_end
):
    """
    Build a DCAT-US PeriodOfTime.

    DCAT-US expects Dataset.temporal
    to be an ARRAY.
    """

    temporal_start = clean(
        temporal_start
    )

    temporal_end = clean(
        temporal_end
    )

    if (
        temporal_start is None
        and temporal_end is None
    ):
        return None

    period = {
        "@type": "dct:PeriodOfTime"
    }

    if temporal_start:
        period["startDate"] = temporal_start

    if temporal_end:
        period["endDate"] = temporal_end

    return [
        period
    ]


# ============================================================
# DOCUMENT
# ============================================================

def build_document(
    url,
    title=None
):
    """
    Build a DCAT-US Document object.

    Used for:
        - homepage
        - landingPage
        - describedBy
    """

    url = clean(url)

    if url is None:
        return None

    document = {
        "@type": "dcat:Resource"
    }

    if title:
        document["title"] = title

    document["accessURL"] = url

    return document


# ============================================================
# DATA DICTIONARY
# ============================================================

def build_data_dictionary(
    data_dictionary
):
    """
    Build the describedBy value.

    Supports either:
        - an existing dictionary/object
        - a URL string
    """

    if not data_dictionary:
        return None

    if isinstance(
        data_dictionary,
        dict
    ):
        return data_dictionary

    return build_document(
        data_dictionary,
        "Data Dictionary"
    )


# ============================================================
# DATASET
# ============================================================

def build_dataset(
    bureau_info,
    dataset_number,
    title,
    description,
    office,
    contact_name,
    contact_email,
    contact_phone,
    contact_organization,
    keywords,
    themes,
    access_rights,
    access_restriction,
    cui_restriction,
    use_restriction,
    license,
    rights,
    temporal_start,
    temporal_end,
    spatial,
    modified,
    data_dictionary,
    landing_page
):
    """
    Build a complete DCAT-US 3.0 Dataset.

    Identifier examples:

        BEA-000001
        BEA-000002
        ITA-000001
        CEN-000001
    """

    # --------------------------------------------------------
    # IDENTIFIER
    # --------------------------------------------------------

    identifier = (
        f"{bureau_info['identifier_code']}-"
        f"{dataset_number:06d}"
    )

    # --------------------------------------------------------
    # BASE DATASET
    # --------------------------------------------------------

    dataset = {
        "@type": "dcat:Dataset",
        "identifier": identifier
    }

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    add_if_value(
        dataset,
        "title",
        title
    )

    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    add_if_value(
        dataset,
        "description",
        description
    )

    # --------------------------------------------------------
    # PUBLISHER
    # --------------------------------------------------------

    if office:

        dataset["publisher"] = build_publisher(
            office,
            bureau_info
        )

    # --------------------------------------------------------
    # CONTACT POINT
    # --------------------------------------------------------

    if contact_name:

        contact = build_contact(
            name=contact_name,
            email=contact_email,
            phone=contact_phone,
            organization=contact_organization
        )

        # DCAT-US expects an ARRAY.
        dataset["contactPoint"] = [
            contact
        ]

    # --------------------------------------------------------
    # KEYWORDS
    # --------------------------------------------------------

    if keywords:

        cleaned_keywords = []

        for keyword in keywords:

            keyword = str(
                keyword
            ).strip().lower()

            if (
                keyword
                and keyword not in cleaned_keywords
            ):
                cleaned_keywords.append(
                    keyword
                )

        if cleaned_keywords:

            dataset["keyword"] = (
                cleaned_keywords
            )

    # --------------------------------------------------------
    # THEMES
    # --------------------------------------------------------

    if themes:

        cleaned_themes = []

        for theme in themes:

            theme = str(
                theme
            ).strip().lower()

            if (
                theme
                and theme not in cleaned_themes
            ):
                cleaned_themes.append(
                    theme
                )

        if cleaned_themes:

            dataset["theme"] = (
                cleaned_themes
            )

    # --------------------------------------------------------
    # ACCESS RIGHTS
    # --------------------------------------------------------

    add_if_value(
        dataset,
        "accessRights",
        access_rights
    )

    # --------------------------------------------------------
    # ACCESS RESTRICTION
    # --------------------------------------------------------

    restriction = (
        build_access_restriction(
            access_restriction
        )
    )

    if restriction:

        # IMPORTANT:
        # accessRestriction is an ARRAY.
        dataset["accessRestriction"] = [
            restriction
        ]

    # --------------------------------------------------------
    # CUI RESTRICTION
    # --------------------------------------------------------

    cui = build_cui_restriction(
        cui_restriction
    )

    if cui:

        # CUIRestriction is currently an OBJECT.
        dataset["CUIRestriction"] = cui

    # --------------------------------------------------------
    # USE RESTRICTION
    # --------------------------------------------------------

    use = build_use_restriction(
        use_restriction
    )

    if use:

        # IMPORTANT:
        # useRestriction is an ARRAY.
        dataset["useRestriction"] = [
            use
        ]

    # --------------------------------------------------------
    # LICENSE
    # --------------------------------------------------------

    add_if_value(
        dataset,
        "license",
        license
    )
    # --------------------------------------------------------
    # --------------------------------------------------------
    # RIGHTS
    # --------------------------------------------------------

    rights_value = normalize_single_value(
        rights
    )

    rights_value = clean(
        rights_value
    )

    if rights_value is not None:

        dataset["rights"] = [
            rights_value
        ]

    # --------------------------------------------------------
    # TEMPORAL
    # --------------------------------------------------------

    temporal = build_temporal(
        temporal_start,
        temporal_end
    )

    if temporal:

        # IMPORTANT:
        # temporal is an ARRAY.
        dataset["temporal"] = temporal

    # --------------------------------------------------------
    # SPATIAL
    # --------------------------------------------------------

    spatial_object = build_spatial(
        spatial
    )

    if spatial_object:

        dataset["spatial"] = (
            spatial_object
        )

    # --------------------------------------------------------
    # MODIFIED
    # --------------------------------------------------------

    add_if_value(
        dataset,
        "modified",
        modified
    )

    # --------------------------------------------------------
    # DATA DICTIONARY
    # --------------------------------------------------------

    described_by = build_data_dictionary(
        data_dictionary
    )

    if described_by:

        dataset["describedBy"] = (
            described_by
        )

    # --------------------------------------------------------
    # LANDING PAGE
    # --------------------------------------------------------

    if landing_page:

        landing_page_object = (
            build_document(
                landing_page,
                "Dataset Landing Page"
            )
        )

        if landing_page_object:

            dataset["landingPage"] = (
                landing_page_object
            )

    # --------------------------------------------------------
    # INVENTORIED
    # --------------------------------------------------------

    dataset["inventoried"] = (
        datetime.date.today().isoformat()
    )

    return dataset


# ============================================================
# CATALOG
# ============================================================

def build_catalog(
    bureau_info,
    catalog_contact_name,
    catalog_contact_email,
    catalog_contact_phone,
    catalog_contact_organization,
    datasets
):
    """
    Build the complete DCAT-US Catalog.

    MVP currently includes:
        - Catalog
        - Dataset

    Dataservice and Dataseries are excluded.
    """

    # --------------------------------------------------------
    # BASE CATALOG
    # --------------------------------------------------------

    catalog = {

        "@context": (
            "https://resources.data.gov/"
            "schemas/dcat-us/v3.0/context.jsonld"
        ),

        "@type": "dcat:Catalog"
    }

    # --------------------------------------------------------
    # TITLE
    # --------------------------------------------------------

    catalog["title"] = (
        f"{bureau_info['publisher']} Data Catalog"
    )

    # --------------------------------------------------------
    # DESCRIPTION
    # --------------------------------------------------------

    catalog["description"] = (
        f"This is a catalog of "
        f"{bureau_info['publisher']} data."
    )

    # --------------------------------------------------------
    # HOMEPAGE
    # --------------------------------------------------------

    if bureau_info.get("homepage"):

        homepage = build_document(
            bureau_info["homepage"],
            f"{bureau_info['publisher']} Data Catalog Homepage"
        )

        if homepage:

            catalog["homepage"] = homepage

    # --------------------------------------------------------
    # PUBLISHER
    # --------------------------------------------------------

    catalog["publisher"] = {

        "@type": "org:Organization",

        "name": bureau_info["publisher"]
    }

    # --------------------------------------------------------
    # BUREAU CODE
    # --------------------------------------------------------

    if bureau_info.get("bureauCode"):

        catalog["bureauCode"] = (
            bureau_info["bureauCode"]
        )

    # --------------------------------------------------------
    # PROGRAM CODE
    # --------------------------------------------------------

    if bureau_info.get("programCode"):

        catalog["programCode"] = (
            bureau_info["programCode"]
        )

    # --------------------------------------------------------
    # CATALOG CONTACT
    # --------------------------------------------------------

    if catalog_contact_name:

        contact = build_contact(
            name=catalog_contact_name,
            email=catalog_contact_email,
            phone=catalog_contact_phone,
            organization=catalog_contact_organization
        )

        # DCAT-US expects an ARRAY.
        catalog["contactPoint"] = [
            contact
        ]

    # --------------------------------------------------------
    # DATASETS
    # --------------------------------------------------------

    catalog["dataset"] = datasets

    return catalog