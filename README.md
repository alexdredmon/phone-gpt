# ☎️ PhoneGPT

Interface for conversational ChatGPT via SMS or audio call

To set up, acquire an [OpenAI API key](https://platform.openai.com/account/api-keys) and set it in `env.sh` - you'll also want to set PHONE_GPT_KEY to an arbitrary key of your choosing for highly rudimentary authentication.

To get started, create a virtual environment:
```bash
virtualenv venv
source venv/bin/activate.sh
```

Install requirements:
```bash
pip install -r requirements.txt
```

And start:
```bash
./start.sh
```

Wire up the corresponding Twilio Flow in Twilio Flow Studio, assign it to a number, and you're all set!