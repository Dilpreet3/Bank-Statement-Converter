from flask import jsonify
from models import Conversion
from utils import convert_pdf_to_excel
from flask_login import current_user

def handle_upload(file, user=None):
    filename = file.filename
    path = os.path.join("uploads", filename)
    file.save(path)

    output_filename = convert_pdf_to_excel(path)

    conversion = Conversion(
        user_id=user.id if user else None,
        pdf_path=path,
        excel_path=output_filename,
        status="READY" if output_filename else "PROCESSING"
    )
    db.session.add(conversion)
    db.session.commit()

    return jsonify([{
        "uuid": conversion.id,
        "filename": filename,
        "pdfType": "TEXT_BASED" if output_filename else "IMAGE_BASED",
        "state": "READY" if output_filename else "PROCESSING"
    }])

def get_upload_status(uuids):
    results = []
    for uuid in uuids:
        conv = Conversion.query.get(uuid)
        if conv:
            results.append({
                "uuid": conv.id,
                "filename": conv.pdf_path,
                "pdfType": "TEXT_BASED",
                "state": "READY",
                "numberOfPages": 1
            })
    return jsonify(results)

def convert_statements(uuids):
    results = []
    for uuid in uuids:
        conv = Conversion.query.get(uuid)
        if conv and conv.excel_path:
            df = pd.read_excel(os.path.join("outputs", conv.excel_path))
            results.append({"normalised": df.to_dict(orient="records")})
    return jsonify(results)

def set_password(passwords):
    results = []
    for item in passwords:
        results.append({
            "uuid": item['uuid'],
            "filename": "locked.pdf",
            "pdfType": "TEXT_BASED",
            "state": "READY",
            "numberOfPages": 3
        })
    return jsonify(results)

def get_user_info(user):
    return jsonify({
        "user": {
            "userId": user.id,
            "firstName": user.username,
            "email": user.email,
            "apiKey": user.id
        },
        "credits": {
            "paidCredits": user.paid_credits,
            "freeCredits": user.free_credits
        },
        "unlimitedCredits": user.unlimited_credits
    })
