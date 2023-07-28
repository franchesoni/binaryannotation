import requests
import time
import argparse
import random

def get_image():
    url = "http://localhost:8000/get_next_img"
    response = requests.get(url)
    if response.status_code == 200:
        return response.headers
    else:
        print(f"Erreur lors de l'appel API - Statut : {response.status_code}")
        return None
    
def annotate_image(data=None):
    url = "http://localhost:8000/add_annotation"
    response = requests.post(url, json=data)

    if response.status_code == 200:
        if response.text:
            return response.json()
        else:
            print("Réponse vide après un POST réussi.")
            return None
    else:
        print(f"Erreur lors de l'appel POST - Statut : {response.status_code}")
        return None


def true_mode(iterations):
    for i in range (iterations):
        data = get_image()
        time.sleep(0.2)
        body = {
            "image_index": data['image_index'],
            "is_positive": True,
            "file_name": data['file_name'],
        }
        result = annotate_image(data=body)
        time.sleep(0.3)

def false_mode(iterations):
    for i in range (iterations):
        data = get_image()
        time.sleep(0.2)
        body = {
            "image_index": data['image_index'],
            "is_positive": False,
            "file_name": data['file_name'],
        }
        result = annotate_image(data=body)
        time.sleep(0.3)

def random_mode(iterations):
    for i in range (iterations):
        is_positive = random.choice([True, False])
        data = get_image()
        time.sleep(0.2)
        body = {
            "image_index": data['image_index'],
            "is_positive": is_positive,
            "file_name": data['file_name'],
        }
        result = annotate_image(data=body)
        time.sleep(0.3)

def main():
    parser = argparse.ArgumentParser(description="Script with mode and number of iterations.")
    parser.add_argument("--mode", choices=["false_mode", "true_mode", "random_mode"], required=True, help="Choose the mode(false_mode, true_mode où random_mode)")
    parser.add_argument("--iterations", type=int, default=1, help="Number of iterations to execute (default: 1)")
    args = parser.parse_args()
    
    if args.mode == "random_mode":
        random_mode(args.iterations)
    elif args.mode == "true_mode":
        true_mode(args.iterations)
    elif args.mode == "false_mode":
        false_mode(args.iterations)



if __name__ == "__main__":
    main()
