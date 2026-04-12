import pandas as pd
from etl_pipeline import transform


def test_normal_data():
    df = pd.DataFrame({
        "email": ["a@test.com"],
        "gender": ["male"],
        "name.first": ["John"],
        "name.last": ["Doe"],
        "dob.age": [25],
        "dob.date": ["2000-01-01"],
        "nat": ["US"]
    })

    result = transform(df)

    assert result["age_group"].iloc[0] == "Young Adult"
    assert result["email_domain"].iloc[0] == "test.com"


def test_duplicates():
    df = pd.DataFrame({
        "email": ["a@test.com", "a@test.com"],
        "gender": ["male", "male"],
        "name.first": ["John", "John"],
        "name.last": ["Doe", "Doe"],
        "dob.age": [25, 25],
        "dob.date": ["2000-01-01", "2000-01-01"],
        "nat": ["US", "US"]
    })

    result = transform(df)
    assert len(result) == 1


def test_missing_email():
    df = pd.DataFrame({
        "email": [None],
        "gender": ["male"],
        "name.first": ["John"],
        "name.last": ["Doe"],
        "dob.age": [25],
        "dob.date": ["2000-01-01"],
        "nat": ["US"]
    })

    result = transform(df)
    assert result.empty


def test_empty_df():
    df = pd.DataFrame()
    result = transform(df)
    assert result.empty