from fastapi import status

from app.crud.asset import get_asset_by_ticker
from app.crud.position import get_position_for_portfolio
from app.crud.transaction import get_transactions_for_portfolio
from app.models.transaction import TransactionType


#  PORTFOLIO ASSERTIONS
def assert_transaction_created(
        response,
        expected_transaction_id,
        expected_asset_id,
        expected_portfolio_id,
        expected_quantity,
        expected_type,
        expected_price_per_share
):
    body = response.json()[0]
    assert response.status_code == status.HTTP_200_OK
    assert body["id"] == str(expected_transaction_id)
    assert body["asset_id"] == str(expected_asset_id)
    assert body["type"] == TransactionType(expected_type)
    assert body["portfolio_id"] == str(expected_portfolio_id)
    assert float(body["quantity"]) == float(expected_quantity)
    assert float(body["price_per_share"]) == float(expected_price_per_share)


def assert_position_created(
        response,
        expected_position_id,
        expected_asset_id,
        expected_portfolio_id,
        expected_quantity,
        expected_price,
        expected_asset_ticker,
        expected_asset_name,
        expected_asset_type
):
    position = response.json()[0]
    asset = position["asset"]
    assert response.status_code == status.HTTP_200_OK
    assert position["id"] == str(expected_position_id)
    assert position["portfolio_id"] == str(expected_portfolio_id)
    assert float(position["quantity"]) == float(expected_quantity)
    assert float(position["average_buy_price"]) == float(expected_price)
    assert asset["id"] == str(expected_asset_id)
    assert asset["name"] == str(expected_asset_name)
    assert asset["ticker"] == expected_asset_ticker
    assert asset["asset_type"] == expected_asset_type


def assert_position_in_db(
        db_session,
        portfolio_id,
        expected_ticker,
        expected_qty,
        expected_price_per_share
):
    position = get_position_for_portfolio(db_session, portfolio_id)
    assert position is not None, "The position was not created in DB."
    assert position.asset.ticker == expected_ticker
    assert float(position.quantity) == expected_qty
    assert float(position.average_buy_price) == expected_price_per_share


def assert_transaction_in_db(
        db_session,
        expected_portfolio_id,
        expected_quantity
):
    transaction = get_transactions_for_portfolio(db_session, expected_portfolio_id)[0]
    assert transaction is not None, "The transaction was not recorded to the DB."
    assert transaction.type == TransactionType.BUY
    assert float(transaction.quantity) == expected_quantity


def assert_asset_in_db(
        db_session,
        expected_id,
        expected_ticket,
        expected_name,
        expected_asset_type
):
    asset = get_asset_by_ticker(db_session, expected_ticket)
    assert asset is not None, "The transaction was not recorded to the DB."
    assert asset.id == expected_id
    assert asset.name == expected_name
    assert asset.ticker == expected_ticket
    assert asset.asset_type == expected_asset_type


#  ASSETS ASSERTIONS
def assert_asset_created(
        response,
        expected_asset_id,
        expected_asset_name,
        expected_asset_type,
        expected_asset_ticker
):
    body = response.json()
    assert response.status_code == status.HTTP_200_OK, response.status_code
    assert body["name"] == expected_asset_name
    assert body["id"] == str(expected_asset_id)
    assert body["ticker"] == expected_asset_ticker
    assert body["asset_type"] == expected_asset_type
