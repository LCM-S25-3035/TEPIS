from deep_translator import GoogleTranslator

# Input from user: Adjective + Noun
sentence = input("Enter an English sentence (e.g. 'black cat'): ").lower()
words = sentence.split()

if len(words) == 2:
    adj, noun = words

    # Translate each word from English to French
    french_adj = GoogleTranslator(source='en', target='fr').translate(adj)
    french_noun = GoogleTranslator(source='en', target='fr').translate(noun)

    # Reorder for French (Noun comes before Adjective)
    french_sentence = f"{french_noun} {french_adj}"
    print("French:", french_sentence)
else:
    print("Please enter a two-word phrase (adjective + noun).")
