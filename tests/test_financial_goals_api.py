"""
Tests for financial_goals API endpoint: /api/v1/financial_goals/
Pure computation – no external dependencies to mock.
"""

FINANCIAL_GOALS_API = "/api/v1/financial_goals"


class TestCalculateInvestmentHistory:
    """Tests for GET /api/v1/financial_goals/ (calculate_investment_history)."""

    def test_default_params_returns_200(self, client):
        """Default parameters should return a valid 200 response."""
        response = client.get(f"{FINANCIAL_GOALS_API}/")
        assert response.status_code == 200

    def test_returns_list(self, client):
        """Response should be a list of monthly records."""
        response = client.get(f"{FINANCIAL_GOALS_API}/")
        data = response.json()
        assert isinstance(data, list)

    def test_total_months_equals_years_times_12(self, client):
        """Number of records should equal years * 12."""
        years = 5
        response = client.get(
            f"{FINANCIAL_GOALS_API}/",
            params={"years": years},
        )
        data = response.json()
        assert len(data) == years * 12

    def test_record_data_structure(self, client):
        """Each record must have the expected keys."""
        response = client.get(
            f"{FINANCIAL_GOALS_API}/",
            params={"years": 1},
        )
        data = response.json()
        expected_keys = {"month", "label", "invested", "total_balance", "profit", "real_value"}
        for record in data:
            assert expected_keys == set(record.keys())

    def test_month_field_is_sequential(self, client):
        """Month numbers should be 1, 2, 3, …, total_months."""
        years = 2
        response = client.get(
            f"{FINANCIAL_GOALS_API}/",
            params={"years": years},
        )
        data = response.json()
        months = [r["month"] for r in data]
        assert months == list(range(1, years * 12 + 1))

    def test_label_set_every_12_months(self, client):
        """Label should be 'Рік N' only at month multiples of 12, empty otherwise."""
        response = client.get(
            f"{FINANCIAL_GOALS_API}/",
            params={"years": 2},
        )
        data = response.json()
        for record in data:
            if record["month"] % 12 == 0:
                year_num = record["month"] // 12
                assert record["label"] == f"Рік {year_num}"
            else:
                assert record["label"] == ""

    def test_invested_grows_monotonically(self, client):
        """Total invested should never decrease over time."""
        response = client.get(
            f"{FINANCIAL_GOALS_API}/",
            params={"years": 3},
        )
        data = response.json()
        invested_values = [r["invested"] for r in data]
        for i in range(1, len(invested_values)):
            assert invested_values[i] >= invested_values[i - 1]

    def test_profit_equals_balance_minus_invested(self, client):
        """Profit must equal total_balance - invested (within rounding)."""
        response = client.get(
            f"{FINANCIAL_GOALS_API}/",
            params={"years": 2},
        )
        data = response.json()
        for record in data:
            expected_profit = round(record["total_balance"] - record["invested"], 2)
            assert record["profit"] == expected_profit

    def test_custom_principal(self, client):
        """First month invested should include the principal + one monthly contribution."""
        principal = 5000
        monthly = 200
        response = client.get(
            f"{FINANCIAL_GOALS_API}/",
            params={"principal": principal, "monthly_contribution": monthly, "years": 1},
        )
        data = response.json()
        # After month 1: invested = principal + monthly_contribution
        assert data[0]["invested"] == principal + monthly

    def test_zero_return_rate(self, client):
        """With 0% annual return, total_balance should equal total invested."""
        principal = 1000
        monthly = 100
        years = 1
        response = client.get(
            f"{FINANCIAL_GOALS_API}/",
            params={
                "principal": principal,
                "monthly_contribution": monthly,
                "years": years,
                "annual_return": 0.0,
            },
        )
        data = response.json()
        last = data[-1]
        assert last["total_balance"] == last["invested"]
        assert last["profit"] == 0.0

    def test_real_value_less_than_balance_with_inflation(self, client):
        """With positive inflation and positive return, real_value should be < total_balance at end."""
        response = client.get(
            f"{FINANCIAL_GOALS_API}/",
            params={
                "years": 10,
                "annual_return": 0.12,
                "annual_inflation": 0.05,
            },
        )
        data = response.json()
        last = data[-1]
        # real_value accounts for tax + inflation, so it must be less than gross balance
        assert last["real_value"] < last["total_balance"]

    def test_zero_inflation_real_value(self, client):
        """With 0% inflation and 0% tax, real_value should equal total_balance."""
        response = client.get(
            f"{FINANCIAL_GOALS_API}/",
            params={
                "years": 1,
                "annual_return": 0.0,
                "annual_inflation": 0.0,
                "tax_rate": 0.0,
            },
        )
        data = response.json()
        for record in data:
            # No return → no profit → no tax; no inflation → real_value == balance
            assert record["real_value"] == record["total_balance"]

    def test_contribution_growth_increases_invested(self, client):
        """Higher contribution growth should result in more total invested."""
        params_base = {
            "principal": 1000,
            "monthly_contribution": 500,
            "years": 5,
            "annual_return": 0.0,
            "contribution_growth": 0.0,
        }
        params_growth = {**params_base, "contribution_growth": 0.10}

        resp_base = client.get(f"{FINANCIAL_GOALS_API}/", params=params_base)
        resp_growth = client.get(f"{FINANCIAL_GOALS_API}/", params=params_growth)

        invested_base = resp_base.json()[-1]["invested"]
        invested_growth = resp_growth.json()[-1]["invested"]

        assert invested_growth > invested_base


