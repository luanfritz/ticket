from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_healthcheck():
    response = client.get('/health')
    assert response.status_code == 200
    assert response.json()['status'] == 'ok'


def test_search_endpoint():
    response = client.get(
        '/api/v1/search',
        params={
            'origin': 'gru',
            'destination': 'rec',
            'date': '2026-03-10',
            'prefer_miles_program': 'LATAM_PASS',
        },
    )
    body = response.json()
    assert response.status_code == 200
    assert body['query']['origin'] == 'GRU'
    assert len(body['ranked_options']) >= 1
    assert body['strategic_recommendation']['strategy'] in {'CASH', 'MILES', 'SPLIT_TICKET'}


def test_promotions_and_alerts_endpoints():
    create = client.post('/api/v1/promotions', json={
        'route': 'gru-rec',
        'valid_from': '2026-03-01',
        'valid_to': '2026-03-31',
        'price_brl': 499.9,
        'source': 'crawler-test',
        'notes': 'promo de teste',
    })
    assert create.status_code == 200
    assert create.json()['route'] == 'GRU-REC'

    listed = client.get('/api/v1/promotions', params={'route': 'GRU-REC'})
    assert listed.status_code == 200
    assert len(listed.json()) >= 1

    alert = client.post('/api/v1/alerts', json={
        'route': 'gru-rec',
        'target_price_brl': 450,
        'email': 'user@example.com'
    })
    assert alert.status_code == 200
    assert alert.json()['route'] == 'GRU-REC'


def test_forecast_transfer_and_multicity_endpoints():
    history = client.get('/api/v1/history/GRU-REC')
    assert history.status_code == 200

    forecast = client.get('/api/v1/forecast/GRU-REC')
    assert forecast.status_code == 200
    assert 'trend' in forecast.json()

    bonus = client.post('/api/v1/simulate/transfer-bonus', json={'base_miles': 10000, 'bonus_percent': 80})
    assert bonus.status_code == 200
    assert bonus.json()['total_miles'] == 18000

    multicity = client.post('/api/v1/multicity/recommendation', json={'cities': ['gru', 'lis', 'mad'], 'date': '2026-04-10'})
    assert multicity.status_code == 200
    assert multicity.json()['estimated_total_brl'] > 0


def test_alert_check_endpoint():
    client.post('/api/v1/alerts', json={
        'route': 'GRU-REC',
        'target_price_brl': 500,
        'email': 'price@example.com'
    })
    checked = client.get('/api/v1/alerts/check', params={'route': 'gru-rec', 'price_brl': 450})
    assert checked.status_code == 200
    assert checked.json()['route'] == 'GRU-REC'
    assert len(checked.json()['triggered_alerts']) >= 1
