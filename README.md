# PI-AI TTS API

This project is a Flask-based API deployed on Vercel that provides text-to-speech functionality using the PI.AI service. It offers a single endpoint that accepts text input and a voice ID, returning the corresponding audio output.

## Features

1. Single API endpoint for text-to-speech conversion
2. Integration with PI.AI's TTS service
3. Support for multiple voice options (1-8)
4. Asynchronous processing for improved performance
5. Error handling and input validation

## Setup

1. Clone this repository.
2. Install the required dependencies:
   \```
   pip install -r requirements.txt
   \```
3. Create a `.env` file in the root directory and add your PI.AI session cookies:
   \```
   HOST_SESSION=your_host_session_value
   CF_BM=your_cf_bm_value
   \```
4. Deploy to Vercel:
   \```
   vercel
   \```

## Usage

Send a POST request to the `/api/tts` endpoint with the following JSON payload:

\```json
{
  "text": "Your text to convert to speech",
  "voice": "1"
}
\```

The `voice` parameter should be a string containing a number from 1 to 8, representing different voice options.

The API will return an MP3 file containing the generated speech.

## Security Considerations

- Ensure that the `.env` file is not committed to version control.
- Implement rate limiting to prevent abuse of the API.
- Consider adding authentication to the API endpoint.

## Scalability Enhancements

- Implement caching for frequently requested text-to-speech conversions.
- Use a message queue system for processing requests asynchronously.
- Set up a CDN for serving the generated audio files.

## Future Development

1. Add support for multiple languages and accents.
2. Implement a user system with customizable voice profiles.
3. Create a web interface for testing the API directly from a browser.
