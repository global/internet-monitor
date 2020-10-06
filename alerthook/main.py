from flask import Flask, request
import logging

app = Flask(__name__)
LOGGER = logging.getLogger('alerthook')


@app.route("/", methods=["GET", "POST"])
def echo():
    data = request.get_json()
    LOGGER.info(data)
    return data


if __name__ == "__main__":
    # Setting up logging
    LOGGER.setLevel("INFO")
    # create console handler with a higher log level
    CH = logging.StreamHandler()
    CH.setLevel('INFO')
    # create formatter and add it to the handlers
    FORMATTER = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    CH.setFormatter(FORMATTER)
    # add the handlers to the LOGGER and apscheduler LOGGER
    LOGGER.addHandler(CH)

    LOGGER.info("Starting alerthook on port 5000...")
    app.run(host='0.0.0.0')
