import requests

url = "http://3.20.223.108:8000/stockfish_evaluation"
params = {
    "fen_position": "4k2r/6r1/8/8/8/8/3R4/R3K3 w Qk - 0 1"
}
response = requests.get(url, params=params)
print(response.status_code)
print(response.text)