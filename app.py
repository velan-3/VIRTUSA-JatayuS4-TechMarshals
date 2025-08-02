# from flask import Flask,render_template_string,request,jsonify,send_from_directory,render_template
# from llmmodel import Model
# from imagetest import ImageDiseaseModel
# from location import get_nearby_venues
# from reportgen import graph
# from datetime import datetime
# import joblib
# import pandas as pd
# import sys,os,io
# from cryptography.fernet import Fernet

# model = Model()
# image_model = ImageDiseaseModel()
# print("Models Loaded...")
# app = Flask(__name__)

# @app.route('/',methods=['GET'])
# def home():
#     html = decrypt_html(resource_path("auth/index.enc"))
#     return render_template_string(html)

# @app.route('/asset/<path:filename>')
# def asset(filename):
#     return send_from_directory('asset', filename)

# @app.route('/aiassistant',methods=["GET","POST"])
# def llm():
#     user = request.json
#     print(user)
#     user_input = user["query"]
#     lang = user["lang"]
#     if not user_input:
#         return {"error": "Enter the input"}, 400

#     response = model.run_retrieval(user_input,lang) 
#     return {"answer": response}

# @app.route('/upload_img',methods=["POST"])
# def upload():
#     if 'image' not in request.files:
#         return jsonify({"error": "No image uploaded"}), 400

#     file = request.files["image"]
    
#     try:
#         image_bytes = file.read()
#         # print(image_bytes)
#         result = image_model.detect_image(image_bytes) 
#         print(result)
#         return jsonify(result)
#     except Exception as e:
#         print("Error processing image:", e)
#         return jsonify({"error": "Failed to process image"}), 500

# @app.route('/predictsymptom',methods=["POST"])
# def predictsymptom():
#     data = request.get_json()
#     # print(data)
#     data = {"Primary Symptom":data.get("prime"),
#             "Behavioral Change":data.get("behave"),
#             "Physical Symptom":data.get("physical"),
#             "Digestive Issue":data.get("digestive"),
#             "Other Symptom":data.get("other")}
#     # Load saved model components
#     model_bundle = joblib.load(decrypt_to_memory(resource_path("auth/disease_prediction_model.pkl.enc")))
#     model = model_bundle['model']
#     preprocessor = model_bundle['preprocessor']
#     label_encoder = model_bundle['label_encoder']
#     try:
#             user_df = pd.DataFrame([data])
#             # print(user_df)
#             user_encoded = preprocessor.transform(user_df)
#             probs = model.predict_proba(user_encoded)
#             # print(probs)
#             confidence = probs.max()
#             predicted_class = probs.argmax()
#             predicted_disease = label_encoder.inverse_transform([predicted_class])[0]
#             print(predicted_disease)
#             return jsonify({
#                 'prediction': predicted_disease,
#                 'confidence': round(float(confidence), 2)
#             })
        
#     except Exception as e:
#             print(e)
#             return jsonify({'error': str(e)}), 500


# @app.route('/vet_location',methods=["GET","POST"])
# def vet_location():
#     data = request.get_json()
#     print(data)
#     latitude = data.get("lat")
#     longitude = data.get("lng")

#     results = get_nearby_venues(latitude,longitude,5000,"veterinary","veterinary_clinic")
#     print(results)
#     return jsonify({"hospitals": results})
    
# @app.route('/reportgen',methods=['POST','GET'])
# def report():
#     try:
#             print("🚀 Triggered report generation from Flask")
#             state_in = {
#                 "messages": [
#                     {"role": "user", "content": "Generate a veterinary health report."}
#                 ]
#             }
#             start_time = datetime.now()
#             state_out = graph.invoke(state_in)
#             end_time = datetime.now()
#             print("Report generated")
#             return jsonify({
#                 "status": "success",
#                 "generated_in_seconds": (end_time - start_time).total_seconds(),
#                 "report_path": state_out["final_pdf"]
#             })
#     except Exception as e:
#             return jsonify({"status": "error", "message": str(e)}), 500
        
# @app.route('/report_assets/<path:filename>')
# def serve_pdf(filename):
#     return send_from_directory('report_assets', filename)     

# # @app.route('/favicon.ico')
# # def favicon():
# #     return send_from_directory(os.path.join(app.root_path, 'static'),
# #                             'favicon.ico')

# def resource_path(relative_path):
#         try:
#             base_path = sys._MEIPASS  # Cx_freeze
#         except AttributeError:
#             base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
#         return os.path.join(base_path, relative_path)


# def decrypt_to_memory(enc_path):
#     FERNET_KEY = b'oa5gUlGQ1SLRFHrpiYXkjajwYJddETxli4qXjrCjGnQ='  # 32-byte base64-encoded key
#     fernet = Fernet(FERNET_KEY)
#     with open(resource_path(enc_path), "rb") as f:
#         encrypted_data = f.read()
#     decrypted_data = fernet.decrypt(encrypted_data)
#     return io.BytesIO(decrypted_data)

# def decrypt_html(enc_path):
#     FERNET_KEY = b'oa5gUlGQ1SLRFHrpiYXkjajwYJddETxli4qXjrCjGnQ=' 
#     fernet = Fernet(FERNET_KEY)
#     with open(enc_path, "rb") as f:
#         encrypted_data = f.read()
#     decrypted_data = fernet.decrypt(encrypted_data)
#     return decrypted_data.decode("utf-8")

# if __name__ == "__main__":
#     app.run(debug = False)
# VeterinaryAssistant/app.py

from flask import Flask, render_template_string, request, jsonify, send_from_directory, send_file,render_template
from llmmodel import Model
from imagetest import ImageDiseaseModel
from location import get_nearby_venues
from reportgen import graph
from datetime import datetime
import joblib
import pandas as pd
import sys, os, io
from cryptography.fernet import Fernet
from flask_cors import CORS

class FlaskAppRunner:
    def __init__(self):
        self.model = Model()
        self.image_model = ImageDiseaseModel()
        self.app = Flask(__name__)
        # CORS(self.app)
        self._setup_routes()
        print("Models Loaded...")

    def _setup_routes(self):
        app = self.app

        @app.route('/', methods=['GET'])
        def home():
            html = self.decrypt_html(self.resource_path("auth/index.enc"))
            return render_template_string(html)

        @app.route('/asset/<path:filename>')
        def asset(filename):
            dir = self.resource_path('asset')
            return send_from_directory(dir, filename)

        @app.route('/aiassistant', methods=["GET", "POST"])
        def llm():
            try:
                user = request.get_json()
                user_input = user.get("query")
                lang = user.get("lang")
                print(user_input)
                if not user_input:
                    return jsonify({"error": "Enter the input"}), 400

                response = self.model.run_retrieval(user_input, lang)
                return jsonify({"answer": response})

            except Exception as e:
                print("❌ Error in /aiassistant:", e)
                return jsonify({"error": "Model error: " + str(e)}), 500

        @app.route('/upload_img', methods=["POST"])
        def upload():
            if 'image' not in request.files:
                return jsonify({"error": "No image uploaded"}), 400
            file = request.files["image"]
            try:
                image_bytes = file.read()
                result = self.image_model.detect_image(image_bytes)
                return jsonify(result)
            except Exception as e:
                return jsonify({"error": "Failed to process image"}), 500

        @app.route('/predictsymptom', methods=["POST"])
        def predictsymptom():
            data = request.get_json()
            data = {
                "Primary Symptom": data.get("prime"),
                "Behavioral Change": data.get("behave"),
                "Physical Symptom": data.get("physical"),
                "Digestive Issue": data.get("digestive"),
                "Other Symptom": data.get("other")
            }
            model_bundle = joblib.load(self.decrypt_to_memory(self.resource_path("auth/disease_prediction_model.pkl.enc")))
            model = model_bundle['model']
            preprocessor = model_bundle['preprocessor']
            label_encoder = model_bundle['label_encoder']
            try:
                user_df = pd.DataFrame([data])
                user_encoded = preprocessor.transform(user_df)
                probs = model.predict_proba(user_encoded)
                confidence = probs.max()
                predicted_class = probs.argmax()
                predicted_disease = label_encoder.inverse_transform([predicted_class])[0]
                return jsonify({
                    'prediction': predicted_disease,
                    'confidence': round(float(confidence), 2)
                })
            except Exception as e:
                return jsonify({'error': str(e)}), 500

        @app.route('/vet_location', methods=["POST"])
        def vet_location():
            data = request.get_json()
            latitude = data.get("lat")
            longitude = data.get("lng")
            results = get_nearby_venues(latitude, longitude, 5000, "veterinary", "veterinary_clinic")
            return jsonify({"hospitals": results})

        @app.route('/reportgen', methods=['POST', 'GET'])
        def report():
            try:
                state_in = {"messages": [{"role": "user", "content": "Generate a veterinary health report."}]}
                start_time = datetime.now()
                state_out = graph.invoke(state_in)
                end_time = datetime.now()
                return jsonify({
                    "status": "success",
                    "generated_in_seconds": (end_time - start_time).total_seconds(),
                    "report_path": state_out["final_pdf"]
                })
            except Exception as e:
                return jsonify({"status": "error", "message": str(e)}), 500

        @app.route('/report_assets/<path:filename>')
        def serve_pdf(filename):
            # report_dir = self.resource_path('report_assets')
            # return send_from_directory(os.path.join(os.getenv("TEMP"), "VeterinaryAssistant", "report_assets"), filename)
            report_dir = os.path.join(os.getenv("TEMP"), "VeterinaryAssistant", "report_assets")
            full_path = os.path.join(report_dir, filename)
            return send_from_directory(report_dir,filename)


    def run(self, port=5000):
        self.app.run(debug=False, port=port,use_reloader=False,threaded=True)
        # self.app.

    def resource_path(self, relative_path):
        try:
            base_path = sys._MEIPASS
        except AttributeError:
            base_path = getattr(sys, '_MEIPASS', os.path.abspath("."))
        return os.path.join(base_path, relative_path)

    def decrypt_to_memory(self, enc_path):
        FERNET_KEY = b'oa5gUlGQ1SLRFHrpiYXkjajwYJddETxli4qXjrCjGnQ='
        fernet = Fernet(FERNET_KEY)
        with open(enc_path, "rb") as f:
            encrypted_data = f.read()
        decrypted_data = fernet.decrypt(encrypted_data)
        return io.BytesIO(decrypted_data)

    def decrypt_html(self, enc_path):
        FERNET_KEY = b'oa5gUlGQ1SLRFHrpiYXkjajwYJddETxli4qXjrCjGnQ='
        fernet = Fernet(FERNET_KEY)
        with open(enc_path, "rb") as f:
            encrypted_data = f.read()
        decrypted_data = fernet.decrypt(encrypted_data)
        return decrypted_data.decode("utf-8")
# Optional standalone mode
# if __name__ == "__main__":
#     FlaskAppRunner().run()
