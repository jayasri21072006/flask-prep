from flask import Flask, send_file, jsonify
from fetch_data import fetch_weather_data
from process_data import process_weather_data
from convert_data import convert_to_csv, convert_to_excel, convert_to_xml

app = Flask(__name__)


@app.route("/")
def home():
    return jsonify(
        {
            "message": "Weather API is running",
            "routes": ["/get_weather_data", "/download/csv", "/download/excel", "/download/xml"],
        }
    )


@app.route("/get_weather_data", methods=["GET"])
def get_weather_data():
    raw_data = fetch_weather_data()
    if raw_data is None:
        return jsonify({"error": "Failed to fetch weather data"}), 500

    processed_data = process_weather_data(raw_data)
    if isinstance(processed_data, dict) and "error" in processed_data:
        return jsonify(processed_data), 400

    csv_data = convert_to_csv(processed_data)
    excel_data = convert_to_excel(processed_data)
    xml_data = convert_to_xml(processed_data)
    return jsonify(
        {
            "message": "weather data",
            "csv_file": csv_data,
            "excel_file": excel_data,
            "xml_file": xml_data,
        }
    )


@app.route("/download/<file_type>", methods=["GET"])
def download_file(file_type):
    if file_type == "csv":
        return send_file("weather_data.csv", as_attachment=True)
    if file_type == "excel":
        return send_file("weather_data.xlsx", as_attachment=True)
    if file_type == "xml":
        return send_file("weather_data.xml", as_attachment=True)
    return jsonify({"error": "Invalid file type"}), 400


if __name__ == "__main__":
    app.run(debug=True)
