import luisPython
import http.client, sys, os.path, json

def addUtterance():
    # Programmatic key, available in luis.ai under Account Settings
    LUIS_programmaticKey  = "c574439a46e64d8cb597879499ccf8f9"

    # ID of your LUIS app to which you want to add an utterance
    LUIS_APP_ID      = "6059c365-d88a-412b-8f33-d7393ba3bf9f"

    # The version number of your LUIS app
    LUIS_APP_VERSION = "0.1"

    # Update the host if your LUIS subscription is not in the West US region
    LUIS_HOST       = "westus.api.cognitive.microsoft.com"

    # uploadFile is the file containing JSON for utterance(s) to add to the LUIS app.
    # The contents of the file must be in this format described at: https://aka.ms/add-utterance-json-format
    UTTERANCE_FILE   = "./utterances.json"
    RESULTS_FILE     = "./utterances.results.json"

    luis = luisPython.LUISClient(LUIS_HOST, LUIS_APP_ID, LUIS_APP_VERSION,
                          LUIS_programmaticKey)

    try:
        if len(sys.argv) > 1:
            option = sys.argv[1].lower().lstrip("-")
            if option == "train":
                print("Adding utterance(s).")
                luis.add_utterances()   .write().raise_for_status()
                print("Added utterance(s). Requesting training.")
                luis.train()            .write().raise_for_status()
                print("Requested training. Requesting training status.")
                luis.status()           .write().raise_for_status()
            elif option == "status":
                print("Requesting training status.")
                luis.status().write().raise_for_status()
        else:
            print("Adding utterance(s).")
            luis.add_utterances().write().raise_for_status()
    except Exception as ex:
        luis.print()    # JSON response may have more details
        print("{0.__name__}: {1}".format(type(ex), ex))
    else:
        print("Success: results in", RESULTS_FILE)

