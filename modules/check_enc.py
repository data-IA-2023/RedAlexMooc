import chardet

def check_enc(file:str):
    with open('sentiment_dataset/train.csv', 'rb') as f:
        result = chardet.detect(f.read())
    encoding = result['encoding']
    return encoding