import mlflow
import mlflow.sklearn
from transformers import RobertaTokenizerFast, TFRobertaForSequenceClassification, pipeline
from langdetect import detect
import deep_translator

# Initialisation du tokenizer pour RoBERTa
tokenizer = RobertaTokenizerFast.from_pretrained("arpanghoshal/EmoRoBERTa")

# Initialisation du modèle RoBERTa pour la classification de séquences
model = TFRobertaForSequenceClassification.from_pretrained("arpanghoshal/EmoRoBERTa")

# Initialisation du pipeline pour l'analyse de sentiment avec le modèle RoBERTa
emotion_analysis = pipeline('sentiment-analysis', model='arpanghoshal/EmoRoBERTa')

# Fonction pour traduire un texte en anglais
def translate_to_en(text=""):
    langue = detect(text)
    translated_text = deep_translator.GoogleTranslator(source=langue, target='en').translate(text)
    return {'langue': langue, 'textTraduit': translated_text}

# Fonction pour traduire un texte en anglais et l'analyser pour l'émotion
def translate_and_analyse(text: str):
    trad = translate_to_en(text)
    emo = emotion_analysis(trad['textTraduit'])[0]['label']
    return {'text': text, 'traduction': trad['textTraduit'], "emotion": emo, "langue": trad["langue"], 'emoticon': sentiment_to_emoticon(emo)}

# Fonction pour traduire un texte en anglais et l'analyser pour l'émotion et le sentiment
def translate_and_analyse_sentiment(text: str):
    sentiment_dict = {
        "admiration": "positive",
        "amusement": "positive",
        "anger": "negative",
        "annoyance": "negative",
        "approval": "positive",
        "caring": "positive",
        "confusion": "neutral",
        "curiosity": "neutral",
        "desire": "neutral",
        "disappointment": "negative",
        "disapproval": "negative",
        "disgust": "negative",
        "embarrassment": "negative",
        "excitement": "positive",
        "fear": "negative",
        "gratitude": "positive",
        "grief": "negative",
        "joy": "positive",
        "love": "positive",
        "nervousness": "negative",
        "optimism": "positive",
        "pride": "positive",
        "realization": "neutral",
        "relief": "positive",
        "remorse": "negative",
        "sadness": "negative",
        "surprise": "neutral",
        "neutral": "neutral"
    }
    dict0 = translate_and_analyse(text)
    dict0["sentiment"] = sentiment_dict.get(dict0["emotion"].lower(), None)
    return dict0

def sentiment_to_emoticon(sentiment):
    emoticon_dict = {
        "admiration": "😍",
        "amusement": "😄",
        "anger": "😠",
        "annoyance": "😒",
        "approval": "👍",
        "caring": "❤️",
        "confusion": "😕",
        "curiosity": "🤔",
        "desire": "😏",
        "disappointment": "😞",
        "disapproval": "👎",
        "disgust": "🤢",
        "embarrassment": "😳",
        "excitement": "😃",
        "fear": "😨",
        "gratitude": "🙏",
        "grief": "😢",
        "joy": "😊",
        "love": "😍",
        "nervousness": "😬",
        "optimism": "😊",
        "pride": "😊",
        "realization": "😲",
        "relief": "😌",
        "remorse": "😔",
        "sadness": "😔",
        "surprise": "😮",
        "neutral": "😐"
    }

    return emoticon_dict.get(sentiment.lower(), None)

def translate_emotion_to_fr(emotion):
    emotion_dict = {
        "admiration": "admiration",
        "amusement": "amusement",
        "anger": "colère",
        "annoyance": "agacement",
        "approval": "approbation",
        "caring": "sollicitude",
        "confusion": "confusion",
        "curiosity": "curiosité",
        "desire": "désir",
        "disappointment": "déception",
        "disapproval": "désapprobation",
        "disgust": "dégoût",
        "embarrassment": "embarras",
        "excitement": "excitation",
        "fear": "peur",
        "gratitude": "gratitude",
        "grief": "chagrin",
        "joy": "joie",
        "love": "amour",
        "nervousness": "nervosité",
        "optimism": "optimisme",
        "pride": "fierté",
        "realization": "réalisation",
        "relief": "soulagement",
        "remorse": "remords",
        "sadness": "tristesse",
        "surprise": "surprise",
        "neutral": "neutre"
    }
    try:
        return emotion_dict[emotion.lower()]
    except:
        return None

if __name__ == "__main__":
    # Initialisation de MLflow
    mlflow.set_experiment("Text Analysis with Emotion Detection")

    with mlflow.start_run(run_name="translate_and_analyse_sentiment") as run:
        # Exemple d'utilisation de la fonction translate_and_analyse avec le texte "es increíble"
        text = "es increíble"
        emotion_labels = translate_and_analyse_sentiment(text)
        
        # Enregistrement des paramètres et métriques dans MLflow
        mlflow.log_param("text", text)
        mlflow.log_param("langue", emotion_labels['langue'])
        mlflow.log_param("traduction", emotion_labels['traduction'])
        mlflow.log_param("emotion", emotion_labels['emotion'])
        mlflow.log_param("sentiment", emotion_labels['sentiment'])
        mlflow.log_param("emoticon", emotion_labels['emoticon'])
        
        # Enregistrer le modèle dans MLflow
        mlflow.sklearn.save_model(model, "model")
        
        print(emotion_labels)
