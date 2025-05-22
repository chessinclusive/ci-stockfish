import requests

url = "https://u5qcapulb8.execute-api.us-east-2.amazonaws.com/default/ci-stockfish/stockfish_evaluation"
params = {
    "fen_position": "4k2r/6r1/8/8/8/8/3R4/R3K3 w Qk - 0 1"
}
response = requests.get(url, params=params)
print(response.status_code)
print(response.text)